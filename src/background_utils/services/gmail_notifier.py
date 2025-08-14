from __future__ import annotations

import email
import imaplib
import os
import ssl
import threading
import time
from email.header import decode_header
from pathlib import Path
from typing import NamedTuple

from background_utils.config import load_settings
from background_utils.logging import logger, setup_logging


class EmailSummary(NamedTuple):
    sender: str
    subject: str
    timestamp: str


def _decode_email_header(header: str | None) -> str:
    """Decode email header that might be encoded."""
    if not header:
        return ""
    
    decoded_parts = decode_header(header)
    result = ""
    for part, encoding in decoded_parts:
        if isinstance(part, bytes):
            result += part.decode(encoding or 'utf-8', errors='replace')
        else:
            result += part
    return result.strip()


def _show_notification(title: str, message: str) -> None:
    """Show desktop notification using plyer (cross-platform)."""
    try:
        # Try to import and use plyer for cross-platform notifications
        from plyer import notification
        notification.notify(
            title=title,
            message=message,
            app_name="Background Utils",
            timeout=10,
        )
        logger.info(f"Notification shown: {title}")
    except ImportError:
        logger.warning("plyer not available, falling back to Windows toast")
        try:
            # Windows fallback using win10toast
            from win10toast import ToastNotifier
            toaster = ToastNotifier()
            toaster.show_toast(
                title,
                message,
                duration=10,
                threaded=True,
            )
            logger.info(f"Windows toast shown: {title}")
        except ImportError:
            logger.warning("No notification library available, logging only")
            logger.info(f"NOTIFICATION: {title} - {message}")


def _connect_gmail(email_address: str, password: str) -> imaplib.IMAP4_SSL:
    """Connect to Gmail using IMAP over SSL."""
    try:
        # Create SSL context
        context = ssl.create_default_context()
        
        # Connect to Gmail IMAP server
        mail = imaplib.IMAP4_SSL("imap.gmail.com", 993, ssl_context=context)
        mail.login(email_address, password)
        
        logger.info(f"Successfully connected to Gmail for {email_address}")
        return mail
    except Exception as exc:
        logger.error(f"Failed to connect to Gmail: {exc}")
        raise


def _get_new_emails(mail: imaplib.IMAP4_SSL, last_uid: int) -> tuple[list[EmailSummary], int]:
    """Get new emails since the last UID. Returns (emails, highest_uid_seen)."""
    try:
        # Select inbox
        mail.select("INBOX")
        
        # Search for emails with UID greater than last_uid
        search_criteria = f"UID {last_uid + 1}:*"
        logger.debug(f"Searching with criteria: {search_criteria}")
        _, message_ids = mail.uid("search", None, search_criteria)
        
        if not message_ids[0]:
            logger.debug("No new emails found")
            return [], last_uid
        
        found_uids = message_ids[0].split()
        logger.debug(f"Found UIDs: {[int(uid) for uid in found_uids]}")
        
        email_summaries = []
        highest_uid = last_uid
        
        for uid in message_ids[0].split():
            try:
                uid_int = int(uid)
                
                # Skip if this UID is not actually greater than last_uid
                if uid_int <= last_uid:
                    logger.debug(f"Skipping UID {uid_int} as it's not greater than last_uid {last_uid}")
                    continue
                
                highest_uid = max(highest_uid, uid_int)
                
                # Fetch the email using UID
                _, msg_data = mail.uid("fetch", uid, "(RFC822)")
                if not msg_data or not msg_data[0] or len(msg_data[0]) < 2:
                    continue
                email_body = msg_data[0][1]
                if not isinstance(email_body, bytes):
                    continue
                email_message = email.message_from_bytes(email_body)
                
                # Extract email details
                sender = _decode_email_header(email_message.get("From", ""))
                subject = _decode_email_header(email_message.get("Subject", "No Subject"))
                date = email_message.get("Date", "Unknown")
                
                email_summaries.append(EmailSummary(
                    sender=sender,
                    subject=subject,
                    timestamp=date
                ))
                
                logger.debug(f"New email UID {uid_int} from {sender}: {subject}")
                
            except Exception as exc:
                logger.warning(f"Error processing email UID {uid}: {exc}")
                continue
        
        return email_summaries, highest_uid
        
    except Exception as exc:
        logger.error(f"Error fetching new emails: {exc}")
        return [], last_uid


def _get_uid_cache_path() -> Path:
    """Get the path for storing the last seen UID."""
    localappdata = os.getenv("LOCALAPPDATA") or "."
    cache_dir = Path(localappdata) / "background-utils"
    cache_dir.mkdir(exist_ok=True)
    return cache_dir / "gmail_last_uid.txt"


def _save_last_uid(uid: int) -> None:
    """Save the last seen UID to cache file."""
    try:
        cache_path = _get_uid_cache_path()
        cache_path.write_text(str(uid))
        logger.debug(f"Saved last UID {uid} to {cache_path}")
    except Exception as exc:
        logger.warning(f"Failed to save last UID: {exc}")


def _load_last_uid() -> int:
    """Load the last seen UID from cache file."""
    try:
        cache_path = _get_uid_cache_path()
        if cache_path.exists():
            uid = int(cache_path.read_text().strip())
            logger.debug(f"Loaded last UID {uid} from {cache_path}")
            return uid
    except Exception as exc:
        logger.warning(f"Failed to load last UID: {exc}")
    
    logger.debug("No cached UID found, starting from 0")
    return 0


def _get_highest_uid(mail: imaplib.IMAP4_SSL) -> int:
    """Get the highest UID in the inbox."""
    try:
        mail.select("INBOX")
        _, message_ids = mail.search(None, "ALL")
        
        if not message_ids[0]:
            return 0
        
        # Get the last message ID and fetch its UID
        last_msg_id = message_ids[0].split()[-1]
        _, uid_data = mail.fetch(last_msg_id, "UID")
        
        if not uid_data or not uid_data[0]:
            return 0
        
        # Parse UID from response like: b'1 (UID 12345)'
        uid_response = uid_data[0]
        if isinstance(uid_response, bytes):
            uid_str = uid_response.decode().split()[-1].rstrip(')')
        elif isinstance(uid_response, tuple) and len(uid_response) >= 2:
            uid_str = str(uid_response[1]).split()[-1].rstrip(')')
        else:
            return 0
        return int(uid_str)
        
    except Exception as exc:
        logger.warning(f"Error getting highest UID, starting from 0: {exc}")
        return 0


def run(stop_event: threading.Event, check_interval_seconds: float = 60.0) -> None:
    """
    Gmail notification service that checks for new emails and shows desktop notifications.
    
    Required environment variables:
    - BGU_GMAIL_EMAIL: Gmail email address
    - BGU_GMAIL_PASSWORD: Gmail password or app password
    """
    setup_logging()
    settings = load_settings()
    
    # Get Gmail credentials from settings
    gmail_email = getattr(settings, 'gmail_email', None)
    gmail_password = getattr(settings, 'gmail_password', None)
    
    if not gmail_email or not gmail_password:
        logger.error(
            "Gmail credentials not configured. "
            "Set BGU_GMAIL_EMAIL and BGU_GMAIL_PASSWORD environment variables."
        )
        logger.info("For security, use an App Password instead of your main Gmail password.")
        return
    
    logger.info("Starting Gmail notification service")
    logger.info(f"Monitoring: {gmail_email}")
    logger.info(f"Check interval: {check_interval_seconds}s")
    
    mail_connection = None
    
    # Load last UID from cache, or get current highest UID if no cache
    last_uid = _load_last_uid()
    
    try:
        # Initial connection and setup
        mail_connection = _connect_gmail(gmail_email, gmail_password)
        
        # If no cached UID, get the current highest UID to avoid notifications for old emails
        if last_uid == 0:
            last_uid = _get_highest_uid(mail_connection)
            _save_last_uid(last_uid)
            logger.info(f"No cached UID, starting monitoring from current highest UID: {last_uid}")
        else:
            logger.info(f"Resuming monitoring from cached UID: {last_uid}")
        
        while not stop_event.is_set():
            try:
                # Skip if no connection
                if mail_connection is None:
                    logger.warning("No Gmail connection available, skipping check")
                    continue
                
                # Check for new emails
                new_emails, new_highest_uid = _get_new_emails(mail_connection, last_uid)
                
                if new_emails:
                    logger.info(f"Found {len(new_emails)} new email(s)")
                    
                    # Show notification for each new email
                    for email_summary in new_emails:
                        title = f"New Email from {email_summary.sender}"
                        message = f"Subject: {email_summary.subject}"
                        _show_notification(title, message)
                    
                    # Only update UID if we found emails with higher UIDs
                    if new_highest_uid > last_uid:
                        last_uid = new_highest_uid
                        _save_last_uid(last_uid)
                        logger.info(f"Updated and saved last_uid to: {last_uid}")
                    else:
                        logger.warning(f"Found emails but UID didn't increase: current={last_uid}, new={new_highest_uid}")
                else:
                    logger.debug(f"No new emails found (checking after UID {last_uid})")
                
            except Exception as exc:
                logger.error(f"Error during email check: {exc}")
                # Try to reconnect on error
                try:
                    if mail_connection:
                        mail_connection.close()
                        mail_connection.logout()
                except Exception:
                    pass
                
                try:
                    mail_connection = _connect_gmail(gmail_email, gmail_password)
                    logger.info("Reconnected to Gmail")
                except Exception as reconnect_exc:
                    logger.error(f"Failed to reconnect: {reconnect_exc}")
                    mail_connection = None
            
            # Sleep in small chunks to be responsive to stop_event
            end_time = time.time() + check_interval_seconds
            while time.time() < end_time and not stop_event.is_set():
                time.sleep(0.5)
    
    except Exception as exc:
        logger.exception(f"Gmail service crashed: {exc}")
        raise
    finally:
        # Clean up connection
        if mail_connection:
            try:
                mail_connection.close()
                mail_connection.logout()
                logger.info("Gmail connection closed")
            except Exception as exc:
                logger.warning(f"Error closing Gmail connection: {exc}")
        
        logger.info("Gmail notification service stopped")


def main() -> None:
    """
    Backward-compatible single-service entry point.
    """
    stop_event = threading.Event()
    try:
        run(stop_event)
    except KeyboardInterrupt:
        stop_event.set()


if __name__ == "__main__":
    main()
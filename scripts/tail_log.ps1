# Script to tail the background-utils log file
# Usage: .\scripts\tail_log.ps1

Write-Host "Tailing background-utils.log (last 20 lines, live updates)"
Write-Host "Press Ctrl+C to stop"
Write-Host ""

try {
    Get-Content -Path $env:LOCALAPPDATA\background-utils\background-utils.log -Tail 20 -Wait
} catch {
    Write-Host "Error: Could not access log file at $env:LOCALAPPDATA\background-utils\background-utils.log"
    Write-Host "Make sure the background-utils service is running and generating logs."
    Write-Host "Error details: $_"
    exit 1
}
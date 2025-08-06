#!/usr/bin/env bash
set -euo pipefail

ENV_FILE="${1:-.env}"
SERVICE="${2:-background-utils-service}"

if [[ -f "$ENV_FILE" ]]; then
  echo "Loading environment from $ENV_FILE"
  # shellcheck disable=SC2046
  export $(grep -v '^#' "$ENV_FILE" | xargs -d '\n')
fi

export PYTHONUNBUFFERED=1
echo "Starting service: $SERVICE"
python -m "$SERVICE"
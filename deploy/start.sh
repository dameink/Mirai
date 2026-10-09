#!/bin/sh
set -eu
# Free Render has one instance and no pre-deploy command: explicitly migrate here.
# Existing installations must be backed up/imported before enabling this command.
python -m db.manage upgrade
exec uvicorn main:app --host 0.0.0.0 --port "${PORT:-8000}" --workers 1 --no-access-log

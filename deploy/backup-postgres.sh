#!/bin/sh
set -eu
# Run on a trusted operator host; never put backups on a free Render filesystem.
: "${DATABASE_URL:?Set the PostgreSQL connection URL}"
: "${BACKUP_DIR:?Set a private backup directory outside the service}"
umask 077
mkdir -p "$BACKUP_DIR"
backup_file="$BACKUP_DIR/mirai-$(date -u +%Y%m%dT%H%M%SZ).dump"
if [ -e "$backup_file" ]; then echo 'Backup already exists' >&2; exit 1; fi
python3 - "$backup_file" <<'PYBACKUP'
import hashlib, os, pathlib, subprocess, sys, tempfile
from urllib.parse import urlsplit, unquote, parse_qsl
url = urlsplit(os.environ["DATABASE_URL"])
if url.scheme not in {"postgres", "postgresql", "postgresql+psycopg", "postgresql+psycopg2"}:
    raise SystemExit("Backup requires a PostgreSQL URL")
if not url.hostname or not url.path.strip("/"):
    raise SystemExit("Backup URL must specify a host and database")
env = {key: value for key, value in os.environ.items() if not key.startswith("PG")}
env["PGDATABASE"] = unquote(url.path.lstrip("/"))
for name, value in {"PGHOST": url.hostname, "PGPORT": url.port, "PGUSER": unquote(url.username or ""), "PGPASSWORD": unquote(url.password or "")}.items():
    if value is not None:
        env[name] = str(value)
allowed = {"sslmode", "sslrootcert", "sslcert", "sslkey", "connect_timeout", "channel_binding", "target_session_attrs", "options", "gssencmode"}
for key, value in parse_qsl(url.query):
    if key not in allowed:
        raise SystemExit("Unsupported PostgreSQL backup connection parameter: " + key)
    env[{"connect_timeout": "PGCONNECT_TIMEOUT", "channel_binding": "PGCHANNELBINDING", "target_session_attrs": "PGTARGETSESSIONATTRS"}.get(key, "PG" + key.upper())] = value
target = pathlib.Path(sys.argv[1])
# Publish only a checked, complete dump. Private temporary files share the same
# filesystem so publication is atomic; hard links also refuse to overwrite.
with tempfile.TemporaryDirectory(prefix=".mirai-backup-", dir=target.parent) as work:
    dump = pathlib.Path(work) / "backup.dump"
    subprocess.run(["pg_dump", "--format=custom", "--file=" + str(dump)], env=env, check=True)
    subprocess.run(["pg_restore", "--list", str(dump)], env=env, check=True, stdout=subprocess.DEVNULL)
    digest = hashlib.sha256()
    with dump.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    checksum = pathlib.Path(work) / "backup.sha256"
    checksum.write_text(digest.hexdigest() + "\n")
    os.link(dump, target)
    try:
        os.link(checksum, target.with_suffix(".sha256"))
    except BaseException:
        target.unlink()
        raise
print('Backup complete; verify restore in an isolated database before relying on it.')
PYBACKUP

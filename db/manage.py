"""Explicit schema, legacy import, and SQLite recovery commands.

Run imports with application writers stopped. Source JSON files are never modified.
"""
import argparse
from contextlib import closing
import hashlib
import json
import os
import sqlite3
from datetime import datetime
from pathlib import Path

from sqlalchemy import select
from db.database import engine, SessionLocal
from db.init_db import init_db, check_schema
from db.models import User, UserDocument
from core.state_store import FILES


def validate_payload(kind, payload):
    expected = list if kind == "learning_sessions" else dict
    if not isinstance(payload, expected):
        raise ValueError(f"{kind}: invalid document type")
    json.dumps(payload, allow_nan=False)
    if kind == "emotion":
        from core.emotion import DEFAULT_EMOTION
        state = payload.get("state")
        if not isinstance(state, dict) or not set(DEFAULT_EMOTION["state"]).issubset(state):
            raise ValueError("emotion: incomplete state")
        if any(not isinstance(v, (int, float)) or isinstance(v, bool) or not 0 <= v <= 100 for v in state.values()):
            raise ValueError("emotion: invalid state values")
    if kind == "relationship":
        for key in ("familiarity", "bond", "closeness", "affection", "respect", "comfort"):
            value = payload.get(key)
            if not isinstance(value, (int, float)) or isinstance(value, bool) or not 0 <= value <= 100:
                raise ValueError("relationship: invalid state values")
    if kind == "learning_sessions":
        seen = set()
        for record in payload:
            if not isinstance(record, dict) or not all(k in record for k in ("id", "goal", "mode", "difficulty", "created_at")):
                raise ValueError("learning_sessions: incomplete session")
            if not isinstance(record["id"], str) or record["id"] in seen:
                raise ValueError("learning_sessions: duplicate/invalid session id")
            seen.add(record["id"])
            for field in ("created_at", "completed_at"):
                if record.get(field) is not None:
                    datetime.fromisoformat(record[field])
    return payload


def import_legacy_state(directory, apply=False, session_factory=SessionLocal, skip_orphans=False):
    root = Path(directory)
    if not root.is_dir():
        raise ValueError("Legacy user directory does not exist")
    pending = []
    report = {"files": 0, "inserted": 0, "existing": 0, "dry_run": not apply, "orphan_directories": 0, "orphan_files": 0}
    with session_factory() as db:
        known = set(db.scalars(select(User.id)))
        # Parse/validate everything before writing anything.
        for user_dir in sorted(root.iterdir()):
            if not user_dir.is_dir() or user_dir.name.startswith("."):
                continue
            files = [(kind, user_dir / filename) for kind, filename in FILES.items() if (user_dir / filename).exists()]
            if files and user_dir.name not in known:
                if not skip_orphans:
                    raise ValueError(f"Legacy directory has no matching account: {user_dir.name}")
                report["orphan_directories"] += 1
                report["orphan_files"] += len(files)
                continue
            for kind, path in files:
                raw = path.read_bytes()
                try:
                    payload = validate_payload(kind, json.loads(raw))
                except (ValueError, TypeError, KeyError) as error:
                    raise ValueError(f"Invalid legacy file: {user_dir.name}/{path.name}") from error
                report["files"] += 1
                if db.get(UserDocument, (user_dir.name, kind)) is not None:
                    report["existing"] += 1
                    continue
                pending.append((user_dir.name, kind, payload, hashlib.sha256(raw).hexdigest()))
        report["inserted"] = len(pending)
        if apply:
            for user_id, kind, payload, digest in pending:
                db.add(UserDocument(user_id=user_id, kind=kind, payload=payload, source_digest=digest))
            db.commit()
    return report


def backup_sqlite(output, target_engine=engine):
    if target_engine.dialect.name != "sqlite":
        raise ValueError("For PostgreSQL use pg_dump and test pg_restore on an isolated database")
    output = Path(output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        with target_engine.connect() as source, closing(sqlite3.connect(output)) as destination:
            source.connection.driver_connection.backup(destination)
            if destination.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Backup integrity check failed")
        digest = hashlib.sha256(output.read_bytes()).hexdigest()
        return {"file": str(output), "sha256": digest}
    except BaseException:
        output.unlink(missing_ok=True)
        raise


def restore_sqlite(backup, output, digest):
    backup, output = Path(backup), Path(output)
    if hashlib.sha256(backup.read_bytes()).hexdigest() != digest:
        raise ValueError("Backup checksum mismatch")
    output.parent.mkdir(parents=True, exist_ok=True)
    fd = os.open(output, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    os.close(fd)
    try:
        with closing(sqlite3.connect(backup.resolve().as_uri() + "?mode=ro", uri=True)) as source, closing(sqlite3.connect(output)) as destination:
            source.backup(destination)
            if destination.execute("PRAGMA integrity_check").fetchone()[0] != "ok":
                raise ValueError("Restored database integrity check failed")
        return {"restored": str(output)}
    except BaseException:
        output.unlink(missing_ok=True)
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    commands.add_parser("upgrade")
    commands.add_parser("status")
    commands.add_parser("purge-deleted")
    importer = commands.add_parser("import-state")
    importer.add_argument("--directory", default=os.getenv("MIRAI_USER_DATA_DIR", "data/users"))
    importer.add_argument("--apply", action="store_true")
    importer.add_argument("--skip-orphans", action="store_true", help="Preserve unmatched files without importing them; report their counts")
    backup = commands.add_parser("backup-sqlite")
    backup.add_argument("--output", required=True)
    restore = commands.add_parser("restore-sqlite")
    restore.add_argument("--backup", required=True)
    restore.add_argument("--output", required=True)
    restore.add_argument("--sha256", required=True)
    args = parser.parse_args()
    if args.command == "upgrade":
        init_db()
        result = {"revision": check_schema()}
    elif args.command == "status":
        result = {"revision": check_schema()}
    elif args.command == "import-state":
        check_schema()
        result = import_legacy_state(args.directory, apply=args.apply, skip_orphans=args.skip_orphans)
    elif args.command == "purge-deleted":
        check_schema()
        from auth.deletion import purge_deleted_files
        result = purge_deleted_files()
    elif args.command == "backup-sqlite":
        result = backup_sqlite(args.output)
    else:
        result = restore_sqlite(args.backup, args.output, args.sha256)
    print(json.dumps(result, indent=2))


if __name__ == "__main__":
    main()

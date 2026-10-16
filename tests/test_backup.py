"""Backup failures must never publish a usable-looking dump."""
import os
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parents[1]


def test_failed_backup_leaves_no_final_dump(tmp_path):
    tools = tmp_path / 'bin'
    tools.mkdir()
    fake = tools / 'pg_dump'
    fake.write_text('#!/bin/sh\nfor arg in "$@"; do\n case "$arg" in --file=*) printf partial > "${arg#--file=}";; esac\ndone\nexit 1\n')
    fake.chmod(0o700)
    backups = tmp_path / 'backups'
    env = {**os.environ, 'PATH': str(tools) + os.pathsep + os.environ['PATH'],
           'DATABASE_URL': 'postgresql://test@127.0.0.1/example_test', 'BACKUP_DIR': str(backups)}
    result = subprocess.run(['sh', str(ROOT / 'deploy/backup-postgres.sh')], env=env, capture_output=True)
    assert result.returncode != 0
    assert list(backups.iterdir()) == []


def test_backup_rejects_implicit_database_host(tmp_path):
    backups = tmp_path / 'backups'
    env = {**os.environ, 'DATABASE_URL': 'postgresql:///example_test', 'BACKUP_DIR': str(backups)}
    result = subprocess.run(['sh', str(ROOT / 'deploy/backup-postgres.sh')], env=env, capture_output=True)
    assert result.returncode != 0
    assert b'host and database' in result.stderr
    assert list(backups.iterdir()) == []

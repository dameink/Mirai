"""Offline recovery rehearsal: synthetic data in a disposable local PostgreSQL cluster.

Run from the repository with the project Python and PostgreSQL binaries on PATH.
Never reads DATABASE_URL from the shell or connects to the deployed database.
"""
import hashlib
import json
import os
from pathlib import Path
import shutil
import socket
import subprocess
import tempfile
from datetime import datetime, timezone

import psycopg
from psycopg import sql

ROOT = Path(__file__).resolve().parents[1]


def run(args, env, **kwargs):
    return subprocess.run(args, env=env, cwd=ROOT, check=True, **kwargs)


def snapshot(url):
    result = {}
    with psycopg.connect(url) as connection:
        tables = connection.execute("SELECT tablename FROM pg_tables WHERE schemaname = 'public' ORDER BY tablename").fetchall()
        for (name,) in tables:
            rows = connection.execute(sql.SQL("SELECT row_to_json(t)::text FROM {} AS t").format(sql.Identifier(name))).fetchall()
            encoded = sorted(json.dumps(json.loads(row[0]), sort_keys=True) for row in rows)
            result[name] = {"rows": len(rows), "sha256": hashlib.sha256('\n'.join(encoded).encode()).hexdigest()}
    return result


def main():
    env = {key: value for key, value in os.environ.items() if not key.startswith("PG")}
    for executable in ('initdb', 'pg_ctl', 'createdb', 'pg_dump', 'pg_restore'):
        if not shutil.which(executable):
            raise SystemExit('Put PostgreSQL server/client binaries on PATH: missing ' + executable)
    with tempfile.TemporaryDirectory(prefix='mirai-recovery-') as directory:
        work = Path(directory)
        os.chmod(work, 0o700)
        with socket.socket() as listener:
            listener.bind(('127.0.0.1', 0))
            port = listener.getsockname()[1]
        cluster = work / 'cluster'
        run(['initdb', '-D', str(cluster), '-A', 'trust', '-U', 'mirai_recovery', '--no-locale', '--encoding=UTF8'], env, stdout=subprocess.DEVNULL)
        started = False
        try:
            run(['pg_ctl', '-D', str(cluster), '-l', str(work/'postgres.log'), '-o', f'-h 127.0.0.1 -p {port} -k {work}', '-w', 'start'], env, stdout=subprocess.DEVNULL)
            started = True
            env.update(PGHOST='127.0.0.1', PGPORT=str(port), PGUSER='mirai_recovery')
            for name in ('mirai_source_test', 'mirai_restored_test'):
                run(['createdb', name], env)
            source = f'postgresql://mirai_recovery@127.0.0.1:{port}/mirai_source_test'
            restored = source.replace('/mirai_source_test', '/mirai_restored_test')
            env['MIRAI_TEST_DATABASE_URL'] = source
            run([os.sys.executable, '-m', 'pytest', 'tests/test_release.py', '-q'], env)
            # Seed independently of test order, including Unicode and nested JSON.
            env['DATABASE_URL'] = source
            run([os.sys.executable, '-c', """
from db.database import SessionLocal
from db.models import User, Message, UserDocument
with SessionLocal() as db:
    user = User(email='recovery@example.invalid', password_hash='synthetic-not-a-login', email_verified=False)
    db.add(user)
    db.flush()
    db.add(Message(user_id=user.id, role='user', content='Recovery: Привет 🌱'))
    db.add(UserDocument(user_id=user.id, kind='recovery_fixture', payload={'nested': [1, None, '你好'], 'active': True}))
    db.commit()
"""], env)
            before = snapshot(source)
            assert before.get('users', {}).get('rows', 0) > 0
            assert before.get('messages', {}).get('rows', 0) > 0
            env.update(DATABASE_URL=source, BACKUP_DIR=str(work/'backups'))
            run(['sh', 'deploy/backup-postgres.sh'], env)
            backup, = (work/'backups').glob('*.dump')
            expected = backup.with_suffix('.sha256').read_text().strip()
            assert hashlib.sha256(backup.read_bytes()).hexdigest() == expected
            run(['pg_restore', '--exit-on-error', '--single-transaction', '--no-owner', '--dbname=mirai_restored_test', str(backup)], env)
            assert snapshot(restored) == before, 'Restored data differs from source'
            # Re-run schema validation against the restored copy in a fresh process.
            env['DATABASE_URL'] = restored
            run([os.sys.executable, '-m', 'db.manage', 'status'], env)
            report = {'verified_at': datetime.now(timezone.utc).isoformat(), 'result': 'passed', 'synthetic_data_only': True, 'postgres_client': subprocess.check_output(['pg_dump', '--version'], text=True).strip(), 'tables': before, 'backup_sha256': expected, 'scope': 'Isolated local PostgreSQL dump/restore with synthetic data; production backup scheduling and actual Neon restore not verified'}
            (ROOT/'core/postgres-recovery-result.json').write_text(json.dumps(report, indent=2)+'\n')
            print('RECOVERY PASSED: all table rows match; only synthetic local data was used.')
        finally:
            if started:
                run(['pg_ctl', '-D', str(cluster), '-m', 'fast', '-w', 'stop'], env, stdout=subprocess.DEVNULL)


if __name__ == '__main__':
    main()

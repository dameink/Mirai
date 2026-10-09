"""Offline API regressions. Never connects to the deployed service or an LLM."""
import os
import tempfile
from pathlib import Path
from unittest.mock import patch

sandbox = tempfile.TemporaryDirectory(prefix="mirai-release-tests-")
test_url = os.getenv("MIRAI_TEST_DATABASE_URL")
if test_url:
    from sqlalchemy.engine import make_url
    if not (make_url(test_url).database or "").endswith("_test"):
        raise RuntimeError("External test databases must end in _test; tests delete all their tables")
os.environ["DATABASE_URL"] = test_url or f"sqlite:///{sandbox.name}/test.db"
os.environ["MIRAI_USER_DATA_DIR"] = f"{sandbox.name}/users"
os.environ["MIRAI_EMAIL_DEV_MODE"] = "true"
os.environ["MIRAI_AUTO_MIGRATE"] = "true"

import pytest
from fastapi.testclient import TestClient
import main
from db.database import Base, engine, SessionLocal
from db.models import User, PasswordReset, Session as AuthSession, Message
from auth.password_reset import create_reset_code, verify_reset_code
from auth.service import create_auth_tokens
from core.learning import create_learning_context
from core.llm import LLMUnavailableError


@pytest.fixture
def client(monkeypatch, tmp_path):
    monkeypatch.chdir(tmp_path)
    monkeypatch.setattr("core.user_state.BASE_DIR", str(tmp_path / "users"))
    Base.metadata.drop_all(engine)
    with engine.begin() as connection:
        connection.exec_driver_sql("DROP TABLE IF EXISTS alembic_version")
    with TestClient(main.app) as client:
        with patch("auth.router.send_verification_email"), patch("auth.router.send_password_reset_email"):
            yield client


@pytest.fixture
def account(client):
    payload = {"email": "audit@example.com", "password": "Password-123"}
    assert client.post("/auth/register", json=payload).status_code == 201
    with SessionLocal() as db:
        user = db.query(User).one()
        user.email_verified = True
        db.commit()
        uid = user.id
    response = client.post("/auth/login", json=payload)
    assert response.status_code == 200
    tokens = response.json()
    return uid, {"Authorization": "Bearer " + tokens["access_token"]}, tokens


def test_registration_requires_verification_and_returns_no_tokens(client):
    payload = {"email": "new@example.com", "password": "Password-123"}
    response = client.post("/auth/register", json=payload)
    assert response.status_code == 201
    assert set(response.json()) == {"message"}
    assert client.post("/auth/login", json=payload).status_code == 403


def test_email_misconfiguration_does_not_create_account(client, monkeypatch):
    monkeypatch.setenv("MIRAI_EMAIL_DEV_MODE", "false")
    monkeypatch.setattr("auth.email_service.RESEND_API_KEY", None)
    response = client.post("/auth/register", json={"email": "new@example.com", "password": "Password-123"})
    assert response.status_code == 503
    with SessionLocal() as db:
        assert db.query(User).count() == 0


def test_push_registration_is_repeatable(client, account):
    _, headers, _ = account
    for _ in range(2):
        assert client.post("/notifications/register", headers=headers, json={"token": "ExponentPushToken[fake]", "platform": "ios"}).status_code == 200


def test_session_survives_requests_and_reset(client, account):
    _, headers, _ = account
    first = client.post("/learning/session/start", headers=headers).json()["session"]
    second = client.post("/learning/session/start", headers=headers).json()["session"]
    assert second["id"] == first["id"]
    history = client.get("/learning/history", headers=headers).json()
    assert len(history) == 1 and history[0]["id"] == first["id"]
    assert history[0]["activity"]
    assert client.delete("/reset", headers=headers).status_code == 200
    assert client.get("/learning/history", headers=headers).json() == []


def test_completed_session_persists(client, account):
    uid, _, _ = account
    context = create_learning_context(uid)
    context.learning.start_learning()
    context.learning.process_answer({"fluency": 75, "grammar": 70, "vocabulary": 80})
    reloaded = create_learning_context(uid)
    history = reloaded.learning.get_history()
    assert history[-1]["completed"] is True
    with pytest.raises(RuntimeError, match="already completed"):
        reloaded.learning.process_answer({"fluency": 75})


@pytest.mark.parametrize("message", ["", "   ", "x" * 4001])
def test_invalid_chat_cannot_earn_xp(client, account, message):
    _, headers, _ = account
    assert client.post("/chat", headers=headers, json={"message": message}).status_code == 422
    data = client.get("/gamification", headers=headers).json()
    assert data["xp"] == 0
    assert not any(a["unlocked"] for a in data["achievements"])


@pytest.mark.parametrize("mode,expected", [("Learning", "ACTIVE_LEARNING"), ("Casual", "CASUAL_CONVERSATION")])
def test_mobile_mode_reaches_response(client, account, mode, expected):
    _, headers, _ = account
    with patch("core.mirai.generate_response", return_value="Offline answer") as generate:
        response = client.post("/chat", headers=headers, json={"message": "I like learning English", "mode": mode})
    assert response.status_code == 200
    assert generate.call_args.kwargs["context"]["mode"] == expected


def test_llm_failure_is_not_saved_or_rewarded(client, account):
    _, headers, _ = account
    with patch("core.response.ask_llm", side_effect=LLMUnavailableError("offline")):
        response = client.post("/chat", headers=headers, json={"message": "Hello Mirai"})
    assert response.status_code == 503
    assert client.get("/conversation", headers=headers).json() == []
    assert client.get("/gamification", headers=headers).json()["xp"] == 0


def test_chat_success_persists_pair(client, account):
    _, headers, _ = account
    with patch("core.response.ask_llm", return_value="Hello from offline test"):
        assert client.post("/chat", headers=headers, json={"message": "Hello"}).status_code == 200
    history = client.get("/conversation", headers=headers).json()
    assert [m["role"] for m in history] == ["user", "assistant"]
    assert client.get("/gamification", headers=headers).json()["xp"] == 10


def test_password_reset_cooldown(client, account):
    for _ in range(3):
        assert client.post("/auth/forgot-password", json={"email": "audit@example.com"}).status_code == 200
    with SessionLocal() as db:
        assert db.query(PasswordReset).count() == 1


def test_old_reset_codes_and_replays_are_rejected(client, account):
    uid, _, _ = account
    with SessionLocal() as db:
        old = create_reset_code(db, uid)
        current = create_reset_code(db, uid)
        assert not verify_reset_code(db, uid, old)
        assert verify_reset_code(db, uid, current)
        assert not verify_reset_code(db, uid, old)
        assert not verify_reset_code(db, uid, current)


def test_reset_changes_password_and_revokes_sessions(client, account):
    uid, headers, _ = account
    with SessionLocal() as db:
        code = create_reset_code(db, uid)
    response = client.post("/auth/reset-password", json={"email": "audit@example.com", "code": code, "new_password": "Changed-123"})
    assert response.status_code == 200
    assert client.get("/auth/me", headers=headers).status_code == 401
    assert client.post("/auth/login", json={"email": "audit@example.com", "password": "Changed-123"}).status_code == 200
    assert client.post("/auth/reset-password", json={"email": "audit@example.com", "code": code, "new_password": "Changed-456"}).status_code == 400


def test_refresh_rotation_and_logout(client, account):
    _, headers, tokens = account
    response = client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]})
    assert response.status_code == 200
    assert client.get("/auth/me", headers=headers).status_code == 401
    assert client.post("/auth/refresh", json={"refresh_token": tokens["refresh_token"]}).status_code == 401
    new = response.json()
    assert client.post("/auth/logout", json={"refresh_token": new["refresh_token"]}).status_code == 200
    assert client.post("/auth/refresh", json={"refresh_token": new["refresh_token"]}).status_code == 401


def test_emotion_defaults_are_isolated(client):
    from core.emotion import change_emotion, get_emotion, DEFAULT_EMOTION
    with SessionLocal() as db:
        db.add_all([User(id="a", email="a@example.com", password_hash="unused"), User(id="b", email="b@example.com", password_hash="unused")])
        db.commit()
    before = DEFAULT_EMOTION["state"]["happiness"]
    change_emotion("happiness", 10, user_id="a")
    assert DEFAULT_EMOTION["state"]["happiness"] == before
    assert get_emotion(user_id="b")["state"]["happiness"] == before


def test_atomic_write_failure_preserves_previous_file(tmp_path):
    from core.persistence import atomic_write_json
    path = tmp_path / "state.json"
    atomic_write_json(path, {"value": 1})
    with pytest.raises(TypeError):
        atomic_write_json(path, {"value": object()})
    import json
    assert json.loads(path.read_text()) == {"value": 1}


def test_provider_ticket_error_is_not_success():
    from notifications.push import send_push_notification
    with patch("notifications.push.httpx.post") as post:
        post.return_value.json.return_value = {"data": {"status": "error", "details": {"error": "DeviceNotRegistered"}}}
        assert send_push_notification("fake", "title", "body")["success"] is False


def test_practice_can_finish_only_after_successful_chat(client, account):
    _, headers, _ = account
    session = client.post('/learning/session/start', headers=headers).json()['session']
    url = f"/learning/session/{session['id']}/complete"
    assert client.post(url, headers=headers).status_code == 409
    with patch('core.response.ask_llm', return_value='Offline practice reply'):
        assert client.post('/chat', headers=headers, json={'message': 'Today I studied English.', 'mode': 'Learning'}).status_code == 200
    result = client.post(url, headers=headers)
    assert result.status_code == 200
    assert result.json()['session']['completed'] is True
    assert result.json()['session']['message_count'] == 1
    assert client.post(url, headers=headers).json() == result.json()
    next_session = client.post('/learning/session/start', headers=headers).json()['session']
    assert next_session['id'] != session['id']


def test_conversation_pagination_preserves_order_and_user_isolation(client, account):
    uid, headers, _ = account
    from datetime import datetime, timezone
    instant = datetime.now(timezone.utc)
    with SessionLocal() as db:
        for index in range(105):
            db.add(Message(id=f'{index:036d}', user_id=uid, role='user', content=str(index), created_at=instant))
        db.commit()
    recent = client.get('/conversation', headers=headers).json()
    assert len(recent) == 100
    assert recent[0]['content'] == '5'
    older = client.get('/conversation', headers=headers, params={'before_id': recent[0]['id']}).json()
    assert [message['content'] for message in older] == ['0', '1', '2', '3', '4']
    assert client.get('/conversation?before_id=unknown', headers=headers).json() == []
    assert client.get('/conversation?limit=101', headers=headers).status_code == 422


def test_rate_limit_is_shared_by_database_sessions_and_expires(client):
    from core.rate_limit import admit_request
    from concurrent.futures import ThreadPoolExecutor
    with ThreadPoolExecutor(max_workers=8) as workers:
        allowed = list(workers.map(lambda _: admit_request('same-client', '/auth/login', now=100), range(30)))
    assert sum(allowed) == 20
    assert admit_request('same-client', '/auth/login', now=161)
    assert admit_request('another-client', '/auth/login', now=100)


def test_rate_limit_returns_429_before_work(client):
    from core.rate_limit import admit_request
    for _ in range(5):
        assert admit_request('testclient', '/auth/forgot-password')
    response = client.post('/auth/forgot-password', json={'email': 'unknown@example.com'})
    assert response.status_code == 429
    assert response.headers['Retry-After'] == '60'


def test_parallel_chats_preserve_conversation_and_learning_session(client, account):
    from concurrent.futures import ThreadPoolExecutor
    _, headers, _ = account
    client.post('/learning/session/start', headers=headers)
    with patch('core.response.ask_llm', return_value='Offline reply'), ThreadPoolExecutor(max_workers=4) as workers:
        statuses = list(workers.map(lambda i: client.post('/chat', headers=headers, json={'message': f'Today I learned English lesson {i}.'}).status_code, range(4)))
    assert statuses == [200] * 4
    assert len(client.get('/conversation', headers=headers).json()) == 8
    assert client.get('/learning/history', headers=headers).json()[0]['message_count'] == 4
    assert client.get('/gamification', headers=headers).json()['xp'] == 40


def test_user_state_is_in_database_not_files(client, account, tmp_path):
    from db.models import UserDocument
    uid, headers, _ = account
    assert client.get('/state', headers=headers).status_code == 200
    assert client.post('/learning/session/start', headers=headers).status_code == 200
    with SessionLocal() as db:
        kinds = {row.kind for row in db.query(UserDocument).filter_by(user_id=uid)}
    assert kinds == {'emotion', 'relationship', 'learning_memory', 'learning_sessions'}
    assert not (tmp_path / 'users' / uid).exists()


def test_model_failure_rolls_back_all_state_and_memories(client, account):
    from db.models import UserDocument, Memory, ChatReceipt
    uid, headers, _ = account
    client.get('/state', headers=headers)
    with SessionLocal() as db:
        before = {row.kind: row.payload for row in db.query(UserDocument).filter_by(user_id=uid)}
    with patch('core.response.ask_llm', side_effect=LLMUnavailableError('offline')):
        response = client.post('/chat', headers=headers, json={'message': 'I like learning English every day.', 'request_id': 'rollback-0001'})
    assert response.status_code == 503
    with SessionLocal() as db:
        assert {row.kind: row.payload for row in db.query(UserDocument).filter_by(user_id=uid)} == before
        assert db.query(Memory).count() == 0
        assert db.query(Message).count() == 0
        assert db.query(ChatReceipt).count() == 0


def test_late_failure_rolls_back_messages_and_state(client, account):
    from db.models import UserDocument
    _, headers, _ = account
    with patch('core.response.ask_llm', return_value='Offline answer'), patch('main.register_activity', side_effect=RuntimeError('simulated reward failure')):
        with pytest.raises(RuntimeError, match='simulated reward failure'):
            client.post('/chat', headers=headers, json={'message': 'I like English practice.'})
    with SessionLocal() as db:
        assert db.query(Message).count() == 0
        assert db.query(UserDocument).count() == 0


def test_duplicate_chat_has_one_answer_and_one_reward(client, account):
    _, headers, _ = account
    payload = {'message': 'Hello Mirai', 'request_id': 'retry-00001'}
    with patch('core.response.ask_llm', return_value='Offline answer') as llm:
        first = client.post('/chat', headers=headers, json=payload)
        second = client.post('/chat', headers=headers, json=payload)
    assert first.status_code == second.status_code == 200
    assert first.json() == second.json()
    assert llm.call_count == 1
    assert len(client.get('/conversation', headers=headers).json()) == 2
    assert client.get('/gamification', headers=headers).json()['xp'] == 10
    payload['message'] = 'Different message'
    assert client.post('/chat', headers=headers, json=payload).status_code == 409


def test_failed_chat_can_retry_same_identifier(client, account):
    _, headers, _ = account
    payload = {'message': 'Hello Mirai', 'request_id': 'retry-00002'}
    with patch('core.response.ask_llm', side_effect=LLMUnavailableError('offline')):
        assert client.post('/chat', headers=headers, json=payload).status_code == 503
    with patch('core.response.ask_llm', return_value='Recovered'):
        assert client.post('/chat', headers=headers, json=payload).status_code == 200
    assert len(client.get('/conversation', headers=headers).json()) == 2


def test_parallel_duplicate_chat_runs_once(client, account):
    from concurrent.futures import ThreadPoolExecutor
    _, headers, _ = account
    payload = {'message': 'Hello Mirai', 'request_id': 'parallel-retry-0001'}
    with patch('core.response.ask_llm', return_value='One answer') as llm, ThreadPoolExecutor(max_workers=4) as workers:
        responses = list(workers.map(lambda _: client.post('/chat', headers=headers, json=payload), range(4)))
    assert all(response.status_code == 200 for response in responses)
    assert llm.call_count == 1
    assert len(client.get('/conversation', headers=headers).json()) == 2


def legacy_files(tmp_path, uid):
    import json
    from copy import deepcopy
    from core.emotion import DEFAULT_EMOTION
    from core.relationship import DEFAULT_RELATIONSHIP
    directory = tmp_path / 'legacy' / uid
    directory.mkdir(parents=True)
    emotion = deepcopy(DEFAULT_EMOTION)
    emotion['state']['happiness'] = 88
    (directory / 'emotion.json').write_text(json.dumps(emotion))
    (directory / 'relationship.json').write_text(json.dumps(DEFAULT_RELATIONSHIP))
    (directory / 'learning_memory.json').write_text(json.dumps({'identity': {'native_language': 'Russian', 'learning_language': 'English'}}))
    (directory / 'learning_sessions.json').write_text('[]')
    return directory.parent


def test_import_is_dry_run_idempotent_and_preserves_originals(client, account, tmp_path):
    from db.manage import import_legacy_state
    from db.models import UserDocument
    uid, headers, _ = account
    directory = legacy_files(tmp_path, uid)
    originals = {str(p): p.read_bytes() for p in directory.rglob('*.json')}
    report = import_legacy_state(directory)
    assert report['inserted'] == 4 and report['dry_run']
    with SessionLocal() as db:
        assert db.query(UserDocument).count() == 0
    assert import_legacy_state(directory, apply=True)['inserted'] == 4
    assert client.get('/state', headers=headers).json()['emotion']['happiness'] == 88
    assert import_legacy_state(directory, apply=True)['existing'] == 4
    assert {str(p): p.read_bytes() for p in directory.rglob('*.json')} == originals
    client.delete('/reset', headers=headers)
    assert import_legacy_state(directory, apply=True)['existing'] == 4
    assert client.get('/state', headers=headers).json()['emotion']['happiness'] == 70


def test_invalid_import_makes_no_partial_changes(client, account, tmp_path):
    from db.manage import import_legacy_state
    from db.models import UserDocument
    uid, _, _ = account
    directory = legacy_files(tmp_path, uid)
    (directory / uid / 'learning_sessions.json').write_text('{broken')
    with pytest.raises(ValueError, match='Invalid legacy file'):
        import_legacy_state(directory, apply=True)
    with SessionLocal() as db:
        assert db.query(UserDocument).count() == 0


def test_unimported_legacy_state_is_not_silently_reset(client, account, tmp_path, monkeypatch):
    from db.models import UserDocument
    uid, headers, _ = account
    directory = legacy_files(tmp_path, uid)
    monkeypatch.setattr('core.user_state.BASE_DIR', str(directory))
    assert client.get('/state', headers=headers).status_code == 503
    with SessionLocal() as db:
        assert db.query(UserDocument).count() == 0


def test_fresh_migrations_match_orm_and_repeat_safely(tmp_path):
    from sqlalchemy import create_engine
    from db.init_db import init_db, check_schema
    from alembic.autogenerate import compare_metadata
    from alembic.runtime.migration import MigrationContext
    local = create_engine('sqlite:///' + str(tmp_path / 'fresh.db'))
    try:
        init_db(local)
        init_db(local)
        assert check_schema(local) == '0004_push_delivery'
        with local.connect() as connection:
            assert compare_metadata(MigrationContext.configure(connection), Base.metadata) == []
    finally:
        local.dispose()


def test_legacy_database_upgrade_keeps_accounts(tmp_path):
    from sqlalchemy import create_engine, inspect
    from db.init_db import init_db
    local = create_engine('sqlite:///' + str(tmp_path / 'old.db'))
    try:
        with local.begin() as connection:
            connection.exec_driver_sql('CREATE TABLE users (id VARCHAR(36) PRIMARY KEY, email VARCHAR(255) NOT NULL, password_hash VARCHAR(255) NOT NULL, created_at DATETIME NOT NULL)')
            connection.exec_driver_sql("INSERT INTO users VALUES ('old', 'old@example.com', 'kept-hash', '2026-01-01')")
        init_db(local)
        with local.connect() as connection:
            assert connection.exec_driver_sql('SELECT password_hash FROM users').scalar() == 'kept-hash'
        columns = {column['name'] for column in inspect(local).get_columns('users')}
        assert {'email_verified', 'notifications_enabled'}.issubset(columns)
    finally:
        local.dispose()


def test_backup_restore_preserves_state_and_prevents_overwrite(client, account, tmp_path):
    if engine.dialect.name != "sqlite":
        pytest.skip("SQLite backup implementation; PostgreSQL recovery uses pg_dump/pg_restore")
    from db.manage import backup_sqlite, restore_sqlite
    import sqlite3
    _, headers, _ = account
    client.get('/state', headers=headers)
    backup = tmp_path / 'backup.db'
    restored = tmp_path / 'restored.db'
    receipt = backup_sqlite(backup)
    restore_sqlite(backup, restored, receipt['sha256'])
    with sqlite3.connect(restored) as db:
        assert db.execute('SELECT count(*) FROM users').fetchone()[0] == 1
        assert db.execute('SELECT count(*) FROM user_documents').fetchone()[0] == 4
        assert db.execute('SELECT version_num FROM alembic_version').fetchone()[0] == '0004_push_delivery'
    with pytest.raises(FileExistsError):
        restore_sqlite(backup, restored, receipt['sha256'])
    with pytest.raises(ValueError, match='checksum'):
        restore_sqlite(backup, tmp_path / 'wrong.db', 'bad-checksum')


def test_clear_erases_receipt_content_and_prevents_replay(client, account):
    from db.models import ChatReceipt
    uid, headers, _ = account
    payload = {'message': 'Hello private conversation', 'request_id': 'clear-retry-0001'}
    with patch('core.response.ask_llm', return_value='Private answer'):
        assert client.post('/chat', headers=headers, json=payload).status_code == 200
    assert client.delete('/conversation', headers=headers).status_code == 200
    with SessionLocal() as db:
        assert db.get(ChatReceipt, (uid, payload['request_id'])).response is None
    assert client.post('/chat', headers=headers, json=payload).status_code == 409
    assert client.get('/conversation', headers=headers).json() == []


def test_tokens_are_hashed_and_digest_is_not_a_bearer(client, account):
    from auth.security import token_digest
    _, headers, tokens = account
    with SessionLocal() as db:
        session = db.query(AuthSession).one()
        assert session.access_token == token_digest(tokens['access_token'])
        assert session.refresh_token == token_digest(tokens['refresh_token'])
        digest = session.access_token
    assert client.get('/auth/me', headers=headers).status_code == 200
    assert client.get('/auth/me', headers={'Authorization': 'Bearer ' + digest}).status_code == 401


def test_account_deletion_requires_password_and_erases_only_owner(client, account, tmp_path):
    from db.models import UserDocument, Memory, EmotionalMemory, Notification, AccountErasureJob
    from auth.service import register_user
    from sqlalchemy import select, func
    uid, headers, tokens = account
    client.post('/notifications/register', headers=headers, json={'token': 'ExponentPushToken[delete]', 'platform': 'ios'})
    client.post('/learning/session/start', headers=headers)
    with patch('core.response.ask_llm', return_value='Hello'):
        assert client.post('/chat', headers=headers, json={'message': 'Hello', 'request_id': 'delete-chat-0001'}).status_code == 200
    with SessionLocal() as db:
        other = register_user(db, 'other@example.com', 'Password-456')
        other_id = other.id
        db.add(UserDocument(user_id=other_id, kind='learning_sessions', payload=[]))
        db.add(Memory(user_id=uid, memory_type='fact', content='Private'))
        db.add(EmotionalMemory(user_id=uid, emotion='happy', trigger='Private'))
        db.add(Notification(user_id=uid, type='test', title='Private', body='Private'))
        create_reset_code(db, uid)
        db.commit()
    directory = tmp_path / 'users' / uid
    directory.mkdir(parents=True)
    (directory / 'emotion.json').write_text('{"private": true}')
    assert client.request('DELETE', '/auth/account', headers=headers, json={'password': 'wrong'}).status_code == 403
    assert directory.exists()
    assert client.get('/auth/me', headers=headers).status_code == 200
    assert client.request('DELETE', '/auth/account', headers=headers, json={'password': 'Password-123'}).status_code == 204
    assert not directory.exists()
    with SessionLocal() as db:
        assert db.get(User, uid) is None
        assert db.get(User, other_id) is not None
        assert db.get(UserDocument, (other_id, 'learning_sessions')) is not None
        for table in Base.metadata.sorted_tables:
            if 'user_id' in table.c:
                assert db.scalar(select(func.count()).select_from(table).where(table.c.user_id == uid)) == 0
        assert db.query(AccountErasureJob).count() == 0
    assert client.get('/auth/me', headers=headers).status_code == 401
    assert client.post('/auth/refresh', json={'refresh_token': tokens['refresh_token']}).status_code == 401
    assert client.post('/auth/login', json={'email': 'audit@example.com', 'password': 'Password-123'}).status_code == 401


def test_failed_legacy_erasure_is_durable_and_retryable(client, account, tmp_path):
    from auth.deletion import purge_deleted_files
    from db.models import AccountErasureJob
    uid, headers, _ = account
    directory = tmp_path / 'users' / uid
    directory.mkdir(parents=True)
    (directory / 'private.json').write_text('{}')
    with patch('auth.deletion.shutil.rmtree', side_effect=OSError('simulated filesystem failure')):
        assert client.request('DELETE', '/auth/account', headers=headers, json={'password': 'Password-123'}).status_code == 204
    with SessionLocal() as db:
        assert db.get(User, uid) is None
        assert db.get(AccountErasureJob, uid) is not None
    assert directory.exists()
    assert purge_deleted_files() == {'completed': 1, 'pending': 0}
    assert not directory.exists()


def test_skip_orphans_is_explicit_and_preserves_unknown_data(client, account, tmp_path):
    from db.manage import import_legacy_state
    from db.models import UserDocument
    uid, _, _ = account
    directory = legacy_files(tmp_path, uid)
    unknown = directory / 'unknown-owner'
    unknown.mkdir()
    file = unknown / 'emotion.json'
    file.write_text('{"unmapped": true}')
    with pytest.raises(ValueError, match='no matching account'):
        import_legacy_state(directory, apply=True)
    with SessionLocal() as db:
        assert db.query(UserDocument).count() == 0
    report = import_legacy_state(directory, apply=True, skip_orphans=True)
    assert report['inserted'] == 4
    assert report['orphan_directories'] == report['orphan_files'] == 1
    assert file.read_text() == '{"unmapped": true}'


def test_concurrent_distinct_chats_keep_all_messages_and_rewards(client, account):
    from concurrent.futures import ThreadPoolExecutor
    import time
    from db.models import ChatReceipt
    uid, headers, _ = account
    def answer(*args, **kwargs):
        time.sleep(0.02)
        return 'Offline load test response'
    def send(index):
        return client.post('/chat', headers=headers, json={'message': 'Hello', 'request_id': f'load-test-{index:04d}'})
    with patch('core.response.ask_llm', side_effect=answer), ThreadPoolExecutor(max_workers=6) as pool:
        responses = list(pool.map(send, range(12)))
    assert [r.status_code for r in responses] == [200] * 12
    with SessionLocal() as db:
        assert db.query(Message).filter_by(user_id=uid).count() == 24
        assert db.query(ChatReceipt).filter_by(user_id=uid).count() == 12
    progress = client.get('/gamification', headers=headers).json()
    assert (progress['level'] - 1) * 100 + progress['xp'] == 120


def test_existing_tokens_survive_hash_migration(tmp_path):
    from datetime import datetime, timedelta, timezone
    from sqlalchemy import create_engine
    from sqlalchemy.orm import sessionmaker
    from alembic import command
    from db.init_db import migration_config, init_db
    from auth.service import get_user_from_access_token, get_session_by_refresh_token
    local = create_engine('sqlite:///' + str(tmp_path / 'tokens.db'))
    config = migration_config()
    try:
        with local.begin() as connection:
            config.attributes['connection'] = connection
            command.upgrade(config, '0002_user_state')
        factory = sessionmaker(bind=local)
        now = datetime.now(timezone.utc)
        with factory() as db:
            db.add(User(id='legacy-user', email='legacy@example.com', password_hash='unused'))
            db.commit()
            db.add(AuthSession(user_id='legacy-user', access_token='legacy-access', refresh_token='legacy-refresh', access_expires_at=now+timedelta(minutes=10), refresh_expires_at=now+timedelta(days=1)))
            db.commit()
        init_db(local)
        init_db(local)
        with factory() as db:
            assert get_user_from_access_token(db, 'legacy-access')['id'] == 'legacy-user'
            assert get_session_by_refresh_token(db, 'legacy-refresh') is not None
            assert db.query(AuthSession).one().access_token != 'legacy-access'
    finally:
        local.dispose()


def test_parallel_refresh_has_one_winner(client, account):
    from concurrent.futures import ThreadPoolExecutor
    _, _, tokens = account
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses = list(pool.map(lambda _: client.post('/auth/refresh', json={'refresh_token': tokens['refresh_token']}), range(4)))
    assert sorted(r.status_code for r in responses) == [200, 401, 401, 401]
    with SessionLocal() as db:
        assert db.query(AuthSession).filter_by(revoked=False).count() == 1


def test_delete_serializes_with_refresh(client, account):
    from concurrent.futures import ThreadPoolExecutor
    uid, headers, tokens = account
    with ThreadPoolExecutor(max_workers=2) as pool:
        deletion = pool.submit(client.request, 'DELETE', '/auth/account', headers=headers, json={'password': 'Password-123'})
        refresh = pool.submit(client.post, '/auth/refresh', json={'refresh_token': tokens['refresh_token']})
        deleted, refreshed = deletion.result(), refresh.result()
        assert deleted.status_code in (204, 401)
        assert refreshed.status_code in (200, 401)
    if deleted.status_code == 401:
        assert refreshed.status_code == 200
        fresh_headers = {'Authorization': 'Bearer ' + refreshed.json()['access_token']}
        assert client.request('DELETE', '/auth/account', headers=fresh_headers, json={'password': 'Password-123'}).status_code == 204
    with SessionLocal() as db:
        assert db.get(User, uid) is None
        assert db.query(AuthSession).filter_by(user_id=uid).count() == 0


def test_delete_password_attempts_are_rate_limited(client, account):
    _, headers, _ = account
    for _ in range(5):
        assert client.request('DELETE', '/auth/account', headers=headers, json={'password': 'wrong'}).status_code == 403
    assert client.request('DELETE', '/auth/account', headers=headers, json={'password': 'wrong'}).status_code == 429


def test_reset_failed_attempts_persist(client, account):
    uid, _, _ = account
    with SessionLocal() as db:
        code = create_reset_code(db, uid)
    wrong = '000000' if code != '000000' else '111111'
    for _ in range(5):
        assert client.post('/auth/reset-password', json={'email': 'audit@example.com', 'code': wrong, 'new_password': 'New-password-123'}).status_code == 400
    assert client.post('/auth/reset-password', json={'email': 'audit@example.com', 'code': code, 'new_password': 'New-password-123'}).status_code == 400
    with SessionLocal() as db:
        assert db.query(PasswordReset).one().attempts == 5


def test_preferences_persist_validate_and_are_account_scoped(client, account):
    from auth.service import register_user
    uid, headers, _ = account
    assert client.get('/preferences', headers=headers).json() == {'language': 'English', 'mode': 'Auto'}
    assert client.patch('/preferences', headers=headers, json={'language': 'Japanese', 'mode': 'Learning'}).status_code == 200
    assert client.get('/preferences', headers=headers).json()['language'] == 'Japanese'
    assert client.patch('/preferences', headers=headers, json={'mode': 'invalid'}).status_code == 422
    with SessionLocal() as db:
        other = register_user(db, 'preferences@example.com', 'Password-123')
        token, _ = create_auth_tokens(db, other.id)
    assert client.get('/preferences', headers={'Authorization': 'Bearer '+token}).json()['language'] == 'English'


def test_readiness_hides_database_errors(client):
    assert client.get('/health/live').status_code == 200
    assert client.get('/health/ready').status_code == 200
    with patch('core.operations.check_schema', side_effect=RuntimeError('secret connection string')):
        response = client.get('/health/ready')
    assert response.status_code == 503
    assert 'secret' not in response.text


def test_production_rejects_unsafe_configuration(monkeypatch):
    from core.operations import validate_environment
    monkeypatch.setenv('MIRAI_ENV', 'production')
    monkeypatch.setenv('MIRAI_EMAIL_DEV_MODE', 'true')
    with pytest.raises(RuntimeError, match='MIRAI_EMAIL_DEV_MODE'):
        validate_environment()


def test_push_registration_follows_rotation_and_logout(client, account):
    from db.models import PushToken
    _, headers, tokens = account
    assert client.post('/notifications/register', headers=headers, json={'token':'ExpoPushToken[device]', 'platform':'android'}).status_code == 200
    refreshed = client.post('/auth/refresh', json={'refresh_token':tokens['refresh_token']}).json()
    with SessionLocal() as db:
        registration = db.query(PushToken).one()
        assert db.get(AuthSession, registration.session_id).revoked is False
    assert client.post('/auth/logout', json={'refresh_token':refreshed['refresh_token']}).status_code == 200
    with SessionLocal() as db:
        assert db.query(PushToken).count() == 0


def test_push_receipt_removes_unregistered_device(client, account):
    from datetime import datetime, timedelta, timezone
    from db.models import PushReceipt, PushToken
    from notifications.worker import poll_receipts
    uid, headers, _ = account
    client.post('/notifications/register', headers=headers, json={'token':'ExpoPushToken[receipt]', 'platform':'android'})
    with patch('notifications.notifications.send_push_notification', return_value={'success':True, 'ticket_id':'ticket-one'}):
        assert client.post('/notifications/test', headers=headers).json()['success']
    with SessionLocal() as db:
        receipt = db.query(PushReceipt).one()
        receipt.created_at = datetime.now(timezone.utc)-timedelta(minutes=16)
        db.commit()
    with patch('notifications.worker.get_push_receipts', return_value={'ticket-one':{'status':'error','details':{'error':'DeviceNotRegistered'}}}):
        poll_receipts()
    with SessionLocal() as db:
        assert db.query(PushReceipt).count() == 0
        assert db.query(PushToken).count() == 0


def test_push_opt_out_never_calls_provider(client, account):
    _, headers, _ = account
    client.post('/notifications/register', headers=headers, json={'token':'ExpoPushToken[disabled]', 'platform':'android'})
    client.patch('/notifications/settings', headers=headers, json={'enabled':False})
    with patch('notifications.notifications.send_push_notification') as provider:
        assert client.post('/notifications/test', headers=headers).json()['success'] is False
        provider.assert_not_called()


def test_request_status_tracks_completion_and_clear(client, account):
    _, headers, _ = account
    path='/chat/requests/check-pending-1'
    assert client.get(path, headers=headers).json()['status'] == 'unknown'
    with patch('core.response.ask_llm', return_value='Hello'):
        assert client.post('/chat', headers=headers, json={'message':'Hello','request_id':'check-pending-1'}).status_code == 200
    assert client.get(path, headers=headers).json()['status'] == 'completed'
    client.delete('/conversation', headers=headers)
    assert client.get(path, headers=headers).json()['status'] == 'cleared'


def test_closed_beta_disables_email_flows_but_preserves_login(client, account, monkeypatch):
    monkeypatch.setenv("MIRAI_CLOSED_BETA", "true")
    uid, headers, tokens = account
    assert client.post("/auth/register", json={"email": "beta@example.com", "password": "Password-123"}).status_code == 503
    assert client.get("/auth/me", headers=headers).status_code == 200
    assert client.post("/auth/login", json={"email": "audit@example.com", "password": "Password-123"}).status_code == 200
    from auth.email_service import require_email_configuration
    from fastapi import HTTPException
    with pytest.raises(HTTPException) as error:
        require_email_configuration()
    assert error.value.status_code == 503


def test_closed_beta_production_still_requires_secure_configuration(monkeypatch):
    from core.operations import validate_environment
    monkeypatch.setenv("MIRAI_ENV", "production")
    monkeypatch.setenv("MIRAI_CLOSED_BETA", "true")
    monkeypatch.setenv("MIRAI_EMAIL_DEV_MODE", "true")
    with pytest.raises(RuntimeError, match="MIRAI_EMAIL_DEV_MODE"):
        validate_environment()

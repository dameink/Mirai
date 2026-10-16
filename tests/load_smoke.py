"""Bounded offline concurrency probe; only a dedicated *_test PostgreSQL database."""
import os, sys, time, json, uuid, tempfile
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import patch
from sqlalchemy.engine import make_url
url=os.environ.get('MIRAI_TEST_DATABASE_URL','')
parsed=make_url(url)
if not (parsed.get_backend_name() == 'postgresql' and (parsed.database or '').endswith('_test') and parsed.host in {'127.0.0.1', 'localhost', '::1'}):
    raise SystemExit('Concurrency probe requires a local PostgreSQL database ending in _test')
os.environ['DATABASE_URL']=url
os.environ['MIRAI_AUTO_MIGRATE']='true'
os.environ['MIRAI_EMAIL_DEV_MODE']='true'
os.environ['MIRAI_ENV']='test'
os.environ['MIRAI_CLOSED_BETA']='false'
sandbox = tempfile.TemporaryDirectory(prefix='mirai-load-')
os.environ['MIRAI_USER_DATA_DIR']=sandbox.name
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
from fastapi.testclient import TestClient
from db.database import SessionLocal
from db.models import User, Message, ChatReceipt, GamificationState, UserDocument
from auth.service import create_auth_tokens
import main
run=uuid.uuid4().hex
ids=[]; headers=[]
with TestClient(main.app, client=('load-'+run,12345)) as client:
    with SessionLocal() as db:
        for i in range(6):
            uid=str(uuid.uuid4()); ids.append(uid)
            db.add(User(id=uid,email=f'{run}-{i}@example.invalid',password_hash='disabled-load-account',email_verified=True)); db.commit()
            token,_=create_auth_tokens(db,uid); headers.append({'Authorization':'Bearer '+token})
    def answer(*args,**kwargs):
        time.sleep(0.1)
        return 'Offline load response'
    def send(i):
        start=time.perf_counter()
        response=client.post('/chat',headers=headers[i%6],json={'message':'Hello', 'request_id':f'{run}-{i}'})
        return response.status_code,time.perf_counter()-start
    start=time.perf_counter()
    with patch('core.response.ask_llm',side_effect=answer), ThreadPoolExecutor(max_workers=12) as pool:
        results=list(pool.map(send,range(24)))
    elapsed=time.perf_counter()-start
    assert all(status==200 for status,_ in results),[s for s,_ in results]
    with SessionLocal() as db:
        for uid in ids:
            assert db.query(Message).filter_by(user_id=uid).count()==8
            assert db.query(ChatReceipt).filter_by(user_id=uid).count()==4
            state=db.query(GamificationState).filter_by(user_id=uid).one()
            assert state.xp==40 and state.level==1
latencies=sorted(t for _,t in results)
report={'requests':24,'users':6,'concurrency':12,'errors':0,'mock_llm_ms':100,'p50_ms':round(latencies[11]*1000),'p95_ms':round(latencies[22]*1000),'elapsed_seconds':round(elapsed,3),'note':'Local ASGI probe with mocked LLM; not production capacity or network latency'}
print(json.dumps(report))

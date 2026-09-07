import time
from uuid import uuid4
from concurrent.futures import ThreadPoolExecutor
from threading import Event
import httpx
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.main import create_app
from app.db import Database
from app.camera import Camera
from app.recognition import RoboflowModel

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(Database(tmp_path/'scan.db'),camera=Camera(demo=True))) as c:
        yield c

def supplied(c,detections):
    return c.post('/api/recognition/candidates',json={'detections':detections})

def test_scan_lifecycle_confirmation_correction_and_duplicate(client):
    assert client.post('/api/recognition/scan').status_code==503
    client.post('/api/camera/start')
    result=client.post('/api/recognition/scan').json()
    assert result['mode']=='demo' and len(result['candidates'])==3
    cid=client.post('/api/carts').json()['id']
    assert client.get(f'/api/carts/{cid}').json()['total']==0
    candidate=result['candidates'][0]['candidate_id']
    body={'candidate_id':candidate,'product_id':2,'quantity':1}
    url=f'/api/carts/{cid}/items'
    headers={'Idempotency-Key':str(uuid4())}
    assert client.post(url,json=body,headers=headers).json()['total']==1800
    assert client.post(url,json=body,headers=headers).json()['item_count']==1
    assert client.post(url,json=body,headers={'Idempotency-Key':str(uuid4())}).status_code==409

def test_dismiss_expiry_missing_and_atomic_failure(client):
    cid=client.post('/api/carts').json()['id']
    def candidate():
        return supplied(client,[{'label':'egg','confidence':0.8}]).json()['candidates'][0]['candidate_id']
    first=candidate()
    assert client.post(f'/api/recognition/candidates/{first}/dismiss').status_code==200
    assert client.post(f'/api/recognition/candidates/{first}/dismiss').status_code==409
    second=candidate()
    with client.app.state.database.connect() as c:
        c.execute('UPDATE recognition_candidates SET expires_at=? WHERE id=?',(time.time()-1,second))
    for cand,expected in [(first,409),(second,409),('missing',404)]:
        r=client.post(f'/api/carts/{cid}/items',json={'product_id':1,'candidate_id':cand},headers={'Idempotency-Key':str(uuid4())})
        assert r.status_code==expected
    assert client.get(f'/api/carts/{cid}').json()['total']==0
    assert client.post('/api/recognition/candidates/missing/dismiss').status_code==404

def test_threshold_mapping_dedup_and_empty(client):
    r=supplied(client,[{'label':'egg','confidence':0.75},{'label':'egg','confidence':0.9},{'label':'tofu','confidence':0.749},{'label':'unknown','confidence':1}]).json()
    assert len(r['candidates'])==1 and r['candidates'][0]['confidence']==0.9
    assert len(supplied(client,[{'label':'egg','confidence':0.75}]).json()['candidates'])==1
    assert supplied(client,[]).json()['candidates']==[]
    assert supplied(client,[{'label':'egg','confidence':2}]).status_code==422
    assert supplied(client,[{'label':'egg','confidence':0.8,'width':-1}]).status_code==422

def test_model_timeout_invalid_response_and_secret_redaction():
    def timeout(request):
        raise httpx.ReadTimeout('secret-url',request=request)
    for handler,code in [(timeout,504),(lambda r:httpx.Response(200,json={'wrong':1}),502),(lambda r:httpx.Response(401),502),(lambda r:httpx.Response(200,json={'predictions':[{'class':'egg','confidence':2}]}),502)]:
        with httpx.Client(transport=httpx.MockTransport(handler)) as c:
            with pytest.raises(HTTPException) as error:
                RoboflowModel(client=c,model_id='my-model/1',api_key='private-secret').infer(b'jpeg')
            assert error.value.status_code==code
            assert 'private-secret' not in str(error.value.detail)

def test_model_http_contract_and_missing_configuration():
    def handler(request):
        assert request.url.path=='/my-model/2'
        assert request.content==b'anBlZw=='
        assert request.headers['Content-Type']=='application/x-www-form-urlencoded'
        return httpx.Response(200,json={'predictions':[{'class':'egg','confidence':0.9,'x':1,'y':2,'width':3,'height':4}]})
    with httpx.Client(transport=httpx.MockTransport(handler)) as c:
        assert RoboflowModel(client=c,model_id='my-model/2',api_key='test').infer(b'jpeg')[0].label=='egg'
    with pytest.raises(HTTPException) as error:
        RoboflowModel(api_key='',model_id='').infer(b'jpeg')
    assert error.value.status_code==503

def test_scan_lock_released_on_error(client):
    client.post('/api/camera/start')
    entered,finish=Event(),Event()
    original=client.app.state.model.infer
    def delayed(jpeg):
        entered.set()
        finish.wait(3)
        raise HTTPException(504,'timeout')
    client.app.state.model.infer=delayed
    with ThreadPoolExecutor() as pool:
        pending=pool.submit(client.post,'/api/recognition/scan')
        assert entered.wait(2)
        assert client.post('/api/recognition/scan').status_code==409
        finish.set()
        assert pending.result().status_code==504
    client.app.state.model.infer=original
    assert client.post('/api/recognition/scan').status_code==200

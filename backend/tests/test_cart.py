from concurrent.futures import ThreadPoolExecutor
from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.db import Database

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(Database(tmp_path/'cart.db'))) as client:
        yield client

def add(client,cid,pid=1,qty=1,key=None,**extra):
    return client.post(f'/api/carts/{cid}/items',json={'product_id':pid,'quantity':qty,**extra},headers={'Idempotency-Key':key or str(uuid4())})

def test_cart_crud_price_and_persistence(tmp_path):
    path=tmp_path/'persist.db'
    with TestClient(create_app(Database(path))) as c:
        assert c.get('/api/carts/active').status_code == 404
        cid=c.post('/api/carts').json()['id']
        assert c.post('/api/carts').json()['id'] == cid
        assert add(c,cid,qty=2).json()['total'] == 6400
        assert add(c,cid,pid=2).json()['total'] == 8200
        changed=c.patch(f'/api/carts/{cid}/items/1',json={'quantity':3}).json()
        assert changed['total']==11400 and changed['item_count']==4
    with TestClient(create_app(Database(path))) as c:
        assert c.get('/api/carts/active').json()['total']==11400
        assert c.delete(f'/api/carts/{cid}/items/2').json()['total']==9600
        assert c.delete(f'/api/carts/{cid}/items/1').json()['items']==[]


def test_duplicate_request_and_conflict(client):
    cid=client.post('/api/carts').json()['id']
    key=str(uuid4())
    first=add(client,cid,key=key)
    assert add(client,cid,key=key).json()==first.json()
    assert add(client,cid,qty=2,key=key).status_code==409
    assert client.get(f'/api/carts/{cid}').json()['item_count']==1


def test_concurrent_same_request_is_once(client):
    cid=client.post('/api/carts').json()['id']
    key=str(uuid4())
    with ThreadPoolExecutor(max_workers=4) as pool:
        responses=list(pool.map(lambda _:add(client,cid,key=key),range(4)))
    assert all(r.status_code==200 for r in responses)
    assert client.get(f'/api/carts/{cid}').json()['item_count']==1


@pytest.mark.parametrize('qty',[0,-1,1000,1.5,'2',True])
def test_quantity_validation(client,qty):
    cid=client.post('/api/carts').json()['id']
    assert add(client,cid,qty=qty).status_code==422
    assert client.patch(f'/api/carts/{cid}/items/1',json={'quantity':qty}).status_code==422


def test_missing_and_quantity_limit(client):
    cid=client.post('/api/carts').json()['id']
    assert add(client,'missing').status_code==404
    assert add(client,cid,pid=999).status_code==404
    assert client.delete(f'/api/carts/{cid}/items/1').status_code==404
    assert client.patch(f'/api/carts/{cid}/items/1',json={'quantity':1}).status_code==404
    assert add(client,cid,qty=999).status_code==200
    assert add(client,cid).status_code==409


def test_unit_price_is_snapshot(client):
    cid=client.post('/api/carts').json()['id']
    add(client,cid)
    with client.app.state.database.connect() as c:
        c.execute('UPDATE products SET price=1 WHERE id=1')
    assert add(client,cid).json()['total']==6400

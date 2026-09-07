from uuid import uuid4
import pytest
from fastapi.testclient import TestClient
from app.main import create_app
from app.db import Database

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(Database(tmp_path/'recipes.db'))) as c:
        yield c

def add(c,cid,pid):
    assert c.post(f'/api/carts/{cid}/items',json={'product_id':pid},headers={'Idempotency-Key':str(uuid4())}).status_code==200

def test_catalog_and_detail(client):
    recipes=client.get('/api/recipes').json()
    assert len(recipes)==14
    assert all(r['is_dummy'] and r['steps'] and r['ingredients'] for r in recipes)
    assert client.get('/api/recipes/1').json()==recipes[0]
    assert client.get('/api/recipes/999').status_code==404

def test_empty_and_unknown_cart(client):
    cid=client.post('/api/carts').json()['id']
    assert client.get(f'/api/carts/{cid}/recommendations').json()['recipes']==[]
    assert client.get('/api/carts/missing/recommendations').status_code==404

def test_required_optional_and_recalculation(client):
    cid=client.post('/api/carts').json()['id']
    for pid in [1,3,17]:
        add(client,cid,pid)
    data=client.get(f'/api/carts/{cid}/recommendations').json()
    ready=data['recipes'][0]
    assert ready['name']=='파계란탕' and ready['category']=='ready'
    assert ready['missing']==[] and ready['optional_missing']==['참기름']
    tofu=next(r for r in data['recipes'] if r['id']==2)
    assert tofu['missing']==['두부'] and tofu['category']=='almost'
    assert 1 not in [r['id'] for r in data['recipes']]
    client.delete(f'/api/carts/{cid}/items/17')
    changed=client.get(f'/api/carts/{cid}/recommendations').json()
    assert next(r for r in changed['recipes'] if r['id']==3)['missing']==['소금']
    assert changed['revision']>data['revision']

def test_no_matching_required_and_sort_stable(client):
    cid=client.post('/api/carts').json()['id']
    add(client,cid,18)
    assert client.get(f'/api/carts/{cid}/recommendations').json()['recipes']==[]
    add(client,cid,1)
    data=client.get(f'/api/carts/{cid}/recommendations').json()['recipes']
    assert data==sorted(data,key=lambda r:(len(r['missing']),-r['match_ratio'],r['cooking_time_minutes'],r['id']))
    assert all(r['matched'] and len(r['missing'])<=2 for r in data)

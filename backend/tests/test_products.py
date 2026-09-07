import pytest
from fastapi.testclient import TestClient
from app.db import Database
from app.main import create_app

@pytest.fixture
def client(tmp_path):
    with TestClient(create_app(Database(tmp_path / 'test.db'))) as c:
        yield c

def test_catalog_search_and_health(client):
    assert client.get('/api/health').json()['ok'] is True
    products = client.get('/api/products').json()
    assert len(products) == 18
    assert products[0]['ingredients'] == ['계란']
    assert client.get('/api/products',params={'q':'계란'}).json() == [products[0]]
    assert client.get('/api/products',params={'q':'없는상품'}).json() == []

def test_unknown_product_is_not_free(client):
    response = client.post('/api/cart/estimate',json={'items':[{'product_id':999,'quantity':1}]})
    assert response.status_code == 404

def test_estimate_empty_and_invalid(client):
    assert client.post('/api/cart/estimate',json={'items':[]}).json() == {'total':0,'item_count':0}
    assert client.post('/api/cart/estimate',json={'items':[{'product_id':1,'quantity':-1}]}).status_code == 422

def test_swagger_contract(client):
    assert client.get('/docs').status_code == 200
    spec=client.get('/openapi.json').json()
    assert spec['paths']['/api/products']['get']['tags'] == ['Products']
    assert spec['paths']['/api/cart/items']['post']['deprecated'] is True
    assert 'Product' in spec['components']['schemas']

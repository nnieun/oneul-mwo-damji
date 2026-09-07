import json
import time
from uuid import uuid4
from fastapi.testclient import TestClient
from app.main import create_app
from app.db import Database
from app.recognition import RoboflowModel


def test_complete_demo_and_swagger_contract(tmp_path):
    with TestClient(create_app(Database(tmp_path/'integration.db'),model=RoboflowModel(demo=True))) as c:
        spec=c.get('/openapi.json').json()
        expected={
            '/api/health':['get'],'/api/products':['get'],
            '/api/recognition/config':['get'],'/api/recognition/scan':['post'],'/api/recognition/candidates':['post'],'/api/recognition/candidates/{candidate_id}/dismiss':['post'],
            '/api/carts':['post'],'/api/carts/active':['get'],'/api/carts/{cart_id}':['get'],
            '/api/carts/{cart_id}/items':['post'],'/api/carts/{cart_id}/items/{product_id}':['patch','delete'],
            '/api/recipes':['get'],'/api/recipes/{recipe_id}':['get'],'/api/carts/{cart_id}/recommendations':['get'],
        }
        for path,methods in expected.items():
            for method in methods:
                operation=spec['paths'][path][method]
                assert operation['summary'] and '??' not in operation['summary']
                assert operation['tags']
                assert '200' in operation['responses']
                assert '404' in operation['responses']
        assert 'Idempotency-Key' in json.dumps(spec)
        assert c.get('/docs').status_code==200
        assert c.options('/api/carts',headers={'Origin':'http://localhost:8443','Access-Control-Request-Method':'POST','Access-Control-Request-Headers':'idempotency-key,content-type'}).status_code==200
        cid=c.post('/api/carts').json()['id']
        assert c.get('/api/recognition/config').json()['mode']=='demo'
        scan=c.post('/api/recognition/scan',files={'image':('frame.jpg',b'\xff\xd8\xff\xe0fake-browser-frame','image/jpeg')}).json()
        for candidate in scan['candidates']:
            r=c.post(f'/api/carts/{cid}/items',json={'product_id':candidate['product']['id'],'candidate_id':candidate['candidate_id']},headers={'Idempotency-Key':str(uuid4())})
            assert r.status_code==200
        assert c.get(f'/api/carts/{cid}').json()['total']==7500
        assert c.get(f'/api/carts/{cid}/recommendations').json()['recipes']


def test_model_specific_label_mapping_and_candidate_rollback(tmp_path,monkeypatch):
    monkeypatch.setenv('ROBOFLOW_MODEL_ID','demo-model/3')
    monkeypatch.setenv('ROBOFLOW_LABEL_MAP',json.dumps({'egg':2}))
    with TestClient(create_app(Database(tmp_path/'mapping.db'),model=RoboflowModel(demo=True))) as c:
        cid=c.post('/api/carts').json()['id']
        response=c.post('/api/recognition/candidates',json={'detections':[{'label':'egg','confidence':0.99}]})
        candidate=response.json()['candidates'][0]
        assert candidate['product']['id']==2
        # Invalid replacement product must not consume the pending candidate.
        assert c.post(f'/api/carts/{cid}/items',json={'product_id':999,'candidate_id':candidate['candidate_id']},headers={'Idempotency-Key':str(uuid4())}).status_code==404
        assert c.post(f'/api/carts/{cid}/items',json={'product_id':2,'candidate_id':candidate['candidate_id']},headers={'Idempotency-Key':str(uuid4())}).status_code==200

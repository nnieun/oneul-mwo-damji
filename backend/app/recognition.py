import base64
import json
import os
import re
from threading import Lock
import time
from uuid import uuid4
import httpx
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field, ValidationError
from .schemas import Product

class Detection(BaseModel):
    label: str = Field(min_length=1,max_length=200)
    confidence: float = Field(ge=0,le=1,allow_inf_nan=False)
    x: float | None = Field(default=None,ge=0,allow_inf_nan=False)
    y: float | None = Field(default=None,ge=0,allow_inf_nan=False)
    width: float | None = Field(default=None,ge=0,allow_inf_nan=False)
    height: float | None = Field(default=None,ge=0,allow_inf_nan=False)

class RecognitionRequest(BaseModel):
    detections: list[Detection] = Field(default_factory=list,max_length=1000)
    confidence_threshold: float = Field(default=0.75,ge=0,le=1)

class Candidate(BaseModel):
    candidate_id: str
    product: Product
    confidence: float
    position: dict[str,float | None]
    status: str
    expires_at: float = Field(description='만료 시각, Unix seconds')

class RecognitionResponse(BaseModel):
    scan_id: str
    candidates: list[Candidate]
    mode: str
    message: str

class RoboflowModel:
    def __init__(self, demo=False, client=None, model_id=None, api_key=None):
        self.demo=demo
        self.model_id=model_id if model_id is not None else os.getenv('ROBOFLOW_MODEL_ID','')
        self.api_key=api_key if api_key is not None else os.getenv('ROBOFLOW_API_KEY','')
        self.client=client

    def infer(self,jpeg):
        if self.demo:
            return [Detection(label=label,confidence=confidence,x=100+idx*150,y=200,width=100,height=140) for idx,(label,confidence) in enumerate([('egg',0.96),('tofu',0.91),('green_onion',0.87)])]
        if not self.api_key or not re.fullmatch(r'[A-Za-z0-9_-]+/\d+',self.model_id):
            raise HTTPException(503,'Roboflow 모델 ID와 API 키를 백엔드 환경변수에 설정해 주세요.')
        def call(client):
            response=client.post(f'https://detect.roboflow.com/{self.model_id}',params={'api_key':self.api_key,'confidence':0},content=base64.b64encode(jpeg),headers={'Content-Type':'application/x-www-form-urlencoded'},timeout=15)
            response.raise_for_status()
            data=response.json()
            predictions=data['predictions']
            if not isinstance(predictions,list) or len(predictions)>1000:
                raise ValueError('invalid predictions')
            return [Detection(label=p['class'],**{k:p[k] for k in ['confidence','x','y','width','height'] if k in p}) for p in predictions]
        try:
            if self.client:
                return call(self.client)
            with httpx.Client() as client:
                return call(client)
        except httpx.TimeoutException:
            raise HTTPException(504,'모델 응답 시간이 초과되었습니다. 다시 스캔해 주세요.') from None
        except (httpx.HTTPError,ValueError,KeyError,TypeError,ValidationError):
            # Never expose provider request URLs (which contain the API key).
            raise HTTPException(502,'모델 응답을 처리할 수 없습니다. 모델 설정과 연결 상태를 확인해 주세요.') from None


def configure_labels(db, model):
    mapping=json.loads(os.getenv('ROBOFLOW_LABEL_MAP','{}'))
    if not isinstance(mapping,dict):
        raise ValueError('ROBOFLOW_LABEL_MAP must be an object of label: product_id')
    with db.connect() as c:
        for label,pid in mapping.items():
            if not isinstance(label,str) or type(pid) is not int or not c.execute('SELECT 1 FROM products WHERE id=?',(pid,)).fetchone():
                raise ValueError('ROBOFLOW_LABEL_MAP contains an invalid label or product ID')
            c.execute('INSERT INTO product_labels VALUES (?,?,?) ON CONFLICT(model_version,label) DO UPDATE SET product_id=excluded.product_id',(model.model_id,label,pid))


def router(db,camera,model):
    api=APIRouter(prefix='/api/recognition',tags=['Recognition'])
    scan_lock=Lock()
    threshold=float(os.getenv('CONFIDENCE_THRESHOLD','0.75'))
    if not 0<=threshold<=1:
        raise ValueError('CONFIDENCE_THRESHOLD must be between 0 and 1')

    def candidates(detections,threshold,mode):
        now=time.time()
        scan_id=str(uuid4())
        products={p['id']:p for p in db.products()}
        with db.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            c.execute("UPDATE recognition_candidates SET status='expired' WHERE status='pending' AND expires_at<=?",(now,))
            rows=c.execute('SELECT * FROM product_labels WHERE model_version IN (?,?) ORDER BY CASE WHEN model_version=? THEN 1 ELSE 0 END',('*',model.model_id,model.model_id)).fetchall()
            mapping={row['label']:row['product_id'] for row in rows}
            best={}
            for detection in detections:
                pid=mapping.get(detection.label)
                if pid in products and detection.confidence>=threshold and (pid not in best or detection.confidence>best[pid].confidence):
                    best[pid]=detection
            results=[]
            for pid,detection in sorted(best.items()):
                cid=str(uuid4())
                position=detection.model_dump(exclude={'label','confidence'})
                c.execute('INSERT INTO recognition_candidates VALUES (?,?,?,?,?,?,?)',(cid,scan_id,pid,detection.confidence,json.dumps(position),'pending',now+120))
                results.append(dict(candidate_id=cid,product=products[pid],confidence=detection.confidence,position=position,status='pending',expires_at=now+120))
            return dict(scan_id=scan_id,candidates=results,mode=mode,message=f'{len(results)}개 후보를 확인해 주세요.' if results else '등록된 상품을 인식하지 못했습니다. 다시 스캔하거나 직접 선택해 주세요.')

    @api.post('/scan',response_model=RecognitionResponse,summary='최신 카메라 프레임으로 상품 인식',description='추론 요청은 한 번에 하나만 처리합니다. 후보는 120초 동안 유효하며 장바구니에 자동 추가하지 않습니다.')
    def scan():
        if not scan_lock.acquire(blocking=False):
            raise HTTPException(409,'이미 인식 중입니다. 잠시 기다려 주세요.')
        try:
            jpeg=camera.snapshot()
            return candidates(model.infer(jpeg),threshold,'demo' if model.demo else 'live')
        finally:
            scan_lock.release()

    @api.post('/candidates',response_model=RecognitionResponse,summary='외부 탐지 결과를 상품 후보로 변환',description='전달된 라벨·신뢰도를 검증하는 연동용 API. 직접 추론하지 않으며 mode=supplied로 구분합니다.')
    def from_results(body: RecognitionRequest):
        return candidates(body.detections,body.confidence_threshold,'supplied')

    @api.post('/candidates/{candidate_id}/dismiss',response_model=Candidate,summary='인식 후보 제외')
    def dismiss(candidate_id: str):
        with db.connect() as c:
            c.execute('BEGIN IMMEDIATE')
            row=c.execute('SELECT * FROM recognition_candidates WHERE id=?',(candidate_id,)).fetchone()
            if not row:
                raise HTTPException(404,'후보를 찾을 수 없습니다.')
            if row['status']!='pending' or row['expires_at']<=time.time():
                raise HTTPException(409,'처리되었거나 만료된 후보입니다.')
            c.execute("UPDATE recognition_candidates SET status='dismissed' WHERE id=?",(candidate_id,))
            product=next(p for p in db.products() if p['id']==row['product_id'])
            return dict(candidate_id=candidate_id,product=product,confidence=row['confidence'],position=json.loads(row['position']),status='dismissed',expires_at=row['expires_at'])
    return api

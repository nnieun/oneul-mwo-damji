"""One capture worker owns the device; every client shares the latest JPEG."""
import os
from threading import Event, Lock, Thread
import time
import cv2
import numpy as np
from fastapi import APIRouter, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel

class CameraStatus(BaseModel):
    state: str
    mode: str
    message: str

class DemoCapture:
    def isOpened(self):
        return True
    def read(self):
        frame=np.zeros((480,640,3),dtype=np.uint8)
        frame[:]=(40,31,25)
        cv2.putText(frame,'DEMO CAMERA - NOT LIVE',(30,210),cv2.FONT_HERSHEY_SIMPLEX,0.8,(255,255,255),2)
        cv2.putText(frame,'Sample: egg / tofu / green onion',(30,255),cv2.FONT_HERSHEY_SIMPLEX,0.6,(100,190,255),1)
        return True,frame
    def release(self):
        pass

class Camera:
    def __init__(self, demo=False, device=0, factory=None):
        self.demo=demo
        self.factory=factory or (lambda: DemoCapture() if demo else cv2.VideoCapture(device))
        self._control=Lock()
        self._lock=Lock()
        self._stop=Event()
        self._ready=Event()
        self._thread=None
        self._jpeg=None
        self._captured=0.0
        self._state='stopped'
        self._message='카메라를 시작해 주세요.'

    def status(self):
        with self._lock:
            return dict(state=self._state,mode='demo' if self.demo else 'live',message=self._message)

    def _set(self,state,message):
        with self._lock:
            self._state=state
            self._message=message

    def start(self):
        with self._control:
            if self._thread and self._thread.is_alive():
                if self.status()['state']=='running':
                    return self.status()
                raise HTTPException(503,'카메라 작업 종료를 기다린 뒤 다시 시작해 주세요.')
            self._stop.clear()
            self._ready.clear()
            self._set('starting','카메라 연결 중입니다.')
            self._thread=Thread(target=self._capture,daemon=True,name='cart-camera')
            self._thread.start()
            self._ready.wait(3)
            if self.status()['state']!='running':
                self._stop.set()
                self._set('error','카메라 연결에 실패했습니다. 장치와 운영체제 권한을 확인해 주세요.')
                raise HTTPException(503,self.status()['message'])
            return self.status()

    def _capture(self):
        capture=None
        try:
            capture=self.factory()
            if not capture.isOpened():
                raise RuntimeError('camera unavailable')
            while not self._stop.is_set():
                ok,frame=capture.read()
                if not ok or frame is None:
                    raise RuntimeError('frame unavailable')
                ok,encoded=cv2.imencode('.jpg',frame,[cv2.IMWRITE_JPEG_QUALITY,80])
                if not ok:
                    raise RuntimeError('encode failed')
                with self._lock:
                    self._jpeg=encoded.tobytes()
                    self._captured=time.monotonic()
                    self._state='running'
                    self._message='더미 영상입니다.' if self.demo else '카메라 연결됨'
                self._ready.set()
                self._stop.wait(0.08)
        except Exception:
            self._set('error','영상을 읽을 수 없습니다. 장치 연결 후 다시 시작해 주세요.')
        finally:
            if capture is not None:
                capture.release()
            with self._lock:
                self._jpeg=None
            self._ready.set()

    def stop(self):
        with self._control:
            self._stop.set()
            if self._thread:
                self._thread.join(timeout=2)
            if self._thread and self._thread.is_alive():
                self._set('error','장치 응답을 기다리고 있습니다. 장치 연결을 확인해 주세요.')
            else:
                self._set('stopped','카메라가 종료되었습니다.')
            return self.status()

    def snapshot(self):
        with self._lock:
            if self._state!='running' or self._jpeg is None or time.monotonic()-self._captured>2:
                raise HTTPException(503,'최신 카메라 영상이 없습니다. 카메라를 다시 시작해 주세요.')
            return self._jpeg

    def mjpeg(self):
        while not self._stop.is_set():
            try:
                jpeg=self.snapshot()
            except HTTPException:
                return
            yield b'--frame\r\nContent-Type: image/jpeg\r\n\r\n'+jpeg+b'\r\n'
            self._stop.wait(0.1)


def router(camera):
    api=APIRouter(prefix='/api/camera',tags=['Camera'])
    @api.get('/status',response_model=CameraStatus,summary='카메라 연결 상태 및 더미 여부')
    def status():
        return camera.status()
    @api.post('/start',response_model=CameraStatus,summary='백엔드 PC의 카메라 시작')
    def start():
        return camera.start()
    @api.post('/stop',response_model=CameraStatus,summary='카메라 종료 및 장치 자원 해제')
    def stop():
        return camera.stop()
    @api.get('/stream',response_class=StreamingResponse,summary='MJPEG 미리보기',responses={200:{'content':{'multipart/x-mixed-replace':{}},'description':'JPEG 프레임 스트림'}})
    def stream():
        camera.snapshot()
        return StreamingResponse(camera.mjpeg(),media_type='multipart/x-mixed-replace; boundary=frame',headers={'Cache-Control':'no-store'})
    return api

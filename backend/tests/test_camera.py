import time
import numpy as np
import pytest
from fastapi import HTTPException
from fastapi.testclient import TestClient
from app.camera import Camera
from app.db import Database
from app.main import create_app

class Capture:
    def __init__(self,opened=True,valid=True):
        self.opened=opened
        self.valid=valid
        self.released=False
    def isOpened(self):
        return self.opened
    def read(self):
        return self.valid,np.zeros((40,40,3),dtype=np.uint8) if self.valid else None
    def release(self):
        self.released=True


def test_camera_start_frame_repeat_stop_and_shutdown(tmp_path):
    device=Capture()
    calls=[]
    camera=Camera(factory=lambda:(calls.append(1) or device))
    with TestClient(create_app(Database(tmp_path/'camera.db'),camera=camera)) as c:
        assert c.get('/api/camera/status').json()['state']=='stopped'
        assert c.get('/api/camera/stream').status_code==503
        assert c.post('/api/camera/start').json()['state']=='running'
        assert c.post('/api/camera/start').status_code==200
        assert len(calls)==1
        assert camera.snapshot().startswith(b'\xff\xd8')
        stream=camera.mjpeg()
        assert next(stream).startswith(b'--frame\r\nContent-Type: image/jpeg')
        stream.close()
        assert c.post('/api/camera/stop').json()['state']=='stopped'
        assert c.post('/api/camera/stop').status_code==200
    assert device.released
    assert not camera._thread.is_alive()

@pytest.mark.parametrize('opened,valid',[(False,True),(True,False)])
def test_device_and_read_errors_release(opened,valid):
    device=Capture(opened,valid)
    camera=Camera(factory=lambda:device)
    with pytest.raises(HTTPException) as error:
        camera.start()
    assert error.value.status_code==503
    camera.stop()
    assert device.released


def test_stale_frame_rejected():
    camera=Camera(demo=True)
    camera.start()
    try:
        with camera._lock:
            camera._captured=time.monotonic()-10
        with pytest.raises(HTTPException):
            camera.snapshot()
    finally:
        camera.stop()


def test_demo_mode_and_restart():
    camera=Camera(demo=True)
    for _ in range(2):
        assert camera.start()['mode']=='demo'
        assert camera.snapshot()
        camera.stop()

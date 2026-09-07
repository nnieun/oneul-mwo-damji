import os
import pytest
from app.camera import Camera
from app.recognition import RoboflowModel

@pytest.mark.hardware
@pytest.mark.skipif(os.getenv('RUN_CAMERA_TESTS')!='1',reason='실제 카메라 검증은 RUN_CAMERA_TESTS=1로 별도 실행')
def test_physical_camera_capture():
    camera=Camera(device=int(os.getenv('CAMERA_DEVICE','0')))
    try:
        assert camera.start()['mode']=='live'
        assert camera.snapshot().startswith(b'\xff\xd8')
    finally:
        camera.stop()

@pytest.mark.hardware
@pytest.mark.skipif(os.getenv('RUN_LIVE_MODEL_TESTS')!='1',reason='실제 Roboflow 검증은 모델 설정 후 RUN_LIVE_MODEL_TESTS=1로 별도 실행')
def test_physical_camera_and_roboflow():
    camera=Camera(device=int(os.getenv('CAMERA_DEVICE','0')))
    try:
        camera.start()
        detections=RoboflowModel().infer(camera.snapshot())
        assert isinstance(detections,list)
    finally:
        camera.stop()

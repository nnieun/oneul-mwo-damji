import os
import pytest
from app.recognition import RoboflowModel

# Real hardware check: camera capture now happens in the browser (getUserMedia),
# so this test verifies Roboflow inference against a real JPEG frame you supply,
# e.g. one saved from the browser camera preview during a manual demo run.

@pytest.mark.hardware
@pytest.mark.skipif(os.getenv('RUN_LIVE_MODEL_TESTS')!='1',reason='실제 Roboflow 검증은 모델 설정 후 RUN_LIVE_MODEL_TESTS=1로 별도 실행')
def test_live_roboflow_inference_with_sample_frame():
    path=os.getenv('SAMPLE_IMAGE_PATH')
    assert path,'SAMPLE_IMAGE_PATH에 브라우저 카메라로 촬영한 JPEG 경로를 지정해 주세요.'
    with open(path,'rb') as f:
        detections=RoboflowModel().infer(f.read())
    assert isinstance(detections,list)

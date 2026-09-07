
# F04-camera 테스트 실행

- 실행 일시: 2026-09-07T11:03:38.975283+09:00
- 환경: Windows-11-10.0.26200-SP0, Python 3.12.14
- 기준 커밋: 6ebec23 + 해당 기능 작업 트리
- 실행 위치: backend
- 실행 명령: `python -m pytest -v tests/test_camera.py`
- 종료 코드: 0
- 결과: PASS
- 소요 시간: 2.20초

## 실제 실행 로그 (항목별 결과·집계)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-8.3.4, pluggy-1.6.0 -- C:\worksapces\oneul-mwo-damji\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\worksapces\oneul-mwo-damji\backend
plugins: anyio-4.15.1
collecting ... collected 5 items

tests/test_camera.py::test_camera_start_frame_repeat_stop_and_shutdown PASSED [ 20%]
tests/test_camera.py::test_device_and_read_errors_release[False-True] PASSED [ 40%]
tests/test_camera.py::test_device_and_read_errors_release[True-False] PASSED [ 60%]
tests/test_camera.py::test_stale_frame_rejected PASSED                   [ 80%]
tests/test_camera.py::test_demo_mode_and_restart PASSED                  [100%]

============================== warnings summary ===============================
.venv\Lib\site-packages\starlette\testclient.py:40
  C:\worksapces\oneul-mwo-damji\backend\.venv\Lib\site-packages\starlette\testclient.py:40: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 5 passed, 1 warning in 1.32s =========================

```

- 실제 카메라·Roboflow 검증은 별도 hardware 테스트 및 시연 기록을 따른다.

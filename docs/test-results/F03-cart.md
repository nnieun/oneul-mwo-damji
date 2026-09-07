
# F03-cart 테스트 실행

- 실행 일시: 2026-09-07T10:57:55.662735+09:00
- 환경: Windows-11-10.0.26200-SP0, Python 3.12.14
- 기준 커밋: 82255d4 + 해당 기능 작업 트리
- 실행 위치: backend
- 실행 명령: `python -m pytest -v tests/test_cart.py`
- 종료 코드: 0
- 결과: PASS
- 소요 시간: 2.16초

## 실제 실행 로그 (항목별 결과·집계)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-8.3.4, pluggy-1.6.0 -- C:\worksapces\oneul-mwo-damji\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\worksapces\oneul-mwo-damji\backend
plugins: anyio-4.15.1
collecting ... collected 11 items

tests/test_cart.py::test_cart_crud_price_and_persistence PASSED          [  9%]
tests/test_cart.py::test_duplicate_request_and_conflict PASSED           [ 18%]
tests/test_cart.py::test_concurrent_same_request_is_once PASSED          [ 27%]
tests/test_cart.py::test_quantity_validation[0] PASSED                   [ 36%]
tests/test_cart.py::test_quantity_validation[-1] PASSED                  [ 45%]
tests/test_cart.py::test_quantity_validation[1000] PASSED                [ 54%]
tests/test_cart.py::test_quantity_validation[1.5] PASSED                 [ 63%]
tests/test_cart.py::test_quantity_validation[2] PASSED                   [ 72%]
tests/test_cart.py::test_quantity_validation[True] PASSED                [ 81%]
tests/test_cart.py::test_missing_and_quantity_limit PASSED               [ 90%]
tests/test_cart.py::test_unit_price_is_snapshot PASSED                   [100%]

============================== warnings summary ===============================
.venv\Lib\site-packages\starlette\testclient.py:40
  C:\worksapces\oneul-mwo-damji\backend\.venv\Lib\site-packages\starlette\testclient.py:40: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 11 passed, 1 warning in 1.40s ========================

```

- 실제 카메라·Roboflow 검증은 별도 hardware 테스트 및 시연 기록을 따른다.

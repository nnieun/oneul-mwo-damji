
# F06-recipes 테스트 실행

- 실행 일시: 2026-09-07T10:59:35.284771+09:00
- 환경: Windows-11-10.0.26200-SP0, Python 3.12.14
- 기준 커밋: 6415993 + 해당 기능 작업 트리
- 실행 위치: backend
- 실행 명령: `python -m pytest -v tests/test_recipes.py tests/test_api.py`
- 종료 코드: 0
- 결과: PASS
- 소요 시간: 1.59초

## 실제 실행 로그 (항목별 결과·집계)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-8.3.4, pluggy-1.6.0 -- C:\worksapces\oneul-mwo-damji\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\worksapces\oneul-mwo-damji\backend
plugins: anyio-4.15.1
collecting ... collected 9 items

tests/test_recipes.py::test_catalog_and_detail PASSED                    [ 11%]
tests/test_recipes.py::test_empty_and_unknown_cart PASSED                [ 22%]
tests/test_recipes.py::test_required_optional_and_recalculation PASSED   [ 33%]
tests/test_recipes.py::test_no_matching_required_and_sort_stable PASSED  [ 44%]
tests/test_api.py::test_products_are_loaded_from_sqlite PASSED           [ 55%]
tests/test_api.py::test_cart_estimate_uses_quantity_and_product_price PASSED [ 66%]
tests/test_api.py::test_recognition_filters_low_confidence_and_deduplicates_product PASSED [ 77%]
tests/test_api.py::test_recipes_are_sorted_by_owned_ingredients PASSED   [ 88%]
tests/test_api.py::test_unknown_product_cannot_be_confirmed PASSED       [100%]

============================== warnings summary ===============================
.venv\Lib\site-packages\starlette\testclient.py:40
  C:\worksapces\oneul-mwo-damji\backend\.venv\Lib\site-packages\starlette\testclient.py:40: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 9 passed, 1 warning in 0.88s =========================

```

- 실제 카메라·Roboflow 검증은 별도 hardware 테스트 및 시연 기록을 따른다.

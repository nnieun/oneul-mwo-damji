
# F01-database 테스트 실행

- 실행 일시: 2026-09-07T10:54:49.837710+09:00
- 환경: Windows-11-10.0.26200-SP0, Python 3.12.14
- 기준 커밋: 9147bfd + 해당 기능 작업 트리
- 실행 위치: backend
- 실행 명령: `python -m pytest -v tests/test_database.py tests/test_api.py`
- 종료 코드: 0
- 결과: PASS
- 소요 시간: 1.28초

## 실제 실행 로그 (항목별 결과·집계)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-8.3.4, pluggy-1.6.0 -- C:\worksapces\oneul-mwo-damji\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\worksapces\oneul-mwo-damji\backend
plugins: anyio-4.15.1
collecting ... collected 8 items

tests/test_database.py::test_seed_idempotent_and_normalized PASSED       [ 12%]
tests/test_database.py::test_memory_connections_work_across_threads PASSED [ 25%]
tests/test_database.py::test_upgrade_preserves_existing_product_and_custom_recipe PASSED [ 37%]
tests/test_api.py::test_products_are_loaded_from_sqlite PASSED           [ 50%]
tests/test_api.py::test_cart_estimate_uses_quantity_and_product_price PASSED [ 62%]
tests/test_api.py::test_recognition_filters_low_confidence_and_deduplicates_product PASSED [ 75%]
tests/test_api.py::test_recipes_are_sorted_by_owned_ingredients PASSED   [ 87%]
tests/test_api.py::test_unknown_product_cannot_be_confirmed PASSED       [100%]

============================== warnings summary ===============================
.venv\Lib\site-packages\starlette\testclient.py:40
  C:\worksapces\oneul-mwo-damji\backend\.venv\Lib\site-packages\starlette\testclient.py:40: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
======================== 8 passed, 1 warning in 0.51s =========================

```

- 실제 카메라·Roboflow 검증은 별도 hardware 테스트 및 시연 기록을 따른다.

# F01-database 테스트 실행

- 실행 일시: 2026-09-07T11:23:48.368259+09:00
- 환경: Windows-11-10.0.26200-SP0, Python 3.12.14
- 기준 커밋: 51b6dea + 해당 기능 작업 트리
- 실행 위치: backend
- 실행 명령: `python -m pytest -v tests/test_database.py`
- 종료 코드: 0
- 결과: PASS
- 소요 시간: 1.03초

## 실제 실행 로그 (항목별 결과·집계)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-8.3.4, pluggy-1.6.0 -- C:\worksapces\oneul-mwo-damji\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\worksapces\oneul-mwo-damji\backend
configfile: pytest.ini
plugins: anyio-4.15.1
collecting ... collected 4 items

tests/test_database.py::test_seed_idempotent_and_normalized PASSED       [ 25%]
tests/test_database.py::test_memory_connections_work_across_threads PASSED [ 50%]
tests/test_database.py::test_upgrade_preserves_existing_product_and_custom_recipe PASSED [ 75%]
tests/test_database.py::test_failed_migration_rolls_back_all_schema PASSED [100%]

============================== 4 passed in 0.15s ==============================

```

- 실제 카메라·Roboflow 검증은 별도 hardware 테스트 및 시연 기록을 따른다.

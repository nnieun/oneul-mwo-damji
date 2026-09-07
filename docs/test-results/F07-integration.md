
# F07-integration 테스트 실행

- 실행 일시: 2026-09-07T11:21:19.986187+09:00
- 환경: Windows-11-10.0.26200-SP0, Python 3.12.14
- 기준 커밋: 51b6dea + 해당 기능 작업 트리
- 실행 위치: backend
- 실행 명령: `python -m pytest -v `
- 종료 코드: 0
- 결과: PASS
- 소요 시간: 3.06초

## 실제 실행 로그 (항목별 결과·집계)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-8.3.4, pluggy-1.6.0 -- C:\worksapces\oneul-mwo-damji\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\worksapces\oneul-mwo-damji\backend
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.15.1
collecting ... collected 43 items

tests/test_api.py::test_products_are_loaded_from_sqlite PASSED           [  2%]
tests/test_api.py::test_cart_estimate_uses_quantity_and_product_price PASSED [  4%]
tests/test_api.py::test_recognition_filters_low_confidence_and_deduplicates_product PASSED [  6%]
tests/test_api.py::test_recipes_are_sorted_by_owned_ingredients PASSED   [  9%]
tests/test_api.py::test_unknown_product_cannot_be_confirmed PASSED       [ 11%]
tests/test_camera.py::test_camera_start_frame_repeat_stop_and_shutdown PASSED [ 13%]
tests/test_camera.py::test_device_and_read_errors_release[False-True] PASSED [ 16%]
tests/test_camera.py::test_device_and_read_errors_release[True-False] PASSED [ 18%]
tests/test_camera.py::test_stale_frame_rejected PASSED                   [ 20%]
tests/test_camera.py::test_demo_mode_and_restart PASSED                  [ 23%]
tests/test_cart.py::test_cart_crud_price_and_persistence PASSED          [ 25%]
tests/test_cart.py::test_duplicate_request_and_conflict PASSED           [ 27%]
tests/test_cart.py::test_concurrent_same_request_is_once PASSED          [ 30%]
tests/test_cart.py::test_quantity_validation[0] PASSED                   [ 32%]
tests/test_cart.py::test_quantity_validation[-1] PASSED                  [ 34%]
tests/test_cart.py::test_quantity_validation[1000] PASSED                [ 37%]
tests/test_cart.py::test_quantity_validation[1.5] PASSED                 [ 39%]
tests/test_cart.py::test_quantity_validation[2] PASSED                   [ 41%]
tests/test_cart.py::test_quantity_validation[True] PASSED                [ 44%]
tests/test_cart.py::test_missing_and_quantity_limit PASSED               [ 46%]
tests/test_cart.py::test_unit_price_is_snapshot PASSED                   [ 48%]
tests/test_database.py::test_seed_idempotent_and_normalized PASSED       [ 51%]
tests/test_database.py::test_memory_connections_work_across_threads PASSED [ 53%]
tests/test_database.py::test_upgrade_preserves_existing_product_and_custom_recipe PASSED [ 55%]
tests/test_database.py::test_failed_migration_rolls_back_all_schema PASSED [ 58%]
tests/test_hardware.py::test_physical_camera_capture SKIPPED (실제 ...)  [ 60%]
tests/test_hardware.py::test_physical_camera_and_roboflow SKIPPED (...)  [ 62%]
tests/test_integration.py::test_complete_demo_and_swagger_contract PASSED [ 65%]
tests/test_integration.py::test_model_specific_label_mapping_and_candidate_rollback PASSED [ 67%]
tests/test_products.py::test_catalog_search_and_health PASSED            [ 69%]
tests/test_products.py::test_unknown_product_is_not_free PASSED          [ 72%]
tests/test_products.py::test_estimate_empty_and_invalid PASSED           [ 74%]
tests/test_products.py::test_swagger_contract PASSED                     [ 76%]
tests/test_recipes.py::test_catalog_and_detail PASSED                    [ 79%]
tests/test_recipes.py::test_empty_and_unknown_cart PASSED                [ 81%]
tests/test_recipes.py::test_required_optional_and_recalculation PASSED   [ 83%]
tests/test_recipes.py::test_no_matching_required_and_sort_stable PASSED  [ 86%]
tests/test_recognition.py::test_scan_lifecycle_confirmation_correction_and_duplicate PASSED [ 88%]
tests/test_recognition.py::test_dismiss_expiry_missing_and_atomic_failure PASSED [ 90%]
tests/test_recognition.py::test_threshold_mapping_dedup_and_empty PASSED [ 93%]
tests/test_recognition.py::test_model_timeout_invalid_response_and_secret_redaction PASSED [ 95%]
tests/test_recognition.py::test_model_http_contract_and_missing_configuration PASSED [ 97%]
tests/test_recognition.py::test_scan_lock_released_on_error PASSED       [100%]

============================== warnings summary ===============================
.venv\Lib\site-packages\starlette\testclient.py:40
  C:\worksapces\oneul-mwo-damji\backend\.venv\Lib\site-packages\starlette\testclient.py:40: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
================== 41 passed, 2 skipped, 1 warning in 2.25s ===================

```

- 실제 카메라·Roboflow 검증은 별도 hardware 테스트 및 시연 기록을 따른다.

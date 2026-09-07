
# F00-baseline 테스트 실행

- 실행 일시: 2026-09-07T10:51:06.317431+09:00
- 환경: Windows-11-10.0.26200-SP0, Python 3.12.14
- 기준 커밋: 9147bfd + 해당 기능 작업 트리
- 실행 위치: backend
- 실행 명령: `python -m pytest -v tests/test_api.py`
- 종료 코드: 1
- 결과: FAIL
- 소요 시간: 4.52초

## 실제 실행 로그 (항목별 결과·집계)

```text
============================= test session starts =============================
platform win32 -- Python 3.12.14, pytest-8.3.4, pluggy-1.6.0 -- C:\worksapces\oneul-mwo-damji\backend\.venv\Scripts\python.exe
cachedir: .pytest_cache
rootdir: C:\worksapces\oneul-mwo-damji\backend
plugins: anyio-4.15.1
collecting ... collected 5 items

tests/test_api.py::test_products_are_loaded_from_sqlite ERROR            [ 20%]
tests/test_api.py::test_cart_estimate_uses_quantity_and_product_price ERROR [ 40%]
tests/test_api.py::test_recognition_filters_low_confidence_and_deduplicates_product ERROR [ 60%]
tests/test_api.py::test_recipes_are_sorted_by_owned_ingredients ERROR    [ 80%]
tests/test_api.py::test_unknown_product_cannot_be_confirmed ERROR        [100%]

=================================== ERRORS ====================================
___________ ERROR at setup of test_products_are_loaded_from_sqlite ____________

self = <app.db.Database object at 0x000001CE4B1B1550>

    def initialize(self) -> None:
        with self.connect() as connection:
>           connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL CHECK (price >= 0),
                    ingredient TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    cooking_time TEXT NOT NULL
                );
                """
            )
E           sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 16916 and this is thread id 6380.

app\db.py:37: ProgrammingError

During handling of the above exception, another exception occurred:

    @pytest.fixture
    def client() -> TestClient:
>       with TestClient(create_app(Database(":memory:"))) as test_client:

tests\test_api.py:10: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
.venv\Lib\site-packages\starlette\testclient.py:739: in __enter__
    portal.call(self.wait_startup)
.venv\Lib\site-packages\anyio\from_thread.py:340: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:456: in result
    return self.__get_result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:401: in __get_result
    raise self._exception
.venv\Lib\site-packages\anyio\from_thread.py:265: in _call_func
    retval = await retval_or_awaitable
.venv\Lib\site-packages\starlette\testclient.py:774: in wait_startup
    await receive()
.venv\Lib\site-packages\starlette\testclient.py:765: in receive
    self.task.result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:449: in result
    return self.__get_result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:401: in __get_result
    raise self._exception
.venv\Lib\site-packages\anyio\from_thread.py:265: in _call_func
    retval = await retval_or_awaitable
.venv\Lib\site-packages\starlette\testclient.py:755: in lifespan
    await self.app(scope, self.stream_receive.receive, self.stream_send.send)
.venv\Lib\site-packages\fastapi\applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
.venv\Lib\site-packages\starlette\applications.py:113: in __call__
    await self.middleware_stack(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\errors.py:152: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\cors.py:77: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\exceptions.py:48: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:715: in __call__
    await self.middleware_stack(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:724: in app
    await self.lifespan(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:693: in lifespan
    async with self.lifespan_context(app) as maybe_state:
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\contextlib.py:210: in __aenter__
    return await anext(self.gen)
app\main.py:76: in lifespan
    db.initialize()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <app.db.Database object at 0x000001CE4B1B1550>

    def initialize(self) -> None:
>       with self.connect() as connection:
E       sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 16916 and this is thread id 6380.

app\db.py:36: ProgrammingError
____ ERROR at setup of test_cart_estimate_uses_quantity_and_product_price _____

self = <app.db.Database object at 0x000001CE4E6593D0>

    def initialize(self) -> None:
        with self.connect() as connection:
>           connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL CHECK (price >= 0),
                    ingredient TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    cooking_time TEXT NOT NULL
                );
                """
            )
E           sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 16916 and this is thread id 12788.

app\db.py:37: ProgrammingError

During handling of the above exception, another exception occurred:

    @pytest.fixture
    def client() -> TestClient:
>       with TestClient(create_app(Database(":memory:"))) as test_client:

tests\test_api.py:10: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
.venv\Lib\site-packages\starlette\testclient.py:739: in __enter__
    portal.call(self.wait_startup)
.venv\Lib\site-packages\anyio\from_thread.py:340: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:456: in result
    return self.__get_result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:401: in __get_result
    raise self._exception
.venv\Lib\site-packages\anyio\from_thread.py:265: in _call_func
    retval = await retval_or_awaitable
.venv\Lib\site-packages\starlette\testclient.py:774: in wait_startup
    await receive()
.venv\Lib\site-packages\starlette\testclient.py:765: in receive
    self.task.result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:449: in result
    return self.__get_result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:401: in __get_result
    raise self._exception
.venv\Lib\site-packages\anyio\from_thread.py:265: in _call_func
    retval = await retval_or_awaitable
.venv\Lib\site-packages\starlette\testclient.py:755: in lifespan
    await self.app(scope, self.stream_receive.receive, self.stream_send.send)
.venv\Lib\site-packages\fastapi\applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
.venv\Lib\site-packages\starlette\applications.py:113: in __call__
    await self.middleware_stack(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\errors.py:152: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\cors.py:77: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\exceptions.py:48: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:715: in __call__
    await self.middleware_stack(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:724: in app
    await self.lifespan(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:693: in lifespan
    async with self.lifespan_context(app) as maybe_state:
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\contextlib.py:210: in __aenter__
    return await anext(self.gen)
app\main.py:76: in lifespan
    db.initialize()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <app.db.Database object at 0x000001CE4E6593D0>

    def initialize(self) -> None:
>       with self.connect() as connection:
E       sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 16916 and this is thread id 12788.

app\db.py:36: ProgrammingError
_ ERROR at setup of test_recognition_filters_low_confidence_and_deduplicates_product _

self = <app.db.Database object at 0x000001CE4E71D100>

    def initialize(self) -> None:
        with self.connect() as connection:
>           connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL CHECK (price >= 0),
                    ingredient TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    cooking_time TEXT NOT NULL
                );
                """
            )
E           sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 16916 and this is thread id 22752.

app\db.py:37: ProgrammingError

During handling of the above exception, another exception occurred:

    @pytest.fixture
    def client() -> TestClient:
>       with TestClient(create_app(Database(":memory:"))) as test_client:

tests\test_api.py:10: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
.venv\Lib\site-packages\starlette\testclient.py:739: in __enter__
    portal.call(self.wait_startup)
.venv\Lib\site-packages\anyio\from_thread.py:340: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:456: in result
    return self.__get_result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:401: in __get_result
    raise self._exception
.venv\Lib\site-packages\anyio\from_thread.py:265: in _call_func
    retval = await retval_or_awaitable
.venv\Lib\site-packages\starlette\testclient.py:774: in wait_startup
    await receive()
.venv\Lib\site-packages\starlette\testclient.py:765: in receive
    self.task.result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:449: in result
    return self.__get_result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:401: in __get_result
    raise self._exception
.venv\Lib\site-packages\anyio\from_thread.py:265: in _call_func
    retval = await retval_or_awaitable
.venv\Lib\site-packages\starlette\testclient.py:755: in lifespan
    await self.app(scope, self.stream_receive.receive, self.stream_send.send)
.venv\Lib\site-packages\fastapi\applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
.venv\Lib\site-packages\starlette\applications.py:113: in __call__
    await self.middleware_stack(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\errors.py:152: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\cors.py:77: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\exceptions.py:48: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:715: in __call__
    await self.middleware_stack(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:724: in app
    await self.lifespan(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:693: in lifespan
    async with self.lifespan_context(app) as maybe_state:
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\contextlib.py:210: in __aenter__
    return await anext(self.gen)
app\main.py:76: in lifespan
    db.initialize()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <app.db.Database object at 0x000001CE4E71D100>

    def initialize(self) -> None:
>       with self.connect() as connection:
E       sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 16916 and this is thread id 22752.

app\db.py:36: ProgrammingError
_______ ERROR at setup of test_recipes_are_sorted_by_owned_ingredients ________

self = <app.db.Database object at 0x000001CE4E7236B0>

    def initialize(self) -> None:
        with self.connect() as connection:
>           connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL CHECK (price >= 0),
                    ingredient TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    cooking_time TEXT NOT NULL
                );
                """
            )
E           sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 16916 and this is thread id 18572.

app\db.py:37: ProgrammingError

During handling of the above exception, another exception occurred:

    @pytest.fixture
    def client() -> TestClient:
>       with TestClient(create_app(Database(":memory:"))) as test_client:

tests\test_api.py:10: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
.venv\Lib\site-packages\starlette\testclient.py:739: in __enter__
    portal.call(self.wait_startup)
.venv\Lib\site-packages\anyio\from_thread.py:340: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:456: in result
    return self.__get_result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:401: in __get_result
    raise self._exception
.venv\Lib\site-packages\anyio\from_thread.py:265: in _call_func
    retval = await retval_or_awaitable
.venv\Lib\site-packages\starlette\testclient.py:774: in wait_startup
    await receive()
.venv\Lib\site-packages\starlette\testclient.py:765: in receive
    self.task.result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:449: in result
    return self.__get_result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:401: in __get_result
    raise self._exception
.venv\Lib\site-packages\anyio\from_thread.py:265: in _call_func
    retval = await retval_or_awaitable
.venv\Lib\site-packages\starlette\testclient.py:755: in lifespan
    await self.app(scope, self.stream_receive.receive, self.stream_send.send)
.venv\Lib\site-packages\fastapi\applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
.venv\Lib\site-packages\starlette\applications.py:113: in __call__
    await self.middleware_stack(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\errors.py:152: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\cors.py:77: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\exceptions.py:48: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:715: in __call__
    await self.middleware_stack(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:724: in app
    await self.lifespan(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:693: in lifespan
    async with self.lifespan_context(app) as maybe_state:
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\contextlib.py:210: in __aenter__
    return await anext(self.gen)
app\main.py:76: in lifespan
    db.initialize()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <app.db.Database object at 0x000001CE4E7236B0>

    def initialize(self) -> None:
>       with self.connect() as connection:
E       sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 16916 and this is thread id 18572.

app\db.py:36: ProgrammingError
_________ ERROR at setup of test_unknown_product_cannot_be_confirmed __________

self = <app.db.Database object at 0x000001CE4E72C3E0>

    def initialize(self) -> None:
        with self.connect() as connection:
>           connection.executescript(
                """
                CREATE TABLE IF NOT EXISTS products (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    price INTEGER NOT NULL CHECK (price >= 0),
                    ingredient TEXT NOT NULL
                );
                CREATE TABLE IF NOT EXISTS recipes (
                    id INTEGER PRIMARY KEY,
                    name TEXT NOT NULL,
                    ingredients TEXT NOT NULL,
                    cooking_time TEXT NOT NULL
                );
                """
            )
E           sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 16916 and this is thread id 9648.

app\db.py:37: ProgrammingError

During handling of the above exception, another exception occurred:

    @pytest.fixture
    def client() -> TestClient:
>       with TestClient(create_app(Database(":memory:"))) as test_client:

tests\test_api.py:10: 
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _
.venv\Lib\site-packages\starlette\testclient.py:739: in __enter__
    portal.call(self.wait_startup)
.venv\Lib\site-packages\anyio\from_thread.py:340: in call
    return cast(T_Retval, self.start_task_soon(func, *args).result())
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:456: in result
    return self.__get_result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:401: in __get_result
    raise self._exception
.venv\Lib\site-packages\anyio\from_thread.py:265: in _call_func
    retval = await retval_or_awaitable
.venv\Lib\site-packages\starlette\testclient.py:774: in wait_startup
    await receive()
.venv\Lib\site-packages\starlette\testclient.py:765: in receive
    self.task.result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:449: in result
    return self.__get_result()
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\concurrent\futures\_base.py:401: in __get_result
    raise self._exception
.venv\Lib\site-packages\anyio\from_thread.py:265: in _call_func
    retval = await retval_or_awaitable
.venv\Lib\site-packages\starlette\testclient.py:755: in lifespan
    await self.app(scope, self.stream_receive.receive, self.stream_send.send)
.venv\Lib\site-packages\fastapi\applications.py:1054: in __call__
    await super().__call__(scope, receive, send)
.venv\Lib\site-packages\starlette\applications.py:113: in __call__
    await self.middleware_stack(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\errors.py:152: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\cors.py:77: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\middleware\exceptions.py:48: in __call__
    await self.app(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:715: in __call__
    await self.middleware_stack(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:724: in app
    await self.lifespan(scope, receive, send)
.venv\Lib\site-packages\starlette\routing.py:693: in lifespan
    async with self.lifespan_context(app) as maybe_state:
C:\Users\Admin\AppData\Roaming\uv\python\cpython-3.12-windows-x86_64-none\Lib\contextlib.py:210: in __aenter__
    return await anext(self.gen)
app\main.py:76: in lifespan
    db.initialize()
_ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _ _

self = <app.db.Database object at 0x000001CE4E72C3E0>

    def initialize(self) -> None:
>       with self.connect() as connection:
E       sqlite3.ProgrammingError: SQLite objects created in a thread can only be used in that same thread. The object was created in thread id 16916 and this is thread id 9648.

app\db.py:36: ProgrammingError
============================== warnings summary ===============================
.venv\Lib\site-packages\starlette\testclient.py:40
  C:\worksapces\oneul-mwo-damji\backend\.venv\Lib\site-packages\starlette\testclient.py:40: DeprecationWarning: The anyio.abc.BlockingPortal alias is deprecated, use anyio.from_thread.BlockingPortal instead.
    _PortalFactoryType = typing.Callable[[], typing.ContextManager[anyio.abc.BlockingPortal]]

-- Docs: https://docs.pytest.org/en/stable/how-to/capture-warnings.html
=========================== short test summary info ===========================
ERROR tests/test_api.py::test_products_are_loaded_from_sqlite - sqlite3.Progr...
ERROR tests/test_api.py::test_cart_estimate_uses_quantity_and_product_price
ERROR tests/test_api.py::test_recognition_filters_low_confidence_and_deduplicates_product
ERROR tests/test_api.py::test_recipes_are_sorted_by_owned_ingredients - sqlit...
ERROR tests/test_api.py::test_unknown_product_cannot_be_confirmed - sqlite3.P...
======================== 1 warning, 5 errors in 3.24s =========================

```

- 실제 카메라·Roboflow 검증은 별도 hardware 테스트 및 시연 기록을 따른다.

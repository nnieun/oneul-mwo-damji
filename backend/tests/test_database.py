import sqlite3
from concurrent.futures import ThreadPoolExecutor
import pytest
from app.db import Database


def test_seed_idempotent_and_normalized(tmp_path):
    db = Database(tmp_path / 'test.db')
    db.initialize()
    db.initialize()
    assert len(db.products()) == 18
    assert len(db.recipes()) == 10
    with db.connect() as c:
        assert c.execute('PRAGMA user_version').fetchone()[0] == 1
        assert c.execute('SELECT COUNT(*) FROM recipe_ingredients').fetchone()[0] > 40
        with pytest.raises(sqlite3.IntegrityError):
            c.execute("INSERT INTO products VALUES (99,'bad',-1,'bad','')")
    with pytest.raises(sqlite3.ProgrammingError):
        c.execute('SELECT 1')


def test_memory_connections_work_across_threads():
    db = Database(':memory:')
    db.initialize()
    with ThreadPoolExecutor() as pool:
        assert len(pool.submit(db.products).result()) == 18
    db.close()


def test_upgrade_preserves_existing_product_and_custom_recipe(tmp_path):
    path = tmp_path / 'legacy.db'
    with sqlite3.connect(path) as c:
        c.executescript("CREATE TABLE products(id INTEGER PRIMARY KEY,name TEXT,price INTEGER,ingredient TEXT); CREATE TABLE recipes(id INTEGER PRIMARY KEY,name TEXT,ingredients TEXT,cooking_time TEXT); INSERT INTO products VALUES(1,'사용자 계란',7777,'계란'); INSERT INTO recipes VALUES(99,'사용자 요리','계란,소금','5분');")
    db = Database(path)
    db.initialize()
    assert db.products()[0]['price'] == 7777
    assert db.products()[0]['name'] == '사용자 계란'
    assert db.recipes()[-1]['name'] == '사용자 요리'
    with db.connect() as c:
        assert c.execute('SELECT COUNT(*) FROM recipe_ingredients WHERE recipe_id=99').fetchone()[0] == 2

def test_failed_migration_rolls_back_all_schema(tmp_path,monkeypatch):
    db=Database(tmp_path/'rollback.db')
    def fail(c):
        raise RuntimeError('seed failed')
    monkeypatch.setattr(db,'_seed',fail)
    with pytest.raises(RuntimeError):
        db.initialize()
    with db.connect() as c:
        assert c.execute('PRAGMA user_version').fetchone()[0]==0
        assert c.execute("SELECT name FROM sqlite_master WHERE type='table'").fetchall()==[]

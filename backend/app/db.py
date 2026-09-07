from contextlib import contextmanager
import json
from pathlib import Path
import sqlite3
from uuid import uuid4
from .seed import PRODUCTS, RECIPES

SCHEMA = """
CREATE TABLE IF NOT EXISTS ingredients(id INTEGER PRIMARY KEY, name TEXT NOT NULL UNIQUE);
CREATE TABLE IF NOT EXISTS product_ingredients(product_id INTEGER REFERENCES products(id), ingredient_id INTEGER REFERENCES ingredients(id), PRIMARY KEY(product_id, ingredient_id));
CREATE TABLE IF NOT EXISTS product_labels(model_version TEXT NOT NULL, label TEXT NOT NULL, product_id INTEGER NOT NULL REFERENCES products(id), PRIMARY KEY(model_version,label));
CREATE TABLE IF NOT EXISTS recipe_ingredients(recipe_id INTEGER REFERENCES recipes(id), ingredient_id INTEGER REFERENCES ingredients(id), amount TEXT NOT NULL, required INTEGER NOT NULL CHECK(required IN (0,1)), position INTEGER NOT NULL, PRIMARY KEY(recipe_id,ingredient_id));
CREATE TABLE IF NOT EXISTS carts(id TEXT PRIMARY KEY, status TEXT NOT NULL DEFAULT 'active' CHECK(status IN ('active','closed')), revision INTEGER NOT NULL DEFAULT 0, created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP, updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP);
CREATE UNIQUE INDEX IF NOT EXISTS one_active_cart ON carts(status) WHERE status='active';
CREATE TABLE IF NOT EXISTS cart_items(cart_id TEXT REFERENCES carts(id), product_id INTEGER REFERENCES products(id), quantity INTEGER NOT NULL CHECK(quantity BETWEEN 1 AND 999), unit_price INTEGER NOT NULL CHECK(unit_price>=0), PRIMARY KEY(cart_id,product_id));
CREATE TABLE IF NOT EXISTS recognition_candidates(id TEXT PRIMARY KEY, scan_id TEXT NOT NULL, product_id INTEGER NOT NULL REFERENCES products(id), confidence REAL NOT NULL CHECK(confidence BETWEEN 0 AND 1), position TEXT NOT NULL, status TEXT NOT NULL CHECK(status IN ('pending','confirmed','dismissed','expired')), expires_at REAL NOT NULL);
CREATE TABLE IF NOT EXISTS processed_requests(cart_id TEXT REFERENCES carts(id), request_key TEXT NOT NULL, payload TEXT NOT NULL, response TEXT NOT NULL, PRIMARY KEY(cart_id,request_key));
"""

class Database:
    def __init__(self, path: str | Path = 'data/app.db'):
        self.path = str(path)
        self._uri = f'file:{uuid4()}?mode=memory&cache=shared' if self.path == ':memory:' else self.path
        self._keeper = None

    def _open(self):
        connection = sqlite3.connect(self._uri, uri=self.path == ':memory:', timeout=10)
        connection.row_factory = sqlite3.Row
        connection.execute('PRAGMA foreign_keys=ON')
        connection.execute('PRAGMA busy_timeout=10000')
        return connection

    @contextmanager
    def connect(self):
        connection = self._open()
        try:
            with connection:
                yield connection
        finally:
            connection.close()

    def close(self):
        if self._keeper is not None:
            self._keeper.close()
            self._keeper = None

    def initialize(self):
        if self.path == ':memory:':
            if self._keeper is None:
                # Keeper only preserves lifetime. Each worker uses its own connection.
                self._keeper = sqlite3.connect(self._uri, uri=True, check_same_thread=False)
        else:
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as c:
            version = c.execute('PRAGMA user_version').fetchone()[0]
            if version > 1:
                raise RuntimeError('Unsupported database schema version')
            if version == 0:
                c.executescript('BEGIN IMMEDIATE; CREATE TABLE IF NOT EXISTS products(id INTEGER PRIMARY KEY, name TEXT NOT NULL, price INTEGER NOT NULL CHECK(price>=0), ingredient TEXT NOT NULL); CREATE TABLE IF NOT EXISTS recipes(id INTEGER PRIMARY KEY,name TEXT NOT NULL,ingredients TEXT NOT NULL,cooking_time TEXT NOT NULL);')
                for table, name, definition in [
                    ('products','emoji',"TEXT NOT NULL DEFAULT '🛒'"),
                    ('recipes','minutes','INTEGER NOT NULL DEFAULT 10'),
                    ('recipes','servings','INTEGER NOT NULL DEFAULT 1'),
                    ('recipes','steps',"TEXT NOT NULL DEFAULT '[]'"),
                    ('recipes','is_dummy','INTEGER NOT NULL DEFAULT 1'),
                ]:
                    if name not in {r['name'] for r in c.execute(f'PRAGMA table_info({table})')}:
                        c.execute(f'ALTER TABLE {table} ADD COLUMN {name} {definition}')
                # Keep DDL, seed data and schema version in the same transaction.
                for statement in SCHEMA.split(";"):
                    if statement.strip():
                        c.execute(statement)
                self._seed(c)
                c.execute('PRAGMA user_version=1')

    def _seed(self, c):
        def ingredient_id(name):
            c.execute('INSERT OR IGNORE INTO ingredients(name) VALUES (?)', (name,))
            return c.execute('SELECT id FROM ingredients WHERE name=?', (name,)).fetchone()[0]
        for pid, (name, price, ingredient, label, emoji) in enumerate(PRODUCTS, 1):
            c.execute('INSERT OR IGNORE INTO products(id,name,price,ingredient,emoji) VALUES (?,?,?,?,?)', (pid,name,price,ingredient,emoji))
            # Preserve existing catalog names, prices and ingredient mappings.
            row = c.execute('SELECT ingredient FROM products WHERE id=?', (pid,)).fetchone()
            c.execute('INSERT OR IGNORE INTO product_ingredients VALUES (?,?)', (pid, ingredient_id(row['ingredient'])))
            if row['ingredient'] == ingredient:
                c.execute('UPDATE products SET emoji=? WHERE id=?', (emoji,pid))
                for alias in (label, ingredient):
                    c.execute('INSERT OR IGNORE INTO product_labels VALUES (?,?,?)', ('*',alias,pid))
        for row in c.execute('SELECT id,ingredient FROM products').fetchall():
            c.execute('INSERT OR IGNORE INTO product_ingredients VALUES (?,?)', (row['id'],ingredient_id(row['ingredient'])))
        for rid, (name, minutes, required, optional, steps) in enumerate(RECIPES, 1):
            old = c.execute('SELECT name FROM recipes WHERE id=?', (rid,)).fetchone()
            if old and old['name'] not in (name, '순두부찌개' if rid == 2 else name):
                continue
            c.execute('INSERT INTO recipes(id,name,ingredients,cooking_time,minutes,servings,steps,is_dummy) VALUES (?,?,?,?,?,1,?,1) ON CONFLICT(id) DO UPDATE SET name=excluded.name,ingredients=excluded.ingredients,cooking_time=excluded.cooking_time,minutes=excluded.minutes,steps=excluded.steps', (rid,name,','.join(x[0] for x in required),f'{minutes}분',minutes,json.dumps(steps,ensure_ascii=False)))
            for pos, (ingredient, amount) in enumerate(required + optional):
                c.execute('INSERT OR IGNORE INTO recipe_ingredients VALUES (?,?,?,?,?)', (rid,ingredient_id(ingredient),amount,int(pos<len(required)),pos))
        for row in c.execute('SELECT id,ingredients FROM recipes').fetchall():
            if not c.execute('SELECT 1 FROM recipe_ingredients WHERE recipe_id=?', (row['id'],)).fetchone():
                for pos, name in enumerate(filter(None, map(str.strip,row['ingredients'].split(',')))):
                    c.execute('INSERT INTO recipe_ingredients VALUES (?,?,?,?,?)', (row['id'],ingredient_id(name),'적당량',1,pos))

    def products(self):
        with self.connect() as c:
            rows = [dict(r) for r in c.execute('SELECT * FROM products ORDER BY id')]
            for row in rows:
                row['ingredients'] = [r[0] for r in c.execute('SELECT i.name FROM ingredients i JOIN product_ingredients p ON p.ingredient_id=i.id WHERE p.product_id=? ORDER BY i.id', (row['id'],))]
            return rows

    def product_prices(self):
        return {p['id']:p['price'] for p in self.products()}

    def recipes(self):
        with self.connect() as c:
            return [dict(r) for r in c.execute('SELECT * FROM recipes ORDER BY id')]

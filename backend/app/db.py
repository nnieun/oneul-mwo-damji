from pathlib import Path
import sqlite3
from typing import Any


DEFAULT_PRODUCTS = [
    (1, "계란 (10구)", 3200, "계란"),
    (2, "두부 (300g)", 1800, "두부"),
    (3, "대파 (1단)", 2500, "대파"),
]

DEFAULT_RECIPES = [
    (1, "계란볶음밥", "계란,대파,밥,간장", "10분"),
    (2, "순두부찌개", "두부,계란,고춧가루,멸치육수,애호박", "20분"),
    (3, "파계란탕", "계란,대파,소금,참기름", "8분"),
]


class Database:
    def __init__(self, path: str | Path = "data/app.db") -> None:
        self.path = str(path)
        self._memory_connection = sqlite3.connect(":memory:") if self.path == ":memory:" else None
        if self._memory_connection is not None:
            self._memory_connection.row_factory = sqlite3.Row

    def connect(self) -> sqlite3.Connection:
        if self._memory_connection is not None:
            return self._memory_connection
        if self.path != ":memory:":
            Path(self.path).parent.mkdir(parents=True, exist_ok=True)
        connection = sqlite3.connect(self.path)
        connection.row_factory = sqlite3.Row
        return connection

    def initialize(self) -> None:
        with self.connect() as connection:
            connection.executescript(
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
            if connection.execute("SELECT COUNT(*) FROM products").fetchone()[0] == 0:
                connection.executemany("INSERT INTO products VALUES (?, ?, ?, ?)", DEFAULT_PRODUCTS)
            if connection.execute("SELECT COUNT(*) FROM recipes").fetchone()[0] == 0:
                connection.executemany("INSERT INTO recipes VALUES (?, ?, ?, ?)", DEFAULT_RECIPES)

    def products(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute("SELECT id, name, price, ingredient FROM products ORDER BY id").fetchall()
        return [dict(row) for row in rows]

    def product_prices(self) -> dict[int, int]:
        return {product["id"]: product["price"] for product in self.products()}

    def recipes(self) -> list[dict[str, Any]]:
        with self.connect() as connection:
            rows = connection.execute("SELECT id, name, ingredients, cooking_time FROM recipes ORDER BY id").fetchall()
        return [dict(row) for row in rows]

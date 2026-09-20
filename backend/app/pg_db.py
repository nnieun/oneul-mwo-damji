import re
from contextlib import contextmanager
from pathlib import Path
import psycopg
from .db import Database

class Row(dict):
    def __getitem__(self, key):
        return list(self.values())[key] if isinstance(key, int) else super().__getitem__(key)

def row_factory(cursor):
    names = [d.name for d in cursor.description]
    return lambda values: Row(zip(names, values))

def translate(sql: str) -> str:
    sql = sql.replace('BEGIN IMMEDIATE', 'BEGIN')
    sql = sql.replace('?', '%s')
    sql = re.sub(r'INSERT OR IGNORE INTO\s+', 'INSERT INTO ', sql, flags=re.I)
    if sql.lstrip().upper().startswith('INSERT INTO ') and ' ON CONFLICT' not in sql.upper():
        sql += ' ON CONFLICT DO NOTHING'
    return sql

class Cursor:
    def __init__(self, cursor): self.cursor = cursor
    def execute(self, sql, params=()): self.cursor.execute(translate(sql), params); return self
    def executescript(self, script):
        for statement in script.split(';'):
            if statement.strip(): self.cursor.execute(statement)
        return self
    def fetchone(self): return self.cursor.fetchone()
    def fetchall(self): return self.cursor.fetchall()
    def __iter__(self): return iter(self.cursor)

class Connection:
    def __init__(self, connection): self.connection = connection
    def execute(self, sql, params=()): return Cursor(self.connection.execute(translate(sql), params))
    def executescript(self, script):
        for statement in script.split(';'):
            if statement.strip(): self.connection.execute(statement)
    def __enter__(self): self.connection.__enter__(); return self
    def __exit__(self, *args): return self.connection.__exit__(*args)
    def close(self): self.connection.close()
    @property
    def in_transaction(self): return self.connection.info.transaction_status != 0

class PostgresDatabase(Database):
    def __init__(self, url: str): super().__init__(url)
    def _open(self): return Connection(psycopg.connect(self.path, row_factory=row_factory))
    def initialize(self):
        schema = Path(__file__).parents[1] / 'migrations' / '001_initial_postgres.sql'
        with self.connect() as c:
            c.executescript(schema.read_text(encoding='utf-8'))
            self._seed(c)

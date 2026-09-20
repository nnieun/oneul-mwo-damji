"""Seed the Supabase PostgreSQL database once using the app's canonical catalog."""
import os
from app.pg_db import PostgresDatabase

url = os.getenv('DATABASE_URL')
if not url:
    raise SystemExit('DATABASE_URL 환경 변수를 설정한 뒤 실행하세요.')

PostgresDatabase(url).initialize()
print('Supabase PostgreSQL 상품·레시피 시드 완료')

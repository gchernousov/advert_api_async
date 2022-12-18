import os

PG_DB = os.getenv("PG_DB", "adverts_api_db_1")
PG_USER = os.getenv("PG_USER", "adv_admin")
PG_PASSWORD = os.getenv("PG_PASSWORD", "qwerty123")
PG_HOST = os.getenv("PG_HOST", "127.0.0.1")
PG_PORT = os.getenv("PG_PORT", 5500)

PG_DSN = f'postgresql+asyncpg://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'
TOKEN_TTL = int(60 * 60 * 24)
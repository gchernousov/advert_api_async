import pytest
from sqlalchemy import create_engine

from app.config import PG_DB, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT
from app.models import Base


PG_DSN = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'
engine = create_engine(PG_DSN)


@pytest.fixture(scope='session', autouse=True)
def init_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()

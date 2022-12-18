import pytest
import time
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import PG_DB, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT
from app.models import Base, UserModel
from app.auth import hash_password
from .config import DEFAULT_PASSWORD


PG_DSN = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'
engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)


@pytest.fixture(scope='session', autouse=True)
def init_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


def create_user(name: str, password: str, email: str = None):
    with Session() as session:
        password = hash_password(password)
        user = UserModel(name=name, password=password, email=email)
        session.add(user)
        session.commit()
        user_data = {'id': user.id, 'name': name,
                     'password': password, 'email': email,
                     'registration_date': str(user.registration_date),
                     'advertisements': user.advertisement}
        return user_data


@pytest.fixture(scope='session', autouse=True)
def root_user():
    root_user = create_user('root_user', 'root_password', 'rootemail@mail.com')
    return root_user


@pytest.fixture()
def new_user():
    username = f'new_user_{time.time()}'
    user = create_user(username, DEFAULT_PASSWORD)
    return user

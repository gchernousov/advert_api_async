import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from app.config import PG_DB, PG_USER, PG_PASSWORD, PG_HOST, PG_PORT
from app.models import Base, UserModel
from app.auth import hash_password


PG_DSN = f'postgresql://{PG_USER}:{PG_PASSWORD}@{PG_HOST}:{PG_PORT}/{PG_DB}'
engine = create_engine(PG_DSN)
Session = sessionmaker(bind=engine)


@pytest.fixture(scope='session', autouse=True)
def init_database():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    yield
    engine.dispose()


def create_default_user(name: str, password: str, email: str):
    with Session() as session:
        password = hash_password(password)
        new_user = UserModel(name=name, password=password, email=email)
        session.add(new_user)
        session.commit()
        user_data = {'id': new_user.id, 'name': new_user.name,
                     'password': new_user.password, 'email': new_user.email,
                     'registration_date': str(new_user.registration_date),
                     'advertisement': new_user.advertisement}
        return user_data


@pytest.fixture(scope='session', autouse=True)
def root_user():
    root_user = create_default_user('root_user', 'root_password', 'rootemail@mail.com')
    return root_user
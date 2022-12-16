import requests

from .api import get_user, create_user
from .config import API_URL


def test_root():
    response = requests.get(API_URL)
    assert response.status_code == 404


def test_create_user():
    response = create_user('user_123', 'password456', 'mrsmith@gmail.com')
    data = response.json()
    new_user = get_user(int(data['id']))
    assert response.status_code == 200
    assert new_user['name'] == 'user_123'


    # def test_create_user(self, root_user_token):
    #     user_id = api.create_user("user_2", DEFAULT_PASSWORD)["id"]
    #     user = api.get_user(user_id, root_user_token)
    #     assert user["name"] == "user_2"
    #
    # def test_create_user(self):
    #     print('>>> test create user')
    #     result = create_user('user_1', 'psw123', 'testuser1@yandex.ru')
    #     data = result.json()
    #     user = get_user(data['id'])
    #     print(f'result.id = {data["id"]}')
    #     print(f'user.name = {user["name"]}')
    #     assert result.status_code == 200
    #     assert user['name'] == 'user_1'

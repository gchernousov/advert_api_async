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


def test_get_user(root_user):
    user = get_user(root_user['id'])
    assert user == {'id': root_user['id'], 'name': root_user['name'],
                    'email': root_user['email'], 'registration': root_user['registration_date'],
                    'advertisements': root_user['advertisements']}

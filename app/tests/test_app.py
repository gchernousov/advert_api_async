import requests
import pytest

from app.tests import api
from .config import API_URL, DEFAULT_PASSWORD


def test_root():
    response = requests.get(API_URL)
    assert response.status_code == 404


def test_create_user():
    """test users.post"""
    response = api.create_user('user_123', 'password456', 'mrsmith@gmail.com')
    data = response.json()
    new_user = api.get_user(int(data['id']))
    assert response.status_code == 200
    assert new_user['name'] == 'user_123'


def test_get_user(root_user):
    """test users.get"""
    user = api.get_user(root_user['id'])
    assert user == {'id': root_user['id'], 'name': root_user['name'],
                    'email': root_user['email'], 'registration': root_user['registration_date'],
                    'advertisements': root_user['advertisements']}


def test_login(new_user):
    response = api.login(new_user['name'], DEFAULT_PASSWORD)
    assert response.status_code == 200
    assert 'token' in response.json()


def test_patch_user(new_user):
    token = api.login(new_user['name'], DEFAULT_PASSWORD)
    token = token.json()
    new_email = 'absolutenewmail@mail.com'
    response = api.patch_user(new_user['id'], {'email': new_email}, token['token'])
    assert response.status_code == 200
    assert {'status': 'user is changed'} == response.json()
    user = api.get_user(new_user['id'])
    assert user['email'] == new_email


def test_delete_user(new_user):
    token = api.login(new_user['name'], DEFAULT_PASSWORD)
    token = token.json()
    response = api.delete_user(new_user['id'], token['token'])
    assert {'status': 'user is delete'} == response.json()
    result = api.get_user(new_user['id'])
    assert result == {'status': 'ERROR', 'description': 'UserModel is not found'}

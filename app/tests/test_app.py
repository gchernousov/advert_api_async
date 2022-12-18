import requests

from app.tests import api
from .config import API_URL, DEFAULT_PASSWORD


def test_root():
    response = requests.get(API_URL)
    assert response.status_code == 404


class TestUser:

    def test_login(self, new_user):
        response = api.login(new_user['name'], DEFAULT_PASSWORD)
        assert response.status_code == 200
        assert 'token' in response.json()

    def test_create_user(self):
        """test users.post"""
        response = api.create_user('user_123', 'password456', 'mrsmith@gmail.com')
        data = response.json()
        new_user = api.get_user(int(data['id']))
        assert response.status_code == 200
        assert new_user['name'] == 'user_123'

    def test_get_user(self, root_user):
        """test users.get"""
        user = api.get_user(root_user['id'])
        assert user == {'id': root_user['id'], 'name': root_user['name'],
                        'email': root_user['email'], 'registration': root_user['registration_date'],
                        'advertisements': root_user['advertisements']}

    def test_patch_user(self, new_user):
        token = api.login(new_user['name'], DEFAULT_PASSWORD)
        token = token.json()['token']
        new_email = 'absolutenewmail@mail.com'
        response = api.patch_user(new_user['id'], {'email': new_email}, token)
        assert response.status_code == 200
        assert response.json() == {'status': 'user is changed'}
        user = api.get_user(new_user['id'])
        assert user['email'] == new_email

    def test_delete_user(self, new_user):
        token = api.login(new_user['name'], DEFAULT_PASSWORD)
        token = token.json()['token']
        response = api.delete_user(new_user['id'], token)
        assert response.status_code == 200
        assert response.json() == {'status': 'user is delete'}
        result = api.get_user(new_user['id'])
        assert result == {'status': 'ERROR', 'description': 'UserModel is not found'}


class TestAdvertisement:

    def test_create_advert(self, new_user):
        token = api.login(new_user['name'], DEFAULT_PASSWORD)
        token = token.json()['token']
        response = api.create_advert('new advertisement', 'some text', token)
        adv_id = response.json()['id']
        new_advertisement = api.get_advert(adv_id)
        assert response.status_code == 200
        assert new_advertisement['title'] == 'new advertisement'

    def test_create_advert_without_authentication(self):
        response = api.create_advert('advertisement 123', 'advert without token')
        assert response.status_code == 403
        assert response.json() == {'status': 'ERROR', 'description': 'need Token for this request'}

    def test_get_advert(self, default_advertisement):
        advertisement = api.get_advert(default_advertisement['id'])
        assert advertisement == {'id': default_advertisement['id'], 'title': default_advertisement['title'],
                                 'description': default_advertisement['description'],
                                 'created': default_advertisement['created'],
                                 'user id': default_advertisement['user_id']}

    def test_patch_advert(self, default_advertisement):
        user = api.get_user(default_advertisement['user_id'])
        token = api.login(user['name'], DEFAULT_PASSWORD)
        token = token.json()['token']
        response = api.patch_advert(default_advertisement['id'], {'title': 'new title'}, token)
        assert response.status_code == 200
        assert response.json() == {'status': 'advertisement is changed'}
        advertisement = api.get_advert(default_advertisement['id'])
        assert advertisement['title'] == 'new title'

    def test_delete_advert(self, default_advertisement):
        user = api.get_user(default_advertisement['user_id'])
        token = api.login(user['name'], DEFAULT_PASSWORD)
        token = token.json()['token']
        response = api.delete_advert(default_advertisement['id'], token)
        assert response.status_code == 200
        assert response.json() == {'status': 'advertisement is delete'}
        result = api.get_advert(default_advertisement['id'])
        assert result == {'status': 'ERROR', 'description': 'AdvertisementModel is not found'}

    def test_delete_advert_with_incorrect_token(self, new_user, default_advertisement):
        token = api.login(new_user['name'], DEFAULT_PASSWORD)
        token = token.json()['token']
        assert new_user['id'] != default_advertisement['user_id']
        result = api.delete_advert(default_advertisement['id'], token)
        assert result.status_code == 401
        assert result.json() == {'status': 'ERROR', 'description': 'permission denied'}

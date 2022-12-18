import requests
from .config import API_URL


def login(name: str, password: str):
    url = f'{API_URL}/login/'
    token = requests.post(url, json={'name': name, 'password': password})
    return token


def get_user(user_id: int):
    url = f'{API_URL}/users/{user_id}'
    response = requests.get(url)
    return response.json()


def create_user(name: str, password: str, email: str):
    url = f'{API_URL}/users/'
    response = requests.post(url, json={'name': name, 'password': password, 'email': email})
    return response


def patch_user(user_id: int, patch_data: dict, token: str):
    url = f'{API_URL}/users/{user_id}'
    response = requests.patch(url, json=patch_data, headers={'Token': token})
    return response


def delete_user(user_id: int, token: str):
    url = f'{API_URL}/users/{user_id}'
    response = requests.delete(url, headers={'Token': token})
    return response


def create_advert(title: str, description: str, token: str = None):
    url = f'{API_URL}/advertisements/'
    response = requests.post(url, json={'title': title, 'description': description}, headers={'Token': token})
    return response


def get_advert(adv_id: int):
    url = f'{API_URL}/advertisements/{adv_id}'
    response = requests.get(url)
    return response.json()


def patch_advert(adv_id: int, patch_data: dict, token: str):
    url = f'{API_URL}/advertisements/{adv_id}'
    response = requests.patch(url, json=patch_data, headers={'Token': token})
    return response


def delete_advert(adv_id: int, token: str):
    url = f'{API_URL}/advertisements/{adv_id}'
    response = requests.delete(url, headers={'Token': token})
    return response

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
    url = API_URL + '/users/'
    response = requests.post(url, json={'name': name, 'password': password, 'email': email})
    return response
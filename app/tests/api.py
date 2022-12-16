from typing import Literal
import requests
from .config import API_URL


# def base_request(method: Literal["get", "post", "patch", "delete"], path: str, *args, **kwargs):
#     print(f'>>> request to URL :: {API_URL}{path}')


def get_user(user_id: int):
    url = f'{API_URL}/users/{user_id}'
    response = requests.get(url)
    return response.json()


def create_user(name: str, password: str, email: str):
    url = API_URL + '/users/'
    response = requests.post(url, json={'name': name, 'password': password, 'email': email})
    return response
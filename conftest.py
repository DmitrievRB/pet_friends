from settings import *
import requests
import pytest
import json
import datetime


@pytest.fixture(autouse=True)
def get_api_key() -> json:
    """Метод делает запрос к API сервера и возвращает статус запроса и результат в формате
    JSON с уникальным ключом пользователя, найденного по указанным email и паролем"""

    headers = {
        'email': valid_email,
        'password': valid_password,
    }
    res = requests.get("https://petfriends.skillfactory.ru/api/key", timeout=2, headers=headers)
    # status = res.status_code
    # result = ""
    try:
        result = res.json()
    except json.decoder.JSONDecodeError:
        result = res.text
    return result


@pytest.fixture(autouse=True)
def time_out():
    start_time = datetime.datetime.now()
    yield
    end_time = datetime.datetime.now()
    print(f"\nТест шел: {end_time - start_time}")

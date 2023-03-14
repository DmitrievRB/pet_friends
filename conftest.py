import datetime
import json

import pytest
import requests

from settings import *


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

# @pytest.fixture(autouse=True)
# def add_log(request):
#     print("Начинаем тест")
#     print(f"Running test: {request.function.__name__}")
#
#     yield
#     with open("log.txt", "a") as f:
#         log = request.function.__name__
#
#         f.write(log)
#     # print(len(request.session.items))
#     print(f"Running test: {request.function.__name__}")
#     for i in request.session.items:
#         print("reportinfo:", i.reportinfo())
#
#         for k in i.keywords:
#             print("keywords:", k)
#
#         print("own_markers:", i.own_markers)
#         print("fspath:", i.fspath)
#         print("name:", i.name)
#         print("extra_keyword_matches:", i.extra_keyword_matches)

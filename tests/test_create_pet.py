from api import PetFriends
from settings import *
import os
import pytest

pf = PetFriends()


@pytest.mark.parametrize("name", [
    generate_string(255), generate_string(1001), russian_chars(),
    russian_chars().upper(), chinese_chars(), special_chars(), "123"],
                         ids=["255 symbols", "more than 1000 symbols", "russian", "RUSSIAN",
                              "chinese", "specials", "digit"])
@pytest.mark.parametrize("animal_type", [
    generate_string(255), generate_string(1001)
    , russian_chars(), russian_chars().upper(), chinese_chars()
    , special_chars(), "123"],
                         ids=["255 symbols", "more than 1000 symbols",
                              "russian", "RUSSIAN", "chinese", "specials", "digit"])
@pytest.mark.parametrize("age", ["1"], ids=["min"])
@pytest.mark.post
def test_add_new_pet_with_valid_data_positive(get_api_key, name, animal_type, age, pet_photo='images/muh.jpg'):
    """Проверяем что можно добавить питомца с корректными данными и фото"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    auth_key = get_api_key["key"]

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


@pytest.mark.parametrize("name", [""], ids=["empty"])
@pytest.mark.parametrize("animal_type", [""], ids=["empty"])
@pytest.mark.parametrize("age", ["", "-1", "0", "1", "100", "1.5", "2147483647", "2147483648", special_chars(),
                                 russian_chars(), russian_chars().upper(), chinese_chars()]
    , ids=["empty", "negative", "zero", "min", "greater than max", "float", "int_max", "int_max + 1", "specials",
           "russian", "RUSSIAN", "chinese"])
@pytest.mark.parametrize("pet_photo", ["images/no_valid_photo.jpg", ""],
                         ids=["rename_txt", "empty_photo"])
@pytest.mark.post
def test_add_new_pet_with_photo_negative(get_api_key, name, animal_type, age, pet_photo):
    """Проверяем что запрос с не валидными параметрами, возвращает статус 400"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    auth_key = get_api_key["key"]

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400


@pytest.mark.parametrize("name", [
    generate_string(255), generate_string(1001), russian_chars(),
    russian_chars().upper(), chinese_chars(), special_chars(), "123"],
                         ids=["255 symbols", "more than 1000 symbols", "russian", "RUSSIAN",
                              "chinese", "specials", "digit"])
@pytest.mark.parametrize("animal_type", [
    generate_string(255), generate_string(1001)
    , russian_chars(), russian_chars().upper(), chinese_chars()
    , special_chars(), "123"],
                         ids=["255 symbols", "more than 1000 symbols",
                              "russian", "RUSSIAN", "chinese", "specials", "digit"])
@pytest.mark.parametrize("age", ["1"], ids=["min"])
@pytest.mark.post
def test_add_new_pet_simle_valid_date_positive(get_api_key, name, animal_type, age):
    """ Проверяем возможность создания карточки питомца без фото """
    # Получаем ключ auth_key и отправляем запрос на создание питомца без фото
    auth_key = get_api_key["key"]
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    # Проверяем статус запроса и строку json ответа

    assert status == 200
    assert result["name"] == name
    assert result["age"] == age
    assert result["animal_type"] == animal_type


@pytest.mark.parametrize("name", [""], ids=["empty"])
@pytest.mark.parametrize("animal_type", [""], ids=["empty"])
@pytest.mark.parametrize("age", ["", "-1", "0", "1", "100", "1.5", "2147483647", "2147483648", special_chars(),
                                 russian_chars(), russian_chars().upper(), chinese_chars()]
    , ids=["empty", "negative", "zero", "min", "greater than max", "float", "int_max", "int_max + 1", "specials",
           "russian", "RUSSIAN", "chinese"])
@pytest.mark.post
def test_add_new_pet_simle_valid_date_negative(get_api_key, name, animal_type, age):
    """ Проверяем возможность создания карточки питомца без фото """
    # Получаем ключ auth_key и отправляем запрос на создание питомца без фото
    auth_key = get_api_key["key"]
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    # Проверяем статус запроса и строку json ответа

    assert status == 400


@pytest.mark.post
def test_add_new_pet_simle_not_valid_auth_key(name="Leo", animal_type="cat", age="4"):
    """ Проверяем возможность создания карточки питомца без фото с не валидным
    ключом авторизации"""
    # Получаем ключ auth_key и отправляем запрос на создание питомца без фото
    auth_key = "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae700"
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    # Проверяем статус запроса и строку json ответа
    assert status == 403


@pytest.mark.post
def test_add_photo_simle_pet_positive(get_api_key, pet_photo="images/images.jpg"):
    """ Проверяем возможность добавить фото к карточке без фото питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Получаем ключ auth_key и запрашиваем список своих питомцев
    auth_key = get_api_key["key"]

    # Что бы не натыкаться на карточки с фото создаем нового питомца без фото
    pf.add_new_pet_simple(auth_key, "Суперкот", "кот", "3")
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id нового питомца из списка и отправляем запрос на добавление фото
    pet_id = my_pets['pets'][0]['id']
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)
    # Проверяем статус запроса 200 и json строку ответа,
    assert status == 200
    assert result['id'] == pet_id


@pytest.mark.parametrize("pet_photo", ["images/no_valid_photo.jpg", ""],
                         ids=["rename_txt", "empty_photo"])
@pytest.mark.post
def test_add_photo_simle_pet_negative(get_api_key, pet_photo):
    """ Проверяем возможность добавить фото к карточке без фото питомца с не корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)
    # Получаем ключ auth_key и запрашиваем список своих питомцев
    auth_key = get_api_key["key"]

    # Что бы не натыкаться на карточки с фото создаем нового питомца без фото
    pf.add_new_pet_simple(auth_key, "Суперкот", "кот", "3")
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id нового питомца из списка и отправляем запрос на добавление фото
    pet_id = my_pets['pets'][0]['id']
    status, result = pf.add_pet_photo(auth_key, pet_id, pet_photo)
    # Проверяем статус запроса 200 и json строку ответа,
    assert status == 400

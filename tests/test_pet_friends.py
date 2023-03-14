from api import PetFriends

from settings import valid_email, valid_password, not_valid_email, not_valid_password
import os
import pytest

pf = PetFriends()


# Функция генерации строка размера n
def generate_string(n):
    return "x" * n


# данные для проверки кириллической кодировки
def russian_chars():
    return "абвгдеёжзийклмнопрстуфхцчшщъыьэюя"


# данные для проверки китайской кодировки
def chinese_chars():
    return "北京位於華北平原的西北边缘"


# данные для проверки спецсимволов
def special_chars():
    return "|\\/!@#$%^&*()-_=+`~?№;:[]{}"


# # данные для проверки возраста
# def is_age_valid(age):
#     # Проверяем, что возраст - это число от 1 до 49 и целое
#     return age.isdigit() \
#         and 0 < int(age) < 50 \
#         and float(age) == int(age)


@pytest.mark.get
def test_get_api_key_for_valid_user(email=valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


@pytest.mark.parametrize("filter", ["", "my_pets"], ids=["empty string", "only my pets"])
@pytest.mark.get
def test_get_all_pets_with_valid_key_positive(get_api_key, filter):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """
    auth_key = get_api_key["key"]
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 200
    assert len(result['pets']) > 0


@pytest.mark.parametrize("filter", [generate_string(255), generate_string(1001),
                                    russian_chars(), russian_chars().upper(), chinese_chars(), special_chars(), 123],
                         ids=["255 symbols", "more then 1000 symbols",
                              'russian', 'RUSSIAN', 'chinese', 'specials', 'digit'])
@pytest.mark.get
def test_get_all_pets_with_valid_key_negative(get_api_key, filter):
    """ Проверяем что запрос всех питомцев возвращает не пустой список.
    Для этого сначала получаем api ключ и сохраняем в переменную auth_key. Далее используя этого ключ
    запрашиваем список всех питомцев и проверяем что список не пустой.
    Доступное значение параметра filter - 'my_pets' либо '' """
    auth_key = get_api_key["key"]
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 400
    assert len(result['pets']) > 0


@pytest.mark.post
def test_add_new_pet_with_valid_data(get_api_key, name='Барбоскин', animal_type='двортерьер', age='4',
                                     pet_photo='images/muh.jpg'):
    """Проверяем что можно добавить питомца с корректными данными"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    auth_key = get_api_key["key"]

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 200
    assert result['name'] == name


@pytest.mark.delete
def test_successful_delete_self_pet(get_api_key):
    """Проверяем возможность удаления питомца"""

    # Получаем ключ auth_key и запрашиваем список своих питомцев
    auth_key = get_api_key["key"]
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем - если список своих питомцев пустой, то добавляем нового и опять запрашиваем список своих питомцев
    if len(my_pets['pets']) == 0:
        pf.add_new_pet(auth_key, "Суперкот", "кот", "3", "images/images.jpg")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Берём id первого питомца из списка и отправляем запрос на удаление
    pet_id = my_pets['pets'][0]['id']
    status, _ = pf.delete_pet(auth_key, pet_id)

    # Ещё раз запрашиваем список своих питомцев
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Проверяем что статус ответа равен 200 и в списке питомцев нет id удалённого питомца
    assert status == 200
    assert pet_id not in my_pets.values()


@pytest.mark.put
def test_successful_update_self_pet_info(get_api_key, name='Мурзик', animal_type='Котэ', age=5):
    """Проверяем возможность обновления информации о питомце"""

    # Получаем ключ auth_key и список своих питомцев
    auth_key = get_api_key["key"]
    _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")

    # Если список не пустой, то пробуем обновить его имя, тип и возраст
    if len(my_pets['pets']) > 0:
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)

        # Проверяем что статус ответа = 200 и имя питомца соответствует заданному
        assert status == 200
        assert result['name'] == name
    else:
        # Если список питомцев пустой создаем питомца без фото, а потом его обновляем
        pf.add_new_pet_simple(auth_key, "Суперкот", "кот", "3")
        _, my_pets = pf.get_list_of_pets(auth_key, "my_pets")
        status, result = pf.update_pet_info(auth_key, my_pets['pets'][0]['id'], name, animal_type, age)
        assert status == 200
        assert result['name'] == name


@pytest.mark.parametrize("name", [
    generate_string(255), generate_string(1001)
    , russian_chars(), russian_chars().upper(), chinese_chars()
    , special_chars(), '123'],
                         ids=['255 symbols', 'more than 1000 symbols'
                             , 'russian', 'RUSSIAN', 'chinese', 'specials', 'digit'])
@pytest.mark.parametrize("animal_type", [
    generate_string(255), generate_string(1001)
    , russian_chars(), russian_chars().upper(), chinese_chars()
    , special_chars(), '123'],
                         ids=['255 symbols', 'more than 1000 symbols'
                             , 'russian', 'RUSSIAN', 'chinese', 'specials', 'digit'])
@pytest.mark.parametrize("age", ['1'], ids=['min'])
@pytest.mark.post
def test_add_new_pet_simle_valid_date(get_api_key, name, animal_type, age):
    """ Проверяем возможность создания карточки питомца без фото """
    # Получаем ключ auth_key и отправляем запрос на создание питомца без фото
    auth_key = get_api_key["key"]
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    # Проверяем статус запроса и строку json ответа

    assert status == 200
    assert result['name'] == name
    assert result['age'] == age
    assert result['animal_type'] == animal_type


@pytest.mark.parametrize("name", [""], ids=['empty'])
@pytest.mark.parametrize("animal_type", [""], ids=['empty'])
@pytest.mark.parametrize("age"
    , ['', '-1', '0', '1', '100', '1.5', '2147483647', '2147483648', special_chars(), russian_chars(),
       russian_chars().upper(), chinese_chars()]
    , ids=['empty', 'negative', 'zero', 'min', 'greater than max', 'float', 'int_max', 'int_max + 1', 'specials',
           'russian', 'RUSSIAN', 'chinese'])
@pytest.mark.post
def test_add_new_pet_simle_valid_date_negative(get_api_key, name, animal_type, age):
    """ Проверяем возможность создания карточки питомца без фото """
    # Получаем ключ auth_key и отправляем запрос на создание питомца без фото
    auth_key = get_api_key["key"]
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    # Проверяем статус запроса и строку json ответа

    assert status == 400


@pytest.mark.post
def test_add_photo_simle_pet_valid_date(get_api_key, pet_photo="images/images.jpg"):
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

    # Проверяем возможность получения ключа при не валидной почте


@pytest.mark.get
def test_get_api_key_for_not_valid_email(email=not_valid_email, password=valid_password):
    """ Проверяем что запрос api ключа возвращает статус 403 при использовании не валидной почты"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Проверяем получение статуса 403
    assert status == 403


@pytest.mark.get
def test_get_api_key_for_not_valid_password(email=valid_email, password=not_valid_password):
    """ Проверяем что запрос api ключа возвращает статус 403 при использовании не валидного пароля"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Проверяем получение статуса 403
    assert status == 403


@pytest.mark.skip(reason="Баг с создание нулевых полей")
@pytest.mark.post
def test_add_new_pet_simle_null_fields(get_api_key, name="", animal_type="", age=""):
    """ Проверяем возможность создания карточки питомца без фото
    с пустыми полями по документации запрос должен вернуть статус 400"""
    # Получаем ключ auth_key и отправляем запрос на создание питомца без фото
    auth_key = get_api_key["key"]
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    # Проверяем статус запроса и строку json ответа
    assert status == 400


@pytest.mark.xfail
@pytest.mark.post
def test_add_new_pet_simle_not_valid_auth_key(name="Leo", animal_type="cat", age="4"):
    """ Проверяем возможность создания карточки питомца без фото с не валидным
    ключом авторизации"""
    # Получаем ключ auth_key и отправляем запрос на создание питомца без фото
    auth_key = "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae700"
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    # Проверяем статус запроса и строку json ответа
    assert status == 403


@pytest.mark.get
def test_get_all_pets_with_not_valid_key(filter=''):
    """ Проверяем что запрос всех питомцев возвращает статус 403
    при не валидно значении auth_key"""

    auth_key = "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae700"
    status, result = pf.get_list_of_pets(auth_key, filter)

    assert status == 403


@pytest.mark.skip(reason="Баг с создание нулевых полей")
@pytest.mark.post
def test_add_new_pet_with_null_fields_with_photo(get_api_key, name='', animal_type='', age='',
                                                 pet_photo='images/muh.jpg'):
    """Проверяем что запрос с пустыми полями, но с фото возвращает статус 400"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    auth_key = get_api_key["key"]

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400


@pytest.mark.skip(reason="Баг на битом изображении")
@pytest.mark.post
def test_add_new_pet_with_not_valid_photo(get_api_key, name='Барбоскин', animal_type='двортерьер', age='4',
                                          pet_photo='images/no_valid_photo.jpg'):
    """Проверяем что запрос возвращает статус 400 если вместо фото передать текстовый файл
    переименованный в jpg, остальные поля валидны"""

    # Получаем полный путь изображения питомца и сохраняем в переменную pet_photo
    pet_photo = os.path.join(os.path.dirname(__file__), pet_photo)

    # Запрашиваем ключ api и сохраняем в переменную auth_key
    auth_key = get_api_key["key"]

    # Добавляем питомца
    status, result = pf.add_new_pet(auth_key, name, animal_type, age, pet_photo)

    # Сверяем полученный ответ с ожидаемым результатом
    assert status == 400

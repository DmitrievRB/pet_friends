import pytest

from api import PetFriends
from settings import *

pf = PetFriends()


@pytest.mark.parametrize("email", [valid_email], ids=["Валидная почта"])
@pytest.mark.parametrize("password", [valid_password], ids=["валидный пароль"])
@pytest.mark.get
def test_get_api_key_for_valid_user(email, password):
    """ Проверяем что запрос api ключа возвращает статус 200 и в результате содержится слово key"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 200
    assert 'key' in result


@pytest.mark.parametrize("email", [not_valid_email], ids=["не валидная почта"])
@pytest.mark.parametrize("password", [not_valid_password], ids=["не валидный пароль"])
@pytest.mark.get
def test_get_api_key_for_valid_user(email, password):
    """ Проверяем что запрос api ключа возвращает статус 403 при использовании не валидной почты"""

    # Отправляем запрос и сохраняем полученный ответ с кодом статуса в status, а текст ответа в result
    status, result = pf.get_api_key(email, password)

    # Сверяем полученные данные с нашими ожиданиями
    assert status == 403


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
def test_add_new_pet_simle_not_valid_auth_key(name="Leo", animal_type="cat", age="4"):
    """ Проверяем возможность создания карточки питомца без фото с не валидным
    ключом авторизации"""
    # Получаем ключ auth_key и отправляем запрос на создание питомца без фото
    auth_key = "ea738148a1f19838e1c5d1413877f3691a3731380e733e877b0ae700"
    status, result = pf.add_new_pet_simple(auth_key, name, animal_type, age)
    # Проверяем статус запроса и строку json ответа
    assert status == 403


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
@pytest.mark.put
def test_update_self_pet_info_positive(get_api_key, name, animal_type, age):
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
        assert result["animal_type"] == animal_type
        assert result["age"] == age


@pytest.mark.parametrize("name", [""], ids=["empty"])
@pytest.mark.parametrize("animal_type", [""], ids=["empty"])
@pytest.mark.parametrize("age", ["", "-1", "0", "1", "100", "1.5", "2147483647", "2147483648", special_chars(),
                                 russian_chars(), russian_chars().upper(), chinese_chars()]
    , ids=["empty", "negative", "zero", "min", "greater than max", "float", "int_max", "int_max + 1", "specials",
           "russian", "RUSSIAN", "chinese"])
def test_update_self_pet_info_negative(get_api_key, name, animal_type, age):
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
        assert status == 400

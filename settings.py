valid_email = "grant@gmail.com"
valid_password = "grant"
not_valid_email = "not_valid_email"
not_valid_password = "not_valid_password"


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

# Здесь находятся все конфигурационные переменные.
from os import environ

flask_configs = {
    "DEBUG": False,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 150
}

database_configs = {
    "url": "sqlite:///lore_prof.db",
    "recreate_database": False
}

admin_user = "testMe@gmail.com"
admin_name = "testEr"
admin_password = "MyStaticPassword, bro, calm down... I don't know for whom this one..."

if environ.get("DB_URL"):
    print("I am connecting to Database!")
    database_configs["url"] = environ.get("DB_URL")

token_size = 64
token_symbols = "qwertyuiopasdfghjklzxcvbnm1234567890"
token_expire_date = 86400

# 7 (604800 секунд) дней перед событием.
events_thru_to_date_in_seconds = 604800
event_date_format = "%Y-%m-%d %H:%M %z"

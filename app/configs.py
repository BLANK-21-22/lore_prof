# Здесь находятся все конфигурационные переменные.

flask_configs = {
    "DEBUG": True,
    "CACHE_TYPE": "SimpleCache",
    "CACHE_DEFAULT_TIMEOUT": 150
}
database_configs = {
    "url": "sqlite:///lore_prof.db",
    "recreate_database": False
}

token_size = 64
token_symbols = "qwertyuiopasdfghjklzxcvbnm1234567890"

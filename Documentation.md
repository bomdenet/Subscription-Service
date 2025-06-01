# sub_serv
Наш проект разделён на 2 части: серверную и клиентскую.

## SubServServer
Чтобы запустить сервер, необходимо выполнить команду:
```python
import asyncio
from sub_serv_server import *

# Данный сервер будет работать только на данном пк
asyncio.run(start_server("127.0.0.1", 8888))
```

## SubServClient
Для подключению к серверу необходимо указать его ip и port:
```python
from sub_serv_client import SubServClient


client = SubServClient("127.0.0.1", 8888)
```

```SubServClient``` отвечает за подключение к серверу, а так же авторизацию пользователя. Данный класс имеет 5 основных функций:
```python
# Функция, которая проверяет существует ли пользователь с данным ником
client.user_exists(username)
# Возвращает True/False

# Функция, которая проверяет ник на валидность
client.check_correct_username(username)
# Возвращает True или текст с ошибкой

# Функция, которая проверяет пароль на валидность
client.check_correct_password(password)
# Возвращает True или текст с ошибкой

# Функция, для регистрации пользователя
client.reg(username, password)
# Возвращает SubServClient нового пользователя или строку с ошибкой

# Функция, для авторизации пользователя
client.auth(username, password)
# Возвращает SubServClient или строку с ошибкой
```
Данные функции так же могут вернуть ```None```, при условии, что были проблемы при отправке сообщения

## SubServUser
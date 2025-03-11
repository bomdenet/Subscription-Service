from pyairtable import Api

def connecting(token, appToken):
    # Подключаемся
    api = Api(token)
    table = api.table(appToken, "Base")

    # Получаем данные
    while True:
        records = table.all()
        for record in records:
            print(record["fields"])
        input()

    # Добавляем пользователя
    # table.create({"Имя": "Иван", "Объекты": ["recXXXXXXXXXXXXXX"]})

    # Обновляем запись
    # table.update("recXXXXXXXXXXXXXX", {"Имя": "Иван Петров"})

    # Удаляем запись
    # table.delete("recXXXXXXXXXXXXXX")

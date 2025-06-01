from sub_serv_server.base_data import BaseData
from datetime import datetime, timedelta, timezone

def separator(msg):
    print("\n" + "=" * 20 + f" {msg} " + "=" * 20)

def readable_ts(ts):
    return datetime.fromtimestamp(ts, tz=timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')

def main():
    db = BaseData()

    # Очистка БД для чистого теста (если нужно)
    # db.cursor.execute("DELETE FROM users")
    # db.cursor.execute("DELETE FROM payments")
    # db.cursor.execute("DELETE FROM subscriptions")
    db.conn.commit()

    separator("После инициализации")
    db.print_debug_info()

    username = "testuser"
    password = "securePass123"
    user_id = None

    # Тест регистрации
    try:
        res = db.reg(username, password)
        if isinstance(res, Exception):
            print(f"Ошибка при регистрации: {res}")
            user_id = db.auth(username, password)  # auth возвращает user_id
        else:
            user_id = res
    except Exception as e:
        print(f"Ошибка при регистрации или аутентификации: {e}")

    if not user_id:
        print("Не удалось получить user_id, дальнейшие тесты не выполняются")
        return

    separator("После регистрации пользователя")
    db.print_debug_info()

    # Тест аутентификации
    try:
        auth_result = db.auth(username, password)
        if isinstance(auth_result, Exception):
            print(f"Ошибка при аутентификации: {auth_result}")
        else:
            print("Аутентификация успешна:", auth_result)
    except Exception as e:
        print(f"Ошибка при аутентификации: {e}")

    separator("После аутентификации")
    db.print_debug_info()

    # Регистрация второго пользователя для тестирования назначения админа
    second_username = "newadmin"
    second_password = "password123"
    second_user_id = db.reg(second_username, second_password)
    if isinstance(second_user_id, Exception):
        print(f"Ошибка при регистрации второго пользователя: {second_user_id}")
        return

    print(f"Второй пользователь зарегистрирован: {second_username}, ID: {second_user_id}")

    # Первый пользователь становится админом
    db.cursor.execute("UPDATE users SET is_admin = 1 WHERE user_id = ?", (user_id,))
    db.conn.commit()

    # Назначаем админа по имени
    try:
        result = db.set_admin_status(user_id, second_username, is_admin=1)
        if isinstance(result, Exception):
            print(f"Ошибка при установке статуса админа: {result}")
        else:
            print(f"Статус админа успешно назначен пользователю '{second_username}'")
    except Exception as e:
        print(f"Ошибка в set_admin_status: {e}")

    separator("После установки статуса админа")
    db.print_debug_info()

    # Получаем историю платежей (баланс должен быть 0)
    try:
        history = db.get_user_payments_history(second_user_id)
        print(f"История платежей пользователя {second_username}:")
        if history:
            for payment in history:
                print(payment)
        else:
            print("Нет записей о платежах.")
    except Exception as e:
        print(f"Ошибка при получении истории платежей: {e}")

    # Добавляем подписку
    try:
        db.add_subscribe(user_id, "Standard", 3, 299)
    except Exception as e:
        print(f"Ошибка при добавлении подписки: {e}")

    separator("После добавления подписки 'Standard'")
    db.print_debug_info()

    # Попробуем добавить ещё одну
    try:
        db.add_subscribe(user_id, "Premium", 30, 799)
    except Exception as e:
        print(f"Ошибка при добавлении второй подписки: {e}")

    separator("После добавления подписки 'Premium'")
    db.print_debug_info()

    # Получаем список доступных подписок
    try:
        available_subs = db.get_available_subscriptions()
        print("Доступные подписки:")
        for sub in available_subs:
            print(sub)
    except Exception as e:
        print(f"Ошибка при получении списка подписок: {e}")

    # Пользователь выбирает подписку
    selected_sub_name = "Standard"
    print(f"\nПользователь выбрал подписку: '{selected_sub_name}'")

    # Пробуем купить подписку без пополнения баланса
    try:
        result = db.assign_subscription_to_user(second_user_id, selected_sub_name)
        if isinstance(result, Exception):
            print(f"Ошибка при покупке подписки: {result}")
        else:
            print(f"Подписка '{selected_sub_name}' успешно куплена!")
    except Exception as e:
        print(f"Ошибка при покупке подписки: {e}")

    separator("После неудачной попытки покупки подписки")
    db.print_debug_info()

    # Пополняем баланс пользователя
    amount = 500
    print(f"\nПополняем баланс на {amount}")
    try:
        result = db.add_payment(second_user_id, amount)
        if isinstance(result, Exception):
            print(f"Ошибка при пополнении баланса: {result}")
        else:
            print(f"Баланс успешно увеличен на {amount}")
    except Exception as e:
        print(f"Ошибка при пополнении баланса: {e}")

    separator("После пополнения баланса")
    db.print_debug_info()

    # Пробуем снова купить подписку
    try:
        result = db.assign_subscription_to_user(second_user_id, selected_sub_name)
        if isinstance(result, Exception):
            print(f"Ошибка при покупке подписки: {result}")
        else:
            print(f"Подписка '{selected_sub_name}' успешно куплена!")
    except Exception as e:
        print(f"Ошибка при покупке подписки: {e}")

    separator("После покупки подписки")
    db.print_debug_info()

    # Пробуем купить другую подписку (проверим, хватает ли денег)
    selected_sub_name = "Premium"
    print(f"\nПользователь выбрал подписку: '{selected_sub_name}'")

    try:
        result = db.assign_subscription_to_user(second_user_id, selected_sub_name)
        if isinstance(result, Exception):
            print(f"Ошибка при покупке подписки '{selected_sub_name}': {result}")
        else:
            print(f"Подписка '{selected_sub_name}' успешно куплена!")
    except Exception as e:
        print(f"Ошибка при покупке подписки '{selected_sub_name}': {e}")

    separator("После попытки покупки второй подписки")
    db.print_debug_info()

    # Пробуем купить несуществующую подписку
    invalid_sub_name = "NonExistent"
    print(f"\nПопытка купить несуществующую подписку: '{invalid_sub_name}'")

    try:
        result = db.assign_subscription_to_user(second_user_id, invalid_sub_name)
        if isinstance(result, Exception):
            print(f"Ошибка при покупке подписки: {result}")
        else:
            print(f"Подписка '{invalid_sub_name}' успешно куплена?")
    except Exception as e:
        print(f"Ошибка при покупке подписки: {e}")

if __name__ == "__main__":
    main()
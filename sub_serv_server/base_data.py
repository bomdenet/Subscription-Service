import sqlite3
import time
import uuid
from datetime import datetime, timedelta
import hashlib


class BaseData:
    def __init__(self, db_name="example.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.conn.row_factory = sqlite3.Row
        self.cursor = self.conn.cursor()
        self.min_len_username = 4
        self.min_len_password = 8
        self.characters_in_username = "abcdefghijklmnopqrstuvwxyz0123456789"
        self.incorrect_characters_in_password = " *"
        self.__create_payment_table()
        self.__create_users_table()
        self.__create_subscribe_table()

    def __create_users_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER UNIQUE,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER NOT NULL CHECK (is_admin IN (0, 1)),
                subscription INTEGER,
                subscription_name TEXT,
                balance INTEGER DEFAULT 0
            )
        """)
        self.conn.commit()

    def __create_payment_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER NOT NULL,
                date INTEGER NOT NULL,
                user_id TEXT,
                status INTEGER NOT NULL CHECK (status IN (0, 1)),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        self.conn.commit()

    def __create_subscribe_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_subscr TEXT UNIQUE NOT NULL,
                length INTEGER NOT NULL,
                price INTEGER NOT NULL
            )
        """)
        self.conn.commit()

    def __generate_user_id(self):
        raw = f"{time.time()}{uuid.uuid4()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def __find_user(self, username):
        self.cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        print(row)
        return row["user_id"] if row else None

    def user_exists(self, username):
        return self.__find_user(username) is not None

    def check_correct_username(self, username):
        if len(username) < self.min_len_username:
            return Exception(f"The username is too short. Minimum length is {self.min_len_username} characters")
        for i in username:
            if i.lower() not in self.characters_in_username:
                return Exception("The username contains incorrect characters.")
        return True

    def check_correct_password(self, password):
        if len(password) < self.min_len_password:
            return Exception(f"The password is too short. Minimum length is {self.min_len_password} characters")
        for i in password:
            if i.lower() in self.incorrect_characters_in_password:
                return Exception("The password contains incorrect characters")
        return True

    def reg(self, username, password):
        if (result := self.check_correct_username(username)) is not True:
            return result
        if (result := self.check_correct_password(password)) is not True:
            return result
        if self.__find_user(username):
            return Exception("The username is busy")

        user_id = self.__generate_user_id()

        # Проверяем, первый ли это пользователь
        self.cursor.execute("SELECT COUNT(*) FROM users")
        count = self.cursor.fetchone()[0]
        is_admin = 1 if count == 0 else 0

        self.cursor.execute("""
            INSERT INTO users (username, password, is_admin, subscription, user_id, balance)
            VALUES (?, ?, ?, 0, ?, 0)
        """, (username, password, is_admin, user_id))
        self.conn.commit()
        return user_id

    def auth(self, username, password):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()
        if user is None:
            return Exception("The username is incorrect")
        if user["password"] != password:
            return Exception("The password is incorrect")
        return user["user_id"]

    def add_payment(self, user_id, amount):
        if amount <= 0:
            return Exception("Amount must be positive")

        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = self.cursor.fetchone()
        if user is None:
            return Exception("User not found")

        timestamp = int(datetime.utcnow().timestamp())
        self.cursor.execute("""
            INSERT INTO payments (amount, date, user_id, status)
            VALUES (?, ?, ?, 1)
        """, (amount, timestamp, user_id))

        # Увеличить баланс пользователя
        self.cursor.execute("""
            UPDATE users SET balance = balance + ? WHERE user_id = ?
        """, (amount, user_id))

        self.conn.commit()
        return True

    def add_subscribe(self, user_id, name, length, price):
        if length <= 0 or price < 0:
            return Exception("Invalid length or price")
        user = self.__get_user_info_full(user_id)
        if not user or user["is_admin"] < 1:
            return Exception("Access denied")

        self.cursor.execute("SELECT * FROM subscriptions WHERE name_subscr = ?", (name,))
        if self.cursor.fetchone():
            return Exception("Subscription with this name already exists")

        self.cursor.execute("""
            INSERT INTO subscriptions (name_subscr, length, price)
            VALUES (?, ?, ?)
        """, (name, length, price))
        self.conn.commit()

    def assign_subscription_to_user(self, user_id, subscription_name):
        user = self.__get_user_info_full(user_id)
        if not user:
            return Exception("User not found")

        self.cursor.execute("SELECT length, price FROM subscriptions WHERE name_subscr = ?", (subscription_name,))
        row = self.cursor.fetchone()
        if not row:
            return Exception("Subscription not found")

        length = row["length"]
        price = row["price"]

        if user["balance"] < price:
            return Exception("Not enough balance to purchase this subscription")

        expires_at = int((datetime.utcnow() + timedelta(days=length)).timestamp())

        self.cursor.execute("""
            UPDATE users 
            SET 
                subscription = ?, 
                subscription_name = ?, 
                balance = balance - ?
            WHERE user_id = ?
        """, (expires_at, subscription_name, price, user_id))
        self.conn.commit()

        return True

    def edit_subscribe(self, user_id, name, new_length, new_price):
        if new_length <= 0 or new_price < 0:
            return Exception("Invalid data")
        user = self.__get_user_info_full(user_id)
        if not user or user["is_admin"] < 1:
            return Exception("Access denied")

        self.cursor.execute("SELECT * FROM subscriptions WHERE name_subscr = ?", (name,))
        if not self.cursor.fetchone():
            return Exception("Subscription not found")

        self.cursor.execute("""
            UPDATE subscriptions
            SET length = ?, price = ?
            WHERE name_subscr = ?
        """, (new_length, new_price, name))
        self.conn.commit()

    def delete_subscribe(self, user_id, name):
        user = self.__get_user_info_full(user_id)
        if not user or user["is_admin"] < 1:
            return Exception("Access denied")

        self.cursor.execute("DELETE FROM subscriptions WHERE name_subscr = ?", (name,))
        self.cursor.execute("""
            UPDATE users 
            SET subscription = 0, subscription_name = NULL 
            WHERE subscription_name = ?
        """, (name,))
        self.conn.commit()
    # мб стереть нахуй
    def get_users_with_expiring_subscriptions(self, within_days: int = 3):
        now_ts = int(datetime.utcnow().timestamp())
        future_ts = now_ts + within_days * 86400
        self.cursor.execute("""
            SELECT * FROM users
            WHERE subscription IS NOT NULL AND subscription > 0 AND subscription <= ?
        """, (future_ts,))
        return [dict(row) for row in self.cursor.fetchall()]
    
    def get_available_subscriptions(self):
        self.cursor.execute("SELECT name_subscr, price, length FROM subscriptions")
        return [dict(row) for row in self.cursor.fetchall()]

    def __get_user_info_full(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def get_user_info(self, user_id):
        user = self.__get_user_info_full(user_id)
        if not user:
            return None

        # Удаляем ненужные поля
        for key in ['password', 'id', 'user_id']:
            if key in user:
                del user[key]

        return user


    def print_debug_info(self):
        print("=== USERS TABLE ===")
        self.cursor.execute("SELECT * FROM users")
        for row in self.cursor.fetchall():
            print(dict(row))

        print("\n=== PAYMENTS TABLE ===")
        self.cursor.execute("SELECT * FROM payments")
        for row in self.cursor.fetchall():
            print(dict(row))

        print("\n=== SUBSCRIPTIONS TABLE ===")
        self.cursor.execute("SELECT * FROM subscriptions")
        for row in self.cursor.fetchall():
            print(dict(row))

    # ✅ Новая функция: получить историю платежей пользователя
    def get_user_payments_history(self, user_id):
        self.cursor.execute("SELECT * FROM payments WHERE user_id = ?", (user_id,))
        return [dict(row) for row in self.cursor.fetchall()]

    # ✅ Назначение админа
    def set_admin_status(self, admin_id, target_username, is_admin):

        # Проверяем права у текущего пользователя
        admin_info = self.__get_user_info_full(admin_id)
        if not admin_info or admin_info["is_admin"] < 1:
            return Exception("You don't have permission to change admin status")

        # Находим целевого пользователя по username
        self.cursor.execute("SELECT user_id FROM users WHERE username = ?", (target_username,))
        result = self.cursor.fetchone()
        if not result:
            return Exception(f"User with username '{target_username}' not found")

        target_user_id = result["user_id"]

        # Обновляем статус
        self.cursor.execute("UPDATE users SET is_admin = ? WHERE user_id = ?", (is_admin, target_user_id))
        self.conn.commit()

        return True
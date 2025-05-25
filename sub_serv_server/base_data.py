import sqlite3
import hashlib
import time
import uuid
from datetime import datetime, timedelta, timezone


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
                user_id TEXT UNIQUE,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER NOT NULL CHECK (is_admin IN (0, 1, 2)),
                subscription INTEGER,
                payments INTEGER,
                FOREIGN KEY (payments) REFERENCES payments(id)
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
                name_subscr TEXT NOT NULL,
                length INTEGER NOT NULL,
                price INTEGER NOT NULL,
                discount REAL,
                end_discount INTEGER
            )
        """)
        self.conn.commit()

    def __encrypt(self, text):
        return hashlib.sha256(text.encode()).hexdigest()

    def __generate_user_id(self):
        raw = f"{time.time()}{uuid.uuid4()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]

    def __find_user(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def user_exists(self, username):
        return self.__find_user(username) is not None

    def check_correct_username(self, username):
        if len(username) < self.min_len_username:
            return Exception(f"The username is too short. Minimum length is {self.min_len_username} characters")
        for i in username:
            if i.lower() not in self.characters_in_username:
                return Exception("The username contains incorrect characters. You can use only letters of the Latin alphabet and numbers.")
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
        if self.__find_user(username) is not None:
            return Exception("The username is busy")

        hashed_password = self.__encrypt(password)
        user_id = self.__generate_user_id()
        self.cursor.execute("""
            INSERT INTO users (username, password, is_admin, subscription, payments, user_id)
            VALUES (?, ?, ?, ?, NULL, ?)
        """, (username, hashed_password, 0, 0, user_id))
        self.conn.commit()
        return self.__find_user(username)

    def auth(self, username, password):
        hashed_password = self.__encrypt(password)
        user = self.__find_user(username)
        if user is None:
            return Exception("The username is incorrect")
        if user["password"] != hashed_password:
            return Exception("The password is incorrect")
        return user

    def add_payment(self, username, amount):
        user = self.__find_user(username)
        if user is None:
            return Exception("The username is incorrect")

        user_id = user["user_id"]
        timestamp = int(datetime.utcnow().timestamp())
        status = 1

        self.cursor.execute("""
            INSERT INTO payments (amount, date, user_id, status)
            VALUES (?, ?, ?, ?)
        """, (amount, timestamp, user_id, status))

        payment_id = self.cursor.lastrowid
        self.cursor.execute("""
            UPDATE users SET payments = ? WHERE user_id = ?
        """, (payment_id, user_id))
        self.conn.commit()

    def add_subscribe(self, name, length, price):
        self.cursor.execute("""
            INSERT INTO subscriptions (name_subscr, length, price, discount, end_discount)
            VALUES (?, ?, ?, NULL, NULL)
        """, (name, length, price))
        self.conn.commit()

    def assign_subscription_to_user(self, user_id, subscription_name):
        self.cursor.execute("SELECT length FROM subscriptions WHERE name_subscr = ?", (subscription_name,))
        result = self.cursor.fetchone()
        if not result:
            return Exception("Подписка с таким названием не найдена")

        length_months = int(result["length"])
        end_date = datetime.now(timezone.utc) + timedelta(days=30 * length_months)
        timestamp = int(end_date.timestamp())

        self.cursor.execute(
            "UPDATE users SET subscription = ? WHERE user_id = ?",
            (timestamp, user_id)
        )
        self.conn.commit()

    def set_discount_for_subscription(self, subscription_name, discount_value: float, discount_days: int):
        self.cursor.execute("""
            SELECT id FROM subscriptions WHERE name_subscr = ?
        """, (subscription_name,))
        result = self.cursor.fetchone()
        if not result:
            return Exception("Subscription not found")

        end_discount_date = int((datetime.utcnow() + timedelta(days=discount_days)).timestamp())

        self.cursor.execute("""
            UPDATE subscriptions
            SET discount = ?, end_discount = ?
            WHERE name_subscr = ?
        """, (discount_value, end_discount_date, subscription_name))

        self.conn.commit()

    def get_users_with_expiring_subscriptions(self, within_days: int = 3):
        now_ts = int(datetime.utcnow().timestamp())
        future_ts = now_ts + within_days * 86400
        self.cursor.execute("""
            SELECT * FROM users
            WHERE subscription IS NOT NULL AND subscription > 0 AND subscription <= ?
        """, (future_ts,))
        return [dict(row) for row in self.cursor.fetchall()]

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

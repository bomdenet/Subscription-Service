import sqlite3
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
                is_admin INTEGER NOT NULL CHECK (is_admin IN (0, 1)),
                subscription INTEGER,
                payments INTEGER,
                yoomoney_token TEXT,
                subscription_name TEXT
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
        return raw[:16]

    def __find_user(self, username):
        self.cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
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
        self.cursor.execute("""
            INSERT INTO users (username, password, is_admin, subscription, payments, user_id, yoomoney_token)
            VALUES (?, ?, 0, 0, NULL, ?, NULL)
        """, (username, password, user_id))
        self.conn.commit()
        return self.get_user_info(user_id)

    def auth(self, username, password):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        user = self.cursor.fetchone()
        if user is None:
            return Exception("The username is incorrect")
        if user["password"] != password:
            return Exception("The password is incorrect")
        return dict(user)

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

        payment_id = self.cursor.lastrowid
        self.cursor.execute("UPDATE users SET payments = ? WHERE user_id = ?", (payment_id, user_id))
        self.conn.commit()

    def add_subscribe(self, user_id, name, length, price):
        if length <= 0 or price < 0:
            return Exception("Invalid length or price")
        user = self.get_user_info(user_id)
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
        user = self.get_user_info(user_id)
        if not user:
            return Exception("User not found")

        self.cursor.execute("SELECT length FROM subscriptions WHERE name_subscr = ?", (subscription_name,))
        row = self.cursor.fetchone()
        if not row:
            return Exception("Subscription not found")

        length = row["length"]
        expires_at = int((datetime.utcnow() + timedelta(days=length)).timestamp())

        self.cursor.execute("""
            UPDATE users 
            SET subscription = ?, subscription_name = ?
            WHERE user_id = ?
        """, (expires_at, subscription_name, user_id))
        self.conn.commit()


    def edit_subscribe(self, user_id, name, new_length, new_price):
        if new_length <= 0 or new_price < 0:
            return Exception("Invalid data")
        user = self.get_user_info(user_id)
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
        user = self.get_user_info(user_id)
        if not user or user["is_admin"] < 1:
            return Exception("Access denied")

        self.cursor.execute("DELETE FROM subscriptions WHERE name_subscr = ?", (name,))
        self.cursor.execute("""
            UPDATE users 
            SET subscription = 0, subscription_name = NULL 
            WHERE subscription_name = ?
        """, (name,))
        self.conn.commit()

    def get_users_with_expiring_subscriptions(self, within_days: int = 3):
        now_ts = int(datetime.utcnow().timestamp())
        future_ts = now_ts + within_days * 86400
        self.cursor.execute("""
            SELECT * FROM users
            WHERE subscription IS NOT NULL AND subscription > 0 AND subscription <= ?
        """, (future_ts,))
        return [dict(row) for row in self.cursor.fetchall()]

    def get_user_info(self, user_id):
        self.cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        row = self.cursor.fetchone()
        return dict(row) if row else None

    def edit_yoomoney_token(self, user_id, new_token):
        self.cursor.execute("UPDATE users SET yoomoney_token = ? WHERE user_id = ?", (new_token, user_id))
        self.conn.commit()

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

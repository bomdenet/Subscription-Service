import sqlite3
import hashlib
import time
import uuid
from datetime import datetime, timedelta
from exception import *
 

class BaseData:
 
    def __init__(self, db_name="example.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.min_len_username = 4
        self.min_len_password = 8
        self.characters_in_username = "abcdefghijklmnopqrstuvwxyz0123456789"
        self.incorrect_characters_in_password = " *"
        self.conn.row_factory = sqlite3.Row
        self.create_payment_table()
        self.create_users_table()
        self.create_subscribe_table()

    def create_users_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id TEXT UNIQUE,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER NOT NULL CHECK (is_admin IN (0, 1, 2)),
                subscription TEXT,
                payments INTEGER,
                FOREIGN KEY (payments) REFERENCES payments(id)
            )
 
        """)
        self.conn.commit()
 

    def create_payment_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER NOT NULL,
                date TEXT NOT NULL,
                user_id TEXT,
                status INTEGER NOT NULL CHECK (status IN (0, 1)),
                FOREIGN KEY (user_id) REFERENCES users(user_id)
            )
        """)
        self.conn.commit()
 

    def create_subscribe_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS subscriptions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name_subscr TEXT NOT NULL,
                length TEXT NOT NULL,
                price INTEGER NOT NULL,
                discount REAL,
                end_discount TEXT,
                user_id TEXT,
                FOREIGN KEY (user_id) REFERENCES users(user_id)
 
            )
 
        """)
        self.conn.commit()

 
    def __encrypt(self, text):
        return hashlib.sha256(text.encode()).hexdigest()
 
    def generate_user_id():
        raw = f"{time.time()}{uuid.uuid4()}"
        return hashlib.sha256(raw.encode()).hexdigest()[:16]
 
    def __find_user(self, username):
        self.cursor.execute("SELECT * FROM users WHERE username = ?", (username,))
        row = self.cursor.fetchone()
        if row:
            return dict(row)
        else:
            return None
 
    def user_exists(self, username):
        if self.__find_user(username) is None:
            return False
        return True
    
    def check_correct_username(self, username):
        if len(username) < self.min_len_username:
            return ShortUsername(f"The username is too short. Minimum length is {self.min_len_username} characters")
        for i in username:
            if i.lower() not in self.characters_in_username:
                return IncorrectCharectersInUsername("The username contains incorrect characters. You can use only letters of the Latin alphabet and numbers.")
        return True

    def check_correct_password(self, password):
        if len(password) < self.min_len_password:
            return ShortPassword(f"The password is too short. Minimum length is {self.min_len_password} characters")
        for i in password:
            if i.lower() in self.incorrect_characters_in_password:
                return IncorrectCharectersInPassword("The password contains incorrect characters")
        return True
 
    def reg(self, username, password):
        result_check_correct_username = self.check_correct_username(username)
        if type(result_check_correct_username) is not bool:
            raise result_check_correct_username
 
        result_check_correct_password = self.check_correct_password(password)
        if type(result_check_correct_password) is not bool:
            raise result_check_correct_password
        
        user = self.__find_user(username)
 
        if user is not None:
            raise UsernameIsBusy("The username is busy")
 

        hashed_password = self.__encrypt(password)
        user_id = self.generate_user_id()
 
        self.cursor.execute("""
            INSERT INTO users (username, password, is_admin, subscription, payments, user_id)
            VALUES (?, ?, ?, ?, NULL, ?)
        """, (username, hashed_password, 0, datetime.min.isoformat()), user_id)
        self.conn.commit()

        return user

    def auth(self, username, password):
        hashed_password = self.__encrypt(password)
        user = self.__find_user(username)
        if user is None:
            raise IncorrectUsername("The username is incorrect")
        if (user["fields"]["Password"] != hashed_password):
            raise IncorrectPassword("The password is incorrect")
        return user  
    
    def add_payment(self, username, amount):
        self.cursor.execute("SELECT user_id FROM users WHERE username = ?", (username,))
        result = self.__find_user(username)
        if result is None:
            raise IncorrectUsername("The username is incorrect") 

        user_id = result[0]
        date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        status = 1
        self.cursor.execute("""
            INSERT INTO payments (amount, date, user_id, status)
            VALUES (?, ?, ?, ?)
        """, (amount, date, user_id, status))

        payment_id = self.cursor.lastrowid
 
        self.cursor.execute("""
            UPDATE users SET payments = ? WHERE user_id = ?
        """, (payment_id, user_id))
        self.conn.commit()
 
    def add_subscribe(self, name, length, price):
        self.cursor.execute("""
            INSERT INTO subscriptions (name_subscr, length, price, discount, end_discount, user_id)
            VALUES (?, ?, ?, NULL, NULL, NULL)
        """, (name, length, price))
        self.conn.commit()
 
    def assign_subscribe_to_users(self, subscription_name):
        self.cursor.execute("""
            SELECT length FROM subscriptions WHERE name_subscr = ?
        """, (subscription_name,))

        result = self.cursor.fetchone()
 
        if not result:
            raise IncorrectSubscription("Subscription not found")
 
        duration_days = result[0]
 
        self.cursor.execute("""
            SELECT user_id, payments FROM users WHERE subscription IS NULL
        """)
 
        users = self.cursor.fetchall()

        for user_id, payment_id in users:
            if payment_id is None:
                continue
 
            # Получаем дату платежа
            self.cursor.execute("""
                SELECT date FROM payments WHERE id = ?
            """, (payment_id,))

            payment_result = self.cursor.fetchone()
 
            if not payment_result:
                   continue
            
            payment_date = datetime.strptime(payment_result[0], "%Y-%m-%d %H:%M:%S")
            end_date = payment_date + timedelta(days=duration_days * 30)

            # Обновляем пользователя
            self.cursor.execute("""
                UPDATE users
                SET subscription = ? WHERE user_id = ?
            """, (end_date.strftime("%Y-%m-%d %H:%M:%S"),  user_id))

        self.conn.commit()

    def set_discount_for_subscription(self, subscription_name, discount_value: float, discount_days: int):

        self.cursor.execute("""
            SELECT id FROM subscriptions WHERE name_subscr = ?
        """, (subscription_name,))
        result = self.cursor.fetchone()
        if not result:
            raise IncorrectSubscription("Subscription not found")

        end_discount_date = (datetime.now() + timedelta(days=discount_days)).strftime("%Y-%m-%d %H:%M:%S")

        
        self.cursor.execute("""
            UPDATE subscriptions
            SET discount = ?, end_discount = ?
            WHERE name_subscr = ?
        """, (discount_value, end_discount_date, subscription_name))

        self.conn.commit()

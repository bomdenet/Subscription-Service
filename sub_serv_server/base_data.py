import sqlite3
import hashlib
from datetime import datetime
from sub_serv_server.exception import *


class BaseData:
    def __init__(self, db_name="example.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(self.db_name)
        self.cursor = self.conn.cursor()
        self.min_len_username = 4
        self.min_len_password = 8
        self.characters_in_username = "abcdefghijklmnopqrstuvwxyz0123456789"
        self.incorrect_characters_in_password = " *"

    def create_users_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                is_admin INTEGER NOT NULL CHECK (is_admin IN (0, 1)),
                balance INTEGER NOT NULL DEFAULT 0,
                subscription TEXT,
                payment INTEGER,
                subscription_type TEXT
            )
        """)
        self.conn.commit()

    def create_payment_table(self):
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS payments (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                amount INTEGER NOT NULL,
                date TEXT NOT NULL,
                type_payment TEXT NOT NULL,
                user_id INTEGER NOT NULL,
                is_admin INTEGER NOT NULL CHECK (is_admin IN (0,1)),
                FOREIGN KEY (user_id) REFERENCES users(id)
            )
        """)
        self.conn.commit()

    def __encrypt(self, text):
        return hashlib.sha256(text.encode()).hexdigest()
    
    def __find_user(self, username):
        find_data = self.cursor.fetchone()[1]
        if (len(find_data) == 0):
            return None
        return find_data[1]
    
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
        user = self.__user_table.create({
            "Username": username,
            "Password": hashed_password,
            "Is admin": False,
            "Balance": 0,
            "Subscription": datetime.min.isoformat()
        })
        self.cursor.execute("""
            INSERT INTO users (username, password_hash, is_admin, balance, subscription)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (username, hashed_password, 0, 0, datetime.min.isoformat()))
        self.conn.commit()

        return self.__create_user(user)
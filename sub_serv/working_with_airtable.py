from pyairtable import Api
import hashlib
from sub_serv.exception import *
from datetime import datetime


class BaseData:
    def __init__(self, token, appToken):
        self.__user_table = Api(token).table(appToken, "Users")
        self.min_len_username = 4
        self.min_len_password = 8
        self.characters_in_username = "abcdefghijklmnopqrstuvwxyz0123456789"
        self.incorrect_characters_in_password = " *"

    def __encrypt(self, text):
        return hashlib.sha256(text.encode()).hexdigest()

    def __find_user(self, username):
        find_data = self.__user_table.all(formula=f"Username='{username}'")
        if (len(find_data) == 0):
            return None
        return find_data[0]

    def __create_user(self, user):
        if (user["fields"].get("Is admin", False)):
            return Admin(user["id"], self.__user_table)
        else:
            return User(user["id"], self.__user_table)

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

    def user_exists(self, username):
        if self.__find_user(username) is None:
            return False
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

        return self.__create_user(user)

    def auth(self, username, password):
        hashed_password = self.__encrypt(password)
        user = self.__find_user(username)
        if user is None:
            raise IncorrectUsername("The username is incorrect")
        if (user["fields"]["Password"] != hashed_password):
            raise IncorrectPassword("The password is incorrect")
        return self.__create_user(user)


class User:
    def __init__(self, id, user_table):
        self.__user_table = user_table
        self.__id = id
        self.auto_update = False
        self.update()
    
    def update(self):
        self.__data = self.__user_table.get(self.__id)["fields"]

    @property
    def data(self):
        if self.auto_update:
            self.update()
        
        return self.__data
    
    @property
    def username(self):
        return self.data["Username"]

    @property
    def is_admin(self):
        return self.data.get("Is admin", False)
    
    @property
    def balance(self):
        return self.data["Balance"]
    
    #При определении даты и ремени необходимо не забыть про часовые пояса, в бд использовать время utc
    @property
    def subscription(self):
        return self.data["Subscription"]


class Admin(User):
    pass
from pyairtable import Api
import hashlib
from SubServ.SubServException import *
from datetime import datetime


class BaseData:
    def __init__(self, token, appToken):
        self.__table = Api(token).table(appToken, "Base")

    def writeTable(self):
        records = self.__table.all()
        print(records)
    
    def __encrypt(self, text):
        return hashlib.sha256(text.encode()).hexdigest()

    def reg(self, username, password):
        if len(password) < 8:
            raise ShortPassword("The password is too short")
        filtered_records = self.__table.all(formula=f"Username='{username}'")
        if len(filtered_records) != 0:
            raise UsernameIsBusy("The username is busy")
        
        hashed_password = self.__encrypt(password)
        return self.__table.create({
            "Username": username,
            "Password": hashed_password,
            "Is admin": False,
            "Balance": 0,
            "Is admin": False,
            "Subscription": datetime.min.isoformat()
        })["id"]

    def auth(self, username, password):
        hashed_password = self.__encrypt(password)
        filtered_records = self.__table.all(formula=f"Username='{username}'")
        if (len(filtered_records) == 0):
            raise IncorrectUser("The username is incorrect")
        if (filtered_records[0]["fields"]["Password"] != hashed_password):
            raise IncorrectPassword("The password is incorrect")
        return filtered_records[0]["id"]

    def getData(self, id):
        return self.__table.get(id)["fields"]
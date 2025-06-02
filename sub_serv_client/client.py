import socket
import hashlib
from .user import SubServUser


class SubServClient:
    def __init__(self, host: str, port: int):
        self.host = host
        self.port = port
        self.__socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try:
            self.__socket.connect((self.host, self.port))
            self.__connected = True
        except Exception:
            self.__connected = False

    def __send_message(self, message: str) -> bool:
        if self.__connected:
            try:
                self.__socket.sendall(message.encode())
                return True
            except Exception:
                self.__connected = False
                return False

    def __encrypt(self, text: str):
        return hashlib.sha256(text.encode()).hexdigest()

    def __get_message(self) -> str | None:
        if self.__connected:
            try:
                data = self.__socket.recv(1024)
                if not data:
                    self.__connected = False
                    return None
                return data.decode()
            except Exception:
                self.__connected = False
                return None

    def __check_correct_data(self, data: str) -> bool:
        if "|" in data or "&" in data:
            return False
        return True

    def __check_for_id(self, data: str) -> bool | None:
        if (len(data.split("|")) < 2):
            return None
        
        if data.split("|")[0] == "id":
            return True
        else:
            return False


    # Проверка на то, существует ли пользователь с данным ником
    def user_exists(self, username: str) -> str | bool | None:
        if not self.__check_correct_data(username):
            return "Incorrect data"
        
        self.__send_message(f"user_exists|{username}")
        response = self.__get_message()
        if response.lower() == "true":
            return True
        elif response.lower() == "false":
            return False
        else:
            return None

    # Проверка на корректность ника
    def check_correct_username(self, username: str) -> str | bool | None:
        if not self.__check_correct_data(username):
            return "Incorrect data"
        
        self.__send_message(f"check_correct_username|{username}")
        response = self.__get_message()
        if response is None:
            return None
        elif response.lower() == "true":
            return True
        else:
            return response
    
    # Проверка на корректность пароля
    def check_correct_password(self, password: str) -> str | bool | None:
        if not self.__check_correct_data(password):
            return "Incorrect data"
        
        self.__send_message(f"check_correct_password|{password}")
        response = self.__get_message()
        if response is None:
            return None
        elif response.lower() == "true":
            return True
        else:
            return response
    
    # Регистрация пользователя
    def reg(self, username: str, password: str) -> SubServUser | str | None:
        if not self.__check_correct_data(username) or not self.__check_correct_data(password):
            return "Incorrect data"
        
        self.__send_message(f"reg|{username}&{self.__encrypt(password)}")
        response = self.__get_message()
        if response is None:
            return None
        else:
            if self.__check_for_id(response):
                return SubServUser(self.__socket, response.split("|")[1])
            else:
                return response
    
    # Авторизация пользователя
    def auth(self, username: str, password: str) -> SubServUser | str | None:
        if not self.__check_correct_data(username) or not self.__check_correct_data(password):
            return "Incorrect data"
        
        self.__send_message(f"auth|{username}&{self.__encrypt(password)}")
        response = self.__get_message()
        if response is None:
            return None
        else:
            if self.__check_for_id(response):
                return SubServUser(self.__socket, response.split("|")[1])
            else:
                return response


    def is_connected(self) -> bool:
        return self.__connected

    def disconnect(self):
        if self.__connected:
            self.__connected = False
            try:
                self.__socket.shutdown(socket.SHUT_RDWR)
            except Exception:
                pass
            self.__socket.close()

import ast
import socket


class SubServUser:
    def __init__(self, socket: socket.socket, id: str):
        self.__id = id
        self.__socket = socket
        self.__connected = True

    def __send_message(self, message: str) -> bool:
        if self.__connected:
            try:
                self.__socket.sendall(message.encode())
                return True
            except Exception:
                self.__connected = False
                return False

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

    def __get_big_message(self) -> list | None:
        response = []
        data = self.__get_message().split("&")
        for item in data:
            if item != "":
                response.append(item)
        while response[-1] != "end" and type(response[-1]) is str:
            data = self.__get_message().split("&")
            for item in data:
                if item != "":
                    response.append(item)
        
        return response[:-1:]

    def __check_correct_data(self, data: str) -> bool:
        if "|" in data or "&" in data:
            return False
        return True


    # Получение информации о пользователе
    def get_user_info(self) -> dict | None:
        self.__send_message(f"get_user_info|{self.__id}")
        response = self.__get_message()
        if type(response) is str:
            return ast.literal_eval(response)
        else:
            return None
    
    def get_user_payments_history(self) -> list | None:
        self.__send_message(f"get_user_payments_history|{self.__id}")
        response = self.__get_big_message()
        
        if type(response) is list:
            response = [ast.literal_eval(item) for item in response]
            return response
        else:
            return None

    # Пополнение баланса
    def add_payment(self, amount: int) -> bool | str | None:
        self.__send_message(f"add_payment|{self.__id}&{amount}")
        response = self.__get_message()
        if response.lower() == "true":
            return True
        elif type(response) is str:
            return response
        else:
            return None


    # Получить информацию о типах подписок
    def get_available_subscriptions(self) -> list | None:
        self.__send_message(f"get_available_subscriptions")
        response = self.__get_big_message()
        
        if type(response) is list:
            response = [ast.literal_eval(item) for item in response]
            return response
        else:
            return None

    # Оплата подписки
    def assign_subscription_to_user(self, subscription_name: str) -> bool | str | None:
        if not self.__check_correct_data(subscription_name):
            return "Incorrect data"
        
        self.__send_message(f"assign_subscription_to_user|{self.__id}&{subscription_name}")
        response = self.__get_message()
        if response.lower() == "true":
            return True
        elif type(response) is str:
            return response
        else:
            return None

    # Работа с подписками(только для админа)
    def add_subscribe(self, name: str, length: int, price: int) -> bool | str | None:
        if not self.__check_correct_data(name):
            return "Incorrect data"
        
        self.__send_message(f"add_subscribe|{self.__id}&{name}&{length}&{price}")
        response = self.__get_message()
        if response.lower() == "true":
            return True
        elif type(response) is str:
            return response
        else:
            return None
    
    def edit_subscribe(self, name: str, length: int, price: int) -> bool | str | None:
        if not self.__check_correct_data(name):
            return "Incorrect data"
        
        self.__send_message(f"edit_subscribe|{self.__id}&{name}&{length}&{price}")
        response = self.__get_message()
        if response.lower() == "true":
            return True
        elif type(response) is str:
            return response
        else:
            return None

    def delete_subscribe(self, name: str) -> bool | str | None:
        if not self.__check_correct_data(name):
            return "Incorrect data"
        
        self.__send_message(f"delete_subscribe|{self.__id}&{name}")
        response = self.__get_message()
        if response.lower() == "true":
            return True
        elif type(response) is str:
            return response
        else:
            return None

    # Выдать другому пользователю подписку(только для админа)
    def admin_assign_custom_subscription(self, username: str, length: int) -> bool | str | None:
        if not self.__check_correct_data(username):
            return "Incorrect data"
        
        self.__send_message(f"admin_assign_custom_subscription|{self.__id}&{username}&{length}")
        response = self.__get_message()
        if response.lower() == "true":
            return True
        elif type(response) is str:
            return response
        else:
            return None
    
    # Назначить статус админа другому пользователю(только для админа)
    def set_admin_status(self, username: str, status: int) -> bool | str | None:
        if not self.__check_correct_data(username) or status not in [0, 1]:
            return "Incorrect data"
        
        self.__send_message(f"set_admin_status|{self.__id}&{username}&{status}")
        response = self.__get_message()
        if response.lower() == "true":
            return True
        elif type(response) is str:
            return response
        else:
            return None


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

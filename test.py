import os
from sub_serv import *


if __name__ == "__main__":
    base = BaseData(os.getenv("AIRTABLE_TOKEN"), os.getenv("APP_AIRTABLE_TOKEN"))
    base.write_table()

    while True:
        print("Do you want to register or log in(reg/log)? ", end="")
        param = input()
        if param == "reg" or param == "log":
            break
        else:
            print("You entered incorrect data")
    
    while True:
        print("Please, input username: ", end="")
        username = input()
        result_check_correct_username = base.check_correct_username(username)
        if param == "reg" and base.user_exists(username):
            print("The username is busy")
        elif param == "reg" and type(result_check_correct_username) is not bool:
            print(result_check_correct_username)
        elif param == "log" and not base.user_exists(username):
            print("The username is incorrect")
        else:
            break
    
    while True:
        print("Please, input password: ", end="")
        password = input()
        result_check_correct_password = base.check_correct_password(password)
        if param == "reg":
            if type(result_check_correct_password) is bool:
                id = base.reg(username, password)
            else:
                print(result_check_correct_password)
        elif param == "log":
            try:
                id = base.auth(username, password)
            except IncorrectPassword as e:
                print(e)
            else:
                break
    

    print(f"Hello {base.get_data(id)['Username']}!")
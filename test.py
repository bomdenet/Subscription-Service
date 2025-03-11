import os
from SubServ import *


base = BaseData(os.getenv("AIRTABLE_TOKEN"), os.getenv("APP_AIRTABLE_TOKEN"))
base.writeTable()

while True:
    print("Please, input username: ", end="")
    username = input()
    print("Please, input password: ", end="")
    password = input()
    try:
        id = base.auth(username, password)
    except IncorrectUser as e:
        print(e.args)
        print(base.reg(username, password))
    except IncorrectPassword as e:
        print(e.args)
    else:
        print(base.getData(id))
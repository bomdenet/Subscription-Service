from sub_serv_client import SubServClient, SubServUser


def write_info(user_data, subscriptions):
    print(f"Hello {user_data['username']}")
    print(f"Is admin: {user_data['is_admin']}")
    print(f"Balance: {user_data['balance']}")
    print(f"Subscription: {user_data['subscription']}")

    print("\nAll types of subscriptions:")
    for sub in subscriptions:
        print(f"Name: {sub['name_subscr']}, Duration: {sub['length']} days, Price: {sub['price']} rubles")


if __name__ == "__main__":
    client = SubServClient("127.0.0.1", 8888)

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
        result_check_correct_username = client.check_correct_username(username)
        if param == "reg" and client.user_exists(username):
            print("The username is busy")
        elif param == "reg" and type(result_check_correct_username) is not bool:
            print(result_check_correct_username)
        elif param == "log" and not client.user_exists(username):
            print("The username is incorrect")
        else:
            break

    while True:
        print("Please, input password: ", end="")
        password = input()
        result_check_correct_password = client.check_correct_password(password)
        if param == "reg":
            if type(result_check_correct_password) is bool:
                user = client.reg(username, password)
                if type(user) is SubServUser:
                    break
                else:
                    print(user)
            else:
                print(result_check_correct_password)
        elif param == "log":
            user = client.auth(username, password)
            if type(user) is SubServUser:
                break
            else:
                print(user)

    write_info(user.get_user_info(), user.get_available_subscriptions())

    if user.get_user_info()['is_admin'] == 1:
        while True:
            print("\nYou can manage subscriptions:")
            print("1. Add subscription")
            print("2. Edit subscription")
            print("3. Delete subscription")
            print("4. Print subscription")
            print("Please, select an action (1/2/3/4): ", end="")
            selection = input()
            if selection == "1" or selection == "2" or selection == "3":
                print("Please, input name of subscription: ", end="")
                name = input()
                if selection == "1" or selection == "2":
                    print("Please, input length of subscription (in days): ", end="")
                    length = int(input())
                    print("Please, input price of subscription (in rubles): ", end="")
                    price = int(input())
                    if selection == "1":
                        result = user.add_subscribe(name, length, price)
                    else:
                        result = user.edit_subscribe(name, length, price)
                    if result is True:
                        print("Successfully")
                    else:
                        print(result)
                else:
                    result = user.delete_subscribe(name)
                    if result is True:
                        print("Subscription deleted successfully")
                    else:
                        print(result)
            elif selection == "4":
                for sub in user.get_available_subscriptions():
                    print(f"Name: {sub['name_subscr']}, Duration: {sub['length']} days, Price: {sub['price']} rubles")
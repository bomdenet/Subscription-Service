from sub_serv_client import SubServClient, SubServUser
from datetime import datetime, timezone


def int_to_local_date(timesnap: int):
    if timesnap <= 0:
        return datetime(1970, 1, 1, tzinfo=timezone.utc)
    return datetime.fromtimestamp(timesnap).astimezone()

def write_info(user_data):
    print(f"Hello {user_data['username']}")
    print(f"Is admin: {user_data['is_admin']}")
    print(f"Balance: {user_data['balance']}")
    print(f"Subscription type: {user_data['subscription_name']}")
    if int_to_local_date(user_data['subscription']) > datetime.now(timezone.utc):
        print(f"Subscription: {int_to_local_date(user_data['subscription'])}")


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


    while True:
        print("\n\n\nMenu:")
        print("0. Exit")
        print("1. Print user info")
        print("2. Print history of payments")
        print("3. Add payment")
        print("4. Buy subscription")
        print("5. Print subscription")
        if user.get_user_info()['is_admin'] == 1:
            print("6. Admin menu")
        print("Please, select an action (0/1/2/3/4/5): ", end="")
        selection = input()

        if selection == "0":
            break
        elif selection == "1":
            write_info(user.get_user_info())
        elif selection == "2":
            history = user.get_user_payments_history()
            if history:
                print("History of payments:")
                for payment in history:
                    print(f"Date: {int_to_local_date(payment['date'])}, Amount: {payment['amount']} rubles")
            else:
                print("No payment history available.")
        elif selection == "3":
            print("Please, input amount of payment (in rubles): ", end="")
            amount = int(input())
            result = user.add_payment(amount)
            if result is True:
                print("Payment added successfully")
            else:
                print(result)
        elif selection == "4":
            print("Please, input name of subscription: ", end="")
            sub_name = input()
            result = user.assign_subscription_to_user(sub_name)
            if result is True:
                print("Subscription purchased successfully")
            else:
                print(result)
        elif selection == "5":
            for sub in user.get_available_subscriptions():
                print(f"Name: {sub['name_subscr']}, Duration: {sub['length']} days, Price: {sub['price']} rubles")
        elif selection == "6":
            while True:
                print("\n\n\nAdmin menu:")
                print("0. Exit")
                print("1. Add subscription")
                print("2. Edit subscription")
                print("3. Delete subscription")
                print("4. Print subscription")
                print("5. Issue a subscription")
                print("6. Set admin status")
                print("Please, select an action (0/1/2/3/4/5/6): ", end="")
                selection = input()
                if selection == "0":
                    break
                elif selection == "1" or selection == "2" or selection == "3":
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
                elif selection == "5":
                    print("Please, input username of user: ", end="")
                    target_username = input()
                    print("Please, input length of subscription (in days): ", end="")
                    length = int(input())
                    result = user.admin_assign_custom_subscription(target_username, length)
                    if result is True:
                        print("Subscription assigned successfully")
                    else:
                        print(result)
                elif selection == "6":
                    print("Please, input username of user: ", end="")
                    target_username = input()
                    print("Please, input status (0 - not admin, 1 - admin): ", end="")
                    status = int(input())
                    if status not in [0, 1]:
                        print("Invalid status")
                        continue
                    result = user.set_admin_status(target_username, status)
                    if result is True:
                        print("Status updated successfully")
                    else:
                        print(result)
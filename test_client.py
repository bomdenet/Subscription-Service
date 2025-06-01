from sub_serv_client import SubServClient


client = SubServClient("127.0.0.1", 8888)
while True:
    print("Введите сообщение для отправки на сервер (или 'exit' для выхода): ", end="")
    msg = input()
    if msg.lower() == 'exit':
        break

    print(f"user_exists: {client.user_exists(msg)}")
    print(f"check_correct_username: {client.check_correct_username(msg)}")

client.disconnect()

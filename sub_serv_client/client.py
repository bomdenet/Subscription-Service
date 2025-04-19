import socket


class Client:
    def __init__(self, ip, port):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            print(f"Подключение к серверу {ip}:{port}...")
            client_socket.connect((ip, port))

            while True:
                print("Введите сообщение для отправки на сервер (или 'exit' для выхода): ", end="")
                message = input()
                if message.lower() == 'exit':
                    print("Выход из программы.")
                    break
                client_socket.sendall(message.encode())
                print("Сообщение отправлено.")

            #data = client_socket.recv(1024)
            #print(f"Ответ от сервера: {data.decode()}")
            print("Закрытие соединения с сервером.")

        print("Программа завершина.")

    def send_message(self):
        pass
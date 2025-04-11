import socket

HOST = '127.0.0.1'
PORT = 65432

def main():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
        print(f"Подключение к серверу {HOST}:{PORT}...")
        client_socket.connect((HOST, PORT))

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

if __name__ == "__main__":
    main()
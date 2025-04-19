import asyncio

HOST = '0.0.0.0'
PORT = 65432

async def handle_client(reader, writer):
    addr = writer.get_extra_info('peername')
    print(f"[+] Подключён: {addr}")

    while True:
        data = await reader.read(1024)
        if not data:
            break
        message = data.decode()
        print(f"[{addr}] {message}")
        response = f"Принято: {message}"
        writer.write(response.encode())
        await writer.drain()

    print(f"[-] Отключён: {addr}")
    writer.close()
    await writer.wait_closed()

async def main():
    server = await asyncio.start_server(handle_client, HOST, PORT)
    addr = server.sockets[0].getsockname()
    print(f"[🔌] Сервер запущен на {addr}")

    async with server:
        await server.serve_forever()

if __name__ == "__main__":
    asyncio.run(main())


class Server:
    def __init__(self, port):
        pass

    def start(self):
        pass
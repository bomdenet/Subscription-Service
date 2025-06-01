import asyncio
from datetime import datetime
from .base_data import BaseData


needs_logs = True
LOGS_STREAM = "logs.txt"

def print_debug_info():
    if needs_logs:
        print("\n\n\n")
        base_data.print_debug_info()
        print("\n\n\n")

def write_log(message: str):
    mes = f"[{datetime.now()}] {message}"
    file_logs.write(f"{mes}\n")
    file_logs.flush()
    if needs_logs:
        print(f"[LOG] {mes}")

def return_answer(message: str) -> str | None:
    if (len(message.split("|")) < 2):
        return "Incorrect data"
    
    type_cmd = message.split("|")[0]
    data_cmd = message.split("|")[1]
    if type_cmd == "user_exists":
        return str(base_data.user_exists(data_cmd))
    elif type_cmd == "check_correct_username":
        return str(base_data.check_correct_username(data_cmd))
    elif type_cmd == "check_correct_password":
        return str(base_data.check_correct_password(data_cmd))
    elif type_cmd == "reg":
        data_cmd = data_cmd.split("&")
        if (len(data_cmd) < 2):
            return "Incorrect data"
        return f"id|{base_data.reg(data_cmd[0], data_cmd[1])}"
    elif type_cmd == "auth":
        data_cmd = data_cmd.split("&")
        if (len(data_cmd) < 2):
            return "Incorrect data"
        return f"id|{base_data.auth(data_cmd[0], data_cmd[1])}"
    elif type_cmd == "get_user_info":
        return str(base_data.get_user_info(data_cmd))
    elif type_cmd == "add_subscribe":
        data_cmd = data_cmd.split("&")
        if (len(data_cmd) < 4):
            return "Incorrect data"
        return str(base_data.add_subscribe(data_cmd[0], data_cmd[1], int(data_cmd[2]), int(data_cmd[3])))
    elif type_cmd == "edit_subscribe":
        data_cmd = data_cmd.split("&")
        if (len(data_cmd) < 4):
            return "Incorrect data"
        return str(base_data.edit_subscribe(data_cmd[0], data_cmd[1], int(data_cmd[2]), int(data_cmd[3])))
    elif type_cmd == "delete_subscribe":
        data_cmd = data_cmd.split("&")
        if (len(data_cmd) < 2):
            return "Incorrect data"
        ans = str(base_data.delete_subscribe(data_cmd[0], data_cmd[1]))
        return "True" if ans is None else ans
    else:
        return None

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    write_log(f"Client connected: {addr}")

    try:
        while True:
            data = await reader.read(1024)
            if not data:
                break
            
            print_debug_info()
            message = data.decode()
            write_log(f"Received from {addr}: {message}")

            writer.write(str(return_answer(message)).encode())
            await writer.drain()
    except Exception:
        pass
    finally:
        write_log(f"Client disconnected: {addr}")
        writer.close()
        await writer.wait_closed()

async def start_server(ip: str, port: int, logs: bool = True):
    global needs_logs
    needs_logs = logs
    global file_logs
    file_logs = open(LOGS_STREAM, "a")
    global base_data
    base_data = BaseData()

    server = await asyncio.start_server(handle_client, ip, port)
    addr = server.sockets[0].getsockname()
    write_log(f'Server started on {addr}')

    async with server:
        await server.serve_forever()

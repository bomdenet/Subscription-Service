import asyncio
from sub_serv_server import *


asyncio.run(start_server("127.0.0.1", 8888))
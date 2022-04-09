import asyncio
import multiprocessing
import random
import socket
import time
from typing import Tuple


def get_current_time():
    return int(time.time())


class HeardbeatUdpServer:
    def __init__(self, port: int, timeout: int):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.server_socket.bind(('', port))
        self.server_socket.settimeout(timeout / 10)

        # Last connection with clinets address and package number
        self.clients: dict[str, Tuple[int, int]] = {}

        # Max timeout between connection tests
        self.timeout = timeout

    async def run(self):
        print('Server is active')
        listen_task = asyncio.create_task(
            self.listen()
        )
        await listen_task

    async def listen(self):
        while True:
            try:
                recv, client = self.server_socket.recvfrom(1024)
            except TimeoutError:
                pass
            else:
                if random.random() >= 0.2:
                    message = recv.decode()
                    print(message)
                    package_number = int(message.split(' ')[1])
                    host = client[0]
                    if host in self.clients:
                        last_number = self.clients[host][1]
                        if package_number - last_number > 1:
                            print(f'Missed packages {last_number+1}-{package_number-1} from {host}')
                    self.clients[host] = (get_current_time(), package_number)
                    self.server_socket.sendto(recv, client)
            await asyncio.create_task(
                self.client_check()
            )

    async def client_check(self):
        current_time = get_current_time()
        clients = self.clients.copy()
        for client_addr, (last_connection, _) in clients.items():
            timedelta = current_time - last_connection
            if timedelta > self.timeout:
                print(
                    f'Client {client_addr} does not responding for too long'
                )
                del self.clients[client_addr]


if __name__ == '__main__':
    server = HeardbeatUdpServer(80, 60)
    asyncio.run(server.run())

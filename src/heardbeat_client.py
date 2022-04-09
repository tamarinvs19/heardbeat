import asyncio
import time
import socket


def avg(elements):
    return sum(elements) / len(elements)


class HeardbeatUdpClient:
    def __init__(self, host, port):
        self.addr = (host, port)

        # Time between connection with server
        self.ping_delay = 1

        self.timeout = 1

        self.start_time: dict[int, float] = {}
        self.end_time: dict[int, float] = {}

        self.rtts: list[float] = []
        self.loss_counter = 0

        self.socket_id = 0

    async def run(self):
        print(f'PING {self.addr[0]}')
        while True:
            self.socket_id += 1
            client_socket = socket.socket(
                socket.AF_INET,
                socket.SOCK_DGRAM,
            )
            client_socket.settimeout(self.timeout)
            now_time = time.time()
            str_time = time.strftime(
                '%Y.%m.%d %H:%M:%S',
                time.localtime(now_time),
            )
            self.start_time[self.socket_id] = now_time
            message = f'Ping {self.socket_id} {str_time}'
            client_socket.sendto(message.encode(), self.addr)
            task = asyncio.create_task(
                self.wait_response(client_socket, self.socket_id)
            )
            await task
            await asyncio.sleep(self.ping_delay)

    async def wait_response(self, client_socket, socket_id):
        try:
            data, server = client_socket.recvfrom(1024)
            self.end_time[socket_id] = time.time()
            response_time = 10**5 * (self.end_time[socket_id] - self.start_time[socket_id])
            self.rtts.append(response_time)
            response_size = len(data)
            print(f'{response_size} bytes from {self.addr[0]}: icmp_seq={socket_id} time={response_time:.1f} ms')
        except socket.timeout:
            print(f'Request #{socket_id} timed out')
            self.loss_counter += 1

    def print_statistics(self):
        print('')
        print(f'--- {self.addr[0]} ping statistics ---')
        print(f'{self.socket_id} transmitted, {self.socket_id - self.loss_counter} received, {self.loss_counter / self.socket_id * 100:.0f}% packet loss')
        print(f'rtt min/avg/max = {min(self.rtts):.3f}/{avg(self.rtts):.3f}/{max(self.rtts):.3f} ms')


if __name__ == '__main__':
    client = HeardbeatUdpClient('127.0.0.1', 8080)
    try:
        asyncio.run(client.run())
    except KeyboardInterrupt:
        client.print_statistics()

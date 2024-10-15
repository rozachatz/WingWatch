import socket


class RotatorClient:
    async def execute(self, az, el):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 4532)

        try:
            print("Connecting to Hamlib server...")
            sock.connect(server_address)
            # Construct the command as a single byte string
            command = b'P ' + bytes(f'{az} {el}', 'ascii') + b'\n'
            sock.sendall(command)
        finally:
            print("Closing socket.")
            sock.close()

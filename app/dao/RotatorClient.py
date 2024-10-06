import socket
import time


class RotatorClient:

    def set_rotator(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ('localhost', 4532)

        try:
            print("Connecting to Hamlib server...")
            sock.connect(server_address)
            sock.sendall(b'P 90 30\n')

            time.sleep(3)

        finally:
            print("Closing socket.")
            sock.close()


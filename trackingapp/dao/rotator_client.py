import asyncio
from abc import ABC, abstractmethod


class AbstractAdsbClient(ABC):

    @abstractmethod
    def execute_rotate_command(self):
        pass


class RotatorClient:
    def __init__(self, host='localhost', port=4532):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def execute_rotate_command(self, az, el):
        writer = None
        try:
            # Open a connection to the Hamlib server
            reader, writer = await asyncio.open_connection('localhost', 4532)
            print("Connected to Hamlib server.")
            # Construct the command
            command = b'P ' + bytes(f'{az} {el}', 'ascii') + b'\n'
            print(f"Sending command: {command.strip()}")
            writer.write(command)
            await writer.drain()  # Ensure the command is sent
        except Exception as e:
            print(f"Error: {e}")
        finally:
            if writer:
                print("Closing socket.")
                writer.close()
                await writer.wait_closed()  # Ensure the socket is properly close

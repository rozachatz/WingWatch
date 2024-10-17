import asyncio


class RotatorClient:
    def __init__(self, host='localhost', port=4532):
        self.host = host
        self.port = port
        self.reader = None
        self.writer = None

    async def connect(self):
        if self.writer is None:
            try:
                self.reader, self.writer = await asyncio.wait_for(
                    asyncio.open_connection(self.host, self.port),
                    timeout=5.0  # Timeout for connection
                )
                print("Connected to Hamlib server.")
            except asyncio.TimeoutError:
                print("Connection timed out.")
                self.writer = None

    async def disconnect(self):
        if self.writer:
            print("Closing socket.")
            self.writer.close()
            await self.writer.wait_closed()
            self.writer = None
            self.reader = None

    async def execute(self, az, el):
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

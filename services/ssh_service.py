import asyncssh
import asyncio
from core.logger import logger
from core.config import settings


class SSHSession:

    def __init__(self, host,port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password
        self.conn = None
        self.process = None

    async def connect(self):

        logger.info(f"Connecting to {self.host}")

        self.conn = await asyncio.wait_for(
            asyncssh.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
            ),
            timeout=settings.SSH_CONNECTION_TIMEOUT,
        )

        self.process = await self.conn.create_process(
            term_type="xterm-256color",
            encoding="utf-8"
        )

        logger.info("SSH session started")

    # async def read(self):
    #     return await self.process.stdout.read(1024)

    def write(self, data):
        if self.process:
            self.process.stdin.write(data)
            # self.process.stdin.flush()

    def resize(self, cols: int, rows: int):
        if self.process and self.process.channel:
            self.process.channel.set_terminal_size(cols, rows)

    async def close(self):

        logger.info("Closing SSH session")

        if self.conn:
            self.conn.close()
            await self.conn.wait_closed()
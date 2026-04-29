import asyncio
import asyncssh

from core.logger import logger
from core.config import settings


class SSHSession:
    def __init__(
        self,
        host,
        port,
        username,
        password
    ):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

        self.conn = None
        self.process = None

    async def connect(self):
        logger.info(
            f"Connecting to {self.host}"
        )

        self.conn = await asyncio.wait_for(
            asyncssh.connect(
                self.host,
                port=self.port,
                username=self.username,
                password=self.password,
                known_hosts=None
            ),
            timeout=settings.SSH_CONNECTION_TIMEOUT
        )

        self.process = await self.conn.create_process(
            term_type="xterm-256color",
            encoding="utf-8"
        )

        logger.info(
            f"SSH session started: {self.host}"
        )

    def write(self, data):
        try:
            if (
                self.process and
                self.process.stdin and
                not self.process.stdin.is_closing()
            ):
                self.process.stdin.write(data)
        except Exception as e:
            logger.error(
                f"Write error: {e}"
            )

    def resize(self, cols, rows):
        try:
            if (
                self.process and
                self.process.channel
            ):
                self.process.channel.change_terminal_size(
                    cols,
                    rows
                )
        except Exception as e:
            logger.error(
                f"Resize error: {e}"
            )

    async def close(self):
        logger.info(
            f"Closing SSH session: {self.host}"
        )

        try:
            if self.process:
                self.process.close()

            if self.conn:
                self.conn.close()
                await self.conn.wait_closed()

        except Exception as e:
            logger.error(
                f"Close error: {e}"
            )
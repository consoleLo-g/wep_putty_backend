from fastapi import APIRouter, WebSocket
from services.ssh_service import SSHSession
from schemas.ssh import SSHCredentials
from core.logger import logger
import asyncio
import json

router = APIRouter(prefix="/terminal", tags=["Terminal"])


@router.websocket("/ws")
async def terminal_ws(websocket: WebSocket):

    await websocket.accept()

    ssh = None

    try:

        # receive credentials
        data = await websocket.receive_text()
        credentials = SSHCredentials(**json.loads(data))

        ssh = SSHSession(
            credentials.host,
            credentials.username,
            credentials.password
        )

        await ssh.connect()

        async def read_from_ssh():
            while True:
                data = await ssh.read()
                if not data:
                    break
                await websocket.send_text(data)

        async def write_to_ssh():
            while True:
                data = await websocket.receive_text()
                ssh.write(data)

        await asyncio.gather(
            read_from_ssh(),
            write_to_ssh()
        )

    except Exception as e:

        logger.error(str(e))
        await websocket.send_text(f"Error: {str(e)}")

    finally:

        if ssh:
            await ssh.close()

        await websocket.close()
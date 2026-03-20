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
        # Receive credentials
        init_data = json.loads(await websocket.receive_text())
        credentials = SSHCredentials(**init_data)

        ssh = SSHSession(
            credentials.host,
            credentials.username,
            credentials.password
        )

        await ssh.connect()

        await websocket.send_json({
            "type": "connected",
            "message": "SSH session established"
        })

        async def read_from_ssh():
            while True:
                data = await ssh.read()
                if not data:
                    break

                await websocket.send_json({
                    "type": "output",
                    "data": data
                })

        async def write_to_ssh():
            while True:
                msg = json.loads(await websocket.receive_text())

                if msg["type"] == "input":
                    ssh.write(msg["data"])

                elif msg["type"] == "resize":
                    ssh.resize(msg["cols"], msg["rows"])

        await asyncio.gather(
            read_from_ssh(),
            write_to_ssh()
        )

    except Exception as e:
        logger.error(str(e))

        await websocket.send_json({
            "type": "error",
            "message": str(e)
        })

    finally:
        if ssh:
            await ssh.close()

        await websocket.close()
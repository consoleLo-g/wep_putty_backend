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
            credentials.port,
            credentials.username,
            credentials.password
        )

        await ssh.connect()

        await websocket.send_json({
            "type": "connected",
            "message": "SSH session established"
        })

        async def read_from_ssh():
            try:
                while True:
                    data = await ssh.process.stdout.read(1024)

                    if not data:
                        break

                    if isinstance(data, bytes):
                        data = data.decode(errors="ignore")

                    await websocket.send_json({
                        "type": "output",
                        "data": data
                    })

            except Exception as e:
                print("READ ERROR:", e)

        async def write_to_ssh():
            while True:
                raw = await websocket.receive_text()
                print(raw)
                msg = json.loads(raw)

                if msg["type"] == "input":
                    ssh.write(msg["data"])

                elif msg["type"] == "resize":
                    try:
                        ssh.resize(msg["cols"], msg["rows"])
                    except Exception as e:
                        logger.error(f"Resize error: {e}")

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
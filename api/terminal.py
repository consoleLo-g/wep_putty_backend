from fastapi import APIRouter, WebSocket, WebSocketDisconnect
from core.logger import logger
from core.security import verify_token
from core.session_manager import session_manager
from core.config import settings

from services.ssh_service import SSHSession

import asyncio
import json

router = APIRouter(
    prefix="/terminal",
    tags=["Terminal"]
)


@router.websocket("/ws")
async def terminal_ws(websocket: WebSocket):
    await websocket.accept()

    # -------------------------
    # AUTH CHECK
    # -------------------------
    token = websocket.query_params.get("token")

    if not token or not verify_token(token):
        await websocket.send_json({
            "type": "error",
            "message": "Unauthorized"
        })
        await websocket.close()
        return

    try:
        while True:
            raw = await websocket.receive_text()
            msg = json.loads(raw)

            msg_type = msg.get("type")

            # --------------------------------
            # CREATE SSH SESSION
            # --------------------------------
            if msg_type == "create":

                if session_manager.count() >= settings.MAX_SSH_SESSIONS:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Max SSH sessions reached"
                    })
                    continue

                payload = msg["payload"]

                ssh = SSHSession(
                    payload["host"],
                    payload["port"],
                    payload["username"],
                    payload["password"]
                )

                await ssh.connect()

                session_id = session_manager.create(ssh)

                asyncio.create_task(
                    stream_output(
                        websocket,
                        ssh,
                        session_id
                    )
                )

                await websocket.send_json({
                    "type": "created",
                    "session_id": session_id
                })

            # --------------------------------
            # INPUT
            # --------------------------------
            elif msg_type == "input":
                ssh = session_manager.get(
                    msg["session_id"]
                )

                if ssh:
                    ssh.write(
                        msg["data"]
                    )

            # --------------------------------
            # RESIZE
            # --------------------------------
            elif msg_type == "resize":
                ssh = session_manager.get(
                    msg["session_id"]
                )

                if ssh:
                    ssh.resize(
                        msg["cols"],
                        msg["rows"]
                    )

            # --------------------------------
            # CLOSE ONE SESSION
            # --------------------------------
            elif msg_type == "close":
                session_id = msg["session_id"]

                ssh = session_manager.get(
                    session_id
                )

                if ssh:
                    await ssh.close()

                    session_manager.remove(
                        session_id
                    )

                    await websocket.send_json({
                        "type": "closed",
                        "session_id": session_id
                    })

    except WebSocketDisconnect:
        logger.info("Client disconnected")

    except Exception as e:
        logger.error(
            f"WebSocket error: {e}"
        )

    finally:
        # DO NOT cleanup sessions here
        # allows browser refresh recovery
        try:
            await websocket.close()
        except:
            pass


async def stream_output(
    websocket: WebSocket,
    ssh: SSHSession,
    session_id: str
):
    try:
        while True:
            data = await ssh.process.stdout.read(1024)

            if not data:
                break

            if isinstance(data, bytes):
                data = data.decode(
                    errors="ignore"
                )

            await websocket.send_json({
                "type": "output",
                "session_id": session_id,
                "data": data
            })

    except Exception as e:
        logger.error(
            f"Stream error {session_id}: {e}"
        )
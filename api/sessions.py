from fastapi import APIRouter, HTTPException, Header

from core.security import verify_token
from core.session_manager import session_manager


router = APIRouter(
    prefix="/sessions",
    tags=["Sessions"]
)


# ----------------------------
# AUTH HELPER
# ----------------------------
def authorize(header: str):
    if not header:
        raise HTTPException(
            status_code=401,
            detail="Missing token"
        )

    try:
        scheme, token = header.split(" ")
    except ValueError:
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )

    if scheme.lower() != "bearer":
        raise HTTPException(
            status_code=401,
            detail="Invalid auth scheme"
        )

    if not verify_token(token):
        raise HTTPException(
            status_code=401,
            detail="Invalid token"
        )


# ----------------------------
# LIST ACTIVE SESSIONS
# ----------------------------
@router.get("/")
def list_sessions(
    authorization: str = Header(None)
):
    authorize(authorization)

    data = []

    for session_id, ssh in session_manager.sessions.items():
        data.append({
            "session_id": session_id,
            "host": ssh.host,
            "port": ssh.port,
            "username": ssh.username
        })

    return {
        "count": len(data),
        "sessions": data
    }


# ----------------------------
# DELETE ONE SESSION
# ----------------------------
@router.delete("/{session_id}")
async def delete_session(
    session_id: str,
    authorization: str = Header(None)
):
    authorize(authorization)

    ssh = session_manager.get(session_id)

    if not ssh:
        raise HTTPException(
            status_code=404,
            detail="Session not found"
        )

    await ssh.close()
    session_manager.remove(session_id)

    return {
        "success": True
    }


# ----------------------------
# DELETE ALL
# ----------------------------
@router.delete("/")
async def delete_all_sessions(
    authorization: str = Header(None)
):
    authorize(authorization)

    for session_id, ssh in list(
        session_manager.sessions.items()
    ):
        try:
            await ssh.close()
        except:
            pass

        session_manager.remove(session_id)

    return {
        "success": True
    }
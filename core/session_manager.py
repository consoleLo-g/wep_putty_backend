import uuid
from typing import Dict
from services.ssh_service import SSHSession


class SessionManager:
    def __init__(self):
        self.sessions: Dict[str, SSHSession] = {}

    def create(self, ssh: SSHSession) -> str:
        session_id = str(uuid.uuid4())
        self.sessions[session_id] = ssh
        return session_id

    def get(self, session_id: str) -> SSHSession | None:
        return self.sessions.get(session_id)

    def remove(self, session_id: str):
        if session_id in self.sessions:
            del self.sessions[session_id]

    def count(self) -> int:
        return len(self.sessions)


# Singleton instance
session_manager = SessionManager()
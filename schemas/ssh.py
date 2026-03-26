from pydantic import BaseModel

class SSHCredentials(BaseModel):
    host: str
    port: int = 22
    username: str
    password: str
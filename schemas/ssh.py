from pydantic import BaseModel

class SSHCredentials(BaseModel):
    host: str
    username: str
    password: str
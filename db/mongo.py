from motor.motor_asyncio import AsyncIOMotorClient

from core.config import settings


client = AsyncIOMotorClient(
    settings.MONGO_URI
)

db = client[
    settings.DB_NAME
]


# Collections
connections_collection = db["connections"]
sessions_collection = db["sessions"]
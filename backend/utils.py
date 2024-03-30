from passlib.context import CryptContext
from fastapi_socketio import SocketManager
from bson import ObjectId

crypto = CryptContext(schemes=["bcrypt"], deprecated="auto")

socketio: SocketManager = None

async def socketio_emit(elements:list[str]):
    await socketio.emit("update",elements)

def object_id_to_str(obj: ObjectId) -> str:
    return obj.binary.hex()
    
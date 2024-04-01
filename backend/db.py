from motor.motor_asyncio import AsyncIOMotorClient
from beanie import Document, Indexed, init_beanie
import os, secrets
from pydantic import BaseModel
from models import Role

from typing import Annotated
from utils import crypto

MONGO_URL = os.getenv('MONGO_URL')
assert not MONGO_URL is None
DEFAULT_PSW = os.getenv('DEFAULT_PSW')
DB_NAME = os.getenv('DB_NAME', "spesometro")

db_client = AsyncIOMotorClient(MONGO_URL)
from models import Category, Product, Member

class Board(Document):
    name: str
    categories: list[Category]
    products: list[Product]
    members: list[Member]
    class Settings:
        use_state_management = True
        state_management_save_previous = True

class User(Document):
    username: Annotated[str,Indexed(unique=True)]
    password: str
    role: Role
    class Settings:
        use_state_management = True
        state_management_save_previous = True

class Env(Document):
    key: Annotated[str,Indexed(unique=True)]
    value: str
    class Settings:
        use_state_management = True
        state_management_save_previous = True

async def init_db():
    # Initialize beanie with the Product document class
    await init_beanie(database=db_client[DB_NAME], document_models=[
        Env, User, Board
    ])
    admin_len = await User.find({ "role": Role.admin }).count()
    if admin_len == 0:
        clearpsw = secrets.token_hex(12) if DEFAULT_PSW is None else DEFAULT_PSW
        print("'admin' Created! Password:", clearpsw)
        await User( username="admin", password=crypto.hash(clearpsw), role=Role.admin ).save()

async def shutdown_db():
    db_client.close()
    
async def first_run():
    await init_db()
    await shutdown_db()
        
        
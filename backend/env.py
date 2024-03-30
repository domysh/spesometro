
import os, secrets
from db import Env
from aiocache import cached

DEBUG = os.getenv("DEBUG", "").lower() in ["true", "1", "t"]

JWT_ALGORITHM = "HS256"
JWT_EXPIRE_H = 3
@cached()
async def APP_SECRET():
    secret = await Env.find_one(Env.key == "APP_SECRET")
    secret = secret.value if secret else None
    if secret is None:
        secret = secrets.token_hex(32)
        await Env(key="APP_SECRET", value=secret).save()
    return secret

    
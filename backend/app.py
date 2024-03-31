from dotenv import load_dotenv
load_dotenv()

import uvicorn, utils
import os, asyncio
from fastapi import FastAPI, HTTPException, Depends, APIRouter
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from contextlib import asynccontextmanager
from jose import jwt
from bson import ObjectId
from models import *
import uuid, time
from fastapi.middleware.cors import CORSMiddleware

from fastapi_socketio import SocketManager
from utils import crypto, socketio_emit
from env import DEBUG, JWT_ALGORITHM, APP_SECRET, JWT_EXPIRE_H
from db import Role, init_db, shutdown_db, User, first_run, Board
from fastapi.responses import FileResponse

async def front_refresh(additional:list[str]=None):
    await socketio_emit([] if additional is None else additional)

@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    await front_refresh()
    yield
    await shutdown_db()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/login", auto_error=False)
app = FastAPI(debug=DEBUG, redoc_url=None, lifespan=lifespan)
utils.socketio = SocketManager(app, "/sock", socketio_path="")

@utils.socketio.on("update")
async def updater(): pass

async def create_access_token(data: dict):
    to_encode = data.copy()
    to_encode["exp"] = int(time.time() + JWT_EXPIRE_H*60*60) #3h
    encoded_jwt = jwt.encode(to_encode, await APP_SECRET(), algorithm=JWT_ALGORITHM)
    return encoded_jwt

async def check_login(token: str = Depends(oauth2_scheme)):
    if not token:
        return None
    try:
        payload = jwt.decode(token, await APP_SECRET(), algorithms=[JWT_ALGORITHM])
        userid: str|None = payload.get("userid", None)
        if not userid:
            return None
        user = await User.find_one(User.id == ObjectId(userid))
    except Exception:
        return None
    return user.role if user else None

def has_role(target:Role|None = None):
    async def func(auth: Role = Depends(check_login)):
        if target is None or auth == Role.admin:
            return True
        if target == Role.guest:
            if not auth is None:
                return True
        if target == Role.editor:
            if auth in [Role.editor, Role.admin]:
                return True
        raise HTTPException(
            status_code=401,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    return func

api = APIRouter(prefix="/api", dependencies=[Depends(has_role())])
editor_api = APIRouter(prefix="/api", dependencies=[Depends(has_role(Role.editor))])
admin_api = APIRouter(prefix="/api", dependencies=[Depends(has_role(Role.admin))])
guest_api = APIRouter(prefix="/api", dependencies=[Depends(has_role(Role.guest))])

@api.post("/login", tags=["auth"])
async def login_api(form: OAuth2PasswordRequestForm = Depends()):
    """Get a login token to use the firegex api"""
    if form.password == "" or form.username == "":
        raise HTTPException(400,"Cannot insert an empty value!")
    await asyncio.sleep(0.3) # No bruteforce :)
    user = await User.find_one(User.username == form.username.lower() )
    if not user:
        raise HTTPException(406,"User not found!")
    if not crypto.verify(form.password, user.password):
        raise HTTPException(406,"Wrong password!")
    
    return {"access_token": await create_access_token({"userid": user.id.binary.hex(), "role": user.role}), "token_type": "bearer"}

@guest_api.get("/boards", response_model=list[BoardDTO], tags=["board"])
async def get_boards():
    """ Get created boards list and related data """
    return await Board.find_all().to_list()

@editor_api.put("/boards", response_model=IdResponse, tags=["board"])
async def new_board(form: AddBoardForm):
    """ Create a new board """
    board:Board = await Board(**form.model_dump(), categories=[], members=[], products=[]).save()
    await front_refresh()
    return { "id": board.id.binary.hex() }

@editor_api.delete("/boards/{id}", response_model=IdResponse, tags=["board"])
async def remove_board(id: str):
    """ Create a new board """
    await Board.find_one(Board.id == ObjectId(id)).delete_one()
    await front_refresh()
    return { "id": id }

@guest_api.get("/boards/{id}", response_model=BoardDTO, tags=["board"])
async def get_board(id: str):
    """ Get board """
    return await Board.find_one(Board.id == ObjectId(id))

@editor_api.post("/boards/{id}", response_model=IdResponse, tags=["board"])
async def edit_board(id: str, form: AddBoardForm):
    """ Get board """
    board = await Board.find_one(Board.id == ObjectId(id))
    await board.set(form)
    await front_refresh()
    return { "id": id }

@guest_api.get("/boards/{id}/categories", response_model=list[Category], tags=["category"])
async def get_board_categories(id: str):
    """ Get board category list """
    return (await Board.find_one(Board.id == ObjectId(id))).categories

@editor_api.put("/boards/{id}/categories", response_model=IdResponse, tags=["category"])
async def new_board_categories(id: str, form: AddCategory):
    """ Add a new board category """
    board = await Board.find_one(Board.id == ObjectId(id))
    new_id = uuid.uuid4()
    board.categories.append(Category(**form.model_dump(), id=new_id))
    await board.save()
    await front_refresh()
    return {"id":str(new_id)}

@editor_api.post("/boards/{id}/categories/{category_id}", response_model=IdResponse, tags=["category"])
async def edit_board_categories(id: str, category_id: str, form: AddCategory):
    """ Edit a board category """
    board = await Board.find_one(Board.id == ObjectId(id))
    category_id = uuid.UUID(category_id)
    for ele in board.categories:
        if ele.id == category_id:
            for k, v in form.model_dump().items(): setattr(ele, k, v)
            break
    await board.save()
    await front_refresh()
    return {"id":str(category_id)}

@editor_api.delete("/boards/{id}/categories/{category_id}", response_model=IdResponse, tags=["category"])
async def delete_board_categories(id: str, category_id: str):
    """ Delete a board category """
    board = await Board.find_one(Board.id == ObjectId(id))
    category_id = uuid.UUID(category_id)
    board.categories = [ele for ele in board.categories if ele.id != category_id]
    for prod in board.products:
        prod.categories = [ele for ele in prod.categories if ele != category_id]
    for memb in board.members:
        memb.categories = [ele for ele in memb.categories if ele != category_id]
    await board.save()
    await front_refresh()
    return {"id":str(category_id)}
    
@guest_api.get("/board/{id}/members", response_model=list[Member], tags=["member"])
async def get_board_members(id: str):
    """ Get board member list """
    return (await Board.find_one(Board.id == ObjectId(id))).members

@editor_api.put("/boards/{id}/members", response_model=IdResponse, tags=["member"])
async def new_board_members(id: str, form: AddMember):
    """ Add a new board member """
    board = await Board.find_one(Board.id == ObjectId(id))
    new_id = uuid.uuid4()
    board.members.append(Member(**form.model_dump(), id=new_id))
    await board.save()
    await front_refresh()
    return {"id":str(new_id)}

@editor_api.post("/boards/{id}/members/{member_id}", response_model=IdResponse, tags=["member"])
async def edit_board_members(id: str, member_id: str, form: AddMember):
    """ Edit a board member """
    board = await Board.find_one(Board.id == ObjectId(id))
    member_id = uuid.UUID(member_id)
    for ele in board.members:
        if ele.id == member_id:
            for k, v in form.model_dump().items(): setattr(ele, k, v)
            break
    await board.save()
    await front_refresh()
    return {"id":str(member_id)}

@editor_api.delete("/boards/{id}/members/{member_id}", response_model=IdResponse, tags=["member"])
async def delete_board_members(id: str, member_id: str):
    """ Delete a board category """
    board = await Board.find_one(Board.id == ObjectId(id))
    member_id = uuid.UUID(member_id)
    board.members = [ele for ele in board.members if ele.id != member_id]
    await board.save()
    await front_refresh()
    return {"id":str(member_id)}
    

@guest_api.get("/boards/{id}/products", response_model=list[Product], tags=["product"])
async def get_board_products(id: str):
    """ Get board product list """
    return (await Board.find_one(Board.id == ObjectId(id))).products

@editor_api.put("/boards/{id}/products", response_model=IdResponse, tags=["product"])
async def new_board_products(id: str, form: AddProduct):
    """ Add a new board product """
    board = await Board.find_one(Board.id == ObjectId(id))
    new_id = uuid.uuid4()
    board.products.append(Product(**form.model_dump(), id=new_id))
    await board.save()
    await front_refresh()
    return {"id":str(new_id)}

@editor_api.post("/boards/{id}/products/{product_id}", response_model=IdResponse, tags=["product"])
async def edit_board_products(id: str, product_id: str, form: AddProduct):
    """ Edit a board product """
    board = await Board.find_one(Board.id == ObjectId(id))
    product_id = uuid.UUID(product_id)
    for ele in board.products:
        if ele.id == product_id:
            for k, v in form.model_dump().items(): setattr(ele, k, v)
            break
    await board.save()
    await front_refresh()
    return {"id":str(product_id)}

@editor_api.delete("/boards/{id}/products/{product_id}", response_model=IdResponse, tags=["product"])
async def delete_board_products(id: str, product_id: str):
    """ Delete a board product """
    board = await Board.find_one(Board.id == ObjectId(id))
    product_id = uuid.UUID(product_id)
    board.products = [ele for ele in board.products if ele.id != product_id]
    await board.save()
    await front_refresh()
    return {"id":str(product_id)}

@admin_api.get("/users", response_model=list[UserDTO], tags=["user"])
async def get_users():
    """ Get users """
    return await User.find_all().to_list()

@admin_api.get("/users/{id}", response_model=UserDTO, tags=["user"])
async def get_user(id: str):
    """ Get user """
    return await User.find_one(User.id == ObjectId(id))

@admin_api.put("/users", response_model=IdResponse, tags=["user"])
async def new_user(form: AddUser):
    """ Add a new user """
    form.username = form.username.lower()
    if form.username == "admin":
        raise HTTPException(
            status_code=400,
            detail="'admin' is reserved"
        )
    if not form.password:
        raise HTTPException(
            status_code=400,
            detail="A password is needed!"
        )
    form.password=crypto.hash(form.password)
    user:User = await User(**form.model_dump()).save()
    await front_refresh()
    return {"id": user.id.binary.hex()}

@admin_api.post("/users/{id}", response_model=IdResponse, tags=["user"])
async def edit_user(id: str, form: AddUser):
    """ Edit a user """
    form.username = form.username.lower()
    if form.username == "admin":
        raise HTTPException(
            status_code=400,
            detail="'admin' is reserved"
        )
    if form.password:
        form.password = crypto.hash(form.password)
    user = await User.find_one(User.id == ObjectId(id))
    await user.set(form)
    await front_refresh()
    return {"id":id}

@admin_api.delete("/users/{id}", response_model=IdResponse, tags=["user"])
async def delete_users(id: str):
    """ Delete a user """
    user = await User.find_one(User.id == ObjectId(id))
    if user.username == "admin":
        raise HTTPException(
            status_code=400,
            detail="'admin' is reserved"
        )
    await User.find_one(User.id == ObjectId(id)).delete_one()
    await front_refresh()
    return {"id":id}

app.include_router(api)
app.include_router(editor_api)
app.include_router(admin_api)
app.include_router(guest_api)

if not DEBUG:
    @app.get("/{full_path:path}", include_in_schema=False)
    async def catch_all(full_path:str):
        file_request = os.path.join("frontend", full_path)
        if not os.path.isfile(file_request):
            return FileResponse("frontend/index.html", media_type='text/html')
        else:
            return FileResponse(file_request)
else:
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

if __name__ == '__main__':
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    asyncio.run(first_run())
    uvicorn.run(
        "app:app",
        host="0.0.0.0",
        port=8080,
        reload=DEBUG,
        access_log=True,
        workers=3
    )

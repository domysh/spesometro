from pydantic import BaseModel, UUID4, Field
from enum import Enum
from beanie import PydanticObjectId
from typing import Annotated

class Role(str, Enum):
    admin = "admin"
    editor = "editor"
    guest = "guest"

class IdResponse(BaseModel):
    id: str

class AddCategory(BaseModel):
    name: Annotated[str, Field(min_length=1)]

class Category(AddCategory):
    id: UUID4

class AddProduct(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    price: Annotated[int, Field(ge=0)]
    categories: list[UUID4]

class Product(AddProduct):
    id: UUID4

class AddMember(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    categories: list[UUID4]
    paid: Annotated[int, Field(ge=0)]

class Member(AddMember):
    id: UUID4

class AddBoardForm(BaseModel):
    name: Annotated[str, Field(min_length=1)]

class AddUser(BaseModel):
    username: Annotated[str, Field(min_length=1)]
    password: str
    role: Role

class BoardAddForm(BaseModel):
    name: Annotated[str, Field(min_length=1)]
    categories: list[Category]
    products: list[Product]
    members: list[Member]

class BoardDTO(BoardAddForm):
    id: PydanticObjectId

class UserDTO(BaseModel):
    id: PydanticObjectId
    username: Annotated[str, Field(min_length=1)]
    role: Role
from pydantic import BaseModel
from typing import List

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

class UpdateAddress(BaseModel):
    city: str | None = None
    country: str | None = None

class UpdateStudent(BaseModel):
    name: str | None = None
    age: str | None = None
    address: UpdateAddress | None = None

class StudentGetResponseModel(BaseModel):
    name: str
    age: int

class StudentCollection(BaseModel):
    data: List[StudentGetResponseModel]

class PostResponseModel(BaseModel):
    id: str | None = None
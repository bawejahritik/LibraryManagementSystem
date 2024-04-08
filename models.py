from pydantic import BaseModel
from typing import List, Optional

class Address(BaseModel):
    city: str
    country: str

class Student(BaseModel):
    name: str
    age: int
    address: Address

class UpdateAddress(BaseModel):
    city: Optional[str] = None
    country: Optional[str] = None

class UpdateStudent(BaseModel):
    name: Optional[str] = None
    age: Optional[str] = None
    address: Optional[UpdateAddress] = None

class StudentGetResponseModel(BaseModel):
    name: str
    age: int

class StudentCollection(BaseModel):
    data: List[StudentGetResponseModel]

class PostResponseModel(BaseModel):
    id: Optional[str] = None
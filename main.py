from fastapi import FastAPI, Query, Path, HTTPException, Response
from bson.objectid import ObjectId
from models import Student, UpdateStudent, PostResponseModel, StudentCollection
from database import student_collection
from fastapi.openapi.utils import get_openapi
from datetime import datetime, timedelta
import redis

app = FastAPI()

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title="Backend Intern Hiring Task",
        version="1.0.0",
        routes=app.routes,
    )

    for methods in openapi_schema['paths'].values():
        for tags in methods.values():
            del tags["responses"]["422"]
    app.openapi_schema = openapi_schema
    return app.openapi_schema

def update_nested_fields(existing_obj: dict, new_obj: dict):
    """
    Recursively updates nested fields in the existing object with values from the new object.
    """
    for key, value in new_obj.items():
        if isinstance(value, dict) and key in existing_obj:
            update_nested_fields(existing_obj[key], value)
        else:
            existing_obj[key] = value

app.openapi = custom_openapi


app = FastAPI()

redis_client = redis.Redis(host='localhost', port=6379, db=0)

def time_until_end_of_day():
    now = datetime.now()
    end_of_day = datetime(now.year, now.month, now.day, 23, 59, 59)
    return (end_of_day - now).total_seconds()

async def rate_limit_middleware(request, call_next):
    user_id = request.headers.get('user_id')
    if user_id:
        key = f"{user_id}"
        count = redis_client.get(key)
        if count is None:
            redis_client.setex(key, int(time_until_end_of_day()), 1)
        else:
            count = int(count)
            if count >= 3:
                return Response(content="Rate limit exceeded", status_code=429)
            else:
                redis_client.incr(key)
    response = await call_next(request)
    return response

app.middleware('http')(rate_limit_middleware)


@app.post(
        "/students", 
        description="API to create a student in the system. All fields are manadatory and required while creating the student in the system.",
        status_code=201, 
        responses={201: {"model": PostResponseModel, "description": 'A JSON response sending back the ID of the newly created student record.'}}
    )
async def create_students(student: Student):
    new_student = await student_collection.insert_one(student.model_dump(by_alias=True, exclude=['id']))
    created_student = await student_collection.find_one({"_id": new_student.inserted_id})
    return {"id": str(created_student.pop('_id'))}

@app.get(
        "/students",
        description="An API to find a list of students. You can apply filters on this API by passing the query parameters as listed below.",
        response_model=StudentCollection,
        response_description="Sample Response",
        status_code=200
    )
async def list_students(
        country: str = Query(None, description="To apply filter of country. If not given or empty, this filter shouldn't be applied."), 
        age: int = Query(None, description="Only records which have greater than equal to the provided age should be present in the result. If not given or empty, this filter shouldn't be applied.")
    ):
    
    if country and age:
        return StudentCollection(data = await student_collection.find({"address.country":country, "age":{"$gte":age}}).to_list(None))
    elif country:
        return StudentCollection(data = await student_collection.find({"address.country":country}).to_list(None))
    elif age:
        return StudentCollection(data = await student_collection.find({"age": {"$gte":age}}).to_list(None))
    
    return StudentCollection(data = await student_collection.find().to_list(None))

@app.get(
    "/students/{id}",
    response_model=Student,
)
async def fetch_student(id: str = Path(description="The ID of the student previously created.")):
    if (
        student := await student_collection.find_one({"_id": ObjectId(id)})
    ) is not None:
        return student

@app.patch(
    "/students/{id}",
    description="API to update the student's properties based on information provided. Not mandatory that all information would be sent in PATCH, only what fields are sent should be updated in the Database.",
    status_code=204,
    response_description = 'No Content',
)
async def update_student(id: str, student: UpdateStudent | None = None):
    if student:
        update_fields = student.dict(by_alias=True, exclude_none=True)
        existing_student = await student_collection.find_one({"_id": ObjectId(id)})
        if existing_student:
            update_nested_fields(existing_student, update_fields)
            await student_collection.replace_one({"_id": ObjectId(id)}, existing_student)

    return {}

@app.delete(
    "/students/{id}",
    response_description="Sample Response",
    status_code=200,
)
async def delete_student(id: str) -> dict:
    delete_result = await student_collection.delete_one({"_id": ObjectId(id)}) 
    if delete_result.deleted_count == 1:
        return {}
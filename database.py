import motor.motor_asyncio
client = motor.motor_asyncio.AsyncIOMotorClient('mongodb+srv://user:user@cluster0.6hrmdnc.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0')
db = client.get_database('librarymanagement')
student_collection = db.get_collection('students')
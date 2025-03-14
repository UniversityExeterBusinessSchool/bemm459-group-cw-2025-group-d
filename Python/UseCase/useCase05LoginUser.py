from datetime import datetime
import sys
import os
# regular expression
import re
# Object for mongodb
from bson.objectid import ObjectId
# jwt
import jwt
import bcrypt
from datetime import datetime, timedelta
# Add the parent directory (Project) to sys.path
# ENV file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import env
# # Add the parent directory (Project) to sys.path
# # Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import getMongoConnection

SECRET_KEY = env.jwt_secret

def validateEmail(email: str):
    patternEmail = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patternEmail, email):
        raise ValueError(f"Invalid email address: {email}")

def generateToken(email: str) -> str:
    createDate = datetime.now()
    endDate = createDate + timedelta(hours=1)
    payload = {
        'email': email,
        'createDate': createDate.isoformat(),
        'endDate': endDate.isoformat()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def loginUser(email: str, password: str) -> str:
    validateEmail(email)
    client = getMongoConnection()
    collectionUsers = client['Users']
    user = collectionUsers.find_one({'email': email})

    if not user:
        raise ValueError("User not found")

    if user['isDelete']:
        raise ValueError("User has been deleted")

    if not bcrypt.checkpw(password.encode('utf-8'), user['password'].encode('utf-8')):
        raise ValueError("Invalid password")

    token = generateToken(email)
    collectionUsers.update_one({'_id': ObjectId(user['_id'])}, {'$set': {'loginToken': token, 'loginDate': datetime.utcnow()}})
    print('User logged in and token updated')
    return token

# Example usage
if __name__ == "__main__":
    email = "test3@gmail.com"
    password = "your_password_here"
    token = loginUser(email, password)
    print("JWT Token:", token)

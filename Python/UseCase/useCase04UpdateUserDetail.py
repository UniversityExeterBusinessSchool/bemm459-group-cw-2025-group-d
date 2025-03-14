from datetime import datetime
import sys
import os
# regular expression
import re
# Object for mongodb
from bson.objectid import ObjectId
# # Add the parent directory (Project) to sys.path
# # Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import getMongoConnection

def validateEmail(email: str):
    patternEmail = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patternEmail, email):
        raise ValueError(f"Invalid email address: {email}")

def updateUserDetail(email: str, userDetails: dict):
    validateEmail(email)
    client = getMongoConnection()
    collectionUsers = client['Users']
    user = collectionUsers.find_one({'email': email})
    if not user:
        raise ValueError("User not found")
    if user['isDelete']:
        raise ValueError("User has already been deleted")
    if user['emailConfirmationStatus'] == 'Unconfirmed':
        updateFields = {}
        for field in userDetails:
            if field in ['email', 'password', 'firstName', 'lastName', 'phoneCountryCode', 'phoneNumber', 'gender']:
                updateFields[field] = userDetails[field]
        updateFields['updateDate'] = datetime.now()
        collectionUsers.update_one({'_id': ObjectId(user['_id'])}, {'$set': updateFields})
        print('User details have been updated')

# Example usage
if __name__ == "__main__":
    userDetails = {
        "email": "newemail@example.com",
        "password": "newhashedpassword",
        "firstName": "John",
        "lastName": "Doe",
        "phoneCountryCode": 1,
        "phoneNumber": 1234567890,
        "gender": "Male"
    }
    updateUserDetail('test3@gmail.com', userDetails)

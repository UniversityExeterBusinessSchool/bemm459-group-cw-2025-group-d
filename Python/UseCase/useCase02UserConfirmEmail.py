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

def validation (email):
    # email
    patternEmail = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patternEmail, email):
        raise ValueError(f"Invalid email address: {email}")
    
def confirmUserEmail(email,idCode):
    # validation
    validation(email)
    # Mongodb
    client = getMongoConnection()
    collectionUsers = client['Users']
    userObjectId = ObjectId(idCode)
    query = {"email": email, "emailConfirmationStatus": "Unconfirmed", "isDelete": False}
    projection = {"_id": 0, "email": 1}
    user = collectionUsers.find_one(query, projection)
    if user:
        # if user exist
        user['emailConfirmationStatus'] = 'Confirmed'
        collectionUsers.update_one({'_id': userObjectId}, {'$set': user})
        print('User email has been confirmed')
    else:
        print("No such user found.")

# Example usage
if __name__ == "__main__":
    confirmUserEmail('test3@gmail.com','67b5d0556820fe9e9d250440')
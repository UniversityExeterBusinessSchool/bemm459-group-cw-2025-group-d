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
    
def updateUserAddress(email,address):
    # validation
    validation(email)
    # Mongodb
    client = getMongoConnection()
    collectionUsers = client['Users']
    query = {"email": email, "emailConfirmationStatus": "Confirmed", "isDelete": False}
    user = collectionUsers.find_one(query)
    query = {"emailConfirmationStatus": "Confirmed", "isDelete": False}
    projection = {"_id": userObjectId, "email": email}  
    user = collectionUsers.find_one(query, projection)
    print('User address has been updated')
    if user['isDelete'] == False:
        raise 'User already have been deleted'
    if(user['email'] == email and user['emailConfirmationStatus'] == 'Unconfirmed'):
        user['address'] = address
        collectionUsers.update_one({'_id': userObjectId}, {'$set': user})
    print('User address has been updated')

# Example usage
if __name__ == "__main__":
    userAddress = {
        "addressLine1": "123 Main St",
        "addressLine2": "Apt 4B",
        "city": "New York",
        "state": "NY",
        "country": "USA",
        "zipCode": 10001
    }
    updateUserAddress('test3@gmail.com',userAddress)
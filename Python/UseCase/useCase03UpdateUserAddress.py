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
    user = collectionUsers.find_one({'email': email})
    print('User address has been updated')

updateUserAddress('test3@gmail.com',[])
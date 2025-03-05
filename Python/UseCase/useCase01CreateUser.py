from datetime import datetime
import sys
import os
# hash library
import hashlib
# regular expression
import re
# # Add the parent directory (Project) to sys.path
# # Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import queryPostgreSQL, getMongoConnection

def hashPassword(password):
    hashObject = hashlib.sha256()
    hashObject.update(password.encode('utf-8'))
    hashedPassword = hashObject.hexdigest()
    return hashedPassword

def validation(email,countryCode,phoneNumber,firstName,lastName,gender,password):
    # email
    patternEmail = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(patternEmail, email):
        raise ValueError(f"Invalid email address: {email}")
    # country code
    if not countryCode.startswith("+") and 1 <= len(countryCode[1:]) <= 3 and countryCode[1:].isdigit():
        raise ValueError(f"Invalid country code: {country_code}")
    # phonenumber
    if not phoneNumber.isdigit():
        raise ValueError(f"Invalid phone number: {phoneNumber}")
    patternAlphabet = r'^[a-zA-Z]+$'
    # firstName
    if len(firstName) < 1:
        raise ValueError('First name should be longer than 1 characters')
    elif not re.match(patternAlphabet, firstName):
        raise ValueError(f"Invalid first name: {firstName}") 
    # lastName
    if len(lastName) < 1:
        raise ValueError('Last name should be longer than 1 characters')
    elif not re.match(patternAlphabet, lastName):
        raise ValueError(f"Invalid last name: {lastName}")
    # gender
    if not (gender == 'Male' or gender == 'Female' or gender == 'Unidentify'):
        raise ValueError('Invalide gender')
    # password
    if len(password) < 8:
        raise ValueError('Password should be longer than 8 characters')

def createUser(email,countryCode,phoneNumber,firstName,lastName,gender,password):
    # Validation
    validation(email,countryCode,phoneNumber,firstName,lastName,gender,password)
    # Hash password
    hashedPassword = hashPassword(password)
    # SQL
    # Validate duplicate email
    queryCheckDuplicateEmail =  "SELECT pkuser FROM marketsync.v_users WHERE email = '" + email + "'"
    pkUser = queryPostgreSQL(operation = "SELECT", query = queryCheckDuplicateEmail)
    if len(pkUser) > 0:
        raise ValueError(f"Duplicate email: {email}")
    # Insert User
    # Example
    # INSERT INTO marketsync.users (email) VALUES ('test@gmail.com') RETURNING pkuser
    queryInsertUser = "INSERT INTO marketsync.users (email) VALUES ('" + email + "') RETURNING pkuser"
    pkUser = queryPostgreSQL(operation = "INSERT", query = queryInsertUser)
    # Mongodb
    client = getMongoConnection()
    collectionUsers = client['Users']
    user = {
        "pkUser": int(pkUser[0]),
        "email": email,
        "password": hashedPassword,
        "firstName": firstName,
        "lastName": lastName,
        "fullName": firstName + " " + lastName,
        "phoneCountryCode": countryCode,
        "phoneNumber": phoneNumber,
        "gender": gender,
        "address": [],
        "cart": [],
        "searchHistory": [],
        "emailConfirmationStatus": "Unconfirmed",
        "loginToken": "",
        "createDate": datetime.now(),
        "updateDate": datetime.now(),
        "isDelete": False
    }
    collectionUsers.insert_one(user)
    print('Successfully create user account')

createUser("test9@gmail.com",'+1','0123456789','testFirstName','testLastName','Male','testPassword')

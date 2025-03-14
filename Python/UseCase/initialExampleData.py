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
from DatabaseConnection import queryMSSQL, getMongoConnection

def hashPassword(password):
    hashObject = hashlib.sha256()
    hashObject.update(password.encode('utf-8'))
    hashedPassword = hashObject.hexdigest()
    return hashedPassword

def validationCreateUserMock(email,countryCode,phoneNumber,firstName,lastName,gender,password):
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

def createUserMock(email,countryCode,phoneNumber,firstName,lastName,gender,password,emailConfirmationStatus,isDelete):
    # Validation
    validationCreateUserMock(email,countryCode,phoneNumber,firstName,lastName,gender,password)
    # Hash password
    hashedPassword = hashPassword(password)
    # SQL
    # Validate duplicate email
    queryCheckDuplicateEmail =  "SELECT pkuser FROM marketsync.v_users WHERE email = '" + email + "'"
    pkUser = queryMSSQL(operation = "SELECT", query = queryCheckDuplicateEmail)
    if len(pkUser) > 0:
        raise ValueError(f"Duplicate email: {email}")
    # Insert User
    # Example
    # INSERT INTO marketsync.users (email) VALUES ('test@gmail.com') RETURNING pkuser
    queryInsertUser = "INSERT INTO marketsync.users (email,isDelete) VALUES ('" + email + "' , '" + str(isDelete) + "') RETURNING pkuser"
    pkUser = queryMSSQL(operation = "INSERT", query = queryInsertUser)
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
        "emailConfirmationStatus": emailConfirmationStatus,
        "loginToken": "",
        "createDate": datetime.now(),
        "updateDate": datetime.now(),
        "isDelete": isDelete
    }
    collectionUsers.insert_one(user)
    print('Successfully create user account')

# Example usage
if __name__ == "__main__":
    # Create Mock Users
    users = [
        ("user1@example.com", "+1", "1234567890", "John", "Doe", "Male", "Password123!", "Confirmed", False),
        ("user2@example.com", "+1", "2345678901", "Jane", "Smith", "Female", "MyP@ssw0rd!", "Confirmed", False),
        ("user3@example.com", "+1", "3456789012", "Alice", "Johnson", "Female", "Secure123*", "Confirmed", False),
        ("user4@example.com", "+1", "4567890123", "Bob", "Brown", "Male", "Passw0rd!", "Confirmed", False),
        ("user5@example.com", "+1", "5678901234", "Charlie", "Davis", "Male", "S@f3Pass!", "Confirmed", False),
        ("user6@example.com", "+1", "6789012345", "David", "Miller", "Male", "Pa$$word1", "Confirmed", False),
        ("user7@example.com", "+1", "7890123456", "Eve", "Wilson", "Female", "GoodPass@", "Confirmed", False),
        ("user8@example.com", "+1", "8901234567", "Frank", "Moore", "Male", "Gr8P@ssw0rd", "Confirmed", False),
        ("user9@example.com", "+1", "9012345678", "Grace", "Taylor", "Female", "Y0urP@ss", "Confirmed", False),
        ("user10@example.com", "+1", "0123456789", "Hannah", "Anderson", "Female", "TopS3cret!", "Confirmed", False),
        ("user11@example.com", "+1", "1234509876", "Ivy", "Thomas", "Female", "B3$tP@ssw0rd", "Confirmed", False),
        ("user12@example.com", "+1", "2345610987", "Jack", "Jackson", "Male", "Str0ngP@ss", "Confirmed", False),
        ("user13@example.com", "+1", "3456721098", "Katy", "White", "Female", "P@ssw0rd123", "Confirmed", False),
        ("user14@example.com", "+1", "4567832109", "Leo", "Harris", "Male", "H@ppyDay!", "Confirmed", False),
        ("user15@example.com", "+1", "5678943210", "Mia", "Clark", "Female", "S3cur3P@ss", "Confirmed", False),
        ("user16@example.com", "+1", "6789054321", "Nick", "Lewis", "Male", "T3mpP@ss!", "Unconfirmed", True),
        ("user17@example.com", "+1", "7890165432", "Olivia", "Walker", "Female", "W3akP@ss123", "Unconfirmed", True),
        ("user18@example.com", "+1", "8901276543", "Paul", "Hall", "Male", "Myp@ssword", "Unconfirmed", True),
        ("user19@example.com", "+1", "9012387654", "Quinn", "Allen", "Female", "BasicP@ss", "Unconfirmed", True),
        ("user20@example.com", "+1", "0123498765", "Rachel", "Young", "Female", "1234P@ss", "Unconfirmed", True)
    ]
    for user in users:
        try:
            createUserMock(*user)
            print(f"Successfully created user: {user[0]}")
        except ValueError as e:
            print(f"Failed to create user: {user[0]}, Error: {e}")


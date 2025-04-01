# This file contain Python code file that integrates all 
# the Python code from the "Main" and "Library" folders into a single Python file.
# This is not optimal because everything is in one file and make it hard to read or develop

##########################################################################################################
# Import Library
# MSSQL connection
import pyodbc
# MongoDB connection
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
# Object for mongodb
from bson.objectid import ObjectId
# import env file
from typing import Literal
# Hash Library
import hashlib
# JSON Web token
import jwt
# Date time
from datetime import datetime, timedelta
# Regular Expression
import re
# logger
import logging

##########################################################################################################
# Initial Data
# MSsql environment
mssql_server = "localhost"
mssql_port = 10001
mssql_database = "marketsync"
mssql_user = "sa"
mssql_password = "YourStrong!Passw0rd"

# MongoDB environment
mongoDB_database = "marketsync"
mongoDB_host = "localhost"
mongoDB_port = 10003
mongoDB_username = "system_admin"
mongoDB_password = "marketsyncpassword"

# JWT
jwt_secret = "marketsyncpassword"

##########################################################################################################
# Library Function
def queryMSSQL(operation: Literal["SELECT", "INSERT", "UPDATE", "DELETE"], query: str, params: tuple = ()):
    """
    Execute a SQL query on the MSSQL database.
    Args:
        operation (Literal["SELECT", "INSERT", "UPDATE", "DELETE"]): The type of SQL operation.
        query (str): The SQL query string.
        params (tuple, optional): Parameters for the SQL query. Defaults to ().
    Raises:
        Exception: If any error occurs during the database operation.
    Returns:
        list or None: The result of the query if it's a SELECT operation, otherwise None.
    """
    mssql_connection = None
    cursor = None
    try:
        mssql_connection = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=' + mssql_server + ',' + str(mssql_port) + ';'
            'DATABASE=' + mssql_database + ';'
            'UID=' + mssql_user + ';'
            'PWD=' + mssql_password
        )
        cursor = mssql_connection.cursor()
        cursor.execute(query, params)
        if operation == "SELECT":
            records = cursor.fetchall()
            return records
        elif operation == "INSERT":
            row = cursor.fetchone()
            mssql_connection.commit()
            return row
        elif operation == "INSERT_WITHOUT_FETCH":
            mssql_connection.commit()
        elif operation in ["UPDATE", "DELETE"]:
            mssql_connection.commit()
    except Exception as error:
        print("MSSQL Error:" + str(error))
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if mssql_connection is not None:
            mssql_connection.close()

def queryFunctionMSSQL(functionQuery, functionParameter):
    """
    Execute a SQL function on the MSSQL database.
    Args:
        functionQuery (str): The SQL function query string.
        functionParameter (tuple, optional): Parameters for the SQL function.
    Raises:
        Exception: If any error occurs during the database operation.
    Returns:
        list or None: The result of the query if it's a SELECT operation, otherwise None.
    """
    try:
        mssql_connection = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=' + mssql_server + ';'
            'DATABASE=' + mssql_database + ';'
            'UID=' + mssql_user + ';'
            'PWD=' + mssql_password
        )
        cursor = mssql_connection.cursor()
        result = functionQuery(cursor=cursor, mssql_connection=mssql_connection, functionParameter=functionParameter)
        return result
    except Exception as error:
        print("MSSQL Error:" + str(error))
        raise
    finally:
        # Closing the database connection
        if mssql_connection:
            cursor.close()
            mssql_connection.close()

# MongoDB connection
def getMongoConnection() -> MongoDatabase:
    """
    Establish a connection to the MongoDB database.
    Raises:
        Exception: If any error occurs during the database operation.
    Returns:
        MongoDatabase: The MongoDB database object.
    """
    try:
        mongo_connection = MongoClient(
            host = mongoDB_host,
            port = mongoDB_port,
            username = mongoDB_username,
            password = mongoDB_password
        )
        client = mongo_connection
        return client, mongoDB_database
    except Exception as error:
        print("MongoDB Error:" + str(error))
        raise
    finally:
        pass
    
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def logError(**kwargs):
    """
    Logs an error message with detailed information.
    Args:
        **kwargs: Keyword arguments representing error details.
    """
    errorDetails = ', '.join(f"{key}={value}" for key, value in kwargs.items())
    print(errorDetails)
    logging.error(f"Error Details: {errorDetails}")

SECRET_KEY = jwt_secret

def hashPassword(password :str,salt :str):
    """
    Hashes a password using SHA256 with a salt.
    Args:
        password (str): The password to hash.
        salt (str): The salt to use for hashing.
    Returns:
        str: The hashed password.
    """
    saltedPassword = password + salt
    hashObject = hashlib.sha256()
    hashObject.update(saltedPassword.encode('utf-8'))
    hashedPassword = hashObject.hexdigest()
    return hashedPassword

def comparePasswords(inputPassword, storedHashedPassword, salt):
    """
    Compares an input password with a stored hashed password using a salt.
    Args:
        inputPassword (str): The password to compare.
        storedHashedPassword (str): The stored hashed password.
        salt (str): The salt used for hashing.
    Returns:
        bool: True if the passwords match, False otherwise.
    """
    hashedInputPassword = hashPassword(inputPassword, salt)
    return hashedInputPassword == storedHashedPassword

def generateToken(email: str) -> str:
    """
    Generates a JWT token for a given email.
    Args:
        email (str): The email to include in the token.
    Returns:
        str: The generated JWT token.
    """
    createDate = datetime.now()
    endDate = createDate + timedelta(hours=1)
    payload = {
        'email': email,
        'createDate': createDate.isoformat(),
        'endDate': endDate.isoformat()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

class TokenExpiredError(Exception):
    """
    Exception raised when a token has expired.
    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="Token has expired"):
        self.message = message
        super().__init__(self.message)
        
    pass

class InvalidTokenError(Exception):
    """
    Exception raised when an invalid token is encountered.
    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="Invalid token"):
        self.message = message
        super().__init__(self.message)

def decodeAndValidateToken(token: str) -> str:
    """
    Decodes and validates a JWT token.
    Args:
        token (str): The JWT token to decode and validate.
    Raises:
        TokenExpiredError: If the token has expired.
        InvalidTokenError: If the token is invalid.
    Returns:
        str: The email associated with the token if it's valid.
    """
    try:
        # Decode the token
        decodedPayload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        # Extract the email and endDate
        email = decodedPayload.get('email')
        endDate = datetime.fromisoformat(decodedPayload.get('endDate'))
        # Check if the token is still valid
        if datetime.now() > endDate:
            raise TokenExpiredError("Token has expired")
        # Return the email if valid
        return email
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token signature has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")
    except Exception as e:
        raise InvalidTokenError(f"Token validation failed: {str(e)}")

def validateNotNull(value, fieldName):
    """
    Validates that a given value is not null or empty.
    Args:
        value: The value to validate.
        fieldName: The name of the field being validated.
    Raises:
        ValueError: If the value is null or empty.
    """
    if not value:
        raise ValueError(f"{fieldName} must not be null or empty.")

def validateMaxLength(value, fieldName, maxLength=200):
    """
    Validates that a given value does not exceed a specified maximum length.
    Args:
        value: The value to validate.
        fieldName: The name of the field being validated.
        maxLength: The maximum allowed length.
    Raises:
        ValueError: If the value exceeds the maximum length.
    """
    if len(value) > maxLength:
        raise ValueError(f"{fieldName} must not exceed {maxLength} characters.")

def validateEmail(email):
    """
    Validates that a given email address is in a valid format.
    Args:
        email (str): The email address to validate.
    Raises:
        ValueError: If the email is not in a valid format.
    """
    validateNotNull(email, "Email")
    validateMaxLength(email, "Email")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email address: {email}")

def validateCountryCode(countryCode):
    """
    Validates that a given country code is in a valid format.
    Args:
        countryCode (str): The country code to validate.
    Raises:
        ValueError: If the country code is not in a valid format.
    """
    validateNotNull(countryCode, "Country code")
    validateMaxLength(countryCode, "Country code")
    if not (countryCode.startswith("+") and countryCode[1:].isdigit() and 1 <= len(countryCode[1:]) <= 3):
        raise ValueError(f"Invalid country code: {countryCode}")

def validatePhoneNumber(phoneNumber):
    """
    Validates that a given phone number is in a valid format.
    Args:
        phoneNumber (str): The phone number to validate.
    Raises:
        ValueError: If the phone number is not in a valid format.
    """
    validateNotNull(phoneNumber, "Phone number")
    validateMaxLength(phoneNumber, "Phone number")
    if not phoneNumber.isdigit():
        raise ValueError(f"Invalid phone number: {phoneNumber}")

def validateString(string, fieldName):
    """
    Validates that a given string is in a valid format.
    Args:
        string (str): The string to validate.
        fieldName (str): The name of the field being validated.
    Raises:
        ValueError: If the string is not in a valid format.
    """
    validateNotNull(string, fieldName)
    validateMaxLength(string, fieldName)
    # pattern string can contain number
    pattern = r'^[a-zA-Z0-9\s]+$'
    if not re.match(pattern, string):
        raise ValueError(f"Invalid {fieldName}: {string}")
    
def validateSentence(string, fieldName):
    """
    Validates that a given sentence is in a valid format.
    Args:
        string (str): The sentence to validate.
        fieldName (str): The name of the field being validated.
    Raises:
        ValueError: If the sentence is not in a valid format.
    """
    validateNotNull(string, fieldName)
    validateMaxLength(string, fieldName)
    pattern = r'^[a-zA-Z0-9\s.,!?;:\'"-]+$'
    if not re.match(pattern, string):
        raise ValueError(f"Invalid {fieldName}: {string}")
    
def validateStringList(stringList, fieldName):
    """
    Validates that a given list of strings is in a valid format.
    Args:
        stringList (list): The list of strings to validate.
        fieldName (str): The name of the field being validated.
    Raises:
        ValueError: If the list or any of its strings are not in a valid format.
    """
    # Check if the list itself is not null
    validateNotNull(stringList, fieldName)
    # Ensure the input is a list
    if not isinstance(stringList, list):
        raise ValueError(f"{fieldName} must be a list of strings")
    # Iterate through the list and validate each string
    for index, item in enumerate(stringList):
        # Ensure each item is not null
        validateNotNull(item, f"{fieldName}[{index}]")
        # Ensure each item adheres to the maximum length
        validateMaxLength(item, f"{fieldName}[{index}]")
        # Ensure each item matches the pattern (sentence)
        pattern = r'^[a-zA-Z0-9\s.,!?;:\'"-]+$'
        if not re.match(pattern, item):
            raise ValueError(f"Invalid {fieldName}[{index}]: {item}")

def validateImagePath(productImagePath, fieldName="productImagePath"):
    """
    Validates that a given product image path is in a valid format.
    Args:
        productImagePath (str): The product image path to validate.
        fieldName (str): The name of the field being validated.
    Raises:
        ValueError: If the product image path is not in a valid format."""
    # Ensure the field is not null
    validateNotNull(productImagePath, fieldName)
    validateMaxLength(productImagePath, fieldName)
    if not isinstance(productImagePath, str):
        raise ValueError(f"Invalid {fieldName}: must be a string.")
    # Ensure the field is a string
    if not productImagePath.endswith(('.png', '.jpg', '.jpeg')):
        raise ValueError(f"Invalid {fieldName}: must be a png, jpg, or jpeg file.")
        

def validateImagePathList(productImagePath, fieldName="productImagePath"):
    """
    Validates that a given list of product image paths is in a valid format.
    Args:
        productImagePath (list): The list of product image paths to validate.
        fieldName (str): The name of the field being validated.
    Raises:
        ValueError: If the list or any of its product image paths are not in a valid format.
    """
    # Ensure the field is not null
    validateNotNull(productImagePath, fieldName)
    # Ensure the field is a list
    if not isinstance(productImagePath, list):
        raise ValueError(f"{fieldName} must be a list of strings.")
    # If the list is not empty, validate each item
    for index, item in enumerate(productImagePath):
        # Ensure each item is not null
        validateNotNull(item, f"{fieldName}[{index}]")
        # Ensure each item is a string
        if not isinstance(item, str):
            raise ValueError(f"Invalid {fieldName}[{index}]: must be a string.")
        # Ensure each item ends with a valid image extension
        if not item.endswith(('.png', '.jpg', '.jpeg')):
            raise ValueError(f"Invalid {fieldName}[{index}]: must be a png, jpg, or jpeg file.")
            

def validateGender(gender):
    """
    Validates that a given gender is in a valid format.
    Args:
        gender (str): The gender to validate.
    Raises:
        ValueError: If the gender is not in a valid format.
    """
    validateNotNull(gender, "Gender")
    validateMaxLength(gender, "Gender")
    if gender not in ['Male', 'Female', 'Unidentify']:
        raise ValueError(f"Invalid gender: {gender}")

def validatePassword(password):
    """
    Validates that a given password meets certain criteria.
    Args:
        password (str): The password to validate.
    Raises:
        ValueError: If the password does not meet the criteria.
    """
    validateNotNull(password, "Password")
    validateMaxLength(password, "Password")
    if len(password) < 8:
        raise ValueError("Password should be longer than 8 characters.")

def validateEmailConfirmationStatus(emailConfirmationStatus):
    """
    Validates that a given email confirmation status is in a valid format.
    Args:
        emailConfirmationStatus (str): The email confirmation status to validate.
    Raises:
        ValueError: If the email confirmation status is not in a valid format.
    """
    validateNotNull(emailConfirmationStatus, "EmailConfirmationStatus")
    validateMaxLength(emailConfirmationStatus, "EmailConfirmationStatus")
    if emailConfirmationStatus not in ['Confirmed', 'Unconfirmed']:
        raise ValueError(f"Invalid EmailConfirmationStatus: {emailConfirmationStatus}")
    
def validateBoolean(booleanData):
    """
    Validates that a given boolean value is in a valid format.
    Args:
        booleanData (bool): The boolean value to validate.
    Raises:
        ValueError: If the boolean value is not in a valid format.
    """
    if not isinstance(booleanData, bool):
        raise ValueError(f"Invalid boolean value: {booleanData}")
    
def validateFloatOrDouble(value, fieldName="value"):
    """
    Validates that a given value is a float or double.
    Args:
        value: The value to validate.
        fieldName: The name of the field being validated.
    Raises:
        ValueError: If the value is not a float or double.
    """
    # Check if the value is not null
    validateNotNull(value, fieldName)
    # Ensure the value is of type float or can be interpreted as a float
    if not isinstance(value, (float, int)):  # Allow int as it can also represent a valid float
        raise ValueError(f"{fieldName} must be a float or double.")
    # Optionally, add further constraints, such as a range
    if value < 0.0:  # Example: ensuring a non-negative value
        raise ValueError(f"{fieldName} must be greater than or equal to 0.0.")

def validateAddressList(addressList):
    """
    Validates that a given list of addresses is in a valid format.
    Args:
        addressList (list): The list of addresses to validate.
    Raises:
        ValueError: If the list or any of its addresses are not in a valid format.
    """
    # Define the expected structure
    expectedStructure = {
        "addressLine1": str,
        "addressLine2": str,
        "city": str,
        "state": str,
        "country": str,
        "zipCode": int,
    }
    errors = []
    for index, address in enumerate(addressList):
        if not isinstance(address, dict):
            errors.append(f"Item at index {index} is not a valid dictionary.")
            continue
        # Validate required keys and their types for each address
        for key, expected_type in expectedStructure.items():
            if key not in address:
                errors.append(f"Address at index {index}: Missing key: {key}")
            elif not isinstance(address[key], expected_type):
                errors.append(f"Address at index {index}: Key '{key}' should be of type {expected_type.__name__}, got {type(address[key]).__name__}.")
        # Additional checks for zipCode
        if "zipCode" in address and isinstance(address["zipCode"], int):
            if address["zipCode"] <= 0:
                errors.append(f"Address at index {index}: zipCode must be a positive integer.")
    # Raise an error if there are validation issues
    if errors:
        raise ValueError("Address validation failed with the following errors:\n" + "\n".join(errors))
    
def validateTransactionStatus(transactionStatus):
    """
    Validates that a given transaction status is in a valid format.
    Args:
        transactionStatus (str): The transaction status to validate.
    Raises:
        ValueError: If the transaction status is not in a valid format.
    """
    validateNotNull(transactionStatus, "TransactionStatus")
    validateMaxLength(transactionStatus, "TransactionStatus")
    if transactionStatus not in ['Processing', 'Wait for payment', 'Completed', 'Cancelled']:
        raise ValueError(f"Invalid TransactionStatus: {transactionStatus}")
        
def validateLogisticStatus(logisticStatus):
    """
    Validates that a given logistic status is in a valid format.
    Args:
        logisticStatus (str): The logistic status to validate.
    Raises:
        ValueError: If the logistic status is not in a valid format.
    """
    validateNotNull(logisticStatus, "LogisticStatus")
    validateMaxLength(logisticStatus, "LogisticStatus")
    if logisticStatus not in ['Processing', 'Shipping', 'Delivered', 'Cancelled']:
        raise ValueError(f"Invalid LogisticStatus: {logisticStatus}")
    
##########################################################################################################
# Function
def getAllMessageRelateToUser(pkUser):
    """
    Gets all messages related to a user.
    Args:
        pkUser (int): The primary key of the user.
    Returns:
        list: A list of messages related to the user.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Get data from mongodb
        client,dbname = getMongoConnection()
        collectionMessage = client[dbname]['Messages']
        # Check if product already in cart
        messages = collectionMessage.find({"$or": [{"fkUserSender": pkUser}, {"fkUserReceiver": pkUser}]})
        if messages is None:
            print("Message not found")
            return None
        messageList = []
        for message in messages:
            messageList.append(message)
        return messageList
    except Exception as error:
        print("Fail to get message:", error)
        logError(error=error, function=getAllMessageRelateToUser.__name__, input= {
            "pkUser": pkUser
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getMessageBetweenUserAndShop(pkUserBuyer, pkShop):
    """
    Gets all messages between a user and a shop.
    Args:
        pkUserBuyer (int): The primary key of the user.
        pkShop (int): The primary key of the shop.
    Returns:
        list: A list of messages between the user and the shop.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUserBuyer)
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # Get data from mongodb
        client,dbname = getMongoConnection()
        collectionMessage = client[dbname]['Messages']
        # Check if product already in cart
        message = collectionMessage.find_one({"pkUserBuyer": pkUserBuyer, "pkShop": pkShop})
        if message is None:
            print("Message not found")
            return None
        return message
    except Exception as error:
        print("Fail to get message:", error)
        logError(error=error, function=getMessageBetweenUserAndShop.__name__, input= {
            "pkUserBuyer": pkUserBuyer,
            "pkShop": pkShop
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def sendUserMessageToShop(pkUser, pkShop, message):
    """
    Sends a message from a user to a shop.
    Args:
        pkUser (int): The primary key of the user.
        pkShop (int): The primary key of the shop.
        message (str): The message to send.
    Returns:
        dict: The message that was sent.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # Get data from mongodb
        client,dbname = getMongoConnection()
        collectionMessage = client[dbname]['Messages']
        # Check if product already in cart
        messageData = {
            "message": message,
            "sender": "User",
            "createDate": datetime.now(),
            "updateDate": datetime.now(),
            "isDelete": False
        }
        message = collectionMessage.find_one({"pkUserBuyer": pkUser, "pkShop": pkShop})
        if message is None:
            newMessage = {
                "pkUserBuyer": pkUser,
                "pkShop": pkShop,
                "chat": [messageData]
            }
            collectionMessage.insert_one(newMessage)
            print("Message sent successfully")
            return newMessage
        else:
            collectionMessage.update_one(
                {"pkUserBuyer": pkUser, "pkShop": pkShop},
                {"$push": {"chat": messageData}}
            )
            print("Message sent successfully")
            return message
    except Exception as error:
        print("Fail to send message:", error)
        logError(error=error, function=sendUserMessageToShop.__name__, input= {
            "pkUser": pkUser,
            "pkShop": pkShop,
            "message": message
        })
        
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def sendShopMessageToUser(pkUser, pkShop, message):
    """
    Sends a message from a shop to a user.
    Args:
        pkUser (int): The primary key of the user.
        pkShop (int): The primary key of the shop.
        message (str): The message to send.
    Returns:
        dict: The message that was sent.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # Get data from mongodb
        client,dbname = getMongoConnection()
        collectionMessage = client[dbname]['Messages']
        # Check if product already in cart
        messageData = {
            "message": message,
            "sender": "Shop",
            "createDate": datetime.now(),
            "updateDate": datetime.now(),
            "isDelete": False
        }
        message = collectionMessage.find_one({"pkUserBuyer": pkUser, "pkShop": pkShop})
        if message is None:
            newMessage = {
                "pkUserBuyer": pkUser,
                "pkShop": pkShop,
                "chat": [messageData]
            }
            collectionMessage.insert_one(newMessage)
            print("Message sent successfully")
            return newMessage
        else:
            collectionMessage.update_one(
                {"pkUserBuyer": pkUser, "pkShop": pkShop},
                {"$push": {"chat": messageData}}
            )
            print("Message sent successfully")
            return message
    except Exception as error:
        print("Fail to send message:", error)
        logError(error=error, function=sendShopMessageToUser.__name__, input= {
            "pkUser": pkUser,
            "pkShop": pkShop,
            "message": message
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    
def userReviewProduct(fkUser,fkProduct,review):
    """
    Adds a review to a product.
    Args:
        fkUser (int): The primary key of the user.
        fkProduct (int): The primary key of the product.
        review (dict): The review to add.
    Returns:
        dict: The product that was reviewed.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Check if product exist in rdbms database
        validatePKProduct(fkProduct)
        # Get data from mongodb
        client,dbname = getMongoConnection()
        collectionProduct = client[dbname]['Products']
        # Check if product already in cart
        reviewData = {
            "pkUser": fkUser,
            "star": review["star"],
            "comment": review["comment"]
        }
        product = collectionProduct.find_one({"product.pkProduct": fkProduct})
        if product is None:
            print("Product not found")
            return None
        else:
            collectionProduct.update_one(
                {"product.pkProduct": fkProduct},
                {"$push": {"reviews": reviewData}}
            )
            print("Review sent successfully")
            return product
    except Exception as error:
        print("Fail to send review:", error)
        logError(error=error, function=userReviewProduct.__name__, input= {
            "fkUser": fkUser,
            "fkProduct": fkProduct,
            "review": review
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def validateProductGroupId(productGroupId) -> bool:
    """
    Validates if a product group ID is valid.
    Args:
        productGroupId: The ID of the product group to validate.
    Raises:
        ValueError: If the product group ID is invalid.
    """
    try:
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        productGroup = collection.find_one({"_id": ObjectId(productGroupId)}, {"_id": 0})
        if productGroup is None:
            raise ValueError(f"Invalid productGroupId: {productGroupId}")
    except Exception as error:
        raise
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def validatePKProduct(pkProduct):
    """
    Validates if a product ID is valid.
    Args:
        pkProduct: The ID of the product to validate.
    Raises:
        ValueError: If the product ID is invalid.
    """
    try:        
        # Get data from rdbms database
        queryCheckPKProduct =  "SELECT pkproduct FROM marketsync.v_products WHERE pkproduct = ?"
        product = queryMSSQL(operation="SELECT", query=queryCheckPKProduct, params=(pkProduct))
        if product is None:
            raise ValueError(f"Invalid productId: {pkProduct}")
    except Exception as error:
        raise

def getfkShopFromProductGroup(productGroupId):
    """
    Gets the foreign key of the shop from a product group ID.
    Args:
        productGroupId: The ID of the product group.
    Returns:
        The foreign key of the shop.
    Raises:
        ValueError: If the product group ID is invalid.
    """
    try:
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        productGroup = collection.find_one({"_id": ObjectId(productGroupId)}, {"pkShop": 1})
        if productGroup is None:
            raise ValueError(f"Invalid productGroupId: {productGroupId}")
        return productGroup["pkShop"]
    except Exception as error:
        raise
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getfkShopfromProduct(pkProduct: int):
    """
    Gets the foreign key of the shop from a product ID.
    Args:
        pkProduct: The ID of the product.
    Returns:
        The foreign key of the shop.
    Raises:
        ValueError: If the product ID is invalid.
    """
    query =  "SELECT fkShop FROM marketsync.v_products WHERE pkProduct = ?"
    shop = queryMSSQL(operation="SELECT", query=query, params=(pkProduct))
    if shop is None:
        raise ValueError(f"Invalid pkProduct: {pkProduct}")
    return shop[0][0]
            

def createProductGroup(fkShop: int, groupName, groupDescription, productImagePath, productCategory, isDelete = False):
    """
    Creates a new product group.
    Args:
        fkShop (int): The foreign key of the shop.
        groupName (str): The name of the product group.
        groupDescription (str): The description of the product group.
        productImagePath (str): The image path of the product group.
        productCategory (list): The category of the product group.
        isDelete (bool): The status of the product group.
    Returns:
        ObjectId: The ID of the newly created product group.
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error creating the product group.
    """
    try:
        # Check if shop exist in rdbms database
        validatePKShop(fkShop)
        # Validate Value
        validateSentence(groupName, "Group name")
        validateSentence(groupDescription, "Group description")
        validateImagePath(productImagePath, "Product image path")
        validateStringList(productCategory, "Product category")
        # Get shop name
        shopName = getShopNameWithPKShop(fkShop)
        # Insert data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        productGroup = {
            "pkShop": fkShop,
            "shopName": shopName,
            "productName": groupName,
            "productDescription": groupDescription,
            "productImagePath": productImagePath,
            "productCategory": productCategory,
            "soldAmount": 0,
            "product": [],
            "reviews": [],
            "createDate": datetime.now(),
            "updateDate": datetime.now(),
            "isDelete": isDelete
        }
        result = collection.insert_one(productGroup)
        return result.inserted_id
    except Exception as error:
        print("Fail to create ProductGroup:", error)
        logError(error=error, function=createProductGroup.__name__, input= {
            "fkShop": fkShop,
            "groupName": groupName,
            "groupDescription": groupDescription,
            "productImagePath": productImagePath,
            "productCategory": productCategory,
            "isDelete": isDelete
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def updateProductGroup(productGroupId, groupName, groupDescription, productImagePath, productCategory):
    """
    Updates an existing product group.
    Args:
        productGroupId (ObjectId): The ID of the product group to update.
        groupName (str): The new name of the product group.
        groupDescription (str): The new description of the product group.
        productImagePath (str): The new image path of the product group.
        productCategory (list): The new category of the product group.
    Returns:
        int: The number of documents modified.
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error updating the product group.
    """
    try:
        # Validate Value
        validateSentence(groupName, "Group name")
        validateSentence(groupDescription, "Group description")
        validateString(productImagePath, "Product image path")
        validateStringList(productCategory, "Product category")
        # Update data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        updatedFields = {
            "productName": groupName,
            "productDescription": groupDescription,
            "productImagePath": productImagePath,
            "productCategory": productCategory,
            "updateDate": datetime.now()
        }
        result = collection.update_one({"_id": ObjectId(productGroupId)}, {"$set": updatedFields})
        print("Product group updated. Matched:", result.matched_count, "Modified:", result.modified_count)
        return result.modified_count
    except Exception as error:
        print("Fail to update product group:", error)
        logError(error=error, function=updateProductGroup.__name__, input= {
            "productGroupId": productGroupId,
            "groupName": groupName,
            "groupDescription": groupDescription,
            "productImagePath": productImagePath,
            "productCategory": productCategory
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
def deleteProductGroup(productGroupId):
    """
    Deletes a product group.
    Args:
        productGroupId (ObjectId): The ID of the product group to delete.
    Returns:
        int: The number of documents modified.
    Raises:
        ValueError: If the product group ID is invalid.
        Exception: If there is an error deleting the product group.
    """
    try:
        # Delete data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        result = collection.update_one(
            {"_id": ObjectId(productGroupId)},
            {"$set": {"isDelete": True, "updateDate": datetime.now()}}
        )
        print("Product group soft-deleted. Matched:", result.matched_count, "Modified:", result.modified_count)
        return result.modified_count
    except Exception as error:
        print("Fail to delete product group:", error)
        logError(error=error, function=deleteProductGroup.__name__, input= {
            "productGroupId": productGroupId
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def createProductToProductGroup(productGroupId, productName, productDescription, productImagePath, productPrice):
    """
    Creates a new product and adds it to a product group.
    Args:
        productGroupId (ObjectId): The ID of the product group to add the product to.
        productName (str): The name of the product.
        productDescription (str): The description of the product.
        productImagePath (str): The image path of the product.
        productPrice (float): The price of the product.
    Returns:
        int: The ID of the newly created product.
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error creating the product.
    """
    try:
        # validate product group id
        validateProductGroupId(productGroupId)
        # get fkshop from product group
        fkShop = getfkShopFromProductGroup(productGroupId)
        # Validate Value
        validateSentence(productName, "Product name")
        validateSentence(productDescription, "Product description")
        validateImagePath(productImagePath, "Product image path")
        validateFloatOrDouble(productPrice, "Product price")
        # Insert product data to rdbms
        queryInsertProduct = """
        SET NOCOUNT ON;
        DECLARE @InsertedProducts TABLE (pkProduct INT);
        INSERT INTO marketsync.Products (productName,fkShop)
        OUTPUT Inserted.pkProduct INTO @InsertedProducts
        VALUES (?,?)
        SELECT pkProduct FROM @InsertedProducts;
        """
        pkProduct = queryMSSQL(operation="INSERT", query=queryInsertProduct, params=(productName,fkShop))[0]
        if pkProduct is None:
            raise ValueError(f"Failed to create product: {productName}")
        # Update data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        product = {
            "pkProduct": int(pkProduct),
            "productName": productName,
            "productDescription": productDescription,
            "productImagePath": productImagePath,
            "productPrice": productPrice,
            "createDate": datetime.now(),
            "updateDate": datetime.now(),
            "isDelete": False
        }
        result = collection.update_one(
            {"_id": ObjectId(productGroupId)},
            {"$push": {"product": product}}
        )
        print("Product added to group. Matched:", result.matched_count, "Modified:", result.modified_count)
        return pkProduct
    except Exception as error:
        print("Fail to add product to group:", error)
        logError(error=error, function=createProductToProductGroup.__name__, input= {
            "productGroupId": productGroupId,
            "productName": productName,
            "productDescription": productDescription,
            "productImagePath": productImagePath,
            "productPrice": productPrice
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    

def updateProductToProductGroup(productGroupId, fkProduct, productName, productDescription, productImagePath, productPrice):
    """
    Updates an existing product within a product group.
    Args:
        productGroupId (ObjectId): The ID of the product group containing the product.
        fkProduct (int): The ID of the product to update.
        productName (str): The new name of the product.
        productDescription (str): The new description of the product.
        productImagePath (str): The new image path of the product.
        productPrice (float): The new price of the product.
    Returns:
        int: The number of documents modified.
    Raises:
        ValueError: If any of the input values are invalid or if the product is not found in the group.
        Exception: If there is an error updating the product.
    """
    try:
        # validate product group id
        validateProductGroupId(productGroupId)
        # validate product id
        validatePKProduct(fkProduct)
        # Validate Value
        validateString(productName, "Product name")
        validateString(productDescription, "Product description")
        validateImagePath(productImagePath, "Product image path")
        validateFloatOrDouble(productPrice, "Product price")
        # Update product name to rdbms dataabase
        queryUpdateProduct = "UPDATE marketsync.Products SET productName = ? WHERE pkProduct = ?"
        queryMSSQL(operation="UPDATE", query=queryUpdateProduct, params=(productName,fkProduct))
        if queryMSSQL(operation="SELECT", query="SELECT pkProduct FROM marketsync.Products WHERE pkProduct = ? AND productName = ?", params=(fkProduct, productName)) is None:
            raise ValueError(f"Failed to update product: {productName}")
        # Check if product exist in product group
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        productGroup = collection.find_one({"_id": ObjectId(productGroupId)}, {"product": 1})
        if productGroup is None:
            raise ValueError(f"Invalid productGroupId: {productGroupId}")
        productExist = False
        for product in productGroup["product"]:
            if product["pkProduct"] == fkProduct:
                productExist = True
                break
        if not productExist:
            raise ValueError(f"Product {fkProduct} not found in product group {productGroupId}")
        # Update product data to mongodb database
        updatedFields = {
            "product.$.productName": productName,
            "product.$.productDescription": productDescription,
            "product.$.productImagePath": productImagePath,
            "product.$.productPrice": productPrice,
            "product.$.updateDate": datetime.now()
        }
        result = collection.update_one(
            {"_id": ObjectId(productGroupId), "product.pkProduct": fkProduct},
            {"$set": updatedFields}
        )
        print("Product updated in group. Matched:", result.matched_count, "Modified:", result.modified_count)
        return result.modified_count
    except Exception as error:
        print("Fail to update product in group:", error)
        logError(error=error, function=updateProductToProductGroup.__name__, input= {
            "productGroupId": productGroupId,
            "fkProduct": fkProduct,
            "productName": productName,
            "productDescription": productDescription,
            "productImagePath": productImagePath,
            "productPrice": productPrice
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
def deleteProductFromProductGroup(productGroupId, fkProduct):
    """
    Deletes a product from a product group.
    Args:
        productGroupId (ObjectId): The ID of the product group to delete the product from.
        fkProduct (int): The ID of the product to delete.
    Returns:
        int: The number of documents modified.
    Raises:
        ValueError: If any of the input values are invalid or if the product is not found in the group.
        Exception: If there is an error deleting the product.
    """
    try:
        # validate product group id
        validateProductGroupId(productGroupId)
        # validate product id
        validatePKProduct(fkProduct)
        # Update product name to rdbms dataabase
        queryUpdateProduct = "UPDATE marketsync.Products SET isDelete = 1, updateDate = ? WHERE pkProduct = ?"
        queryMSSQL(operation="UPDATE", query=queryUpdateProduct, params=(datetime.now(),fkProduct))
        if queryMSSQL(operation="SELECT", query="SELECT pkProduct FROM marketsync.Products WHERE pkProduct = ? AND isDelete = 1", params=(fkProduct)) is None:
            raise ValueError(f"Failed to delete product: {fkProduct}")
        # Check if product exist in product group
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        productGroup = collection.find_one({"_id": ObjectId(productGroupId)}, {"product": 1})
        if productGroup is None:
            raise ValueError(f"Invalid productGroupId: {productGroupId}")
        productExist = False
        for product in productGroup["product"]:
            if product["pkProduct"] == fkProduct:
                productExist = True
                break
        if not productExist:
            raise ValueError(f"Product {fkProduct} not found in product group {productGroupId}")
        # Update product data to mongodb database
        result = collection.update_one(
            {"_id": ObjectId(productGroupId), "product.pkProduct": fkProduct},
            {"$set": {"product.$.isDelete": True, "product.$.updateDate": datetime.now()}}
        )
        print("Product soft-deleted in group. Matched:", result.matched_count, "Modified:", result.modified_count)
        return result.modified_count
    except Exception as error:
        print("Fail to delete product in group:", error)
        logError(error=error, function=deleteProductFromProductGroup.__name__, input= {
            "productGroupId": productGroupId,
            "fkProduct": fkProduct
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
        
def searchProduct(productName):
    """
    Searches for products based on a product name.
    Args:
        productName (str): The name of the product to search for.
    Returns:
        list: A list of product groups that match the search criteria.
    Raises:
        ValueError: If the product name is invalid.
        Exception: If there is an error searching for the product.
    """
    try:
        # Validate Value
        validateString(productName, "Product name")
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        # Search product name or product description in product group
        productGroups = collection.find({
            "$or": [
                {"productName": {"$regex": productName, "$options": "i"}},
                {"productDescription": {"$regex": productName, "$options": "i"}},
                {"product.productName": {"$regex": productName, "$options": "i"}},
                {"product.productDescription": {"$regex": productName, "$options": "i"}}
            ],
            "isDelete": False
        })
        products = []
        for productGroup in productGroups:
            products.append(productGroup)
        return products
    except Exception as error:
        print("Fail to search product:", error)
        logError(error=error, function=searchProduct.__name__, input= {
            "productName": productName
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def searchProductWithCategory(productName,productCategory):
    """
    Searches for products based on a product name and product category.
    Args:
        productName (str): The name of the product to search for.
        productCategory (list): The category of the product to search for.
    Returns:
        list: A list of product groups that match the search criteria.
    Raises:
        ValueError: If the product name or product category is invalid.
        Exception: If there is an error searching for the product.
    """
    try:
        # Validate Value
        validateString(productName, "Product name")
        validateStringList(productCategory, "Product category")
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        # Search product name or product description in product group
        productGroups = collection.find({
            "$and": [
                {
                    "$or": [
                        {"productName": {"$regex": productName, "$options": "i"}},
                        {"productDescription": {"$regex": productName, "$options": "i"}},
                        {"product.productName": {"$regex": productName, "$options": "i"}},
                        {"product.productDescription": {"$regex": productName, "$options": "i"}}
                    ]
                },
                {"productCategory": {"$in": productCategory}},
                {"isDelete": False}
            ]
        })
        products = []
        for productGroup in productGroups:
            products.append(productGroup)
        return products
    except Exception as error:
        print("Fail to search product:", error)
        logError(error=error, function=searchProductWithCategory.__name__, input= {
            "productName": productName,
            "productCategory": productCategory
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
def getUserRecommendations(pkUser,size):
    """
    Gets user recommendations based on their search history and popular products.
    Args:
        pkUser (int): The ID of the user to get recommendations for.
        size (int): The number of recommendations to return.
    Returns:
        list: A list of product groups that are recommended for the user.
    Raises:
        ValueError: If the user ID or size is invalid.
        Exception: If there is an error getting the recommendations.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Validate Value
        if size <= 0:
            raise ValueError(f"Invalid size: {size}")
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUser = db['Users']
        collectionProduct = db['Products']
        # Get user search history
        user = collectionUser.find_one({"pkUser": pkUser}, {"searchHistory": 1})
        if user is None:
            raise ValueError(f"Invalid pkUser: {pkUser}")
        # Get user search history keyword
        keywords = []
        if "searchHistory" in user:
            for searchHistory in user["searchHistory"]:
                keywords.append(searchHistory["keyword"])
        # Get most popular product with keyword
        products = []
        if len(keywords) > 0:
            for keyword in keywords:
                productGroups = collectionProduct.find({
                    "$or": [
                        {"productName": {"$regex": keyword, "$options": "i"}},
                        {"productDescription": {"$regex": keyword, "$options": "i"}},
                        {"product.productName": {"$regex": keyword, "$options": "i"}},
                        {"product.productDescription": {"$regex": keyword, "$options": "i"}}
                    ],
                    "isDelete": False
                }).sort("soldAmount", -1).limit(size)
                for productGroup in productGroups:
                    products.append(productGroup)
        # Get most popular product without keyword
        if len(products) < size:
            productGroups = collectionProduct.find({"isDelete": False}).sort("soldAmount", -1).limit(size - len(products))
            for productGroup in productGroups:
                products.append(productGroup)
        return products
    except Exception as error:
        print("Fail to get user recommendations:", error)
        logError(error=error, function=getUserRecommendations.__name__, input= {
            "pkUser": pkUser,
            "size": size
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def validatePKShop(pkShop: int):
    """
    Validates if a shop ID is valid.
    Args:
        pkShop: The ID of the shop to validate.
    Raises:
        ValueError: If the shop ID is invalid.
    """
    query =  "SELECT pkshop FROM marketsync.v_shops WHERE pkshop = ?"
    shop = queryMSSQL(operation="SELECT", query=query, params=(pkShop))
    if shop is None:
        raise ValueError(f"Invalid pkShop: {pkShop}")
    
def getShopNameWithPKShop(pkShop: int):
    """
    Gets the name of a shop from a shop ID.
    Args:
        pkShop: The ID of the shop.
    Returns:
        The name of the shop.
    Raises:
        ValueError: If the shop ID is invalid.
    """
    query =  "SELECT shopName FROM marketsync.v_shops WHERE pkshop = ?"
    shop = queryMSSQL(operation="SELECT", query=query, params=(pkShop))
    if shop is None:
        raise ValueError(f"Invalid pkShop: {pkShop}")
    return shop[0][0]

def createShop(fkUser: int,shopName):
    """
    Creates a new shop.
    Args:
        fkUser (int): The foreign key of the user who owns the shop.
        shopName (str): The name of the shop.
    Returns:
        int: The primary key of the newly created shop.
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error creating the shop.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Validate Value
        validateString(shopName, "Shop name")
        # Insert data to rdbms database
        queryInsertShop = """
        SET NOCOUNT ON;
        DECLARE @InsertedShop TABLE (pkShop INT);
        INSERT INTO marketsync.Shops (shopName, fkUser)
        OUTPUT Inserted.pkShop INTO @InsertedShop
        VALUES (?, ?);
        SELECT pkShop FROM @InsertedShop;
        """
        pkShop = queryMSSQL(operation = "INSERT", query = queryInsertShop, params=(shopName, fkUser))
        if pkShop is None:
            raise ValueError(f"Failed to create shop: {shopName} for user {fkUser}")
        print("Shop created successfully")
        return pkShop[0]
    except Exception as error:
        print("Fail to create shop:", error)
        logError(error=error, function=createShop.__name__, input= {
            "fkUser": fkUser,
            "shopName": shopName
        })
    
def updateShopName(pkShop: int, shopName):
    """
    Updates the name of an existing shop.
    Args:
        pkShop (int): The primary key of the shop to update.
        shopName (str): The new name for the shop.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error updating the shop name.
    """
    try:
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # Validate Value
        validateString(shopName, "Shop name")
        # Update shop name in rdbms database
        queryUpdateShop = "UPDATE marketsync.Shops SET shopName = ? WHERE pkShop = ?"
        queryMSSQL(operation="UPDATE", query=queryUpdateShop, params=(shopName,pkShop))
        if queryMSSQL(operation="SELECT", query="SELECT pkShop FROM marketsync.Shops WHERE pkShop = ? AND shopName = ?", params=(pkShop, shopName)) is None:
            raise ValueError(f"Failed to update shop: {shopName} for shop {pkShop}")
        print("Shop name updated in rdbms database.")
        # Update shop name in mongodb
        client,dbname = getMongoConnection()
        collectionProducts = client[dbname]['Products']
        updateResult = collectionProducts.update_many(
            {"pkShop": pkShop, "isDelete": False},
            {"$set": {"shopName": shopName}}
        )
        if updateResult.modified_count > 0:
            print(f"Updated {updateResult.modified_count} product group shop names in MongoDB.")
        else:
            print("No product group shop names were updated in MongoDB.")
        print("Shop updated successfully")
    except Exception as error:
        print("Fail to update shop:", error)
        logError(error=error, function=updateShopName.__name__, input= {
            "pkShop": pkShop,
            "shopName": shopName
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            

def softDeleteShop(pkShop: int):
    """
    Deletes a shop by setting its isDelete flag to True.
    Args:
        pkShop (int): The primary key of the shop to delete.
    Returns:
        None
    Raises:
        ValueError: If the shop ID is invalid.
        Exception: If there is an error deleting the shop.
    """
    try:
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # soft delete shop in rdbms database
        queryUpdateShop = "UPDATE marketsync.Shops SET isDelete = 1 WHERE pkShop = ?"
        queryMSSQL(operation="UPDATE", query=queryUpdateShop, params=(pkShop))
        print("Shop soft deleted in rdbms database.")
        # Get all product relate to shop in mongodb
        client,dbname = getMongoConnection()
        collectionProducts = client[dbname]['Products']
        products = collectionProducts.find({"pkShop": pkShop, "isDelete": False})
        # update product isDelete
        for product in products:
            for productItem in product["product"]:
                queryUpdateProduct = "UPDATE marketsync.Products SET isDelete = 1 WHERE pkProduct = ?"
                queryMSSQL(operation="UPDATE", query=queryUpdateProduct, params=(productItem["pkProduct"]))
                print("Product soft deleted in rdbms database.")
        # delete shop in mongodb
        updateResult = collectionProducts.update_many(
            {"pkShop": pkShop, "isDelete": False},
            {"$set": {"isDelete": True}}
        )
        if updateResult.modified_count > 0:
            print(f"Deleted {updateResult.modified_count} every product group with pkshop " + str(pkShop) + " in MongoDB.")
        else:
            print("No product group shop names were updated in MongoDB.")
        print("Shop deleted successfully")
    except Exception as error:
        print("Fail to delete shop:", error)
        logError(error=error, function=softDeleteShop.__name__, input= {
            "pkShop": pkShop
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def validateTransactionPK(pkTransaction: int):
    """
    Validates if a transaction ID is valid.
    Args:
        pkTransaction: The ID of the transaction to validate.
    Raises:
        ValueError: If the transaction ID is invalid.
    """
    queryCheckPKTransaction =  "SELECT pkTransaction FROM marketsync.v_transactions WHERE pkTransaction = ?"
    transaction = queryMSSQL(operation="SELECT", query=queryCheckPKTransaction, params=(pkTransaction))
    if transaction is None:
        raise ValueError(f"Invalid pkTransaction: {pkTransaction}")
                         
def checkIsTransactionCompleted(pkTransaction: int):
    """
    Gets the transaction status.
    Args:
        pkTransaction: The ID of the transaction to check.
    Raises:
        ValueError: If the transaction ID is invalid.
    """
    # check if transaction is completed
    queryCheckPKTransaction =  "SELECT fkTransaction FROM marketsync.v_transactionstates WHERE fkTransaction = ? AND transactionStatus = ?"
    transaction = queryMSSQL(operation="SELECT", query=queryCheckPKTransaction, params=(pkTransaction, "Completed"))
    if transaction is None:
        raise ValueError(f"Transaction Status is not Completed.")

def getProductGroupTransactionHistory(productGroupId):
    """
    Gets the transaction history of a product group.
    Args:
        productGroupId (ObjectId): The ID of the product group to get the transaction history for.
    Returns:
        list: A list of transactions that the product group has been involved in.
    Raises:
        ValueError: If the product group ID is invalid.
        Exception: If there is an error getting the transaction history.
    """
    try:
        # validate product group id
        validateProductGroupId(productGroupId)
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        db = client[dbname]
        collection = db['Products']
        productGroup = collection.find_one({"_id": ObjectId(productGroupId)}, {"product": 1})
        if productGroup is None:
            raise ValueError(f"Invalid productGroupId: {productGroupId}")
        # use pkproduct to search product in transaction table in rdbms
        transactionHistory = []
        for product in productGroup["product"]:
            queryGetTransactionHistory = """
            SELECT t.pkTransaction, t.createDate, t.totalPrice, t.fkUserBuyer, tp.quantity, tp.price, p.productName
            FROM marketsync.Transactions t
            INNER JOIN marketsync.TransactionProducts tp ON t.pkTransaction = tp.fkTransaction
            INNER JOIN marketsync.Products p ON tp.fkProduct = p.pkProduct
            WHERE tp.fkProduct = ?
            """
            transactions = queryMSSQL(operation="SELECT", query=queryGetTransactionHistory, params=(product["pkProduct"]))
            if transactions is not None:
                for transaction in transactions:
                    transactionHistory.append(transaction)
        return transactionHistory
    except Exception as error:
        print("Fail to get product group transaction history:", error)
        logError(error=error, function=getProductGroupTransactionHistory.__name__, input= {
            "productGroupId": productGroupId
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getProductTransactionHistory(pkProduct):
    """
    Gets the transaction history of a product.
    Args:
        pkProduct (int): The ID of the product to get the transaction history for.
    Returns:
        list: A list of transactions that the product has been involved in.
    Raises:
        ValueError: If the product ID is invalid.
        Exception: If there is an error getting the transaction history.
    """
    try:
        # validate product id
        validatePKProduct(pkProduct)
        # Get data from rdbms database
        queryGetTransactionHistory = """
        SELECT t.pkTransaction, t.createDate, t.totalPrice, t.fkUserBuyer, tp.quantity, tp.price, p.productName
        FROM marketsync.Transactions t
        INNER JOIN marketsync.TransactionProducts tp ON t.pkTransaction = tp.fkTransaction
        INNER JOIN marketsync.Products p ON tp.fkProduct = p.pkProduct
        WHERE tp.fkProduct = ?
        """
        transactions = queryMSSQL(operation="SELECT", query=queryGetTransactionHistory, params=(pkProduct))
        return transactions
    except Exception as error:
        print("Fail to get product transaction history:", error)
        logError(error=error, function=getProductTransactionHistory.__name__, input= {
            "pkProduct": pkProduct
        })
            


def addProductToCart(fkUser: int, fkProduct: int, quantity: int):
    """
    Adds a product to a user's cart.
    Args:
        fkUser (int): The ID of the user to add the product to.
        fkProduct (int): The ID of the product to add.
        quantity (int): The quantity of the product to add.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error adding the product to the cart.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Check if product exist in rdbms database
        validatePKProduct(fkProduct)
        # Check if quantity is valid
        if quantity <= 0:
            raise ValueError(f"Invalid quantity: {quantity}")
        # Update data to mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        productExist = False
        for item in user["cart"]:
            if item["pkProduct"] == fkProduct:
                item["quantity"] += quantity
                productExist = True
                break
        if not productExist:
            # Get product price from mongodb
            collectionProduct = db['Products']
            product = collectionProduct.find_one({"product.pkProduct": fkProduct}, {"product.$": 1})
            if product is None:
                raise ValueError(f"Invalid fkProduct: {fkProduct}")
            price = product["product"][0]["productPrice"]
            # Add product to cart
            cartItem = {
                "productId": ObjectId(product["_id"]),
                "pkProduct": fkProduct,
                "quantity": quantity,
                "price": price
            }
            collectionUsers.update_one(
                {"pkUser": fkUser},
                {"$push": {"cart": cartItem}}
            )
        else:
            collectionUsers.update_one(
                {"pkUser": fkUser, "cart.pkProduct": fkProduct},
                {"$set": {"cart.$.quantity": item["quantity"]}}
            )
        print("Product added to cart.")
    except Exception as error:
        print("Fail to add product to cart:", error)
        logError(error=error, function=addProductToCart.__name__, input= {
            "fkUser": fkUser,
            "fkProduct": fkProduct,
            "quantity": quantity
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def removeProductFromCart(fkUser: int, fkProduct: int):
    """
    Removes a product from a user's cart.
    Args:
        fkUser (int): The ID of the user to remove the product from.
        fkProduct (int): The ID of the product to remove.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid or if the product is not found in the cart.
        Exception: If there is an error removing the product from the cart.
    """
    # remove product from cart in user.cart in mongodb
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Check if product exist in rdbms database
        validatePKProduct(fkProduct)
        # Update data to mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        productExist = False
        for item in user["cart"]:
            if item["pkProduct"] == fkProduct:
                productExist = True
                break
        if not productExist:
            raise ValueError(f"Product {fkProduct} not found in cart")
        collectionUsers.update_one(
            {"pkUser": fkUser},
            {"$pull": {"cart": {"pkProduct": fkProduct}}}
        )
        print("Product removed from cart.")
    except Exception as error:
        print("Fail to remove product from cart:", error)
        logError(error=error, function=removeProductFromCart.__name__, input= {
            "fkUser": fkUser,
            "fkProduct": fkProduct
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def editProductQuantityInCart(fkUser: int, fkProduct: int, quantity: int):
    """
    Edits the quantity of a product in a user's cart.
    Args:
        fkUser (int): The ID of the user whose cart to edit.
        fkProduct (int): The ID of the product to edit.
        quantity (int): The new quantity of the product.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid or if the product is not found in the cart.
        Exception: If there is an error editing the product quantity in the cart.
    """
    # edit product quantity in cart
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Check if product exist in rdbms database
        validatePKProduct(fkProduct)
        # Check if quantity is valid
        if quantity <= 0:
            raise ValueError(f"Invalid quantity: {quantity}")
        # Update data to mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        productExist = False
        for item in user["cart"]:
            if item["pkProduct"] == fkProduct:
                item["quantity"] = quantity
                productExist = True
                break
        if not productExist:
            raise ValueError(f"Product {fkProduct} not found in cart")
        collectionUsers.update_one(
            {"pkUser": fkUser, "cart.pkProduct": fkProduct},
            {"$set": {"cart.$.quantity": quantity}}
        )
        print("Product quantity updated in cart.")
    except Exception as error:
        print("Fail to update product quantity in cart:", error)
        logError(error=error, function=editProductQuantityInCart.__name__, input= {
            "fkUser": fkUser,
            "fkProduct": fkProduct,
            "quantity": quantity
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    
def getUserCart(fkUser: int):
    """
    Gets the cart of a user.
    Args:
        fkUser (int): The ID of the user to get the cart for.
    Returns:
        list: A list of products in the user's cart.
    Raises:
        ValueError: If the user ID is invalid.
        Exception: If there is an error getting the cart.
    """
    # get cart
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Get data from mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        return user["cart"]
    except Exception as error:
        print("Fail to get cart:", error)
        logError(error=error, function=getUserCart.__name__, input= {
            "fkUser": fkUser
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    
def clearCart(fkUser: int):
    """
    Clears the cart of a user.
    Args:
        fkUser (int): The ID of the user whose cart to clear.
    Returns:
        None
    Raises:
        ValueError: If the user ID is invalid.
        Exception: If there is an error clearing the cart.
    """
    # clear cart
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Update data to mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        collectionUsers.update_one(
            {"pkUser": fkUser},
            {"$set": {"cart": []}}
        )
        print("Cart cleared.")
    except Exception as error:
        print("Fail to clear cart:", error)
        logError(error=error, function=clearCart.__name__, input= {
            "fkUser": fkUser
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def cartToPayment(fkUser: int):
    """
    Converts a user's cart to a payment transaction.
    Args:
        fkUser (int): The ID of the user whose cart to convert.
    Returns:
        int: The ID of the newly created transaction.
    Raises:
        ValueError: If the user ID is invalid or if the cart is empty.
        Exception: If there is an error creating the transaction.
    """
    # use cart data in mongodb to create transaction in rdbms
    # then create transaction status in rdbms as well it start from 'Processing'
    # after that clear cart
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Get data from mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        if len(user["cart"]) == 0:
            raise ValueError(f"Cart is empty")
        # Validate fkProduct
        for item in user["cart"]:
            validatePKProduct(item["pkProduct"])
        # loop user["cart"] to get pkProduct then use it to create transaction, transactionproduct,transactionstatus "Processing"
        totalPrice = 0
        for item in user["cart"]:
            totalPrice += item["quantity"] * item["price"]
        # Insert data to rdbms database
        queryInsertTransaction = """
        SET NOCOUNT ON;
        DECLARE @InsertedTransaction TABLE (pkTransaction INT);
        INSERT INTO marketsync.Transactions (fkUserBuyer, totalPrice)
        OUTPUT Inserted.pkTransaction INTO @InsertedTransaction
        VALUES (?, ?);
        SELECT pkTransaction FROM @InsertedTransaction;
        """
        pkTransaction = queryMSSQL(operation="INSERT", query=queryInsertTransaction, params=(fkUser, totalPrice))[0]
        if pkTransaction is None:
            raise ValueError(f"Failed to create transaction for user: {fkUser}")
        # Insert transaction product
        for item in user["cart"]:
            # Get fkShop from first product
            queryInsertTransactionProduct = """
            INSERT INTO marketsync.TransactionProducts (fkTransaction, fkProduct, quantity, price)
            VALUES (?, ?, ?, ?);
            """
            queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertTransactionProduct, params=(pkTransaction, item["pkProduct"], item["quantity"], item["price"]))
        # Insert transaction status
        queryInsertTransactionStatus = """
        INSERT INTO marketsync.TransactionStates (fkTransaction, transactionStatus)
        VALUES (?, ?);
        """
        queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertTransactionStatus, params=(pkTransaction, "Processing"))
        # Clear cart
        clearCart(fkUser)
        print("Transaction created.")
        return pkTransaction
    except Exception as error:
        print("Fail to create transaction:", error)
        logError(error=error, function=cartToPayment.__name__, input= {
            "fkUser": fkUser
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def changeTransactionStatus(pkTransaction: int, transactionStatus: str):
    """
    Updates the status of a transaction.
    Args:
        pkTransaction (int): The ID of the transaction to update.
        transactionStatus (str): The new status of the transaction.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error updating the transaction status.
    """
    # change transaction status in SQL
    try:
        # Validate transaction pk
        validateTransactionPK(pkTransaction)
        # Validate transaction status
        validateTransactionStatus(transactionStatus)
        # Check if transaction exist in rdbms database
        queryCheckTransaction = """
        SELECT pkTransaction FROM marketsync.Transactions WHERE pkTransaction = ?
        """
        transaction = queryMSSQL(operation="SELECT", query=queryCheckTransaction, params=(pkTransaction))
        if transaction is None:
            raise ValueError(f"Invalid pkTransaction: {pkTransaction}")
        # Update data to rdbms database
        queryInsertTransactionStatus = """
        INSERT INTO marketsync.TransactionStates (fkTransaction, transactionStatus)
        VALUES (?, ?);
        """
        queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertTransactionStatus, params=(pkTransaction, transactionStatus))
        print("Transaction status updated.")
    except Exception as error:
        print("Fail to update transaction status:", error)
        logError(error=error, function=changeTransactionStatus.__name__, input= {
            "pkTransaction": pkTransaction,
            "transactionStatus": transactionStatus
        })
        
def updateSoldAmount(pkTransacion):
    """
    Updates the sold amount of products in MongoDB after a transaction is completed.
    Args:
        pkTransacion (int): The ID of the transaction to update the sold amount for.
    Returns:
        None
    Raises:
        ValueError: If the transaction ID is invalid or if the transaction is not completed.
        Exception: If there is an error updating the sold amount.
        
    """
    # create logistic with pktransaction also need to check that transaction is completed first
    try:
        # Get data from rdbms database
        queryGetTransactionProduct = """
        SELECT fkProduct, quantity
        FROM marketsync.TransactionProducts
        WHERE fkTransaction = ?
        """
        transactionProducts = queryMSSQL(operation="SELECT", query=queryGetTransactionProduct, params=(pkTransacion))
        if transactionProducts is None:
            raise ValueError(f"Invalid pkTransaction: {pkTransacion}")
        # Update data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        for transactionProduct in transactionProducts:
            pkProduct = transactionProduct[0]
            quantity = transactionProduct[1]
            productGroup = collection.find_one({"product.pkProduct": pkProduct}, {"product.$": 1})
            if productGroup is None:
                raise ValueError(f"Invalid pkProduct: {pkProduct}")
            result = collection.update_one(
                {"_id": ObjectId(productGroup["_id"])},
                {"$inc": {"soldAmount": quantity}}
            )
            print("Product sold amount updated. Matched:", result.matched_count, "Modified:", result.modified_count)
    except Exception as error:
        print("Fail to update sold amount:", error)
        logError(error=error, function=updateSoldAmount.__name__, input= {
            "pkTransacion": pkTransacion
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
def createLogistic(pkTransaction: int, deliveryDate: datetime):
    """
    Creates a new logistic for a transaction.
    Args:
        pkTransaction (int): The ID of the transaction to create the logistic for.
        deliveryDate (datetime): The expected delivery date of the logistic.
    Returns:
        int: The ID of the newly created logistic.
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error creating the logistic.
    """
    try:
        # Validate transaction pk
        validateTransactionPK(pkTransaction)
        # Check if transaction status is completed
        checkIsTransactionCompleted(pkTransaction)
        # Update sold amount
        updateSoldAmount(pkTransaction)
        # Insert data to rdbms database
        queryInsertLogistic = """
        SET NOCOUNT ON;
        DECLARE @InsertedLogistic TABLE (pkLogistic INT);
        INSERT INTO marketsync.Logistics (fkTransaction, expectedDeliveryDate)
        OUTPUT Inserted.pkLogistic INTO @InsertedLogistic
        VALUES (?, ?);
        SELECT pkLogistic FROM @InsertedLogistic;
        """
        pkLogistic = queryMSSQL(operation="INSERT", query=queryInsertLogistic, params=(pkTransaction, deliveryDate))[0]
        if pkLogistic is None:
            raise ValueError(f"Failed to create logistic for transaction: {pkTransaction}")
        # Insert logistic status
        queryInsertLogisticStatus = """
        INSERT INTO marketsync.LogisticStates (fkLogistic, logisticStatus)
        VALUES (?, ?);
        """
        queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertLogisticStatus, params=(pkLogistic, "Processing"))
        print("Logistic created.")
        return pkLogistic
    except Exception as error:
        print("Fail to create logistic:", error)
        logError(error=error, function=createLogistic.__name__, input= {
            "pkTransaction": pkTransaction,
            "deliveryDate": deliveryDate
        })
        
def changeLogisticStatus(pkLogistic: int, logisticStatus: str):
    """
    Updates the status of a logistic.
    Args:
        pkLogistic (int): The ID of the logistic to update.
        logisticStatus (str): The new status of the logistic.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error updating the logistic status.
    """
    # change logistic status in SQL
    try:
        # Validate logistic status
        validateLogisticStatus(logisticStatus)
        # Check if logistic exist in rdbms database
        queryCheckLogistic = """
        SELECT pkLogistic FROM marketsync.Logistics WHERE pkLogistic = ?
        """
        logistic = queryMSSQL(operation="SELECT", query=queryCheckLogistic, params=(pkLogistic))
        if logistic is None:
            raise ValueError(f"Invalid pkLogistic: {pkLogistic}")
        # Update data to rdbms database
        queryInsertLogisticStatus = """
        INSERT INTO marketsync.LogisticStates (fkLogistic, logisticStatus)
        VALUES (?, ?);
        """
        queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertLogisticStatus, params=(pkLogistic, logisticStatus))
        print("Logistic status updated.")
    except Exception as error:
        print("Fail to update logistic status:", error)
        logError(error=error, function=changeLogisticStatus.__name__, input= {
            "pkLogistic": pkLogistic,
            "logisticStatus": logisticStatus
        })
        
def validatePKUserWithoutConfirm(pkUser: int):
    """
    Validates if a user ID is valid.
    Args:
        pkUser: The ID of the user to validate.
    Raises:
        ValueError: If the user ID is invalid.
    """
    queryCheckPKUser =  "SELECT pkuser FROM marketsync.v_users WHERE pkuser = ?"
    user = queryMSSQL(operation="SELECT", query=queryCheckPKUser, params=(pkUser))
    if user is None:
        raise ValueError(f"Invalid pkUser: {pkUser}")

def validatePKUser(pkUser: int):
    validatePKUserWithoutConfirm(pkUser)
    try:
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        user = collectionUsers.find_one({"pkUser": pkUser}, {"emailConfirmationStatus": 1})
        if user is None:
            raise ValueError(f"Invalid pkUser: {pkUser}")
        if user["emailConfirmationStatus"] != "Confirmed":
            raise ValueError(f"User email is not confirmed: {pkUser}")
    except Exception as error:
        raise
    finally:
        if 'client' in locals() and client is not None:
            client.close()

def checkDuplicateEmail(email):
    """
    Checks if an email is already in use.
    Args:
        email: The email to check.
    Raises:
        ValueError: If the email is already in use.
    """
    queryCheckDuplicateEmail =  "SELECT pkuser FROM marketsync.v_users WHERE email = ?"
    pkUser = queryMSSQL(operation="SELECT", query=queryCheckDuplicateEmail, params=(email))
    if pkUser:
        raise ValueError(f"Duplicate email: {email}")

def getPKUserFromEmail(email):
    """
    Gets the primary key of a user from an email.
    Args:
        email: The email of the user.
    Returns:
        The primary key of the user.
    Raises:
        ValueError: If the email is invalid.
    """
    queryCheckPKUser =  "SELECT pkuser FROM marketsync.v_users WHERE email = ?"
    user = queryMSSQL(operation="SELECT", query=queryCheckPKUser, params=(email))
    if user is None:
        raise ValueError(f"Invalid email: {email}")
    return user[0][0]
    

def createUser(email, countryCode, phoneNumber, firstName, lastName, gender, password, emailConfirmationStatus = "Unconfirmed", isDelete = False):
    """
    Creates a new user.
    Args:
        email (str): The email of the user.
        countryCode (str): The country code of the user's phone number.
        phoneNumber (str): The phone number of the user.
        firstName (str): The first name of the user.
        lastName (str): The last name of the user.
        gender (str): The gender of the user.
        password (str): The password of the user.
        emailConfirmationStatus (str): The email confirmation status of the user.
        isDelete (bool): The delete status of the user.
    Returns:
        int: The primary key of the newly created user.
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error creating the user.
    """
    try:
        # Validate Value
        validateEmail(email)
        validateCountryCode(countryCode)
        validatePhoneNumber(phoneNumber)
        validateString(firstName, "First name")
        validateString(lastName, "Last name")
        validateGender(gender)
        validatePassword(password)
        validateEmailConfirmationStatus(emailConfirmationStatus)
        validateBoolean(isDelete)
        # Check dupicate email from rdbms database
        checkDuplicateEmail(email)
        # Insert data to rdbms database)
        queryInsertUser = """
        SET NOCOUNT ON;
        DECLARE @InsertedUsers TABLE (pkUser INT);
        INSERT INTO marketsync.Users (email,isDelete)
        OUTPUT Inserted.pkUser INTO @InsertedUsers
        VALUES (?,?);
        SELECT pkUser FROM @InsertedUsers;
        """
        pkUser = queryMSSQL(operation="INSERT", query=queryInsertUser, params=(email,isDelete))[0]
        if pkUser is None:
            raise ValueError(f"Failed to create user: {email}")
        # Insert data to mongodb collection
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        # Hash password
        hashedPassword = hashPassword(password,str(pkUser))
        user = {
            "pkUser": int(pkUser),
            "email": email,
            "password": hashedPassword,
            "firstName": firstName,
            "lastName": lastName,
            "fullName": f"{firstName} {lastName}",
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
        print('Successfully created user account')
        return pkUser
    except Exception as error:
        print("Fail to create user :", error)
        logError(error=error, function=createUser.__name__, input= {
            "email": email,
            "countryCode": countryCode,
            "phoneNumber": phoneNumber,
            "firstName": firstName,
            "lastName": lastName,
            "gender": gender,
            "emailConfirmationStatus": emailConfirmationStatus,
            "isDelete": isDelete
        })
    finally:
        try:
            if 'client' in locals() and client is not None:
                client.close()
        except Exception as close_error:
            print(f"Error while closing MongoDB connection: {close_error}")

def confirmUserEmail(pkUser: int):
    """
    Confirms a user's email.
    Args:
        pkUser (int): The ID of the user to confirm.
    Returns:
        dict: The updated user document.
    Raises:
        ValueError: If the user ID is invalid.
        Exception: If there is an error confirming the user's email.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUserWithoutConfirm(pkUser)
        # Update data in mongodb collection
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        projection = {"_id": 1, "pkUser": 1, "email": 1, "emailConfirmationStatus": 1}
        user = collectionUsers.find_one({"pkUser": pkUser, "emailConfirmationStatus": "Unconfirmed"}, projection)
        if not user:
            print(f"No user found with pkUser: {pkUser}")
            return None
        # Update emailConfirmationStatus
        userId = user["_id"]  # Retrieve the unique _id
        updateResult = collectionUsers.update_one(
            {"_id": ObjectId(userId)},  # Filter by _id
            {"$set": {"emailConfirmationStatus": "Confirmed"}}  # Update action
        )
        if updateResult.modified_count == 1:
            print("Email confirmation status updated to 'Confirmed'.")
        else:
            print("Update failed or no changes made.")
        return user
    except Exception as error:
        print("Error to update user confirm status:", error)
        logError(error=error, function=confirmUserEmail.__name__, input= {
            "pkUser": pkUser
        })
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def updateUserAddress(pkUser: int,addressList):
    """
    Updates a user's address.
    Args:
        pkUser (int): The ID of the user to update.
        addressList (list): The new address list of the user.
    Returns:
        dict: The updated user document.
    Raises:
        ValueError: If the user ID is invalid.
        Exception: If there is an error updating the user's address.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Vaidate addressList
        # address = {
        #     "addressLine1": str,
        #     "addressLine2": str,
        #     "city": str,
        #     "state": str,
        #     "country": str,
        #     "zipCode": int,
        # }
        validateAddressList(addressList)
        # Update date to mongodb
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        updateResult = collectionUsers.update_one(
            {"pkUser": pkUser, "emailConfirmationStatus": "Confirmed", "isDelete": False},  # Filter
            {"$set": {"address": addressList, "updateDate": datetime.now()}}
        )
        if updateResult.matched_count == 0:
            print(f"No matching user found with pkUser: {pkUser}.")
            return None
        if updateResult.modified_count == 1:
            # Fetch and return the updated document
            updatedUser = collectionUsers.find_one({"pkUser": pkUser, "emailConfirmationStatus": "Confirmed", "isDelete": False}, {"_id": 1, "pkUser": 1, "address": 1, "emailConfirmationStatus": 1, "isDelete": 1})
            print("User successfully updated address:", updatedUser)
            return updatedUser
    except Exception as error:
        print("Fail to update user address:", error)
        logError(error=error, function=updateUserAddress.__name__, input= {
            "pkUser": pkUser,
            "addressList": addressList
        })
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    
def updateUserDetail(pkUser: int, countryCode, phoneNumber, firstName, lastName, gender, password):
    """
    Updates a user's details.
    Args:
        pkUser (int): The ID of the user to update.
        countryCode (str): The new country code of the user's phone number.
        phoneNumber (str): The new phone number of the user.
        firstName (str): The new first name of the user.
        lastName (str): The new last name of the user.
        gender (str): The new gender of the user.
        password (str): The new password of the user.
    Returns:
        dict: The updated user document.
    Raises:
        ValueError: If the user ID is invalid.
        Exception: If there is an error updating the user's details.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Vaidate input
        validateCountryCode(countryCode)
        validatePhoneNumber(phoneNumber)
        validateString(firstName, "First name")
        validateString(lastName, "Last name")
        validateGender(gender)
        validatePassword(password)
        # Hash password
        hashedPassword = hashPassword(password,str(pkUser))
        # Update data to mongodb
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        updateResult = collectionUsers.update_one(
            {"pkUser": pkUser, "emailConfirmationStatus": "Confirmed", "isDelete": False},  # Filter
            {"$set": {
                "countryCode": countryCode,
                "phoneNumber": phoneNumber,
                "firstName": firstName,
                "lastName": lastName,
                "fullName": f"{firstName} {lastName}",
                "gender": gender,
                "password": hashedPassword,
                "updateDate": datetime.now()
            }}
        )
        if updateResult.matched_count == 0:
            print(f"No matching user found with pkUser: {pkUser}.")
            return None
        if updateResult.modified_count == 1:
            # Fetch and return the updated document
            query = {"pkUser": pkUser, "emailConfirmationStatus": "Confirmed", "isDelete": False}
            projection = {"_id": 1, "pkUser": 1, "countryCode": 1, "phoneNumber": 1, "firstName": 1, "lastName": 1, "fullName": 1, "gender": 1, "emailConfirmationStatus": 1, "isDelete": 1}
            updatedUser = collectionUsers.find_one(query, projection)
            print("User successfully updated")
            return updatedUser
    except Exception as error:
        print("Fail to update user detail:", error)
        logError(error=error, function=updateUserDetail.__name__, input= {
            "pkUser": pkUser,
            "countryCode": countryCode,
            "phoneNumber": phoneNumber,
            "firstName": firstName,
            "lastName": lastName,
            "gender": gender
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def loginUser(email: str, password: str) -> str:
    """
    Logs in a user.
    Args:
        email (str): The email of the user.
        password (str): The password of the user.
    Returns:
        str: The login token of the user.
    Raises:
        ValueError: If the email or password is invalid.
        Exception: If there is an error logging in the user.
    """
    try:
        # Vaidate input
        validateEmail(email)
        validatePassword(password)
        # get pk user
        pkUser = getPKUserFromEmail(email)
        # Update login data to mongodb
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        query = {"email": email, "emailConfirmationStatus": "Confirmed", "isDelete": False}
        projection = {"_id": 1, "pkUser": 1, "password": 1}
        user = collectionUsers.find_one(query, projection)
        if not user:
            raise ValueError("User not found")
        if not comparePasswords(password, user['password'],str(pkUser)):
            raise ValueError("Invalid password")
        token = generateToken(email)
        collectionUsers.update_one({'_id': ObjectId(user['_id'])}, {'$set': {'loginToken': token, 'loginDate': datetime.now()}})
        print('User logged in and token updated')
        return token
    except Exception as error:
        print("Fail to login user:", error)
        logError(error=error, function=loginUser.__name__, input= {
            "email": email,
            "password": password
        })
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def validateToken(token: str) -> bool:
    """
    Validates a login token.
    Args:
        token (str): The token to validate.
    Returns:
        bool: True if the token is valid, False otherwise.
    Raises:
        ValueError: If the token is invalid.
        Exception: If there is an error validating the token.
    """
    try:
        # Vaidate input
        email = decodeAndValidateToken(token)
        validateEmail(email)
        # Update login data to mongodb
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        query = {"email": email, "emailConfirmationStatus": "Confirmed", "isDelete": False}
        projection = {"_id": 1, "pkUser": 1, "email": 1, "loginToken": 1}
        user = collectionUsers.find_one(query, projection)
        if not user:
            raise ValueError("User not found")
        elif user['loginToken'] == token:
            print('Token is valid :' + token)
            return True
        else:
            print('Token is invalid :' + token)
            return False
    except Exception as error:
        print("Fail to validate token:", error)
        logError(error=error, function=validateToken.__name__, input= {
            "token": token
        })
        return False
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()


def softDeleteUser(pkUser: int):
    """
    Deletes a user by setting its isDelete flag to True.
    Args:
        pkUser (int): The primary key of the user to delete.
    Returns:
        None
    Raises:
        ValueError: If the user ID is invalid.
        Exception: If there is an error deleting the user.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        queryCheckPKUser =  "UPDATE marketsync.Users SET isDelete = 1 WHERE pkUser = ?"
        queryMSSQL(operation="UPDATE", query=queryCheckPKUser, params=(pkUser))
        print("User soft deleted in rdbms database.")
        # MongoDB: Update isDelete flag to True
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        collectionUsers.update_one(
            {"pkUser": pkUser},
            {"$set": {"isDelete": True, "updateDate": datetime.now()}}
        )
        print("User soft deleted in mongodb database.")
    except Exception as error:
        print("Fail to delete user:", error)
        logError(error=error, function=softDeleteUser.__name__, input= {
            "pkUser": pkUser
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getUserByEmail(email: str):
    """
    Gets a user by their email.
    Args:
        email (str): The email of the user to get.
    Returns:
        dict: The user document.
    Raises:
        ValueError: If the email is invalid.
        Exception: If there is an error getting the user.
    """
    try:
        # Vaidate input
        validateEmail(email)
        # Update login data to mongodb
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        query = {"email": email, "emailConfirmationStatus": "Confirmed", "isDelete": False}
        projection = {"_id": 0, "pkUser": 1, "email": 1, "firstName": 1, "lastName": 1, "fullName": 1, "phoneCountryCode": 1, "phoneNumber": 1, "gender": 1, "address": 1, "cart": 1, "searchHistory": 1, "emailConfirmationStatus": 1, "loginToken": 1, "createDate": 1, "updateDate": 1, "isDelete": 1}
        user = collectionUsers.find_one(query, projection)
        if not user:
            raise ValueError("User not found")
        return user
    except Exception as error:
        print("Fail to get user by email:", error)
        logError(error=error, function=getUserByEmail.__name__, input= {
            "email": email
        })
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getUserByFullName(fullName: str):
    """
    Gets a user by their full name.
    Args:
        fullName (str): The full name of the user to get.
    Returns:
        dict: The user document.
    Raises:
        ValueError: If the full name is invalid.
        Exception: If there is an error getting the user.
    """
    try:
        # Vaidate input
        validateString(fullName, "Full name")
        # Update login data to mongodb
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        query = {"fullName": fullName, "emailConfirmationStatus": "Confirmed", "isDelete": False}
        projection = {"_id": 0, "pkUser": 1, "email": 1, "firstName": 1, "lastName": 1, "fullName": 1, "phoneCountryCode": 1, "phoneNumber": 1, "gender": 1, "address": 1, "cart": 1, "searchHistory": 1, "emailConfirmationStatus": 1, "loginToken": 1, "createDate": 1, "updateDate": 1, "isDelete": 1}
        user = collectionUsers.find_one(query, projection)
        if not user:
            raise ValueError("User not found")
        return user
    except Exception as error:
        print("Fail to get user by full name:", error)
        logError(error=error, function=getUserByFullName.__name__, input= {
            "fullName": fullName
        })
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def createUserSearchHistory(pkUser: int, keyword: str):
    """
    Creates a new search history for a user.
    Args:
        pkUser (int): The ID of the user to update.
        keyword (str): The keyword of the search history.
    Returns:
        dict: The updated user document.
    Raises:
        ValueError: If the user ID is invalid.
        Exception: If there is an error updating the user's search history.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Vaidate input
        validateSentence(keyword, "Keyword")
        # Update data to mongodb
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        searchHistory = {
            "keyword": keyword,
            "createDate": datetime.now()
        }
        updateResult = collectionUsers.update_one(
            {"pkUser": pkUser, "emailConfirmationStatus": "Confirmed", "isDelete": False},  # Filter
            {"$push": {"searchHistory": searchHistory}}
        )
        if updateResult.matched_count == 0:
            # not raise error because it can be annonymous user
            print(f"No matching user found with pkUser: {pkUser}.")
            return None
        if updateResult.modified_count == 1:
            # Fetch and return the updated document
            updatedUser = collectionUsers.find_one({"pkUser": pkUser, "emailConfirmationStatus": "Confirmed", "isDelete": False}, {"_id": 1, "pkUser": 1, "searchHistory": 1, "emailConfirmationStatus": 1, "isDelete": 1})
            print("User successfully updated search history:", updatedUser)
            return updatedUser
    except Exception as error:
        print("Fail to update user search history:", error)
        logError(error=error, function=createUserSearchHistory.__name__, input= {
            "pkUser": pkUser,
            "keyword": keyword
        })
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
##########################################################################################################
# Example
# Initial Example Data
# product data
productData = [
    {
        "name": "Slim Fit Chino Pants",
        "description": "Comfortable and stylish slim fit chino pants, perfect for any occasion.",
        "customize": ["S-Black", "M-Black", "L-Black", "XL-Black", "XXL-Black"],
        "price": 49.99,
        "category": "clothing - pants"
    },    {
        "name": "Cargo Pants with Multiple Pockets",
        "description": "Durable cargo pants with ample pocket space for all your essentials.",
        "customize": ["S-Green", "M-Green", "L-Green", "XL-Green", "XXL-Green"],
        "price": 59.99,
        "category": "clothing - pants"
    },
    {
        "name": "Classic Denim Jeans",
        "description": "A timeless classic, these denim jeans are a wardrobe staple.",
        "customize": ["S-Blue", "M-Blue", "L-Blue", "XL-Blue", "XXL-Blue"],
        "price": 69.99,
        "category": "clothing - pants"
    },
    {
        "name": "Relaxed Fit Linen Trousers",
        "description": "Lightweight and breathable linen trousers, ideal for warm weather.",
        "customize": ["S-Beige", "M-Beige", "L-Beige", "XL-Beige", "XXL-Beige"],
        "price": 54.99,
        "category": "clothing - pants"
    },
    {
        "name": "Jogger Sweatpants",
        "description": "Cozy and comfortable jogger sweatpants, perfect for lounging or working out.",
        "customize": ["S-Grey", "M-Grey", "L-Grey", "XL-Grey", "XXL-Grey"],
        "price": 39.99,
        "category": "clothing - pants"
    },
    {
        "name": "Tailored Dress Pants",
        "description": "Sharp and sophisticated tailored dress pants for formal occasions.",
        "customize": ["S-Navy", "M-Navy", "L-Navy", "XL-Navy", "XXL-Navy"],
        "price": 79.99,
        "category": "clothing - pants"
    },
    {
        "name": "Corduroy Pants",
        "description": "Stylish corduroy pants with a soft texture and comfortable fit.",
        "customize": ["S-Brown", "M-Brown", "L-Brown", "XL-Brown", "XXL-Brown"],
        "price": 54.99,
        "category": "clothing - pants"
    },
    {
        "name": "Straight Leg Khaki Pants",
        "description": "Versatile straight leg khaki pants, suitable for both casual and semi-formal settings.",
        "customize": ["S-Khaki", "M-Khaki", "L-Khaki", "XL-Khaki", "XXL-Khaki"],
        "price": 44.99,
        "category": "clothing - pants"
    },
    {
        "name": "Drawstring Waist Pants",
        "description": "Casual pants with a comfortable drawstring waist for an adjustable fit.",
        "customize": ["S-Olive", "M-Olive", "L-Olive", "XL-Olive", "XXL-Olive"],
        "price": 34.99,
        "category": "clothing - pants"
    },
    {
        "name": "Pleated Front Trousers",
        "description": "Elegant pleated front trousers, adding a touch of sophistication to your look.",
        "customize": ["S-Charcoal", "M-Charcoal", "L-Charcoal", "XL-Charcoal", "XXL-Charcoal"],
        "price": 64.99,
        "category": "clothing - pants"
    },
    {
        "name": "Graphic Print T-Shirt",
        "description": "Express your style with this eye-catching graphic print t-shirt.",
        "customize": ["S-White", "M-White", "L-White", "XL-White", "XXL-White"],
        "price": 24.99,
        "category": "clothing - shirt"
    },
    {
        "name": "Classic Polo Shirt",
        "description": "A timeless classic, the polo shirt is a versatile addition to any wardrobe.",
        "customize": ["S-Red", "M-Red", "L-Red", "XL-Red", "XXL-Red"],
        "price": 34.99,
        "category": "clothing - shirt"
    },
    {
        "name": "Long Sleeve Henley Shirt",
        "description": "Casual and comfortable long sleeve henley shirt, perfect for layering.",
        "customize": ["S-Blue", "M-Blue", "L-Blue", "XL-Blue", "XXL-Blue"],
        "price": 39.99,
        "category": "clothing - shirt"
    },
    {
        "name": "Button-Down Oxford Shirt",
        "description": "A crisp and clean button-down oxford shirt, ideal for business or casual wear.",
        "customize": ["S-LightBlue", "M-LightBlue", "L-LightBlue", "XL-LightBlue", "XXL-LightBlue"],
        "price": 44.99,
        "category": "clothing - shirt"
    },
    {
        "name": "Striped Crew Neck T-Shirt",
        "description": "A classic striped crew neck t-shirt, a versatile piece for any outfit.",
        "customize": ["S-BlackWhite", "M-BlackWhite", "L-BlackWhite", "XL-BlackWhite", "XXL-BlackWhite"],
        "price": 29.99,
        "category": "clothing - shirt"
    },
    {
        "name": "V-Neck T-Shirt",
        "description": "A simple yet stylish v-neck t-shirt, perfect for everyday wear.",
        "customize": ["S-Grey", "M-Grey", "L-Grey", "XL-Grey", "XXL-Grey"],
        "price": 22.99,
        "category": "clothing - shirt"
    },
    {
        "name": "Flannel Plaid Shirt",
        "description": "Cozy and warm flannel plaid shirt, great for colder weather.",
        "customize": ["S-RedBlack", "M-RedBlack", "L-RedBlack", "XL-RedBlack", "XXL-RedBlack"],
        "price": 49.99,
        "category": "clothing - shirt"
    },
    {
        "name": "Pocket Tee",
        "description": "A basic pocket tee, offering both comfort and practicality.",
        "customize": ["S-Navy", "M-Navy", "L-Navy", "XL-Navy", "XXL-Navy"],
        "price": 27.99,
        "category": "clothing - shirt"
    },
    {
        "name": "Short Sleeve Linen Shirt",
        "description": "Lightweight and breathable short sleeve linen shirt, perfect for summer.",
        "customize": ["S-Beige", "M-Beige", "L-Beige", "XL-Beige", "XXL-Beige"],
        "price": 37.99,
        "category": "clothing - shirt"
    },
    {
        "name": "Printed Camp Collar Shirt",
        "description": "A stylish printed camp collar shirt, great for a relaxed yet fashionable look.",
        "customize": ["S-Multi", "M-Multi", "L-Multi", "XL-Multi", "XXL-Multi"],
        "price": 42.99,
        "category": "clothing - shirt"
    },
    {
        "name": "Ankle Socks",
        "description": "Comfortable ankle socks, perfect for everyday wear.",
        "customize": ["S-White", "M-White", "L-White", "XL-White", "XXL-White"],
        "price": 9.99,
        "category": "clothing - socks"
    },
    {
        "name": "Crew Socks",
        "description": "Classic crew socks, a versatile choice for any outfit.",
        "customize": ["S-Black", "M-Black", "L-Black", "XL-Black", "XXL-Black"],
        "price": 12.99,
        "category": "clothing - socks"
    },
    {
        "name": "No-Show Socks",
        "description": "Invisible no-show socks, ideal for wearing with loafers or sneakers.",
        "customize": ["S-Beige", "M-Beige", "L-Beige", "XL-Beige", "XXL-Beige"],
        "price": 14.99,
        "category": "clothing - socks"
    },
    {
        "name": "Striped Dress Socks",
        "description": "Stylish striped dress socks, adding a touch of flair to formal attire.",
        "customize": ["S-NavyWhite", "M-NavyWhite", "L-NavyWhite", "XL-NavyWhite", "XXL-NavyWhite"],
        "price": 16.99,
        "category": "clothing - socks"
    },
    {
        "name": "Wool Blend Socks",
        "description": "Warm and cozy wool blend socks, perfect for colder weather.",
        "customize": ["S-Grey", "M-Grey", "L-Grey", "XL-Grey", "XXL-Grey"],
        "price": 19.99,
        "category": "clothing - socks"
    },
    {
        "name": "Athletic Performance Socks",
        "description": "Moisture-wicking athletic performance socks, designed for sports and workouts.",
        "customize": ["S-White", "M-White", "L-White", "XL-White", "XXL-White"],
        "price": 17.99,
        "category": "clothing - socks"
    },    {
        "name": "Patterned Socks",
        "description": "Fun and colorful patterned socks, perfect for adding personality to your outfit.",
        "customize": ["S-Multi", "M-Multi", "L-Multi", "XL-Multi", "XXL-Multi"],
        "price": 13.99,
        "category": "clothing - socks"
    },
    {
        "name": "Compression Socks",
        "description": "Supportive compression socks, ideal for improving circulation and reducing fatigue.",
        "customize": ["S-Black", "M-Black", "L-Black", "XL-Black", "XXL-Black"],
        "price": 24.99,
        "category": "clothing - socks"
    },
    {
        "name": "Knee-High Socks",
        "description": "Stylish knee-high socks, great for pairing with skirts or boots.",
        "customize": ["S-Black", "M-Black", "L-Black", "XL-Black", "XXL-Black"],
        "price": 18.99,
        "category": "clothing - socks"
    },
    {
        "name": "Thermal Socks",
        "description": "Extra warm thermal socks, perfect for keeping your feet cozy in cold weather.",
        "customize": ["S-Grey", "M-Grey", "L-Grey", "XL-Grey", "XXL-Grey"],
        "price": 21.99,
        "category": "clothing - socks"
    },
    {
        "name": "Cotton Briefs",
        "description": "Classic cotton briefs, providing comfort and support for everyday wear.",
        "customize": ["S-White", "M-White", "L-White", "XL-White", "XXL-White"],
        "price": 14.99,
        "category": "clothing - undergarment"
    },
    {
        "name": "Boxer Shorts",
        "description": "Relaxed fit boxer shorts, offering comfort and breathability.",
        "customize": ["S-Blue", "M-Blue", "L-Blue", "XL-Blue", "XXL-Blue"],
        "price": 16.99,
        "category": "clothing - undergarment"
    },
    {
        "name": "Boxer Briefs",
        "description": "Supportive boxer briefs, combining the best of both boxers and briefs.",
        "customize": ["S-Black", "M-Black", "L-Black", "XL-Black", "XXL-Black"],
        "price": 18.99,
        "category": "clothing - undergarment"
    },
    {
        "name": "Trunks",
        "description": "Modern and stylish trunks, offering a snug and comfortable fit.",
        "customize": ["S-Grey", "M-Grey", "L-Grey", "XL-Grey", "XXL-Grey"],
        "price": 20.99,
        "category": "clothing - undergarment"
    },
    {
        "name": "Low-Rise Briefs",
        "description": "Low-rise briefs, designed for a modern and sleek look.",
        "customize": ["S-White", "M-White", "L-White","XL-White", "XXL-White"],
        "price": 15.99,
        "category": "clothing - undergarment"
    },
    {
        "name": "Seamless Underwear",
        "description": "Invisible seamless underwear, perfect for wearing under tight-fitting clothes.",
        "customize": ["S-Beige", "M-Beige", "L-Beige", "XL-Beige", "XXL-Beige"],
        "price": 22.99,
        "category": "clothing - undergarment"
    },
    {
        "name": "Moisture-Wicking Underwear",
        "description": "Moisture-wicking underwear, designed to keep you dry and comfortable.",
        "customize": ["S-Black", "M-Black", "L-Black", "XL-Black", "XXL-Black"],
        "price": 21.99,
        "category": "clothing - undergarment"
    },
    {
        "name": "Silk Boxer Shorts",
        "description": "Luxurious silk boxer shorts, offering a soft and smooth feel.",
        "customize": ["S-Navy", "M-Navy", "L-Navy", "XL-Navy", "XXL-Navy"],
        "price": 34.99,
        "category": "clothing - undergarment"
    },
    {
        "name": "Thermal Underwear",
        "description": "Warm thermal underwear, perfect for layering in cold weather.",
        "customize": ["S-Grey", "M-Grey", "L-Grey", "XL-Grey", "XXL-Grey"],
        "price": 29.99,
        "category": "clothing - undergarment"
    },
    {
        "name": "Athletic Underwear",
        "description": "Supportive athletic underwear, designed for sports and workouts.",
        "customize": ["S-White", "M-White", "L-White", "XL-White", "XXL-White"],
        "price": 26.99,
        "category": "clothing - undergarment"
    }
]

def simulate():
    # create users
    email = "@example01.com"
    users = []
    for i in range(20):
        # use index to create ascii a-z for name
        firstName = 'firstname'+chr(ord('A') + i % 26)
        lastName = 'lastname'+chr(ord('a') + i % 26)
        user = createUser(f"user{i}" + email, "+44", f"0777777777{i}", firstName, lastName, "Male", "password123")
        users.append(user)
    print(user)
    # confirm all email
    for user in users:
        confirmUserEmail(user)
    # update user address
    addressList = [
        {
            "addressLine1": "123 Main St",
            "addressLine2": "Apt 4B",
            "city": "Anytown",
            "state": "CA",
            "country": "USA",
            "zipCode": 12345,
        },
        {
            "addressLine1": "456 Oak Ave",
            "addressLine2": "Unit 10",
            "city": "Springfield",
            "state": "IL",
            "country": "USA",
            "zipCode": 67890,
        },
    ]
    updateUserAddress(users[0], addressList)
    # update user detail
    updateUserDetail(users[0], "+44", "07777777770", "firstnameA", "lastnamea", "Male", "newpassword123")
    # login user
    token = loginUser("user0" + email, "newpassword123")
    print(token)
    # validate token
    validateToken(token)
    # soft delete user
    softDeleteUser(users[10])
    # create shop
    shops = []
    for i in range(5):
        shop = createShop(users[i], f"Shop{i}")
        shops.append(shop)
    print(shops)
    # create group of product and add product to product group
    productGroups = []
    products = []
    for i in range(len(productData)):
        productGroup = createProductGroup(shops[i % 5], productData[i]["name"], productData[i]["description"], "image.png", [productData[i]["category"]])
        print(productGroup)
        productGroups.append(productGroup)
        for customize in productData[i]["customize"]:
            product = createProductToProductGroup(productGroup, f"{productData[i]['name']} - {customize}", f"{productData[i]['description']} - {customize}", "image1.jpg", productData[i]["price"])
            products.append(product)
    print(productGroups)
    print(products)
    # User add product to their cart
    addProductToCart(users[0], products[0], 1)
    addProductToCart(users[0], products[1], 2)
    addProductToCart(users[0], products[2], 3)
    addProductToCart(users[0], products[3], 4)
    addProductToCart(users[0], products[4], 5)
    # use cart to make transaction
    pkTransaction = cartToPayment(users[0])
    print(pkTransaction)
    # use pktransaction change transaction status to complete
    changeTransactionStatus(pkTransaction, "Wait for payment")
    changeTransactionStatus(pkTransaction, "Completed")
    # create logistic
    deliveryDate = datetime.now() + timedelta(days=7)
    pkLogistic = createLogistic(pkTransaction, deliveryDate)
    # change logistic status to 'complete'
    changeLogisticStatus(pkLogistic, "Shipping")
    changeLogisticStatus(pkLogistic, "Delivered")
    # create 10 message between user and shop
    for i in range(10):
        if i % 2 == 0:
            sendUserMessageToShop(users[0], shops[0], f"Hello Shop1, this is user1 message {i}")
        else:
            sendShopMessageToUser(users[0], shops[0], f"Hello User1, this is shop1 message {i}")
    # get message
    message = getMessageBetweenUserAndShop(users[0], shops[0])
    print(message)
    # search
    searchResult = searchProduct("pants")
    for products in searchResult:
        for product in products["product"]: 
            print(product["productName"])
            print(product["productDescription"])
    # create user search history
    createUserSearchHistory(users[0], "pants")
    createUserSearchHistory(users[0], "jeans")
    createUserSearchHistory(users[0], "trousers")
    # get user recommendation product
    getUserRecommendations(users[0],10)
    # get transaction history
    transactionHistory = getProductGroupTransactionHistory(productGroups[0])
    print(transactionHistory)
    # t.pkTransaction, t.createDate, t.totalPrice, t.fkUserBuyer, tp.quantity, tp.price, p.productName
    # get transaction history
    transactionHistory = getProductTransactionHistory(products[0])
    print(transactionHistory)
    # t.pkTransaction, t.createDate, t.totalPrice, t.fkUserBuyer, tp.quantity, tp.price, p.productName
    # update shop name
    updateShopName(shops[0], "New Shop Name")
    # soft delete shop
    softDeleteShop(shops[1])
    # delete product
    deleteProductGroup(productGroups[2])
    # update product
    updateProductToProductGroup(productGroups[0], products[0], "New Product Name", "New Product Description", "newimage.jpg", 99.99)
    # delete product from product group
    deleteProductFromProductGroup(productGroups[0], products[1])
    # get user by email
    user = getUserByEmail("user0"+email)
    print(user)
    # get user by full name
    user = getUserByFullName("firstnameA lastnamea")
    
simulate()

from datetime import datetime
import sys
import os
# Object for mongodb
from bson.objectid import ObjectId
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import queryMSSQL, getMongoConnection
from ValidatorUtils import validateEmail, validateCountryCode, validatePhoneNumber, validateString, validateSentence, validateGender, validatePassword, validateEmailConfirmationStatus, validateBoolean, validateAddressList
from SecurityUtils import hashPassword, comparePasswords, generateToken, decodeAndValidateToken
from Logger import logError

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
            "email": email
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
            
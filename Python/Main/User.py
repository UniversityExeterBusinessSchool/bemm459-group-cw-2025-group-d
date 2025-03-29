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

def validatePKUser(pkUser: int):
    queryCheckPKUser =  "SELECT pkuser FROM marketsync.v_users WHERE pkuser = ?"
    user = queryMSSQL(operation="SELECT", query=queryCheckPKUser, params=(pkUser))
    if user is None:
        raise ValueError(f"Invalid pkUser: {pkUser}")

def checkDuplicateEmail(email):
    queryCheckDuplicateEmail =  "SELECT pkuser FROM marketsync.v_users WHERE email = ?"
    pkUser = queryMSSQL(operation="SELECT", query=queryCheckDuplicateEmail, params=(email))
    if pkUser:
        raise ValueError(f"Duplicate email: {email}")

def createUser(email, countryCode, phoneNumber, firstName, lastName, gender, password, emailConfirmationStatus = "Unconfirmed", isDelete = False):
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
        # Hash password
        hashedPassword = hashPassword(password)
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
        return None
    finally:
        try:
            if 'client' in locals() and client is not None:
                client.close()
        except Exception as close_error:
            print(f"Error while closing MongoDB connection: {close_error}")

def confirmUserEmail(pkUser: int):
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
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
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def updateUserAddress(pkUser: int,addressList):
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
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    
def updateUserDetail(pkUser: int, countryCode, phoneNumber, firstName, lastName, gender, password):
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
        hashedPassword = hashPassword(password)
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
            print("User successfully updated detail:", updatedUser)
            return updatedUser
    except Exception as error:
        print("Fail to update user detail:", error)
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def loginUser(email: str, password: str) -> str:
    try:
        # Vaidate input
        validateEmail(email)
        validatePassword(password)
        # Update login data to mongodb
        client,dbname = getMongoConnection()
        collectionUsers = client[dbname]['Users']
        query = {"email": email, "emailConfirmationStatus": "Confirmed", "isDelete": False}
        projection = {"_id": 1, "pkUser": 1, "password": 1}
        user = collectionUsers.find_one(query, projection)
        if not user:
            raise ValueError("User not found")
        if not comparePasswords(password, user['password']):
            raise ValueError("Invalid password")
        token = generateToken(email)
        collectionUsers.update_one({'_id': ObjectId(user['_id'])}, {'$set': {'loginToken': token, 'loginDate': datetime.now()}})
        print('User logged in and token updated')
        return token
    except Exception as error:
        print("Fail to login user:", error)
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def validateToken(token: str) -> bool:
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
            raise ValueError("Invalid token")
    except Exception as error:
        print("Fail to validate token:", error)
        return False
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()


def softDeleteUser(pkUser: int):
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getUserByEmail(email: str):
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
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getUserByFullName(fullName: str):
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
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def createUserSearchHistory(pkUser: int, keyword: str):
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
        return None
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
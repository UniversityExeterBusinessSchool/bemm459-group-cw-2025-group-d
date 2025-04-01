from datetime import datetime
import sys
import os
# Object for mongodb
from bson.objectid import ObjectId
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import getMongoConnection
from Logger import logError
from User import validatePKUser
from Shop import validatePKShop
from Product import validatePKProduct

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
            
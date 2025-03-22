from datetime import datetime
import sys
import os
# Object for mongodb
from bson.objectid import ObjectId
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import getMongoConnection
from User import validatePKUser
from Shop import validatePKShop
from Product import validatePKProduct

def getAllMessageRelateToUser(pkUser):
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Get data from mongodb
        client = getMongoConnection()
        collectionMessage = client['Messages']
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getMessageBetweenUserAndShop(pkUserBuyer, pkShop):
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUserBuyer)
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # Get data from mongodb
        client = getMongoConnection()
        collectionMessage = client['Messages']
        # Check if product already in cart
        message = collectionMessage.find_one({"pkUserBuyer": pkUserBuyer, "pkShop": pkShop})
        if message is None:
            print("Message not found")
            return None
        return message
    except Exception as error:
        print("Fail to get message:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def sendUserMessageToShop(pkUser, pkShop, message):
    from datetime import datetime
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # Get data from mongodb
        client = getMongoConnection()
        collectionMessage = client['Messages']
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def sendShopMessageToUser(pkUser, pkShop, message):
    from datetime import datetime
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # Get data from mongodb
        client = getMongoConnection()
        collectionMessage = client['Messages']
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    
def userReviewProduct(fkUser,fkProduct,review):
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Check if product exist in rdbms database
        validatePKProduct(fkProduct)
        # Get data from mongodb
        client = getMongoConnection()
        collectionProduct = client['Products']
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
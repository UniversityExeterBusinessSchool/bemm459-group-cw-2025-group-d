import sys, os, datetime
from bson.objectid import ObjectId
from pymongo import ReturnDocument

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def addMessageBetweenUserAndSeller(pkUserBuyer, pkShop, message_content):
    """
    Sends a message between a user and a seller.
    - If a chat document for the given buyer and shop exists, appends the new message.
    - Otherwise, creates a new chat document.
    """
    client = getMongoConnection()
    db = client["marketsync"]
    messages_coll = db["Messages"]
    current_time = datetime.datetime.now()
    new_message = {
        "message": message_content,
        "createDate": current_time,
        "updateDate": current_time,
        "isDelete": False
    }
    
    # Check if chat exists.
    chat_doc = messages_coll.find_one({"pkUserBuyer": pkUserBuyer, "pkShop": pkShop})
    if chat_doc:
        result = messages_coll.find_one_and_update(
            {"_id": chat_doc["_id"]},
            {"$push": {"chat": new_message}},
            return_document=ReturnDocument.AFTER
        )
        print("Message added to existing chat.")
        return result
    else:
        new_chat = {
            "pkUserBuyer": pkUserBuyer,
            "pkShop": pkShop,
            "chat": [new_message]
        }
        insert_result = messages_coll.insert_one(new_chat)
        print("New chat created and message added. Chat ID:", insert_result.inserted_id)
        return new_chat

if __name__ == "__main__":
    # Example usage: buyer id 1, shop id 10.
    addMessageBetweenUserAndSeller(1, 10, "Hello, I am interested in your product.")

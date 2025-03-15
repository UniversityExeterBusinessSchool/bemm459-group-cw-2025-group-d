import sys, os, datetime
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def deleteMessageBetweenUserAndSeller(chat_id, message_create_date):
    """
    Unsend a message by updating its isDelete flag to True.
    The message is identified by its createDate.
    """
    client = getMongoConnection()
    db = client["marketsync"]
    messages_coll = db["Messages"]
    new_time = datetime.datetime.now()
    
    result = messages_coll.update_one(
        {"_id": ObjectId(chat_id), "chat.createDate": message_create_date},
        {"$set": {"chat.$.isDelete": True, "chat.$.updateDate": new_time}}
    )
    if result.modified_count:
        print("Message unsent (flag updated).")
    else:
        print("No matching message found to unsend.")
    return result.modified_count

if __name__ == "__main__":
    # Example usage: replace with a valid chat_id and message create date.
    example_chat_id = "60d5f4832f8fb814b56fa181"
    example_message_create_date = datetime.datetime(2025, 3, 13, 12, 0, 0)
    deleteMessageBetweenUserAndSeller(example_chat_id, example_message_create_date)

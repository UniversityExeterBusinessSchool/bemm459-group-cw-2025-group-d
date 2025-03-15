import sys, os, datetime
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def getMessagesBetweenUserAndSeller(chat_id):
    """
    Retrieves the messages for a given chat (by chat_id) sorted from newest to oldest.
    """
    client = getMongoConnection()
    db = client["marketsync"]
    messages_coll = db["Messages"]
    
    chat_doc = messages_coll.find_one({"_id": ObjectId(chat_id)})
    if not chat_doc:
        print("Chat not found")
        return []
    
    chat_messages = chat_doc.get("chat", [])
    sorted_messages = sorted(
        chat_messages,
        key=lambda x: x.get("updateDate", datetime.datetime.min),
        reverse=True
    )
    return sorted_messages

if __name__ == "__main__":
    # Replace with a valid chat_id from your database.
    example_chat_id = "60d5f4832f8fb814b56fa181"
    messages = getMessagesBetweenUserAndSeller(example_chat_id)
    for msg in messages:
        print(msg)

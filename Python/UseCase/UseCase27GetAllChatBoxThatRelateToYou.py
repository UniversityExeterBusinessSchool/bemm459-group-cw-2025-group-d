import sys, os, datetime
from bson.objectid import ObjectId

# Add paths for Library and ResultObject
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ResultObject')))

from databaseConnection import getMongoConnection
from MSSQLConnection import query_mssql
from ResultObjectChatBox import ChatBox

def get_last_update(chat_array):
    """Helper to compute the last update date from a list of chat messages."""
    if not chat_array:
        return datetime.datetime.min
    return max(msg.get("updateDate", datetime.datetime.min) for msg in chat_array)

def getAllChatBoxThatRelateToYou(user_id):
    """
    Retrieves all chat boxes related to the given user.
      - As buyer: chats where 'pkUserBuyer' equals the user_id.
      - As seller: chats where 'pkShop' is among shops owned by the user (queried from SQL).
    Returns a list of ChatBox objects sorted by newest update.
    """
    client = getMongoConnection()
    db = client["marketsync"]
    messages_coll = db["Messages"]

    # Get chats where the user is the buyer.
    buyer_chats = list(messages_coll.find({"pkUserBuyer": user_id}))
    
    # Query MSSQL to get the shops that belong to the user.
    sql_query = "SELECT pkShop FROM Shops WHERE fkUser = ? AND isDelete = 0;"
    rows = query_mssql("SELECT", sql_query, (user_id,))
    seller_shop_ids = [row[0] for row in rows] if rows else []
    
    # Get chats where the user is the seller (by shop).
    seller_chats = []
    if seller_shop_ids:
        seller_chats = list(messages_coll.find({"pkShop": {"$in": seller_shop_ids}}))
    
    # Combine and deduplicate chats by _id.
    all_chats = buyer_chats + seller_chats
    seen_ids = set()
    unique_chats = []
    for chat in all_chats:
        cid = str(chat.get("_id"))
        if cid not in seen_ids:
            seen_ids.add(cid)
            unique_chats.append(chat)
    
    # Compute last update from the chat array and sort descending.
    for chat in unique_chats:
        chat["lastUpdate"] = get_last_update(chat.get("chat", []))
    unique_chats.sort(key=lambda x: x.get("lastUpdate", datetime.datetime.min), reverse=True)
    
    # Convert each chat document into a ChatBox result object.
    result = []
    for chat in unique_chats:
        cb = ChatBox(
            chat_id=str(chat.get("_id")),
            buyer=chat.get("pkUserBuyer"),
            shop=chat.get("pkShop"),
            last_update=chat.get("lastUpdate"),
            messages=chat.get("chat")
        )
        result.append(cb)
    return result

if __name__ == "__main__":
    # Example usage for user with ID 1.
    chat_boxes = getAllChatBoxThatRelateToYou(1)
    for cb in chat_boxes:
        print(cb)

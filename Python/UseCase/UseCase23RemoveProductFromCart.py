import sys, os
from pymongo import ReturnDocument
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def removeProductFromCart(userEmail, productId):
    """
    Remove the specified product from the user's cart.
    """
    client = getMongoConnection()
    db = client["marketsync"]
    users_coll = db["Users"]
    result = users_coll.find_one_and_update(
        {"email": userEmail},
        {"$pull": {"cart": {"productId": productId}}},
        return_document=ReturnDocument.AFTER
    )
    print("Updated cart:", result.get("cart", []))
    return result

if __name__ == "__main__":
    removeProductFromCart("test3@gmail.com", 201)

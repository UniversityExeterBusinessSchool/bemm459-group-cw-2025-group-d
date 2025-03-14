import sys, os
from datetime import datetime
from pymongo import ReturnDocument
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def addProductToCart(userEmail, productId, pkProduct, quantity, price):
    """
    Add a product to the user's cart.
    """
    client = getMongoConnection()
    db = client["marketsync"]
    users_coll = db["Users"]
    cart_item = {
        "productId": productId,
        "pkProduct": pkProduct,
        "quantity": quantity,
        "price": price,
        "addedDate": datetime.now()
    }
    result = users_coll.find_one_and_update(
        {"email": userEmail, "isDelete": False},
        {"$push": {"cart": cart_item}},
        return_document=ReturnDocument.AFTER
    )
    print("Updated cart:", result.get("cart", []))
    return result

if __name__ == "__main__":
    addProductToCart("test3@gmail.com", 201, 101, 2, 99.99)

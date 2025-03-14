import sys, os
from pymongo import ReturnDocument
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def editProductInCart(userEmail, productId, newQuantity):
    """
    Change the quantity of a product in the user's cart.
    """
    client = getMongoConnection()
    db = client["marketsync"]
    users_coll = db["Users"]
    result = users_coll.find_one_and_update(
        {"email": userEmail, "cart.productId": productId},
        {"$set": {"cart.$.quantity": newQuantity}},
        return_document=ReturnDocument.AFTER
    )
    print("Updated cart:", result.get("cart", []))
    return result

if __name__ == "__main__":
    editProductInCart("test3@gmail.com", 201, 5)

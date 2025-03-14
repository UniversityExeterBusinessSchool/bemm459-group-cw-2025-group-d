import sys, os
from datetime import datetime
from pymongo import ReturnDocument
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from MSSQLConnection import query_mssql
from databaseConnection import getMongoConnection

def cartToPayment(userEmail, deliveryDate):
    """
    Process the user's cart:
      1. Create a transaction record in SQL (using MSSQL).
      2. Update product sold counters in MongoDB.
      3. Clear the cart.
    """
    # Step 1: Get the cart from MongoDB.
    client = getMongoConnection()
    db = client["marketsync"]
    users_coll = db["Users"]
    user = users_coll.find_one({"email": userEmail, "isDelete": False})
    if not user or not user.get("cart"):
        print("Cart is empty or user not found.")
        return
    cart_items = user["cart"]
    total_price = sum(item["quantity"] * item["price"] for item in cart_items)
    # For demonstration, we use dummy fkUserBuyer and fkShop values.
    fkUserBuyer = 1
    fkShop = 1
    transaction_query = """
    INSERT INTO Transactions (price, currency, fkUserBuyer, fkShop, createDate, updateDate, isDelete)
    OUTPUT INSERTED.pkTransaction
    VALUES (?, 'USD', ?, ?, GETDATE(), GETDATE(), 0);
    """
    transaction_result = query_mssql("INSERT", transaction_query, (total_price, fkUserBuyer, fkShop))
    print("Transaction created with ID:", transaction_result)
    
    # Step 2: Update soldAmount for each product in MongoDB.
    prod_coll = db["Products"]
    for item in cart_items:
        prod_coll.update_many(
            {"product.pkProduct": item["pkProduct"]},
            {"$inc": {"soldAmount": item["quantity"]}}
        )
    
    # Step 3: Clear the user's cart.
    updated_user = users_coll.find_one_and_update(
        {"email": userEmail},
        {"$set": {"cart": []}},
        return_document=ReturnDocument.AFTER
    )
    print("Cart cleared for user. Updated cart:", updated_user.get("cart", []))
    return transaction_result

if __name__ == "__main__":
    cartToPayment("test3@gmail.com", datetime(2025, 4, 15))

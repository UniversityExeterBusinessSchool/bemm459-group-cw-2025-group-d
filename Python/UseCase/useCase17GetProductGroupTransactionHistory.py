import sys
import os
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def getProductGroupTransactionHistory(productGroupId):
    client = getMongoConnection()
    db = client['marketsync']
    # Retrieve the product group document
    productGroup = db['Products'].find_one({"_id": ObjectId(productGroupId), "isDelete": False})
    if not productGroup:
        print("Product group not found or has been deleted.")
        return None
    # Extract active product keys
    product_keys = [prod["pkProduct"] for prod in productGroup.get("product", []) if not prod.get("isDelete", False)]
    
    # Query the Transactions collection using these product keys
    transactions = list(db['Transactions'].find({"pkProduct": {"$in": product_keys}}))
    print("Transactions for product group:", transactions)
    return transactions

if __name__ == "__main__":
    getProductGroupTransactionHistory("60d5f4832f8fb814b56fa181")

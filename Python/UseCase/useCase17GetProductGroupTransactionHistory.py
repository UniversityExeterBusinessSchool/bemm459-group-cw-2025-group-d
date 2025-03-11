import sys
import os
from bson.objectid import ObjectId
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def getProductGroupTransactionHistory(productGroupId):
    """
    Retrieve the transaction history for all products in a given product group.
    Assumes that a MongoDB collection "Transactions" exists with a field "pkProduct".
    :param productGroupId: The _id of the product group document.
    :return: A list of transaction documents.
    """
    client = getMongoConnection()
    db = client.get_default_database()
    collectionProducts = db['Products']
    collectionTransactions = db['Transactions']  # This collection must exist.
    
    # Retrieve the product group document.
    productGroup = collectionProducts.find_one({"_id": ObjectId(productGroupId), "isDelete": False})
    if not productGroup:
        print(f"Product group {productGroupId} not found or is deleted.")
        return []
    
    # Extract non-deleted product keys.
    productKeys = [p["pkProduct"] for p in productGroup.get("product", []) if not p.get("isDelete", False)]
    
    # Find transactions for any of these products.
    transactions = list(collectionTransactions.find({"pkProduct": { "$in": productKeys }}))
    for txn in transactions:
        print(txn)
    return transactions

# Example usage:
if __name__ == '__main__':
    getProductGroupTransactionHistory("603d2c1e3b1a4f2a6c8a9d7e")

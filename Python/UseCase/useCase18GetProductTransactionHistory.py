import sys
import os
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def getProductTransactionHistory(pkProduct):
    client = getMongoConnection()
    db = client['marketsync']
    transactions = list(db['Transactions'].find({"pkProduct": pkProduct}))
    print("Transactions for product:", transactions)
    return transactions

if __name__ == "__main__":
    getProductTransactionHistory(101)

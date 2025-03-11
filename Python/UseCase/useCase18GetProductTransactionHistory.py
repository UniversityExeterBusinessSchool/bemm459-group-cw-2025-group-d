import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def getProductTransactionHistory(pkProduct):
    """
    Retrieve transaction history for a specific product.
    Assumes that a MongoDB collection "Transactions" exists with a field "pkProduct".
    :param pkProduct: The product key to search for.
    :return: A list of transaction documents.
    """
    client = getMongoConnection()
    db = client.get_default_database()
    collectionTransactions = db['Transactions']  # This collection must exist.
    
    transactions = list(collectionTransactions.find({"pkProduct": pkProduct}))
    for txn in transactions:
        print(txn)
    return transactions

# Example usage:
if __name__ == '__main__':
    getProductTransactionHistory(101)

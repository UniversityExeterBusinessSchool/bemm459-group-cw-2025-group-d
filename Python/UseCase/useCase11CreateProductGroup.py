import sys
import os
from datetime import datetime

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def createProductGroup(pkShop, shopName, groupName, groupDescription, productImagePath, productCategory):
    client = getMongoConnection()
    db = client['marketsync']
    collection = db['Products']
    productGroup = {
        "pkShop": pkShop,
        "shopName": shopName,
        "productName": groupName,             # product group name
        "productDescription": groupDescription, # description for the group
        "productImagePath": productImagePath,   # image path as string
        "productCategory": productCategory,     # list of categories
        "soldAmount": 0,
        "product": [],                          # initially empty list of products
        "reviews": [],
        "createDate": datetime.now(),
        "updateDate": datetime.now(),
        "isDelete": False
    }
    result = collection.insert_one(productGroup)
    print("Product group created with id:", result.inserted_id)
    return result.inserted_id

if __name__ == "__main__":
    # Example usage:
    createProductGroup(1, "Test Shop", "Electronics", "Group for electronic products", "path/to/image.jpg", ["Gadgets", "Devices"])

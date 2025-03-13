import sys
import os
from datetime import datetime
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def addProductToGroup(productGroupId, pkProduct, productName, productDescription, productImagePath, productPrice, stock):
    client = getMongoConnection()
    db = client['marketsync']
    collection = db['Products']
    newProduct = {
        "pkProduct": pkProduct,
        "productName": productName,
        "productDescription": productDescription,
        "productImagePath": productImagePath,  # expects a list of image paths
        "productPrice": productPrice,
        "stock": stock,
        "soldAmount": 0,
        "createDate": datetime.now(),
        "updateDate": datetime.now(),
        "isDelete": False
    }
    result = collection.update_one({"_id": ObjectId(productGroupId)}, {"$push": {"product": newProduct}})
    print("Product added to group. Modified count:", result.modified_count)
    return result.modified_count

if __name__ == "__main__":
    addProductToGroup("60d5f4832f8fb814b56fa181", 101, "New Product", "Product description", ["path/to/product.jpg"], 99.99, 10)

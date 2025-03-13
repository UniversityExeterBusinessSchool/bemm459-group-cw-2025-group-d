import sys
import os
from datetime import datetime
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def updateProductInGroup(productGroupId, pkProduct, updatedFields):
    client = getMongoConnection()
    db = client['marketsync']
    collection = db['Products']
    # Ensure the updateDate is refreshed for the product
    updatedFields["updateDate"] = datetime.now()
    # Use the positional operator to update the matched product within the array
    updateSpec = {f"product.$.{key}": value for key, value in updatedFields.items()}
    result = collection.update_one(
        {"_id": ObjectId(productGroupId), "product.pkProduct": pkProduct},
        {"$set": updateSpec}
    )
    print("Product updated in group. Matched:", result.matched_count, "Modified:", result.modified_count)
    return result.modified_count

if __name__ == "__main__":
    updateProductInGroup("60d5f4832f8fb814b56fa181", 101, {"productName": "Updated Product Name", "stock": 20})

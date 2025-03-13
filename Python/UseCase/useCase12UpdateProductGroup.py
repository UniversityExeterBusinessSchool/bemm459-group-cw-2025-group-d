import sys
import os
from datetime import datetime
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def updateProductGroup(productGroupId, updatedFields):
    client = getMongoConnection()
    db = client['marketsync']
    collection = db['Products']
    # Set updateDate automatically
    updatedFields["updateDate"] = datetime.now()
    result = collection.update_one({"_id": ObjectId(productGroupId)}, {"$set": updatedFields})
    print("Product group updated. Matched:", result.matched_count, "Modified:", result.modified_count)
    return result.modified_count

if __name__ == "__main__":
    # Example: Update group name and description
    updateProductGroup("60d5f4832f8fb814b56fa181", {"productName": "Updated Group Name", "productDescription": "Updated description"})

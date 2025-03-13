import sys
import os
from datetime import datetime
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def deleteProductGroup(productGroupId):
    client = getMongoConnection()
    db = client['marketsync']
    collection = db['Products']
    result = collection.update_one(
        {"_id": ObjectId(productGroupId)},
        {"$set": {"isDelete": True, "updateDate": datetime.now()}}
    )
    print("Product group soft-deleted. Matched:", result.matched_count, "Modified:", result.modified_count)
    return result.modified_count

if __name__ == "__main__":
    deleteProductGroup("60d5f4832f8fb814b56fa181")

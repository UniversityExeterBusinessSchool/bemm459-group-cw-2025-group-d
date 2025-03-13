import sys
import os
from datetime import datetime
from bson.objectid import ObjectId

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def deleteProductFromGroup(productGroupId, pkProduct):
    client = getMongoConnection()
    db = client['marketsync']
    collection = db['Products']
    # Soft delete the product (set isDelete flag to True)
    result = collection.update_one(
        {"_id": ObjectId(productGroupId), "product.pkProduct": pkProduct},
        {"$set": {"product.$.isDelete": True, "product.$.updateDate": datetime.now()}}
    )
    print("Product soft-deleted from group. Matched:", result.matched_count, "Modified:", result.modified_count)
    return result.modified_count

if __name__ == "__main__":
    deleteProductFromGroup("60d5f4832f8fb814b56fa181", 101)

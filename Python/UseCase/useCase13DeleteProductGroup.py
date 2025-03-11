import sys
import os
from datetime import datetime
from bson.objectid import ObjectId
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def deleteProductGroup(productGroupId):
    """
    Mark a product group as deleted in MongoDB.
    :param productGroupId: The _id of the product group document.
    """
    client = getMongoConnection()
    db = client.get_default_database()
    collectionProducts = db['Products']
    result = collectionProducts.update_one(
        { "_id": ObjectId(productGroupId) },
        { "$set": { "isDelete": True, "updateDate": datetime.now() } }
    )
    print(f"Product group {productGroupId} marked as deleted. Matched: {result.matched_count}, Modified: {result.modified_count}")
    return result

# Example usage:
if __name__ == '__main__':
    deleteProductGroup("603d2c1e3b1a4f2a6c8a9d7e")

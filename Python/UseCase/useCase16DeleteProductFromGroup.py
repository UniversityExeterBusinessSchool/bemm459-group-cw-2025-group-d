import sys
import os
from datetime import datetime
from bson.objectid import ObjectId
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def deleteProductFromGroup(productGroupId, pkProduct):
    """
    Mark a product in the product group as deleted (set isDelete flag).
    :param productGroupId: The _id of the product group document.
    :param pkProduct: The product's unique key to mark as deleted.
    """
    client = getMongoConnection()
    db = client.get_default_database()
    collectionProducts = db['Products']
    result = collectionProducts.update_one(
        { "_id": ObjectId(productGroupId), "product.pkProduct": pkProduct },
        { "$set": { "product.$.isDelete": True, "product.$.updateDate": datetime.now() } }
    )
    print(f"Product with pkProduct {pkProduct} in product group {productGroupId} marked as deleted. Matched: {result.matched_count}, Modified: {result.modified_count}")
    return result

# Example usage:
if __name__ == '__main__':
    deleteProductFromGroup("603d2c1e3b1a4f2a6c8a9d7e", 101)

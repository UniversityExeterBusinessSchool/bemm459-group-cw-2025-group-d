import sys
import os
from datetime import datetime
from bson.objectid import ObjectId
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def updateProductGroup(productGroupId, updateData):
    """
    Update fields of a product group in MongoDB.
    :param productGroupId: The _id of the product group document.
    :param updateData: A dictionary of fields to update.
    """
    client = getMongoConnection()
    db = client.get_default_database()
    collectionProducts = db['Products']
    # Add/update the updateDate field
    updateData['updateDate'] = datetime.now()
    result = collectionProducts.update_one(
        { "_id": ObjectId(productGroupId) },
        { "$set": updateData }
    )
    print(f"Product group {productGroupId} updated. Matched: {result.matched_count}, Modified: {result.modified_count}")
    return result

# Example usage:
if __name__ == '__main__':
    # Replace with an actual ObjectId string from your MongoDB
    updateProductGroup("603d2c1e3b1a4f2a6c8a9d7e", {"productName": "Updated Group Name", "productDescription": "Updated description"})

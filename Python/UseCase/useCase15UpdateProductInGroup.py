import sys
import os
from datetime import datetime
from bson.objectid import ObjectId
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def updateProductInGroup(productGroupId, pkProduct, updateData):
    """
    Update a specific product within a product group.
    :param productGroupId: The _id of the product group document.
    :param pkProduct: The product's unique key (from RDBMS) in the product array.
    :param updateData: A dictionary of product fields to update.
    """
    client = getMongoConnection()
    db = client.get_default_database()
    collectionProducts = db['Products']
    # Prepare update fields by prefixing with "product.$." for the matched array element.
    setFields = { f"product.$.{k}": v for k, v in updateData.items() }
    setFields["product.$.updateDate"] = datetime.now()
    
    result = collectionProducts.update_one(
        { "_id": ObjectId(productGroupId), "product.pkProduct": pkProduct },
        { "$set": setFields }
    )
    print(f"Product with pkProduct {pkProduct} in product group {productGroupId} updated. Matched: {result.matched_count}, Modified: {result.modified_count}")
    return result

# Example usage:
if __name__ == '__main__':
    updateProductInGroup("603d2c1e3b1a4f2a6c8a9d7e", 101, {"productName": "Updated Product Name", "stock": 45})

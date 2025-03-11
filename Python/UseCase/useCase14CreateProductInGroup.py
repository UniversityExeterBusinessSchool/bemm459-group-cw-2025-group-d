import sys
import os
from datetime import datetime
from bson.objectid import ObjectId
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def createProductInGroup(productGroupId, productData):
    """
    Add a new product to the product group document.
    :param productGroupId: The _id of the product group document.
    :param productData: A dictionary with product details (must include pkProduct, productName, productDescription, productImagePath,
                        productPrice, stock, soldAmount).
    """
    client = getMongoConnection()
    db = client.get_default_database()
    collectionProducts = db['Products']
    
    # Set default fields for the product
    productData['createDate'] = datetime.now()
    productData['updateDate'] = datetime.now()
    productData['isDelete'] = False
    
    result = collectionProducts.update_one(
        { "_id": ObjectId(productGroupId) },
        { "$push": { "product": productData },
          "$set": { "updateDate": datetime.now() } }
    )
    print(f"Product added to product group {productGroupId}. Modified count: {result.modified_count}")
    return result

# Example usage:
if __name__ == '__main__':
    sampleProduct = {
        "pkProduct": 101,
        "productName": "New Product",
        "productDescription": "Description of new product",
        "productImagePath": ["path/to/image1.jpg", "path/to/image2.jpg"],
        "productPrice": 99.99,
        "stock": 50,
        "soldAmount": 0
    }
    createProductInGroup("603d2c1e3b1a4f2a6c8a9d7e", sampleProduct)

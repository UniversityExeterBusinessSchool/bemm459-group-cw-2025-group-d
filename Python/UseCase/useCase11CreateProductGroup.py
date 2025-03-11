import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def createProductGroup(pkShop, shopName, groupName, description, imagePath, productCategory):
    """
    Create a new product group (i.e. a product document) for a shop in MongoDB.
    :param pkShop: The shop's primary key from SQL.
    :param shopName: The shop's name.
    :param groupName: Name of the product group.
    :param description: Description of the group.
    :param imagePath: Image path (or URL) for the group.
    :param productCategory: List of categories for the group.
    :return: The inserted document's _id.
    """
    client = getMongoConnection()
    db = client.get_default_database()
    collectionProducts = db['Products']
    productGroup = {
        "pkShop": pkShop,
        "shopName": shopName,
        "productName": groupName,  # Using productName field for group name
        "productDescription": description,
        "productImagePath": imagePath,
        "productCategory": productCategory,
        "soldAmount": 0,
        "product": [],       # Initially empty list of products
        "reviews": [],
        "createDate": datetime.now(),
        "updateDate": datetime.now(),
        "isDelete": False
    }
    result = collectionProducts.insert_one(productGroup)
    print(f"Product group created with _id: {result.inserted_id}")
    return result.inserted_id

# Example usage:
if __name__ == '__main__':
    createProductGroup(1, "Test Shop", "Electronics", "Group for electronic products", "path/to/image.jpg", ["Gadgets", "Devices"])

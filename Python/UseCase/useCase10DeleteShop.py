import sys
import os
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import queryPostgreSQL, getMongoConnection

def deleteShop(shopId):
    """
    Mark a shop (in SQL) and its related product group documents (in MongoDB) as deleted.
    :param shopId: The shop's primary key.
    """
    # Update related product groups (and their product items) in MongoDB
    client = getMongoConnection()
    # Use the default database (or specify env.mongoDB_database explicitly)
    db = client.get_default_database()
    collectionProducts = db['Products']
    
    # Update all product groups for this shop: set isDelete to True and update nested product items as well
    result_mongo = collectionProducts.update_many(
        { "pkShop": shopId, "isDelete": False },
        { "$set": { "isDelete": True, "updateDate": datetime.now(), "product.$[].isDelete": True } }
    )
    print(f"MongoDB: Updated {result_mongo.modified_count} product group(s) for shop {shopId}")
    
    # Update the shop record in SQL
    query = f"UPDATE marketsync.Shops SET isDelete = TRUE WHERE pkShop = {shopId}"
    queryPostgreSQL("UPDATE", query)
    print(f"SQL: Shop with pkShop {shopId} marked as deleted")

# Example usage:
if __name__ == '__main__':
    deleteShop(1)

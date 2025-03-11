import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import queryPostgreSQL

def updateShopName(shopId, newShopName):
    """
    Update the name of an existing shop.
    :param shopId: The shop's primary key.
    :param newShopName: The new shop name.
    """
    query = f"UPDATE marketsync.Shops SET shopName = '{newShopName}' WHERE pkShop = {shopId}"
    queryPostgreSQL("UPDATE", query)
    print(f"Shop with pkShop {shopId} updated to new name: {newShopName}")

# Example usage:
if __name__ == '__main__':
    updateShopName(1, "Updated Shop Name")

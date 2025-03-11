import sys
import os
# Add Library path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import queryPostgreSQL

def createShop(shopName, fkUser):
    """
    Create a new shop in SQL.
    :param shopName: Name of the shop.
    :param fkUser: Owner's user ID (foreign key to Users table).
    :return: The newly created shop's primary key (pkShop).
    """
    query = f"INSERT INTO marketsync.Shops (shopName, fkUser) VALUES ('{shopName}', {fkUser}) RETURNING pkShop"
    result = queryPostgreSQL("INSERT", query)
    shop_id = result[0] if result else None
    print(f"Shop created with pkShop: {shop_id}")
    return shop_id

# Example usage:
if __name__ == '__main__':
    # Replace with valid values as needed
    createShop("Test Shop", 1)
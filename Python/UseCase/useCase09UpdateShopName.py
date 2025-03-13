import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from MSSQLConnection import query_mssql

def updateShopName(shopId, newName):
    query = """
    UPDATE Shops
    SET shopName = ?, updateDate = GETDATE()
    WHERE pkShop = ? AND isDelete = 0;
    """
    result = query_mssql("UPDATE", query, (newName, shopId))
    print("Shop updated.")
    return result

if __name__ == "__main__":
    # Example usage:
    updateShopName(1, "Updated Shop Name")


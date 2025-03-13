import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from MSSQLConnection import query_mssql

def deleteShop(shopId):
    # Soft-delete (update isDelete flag) for all related products first
    query_products = """
    UPDATE Products
    SET isDelete = 1, updateDate = GETDATE()
    WHERE fkShop = ?;
    """
    query_mssql("UPDATE", query_products, (shopId,))
    
    # Soft-delete the shop record itself
    query_shop = """
    UPDATE Shops
    SET isDelete = 1, updateDate = GETDATE()
    WHERE pkShop = ?;
    """
    result = query_mssql("UPDATE", query_shop, (shopId,))
    print("Shop and its products have been soft-deleted.")
    return result

if __name__ == "__main__":
    # Example usage:
    deleteShop(1)


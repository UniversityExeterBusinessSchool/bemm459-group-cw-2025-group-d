
import sys
import os
from datetime import datetime

# Add Library folder to path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from MSSQLConnection import query_mssql

def createShop(shopName, fkUser):
    # T-SQL: Insert new shop and return inserted identity value.
    # Note: In SQL Server you can use an OUTPUT clause or SCOPE_IDENTITY().
    query = """
    INSERT INTO Shops (shopName, fkUser, createDate, updateDate, isDelete)
    OUTPUT INSERTED.pkShop
    VALUES (?, ?, GETDATE(), GETDATE(), 0);
    """
    result = query_mssql("INSERT", query, (shopName, fkUser))
    print("Shop created with ID:", result)
    return result

if __name__ == "__main__":
    # Example usage:
    createShop("Test Shop", 1)

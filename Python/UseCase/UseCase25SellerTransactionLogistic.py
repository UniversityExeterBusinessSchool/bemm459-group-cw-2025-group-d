import sys, os
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from MSSQLConnection import query_mssql

def sellerChangeTransactionAndCreateLogistic(transactionId, newStatus, fkShop, fkUserBuyer):
    """
    1. Update the transaction status in SQL.
    2. Create a logistic record in SQL.
    """
    # Update transaction status in TransactionStates table (assumed to be used for status tracking).
    update_status_query = """
    UPDATE TransactionStates
    SET transactionStatus = ?, updateDate = GETDATE()
    WHERE fkTransaction = ?;
    """
    query_mssql("UPDATE", update_status_query, (newStatus, transactionId))
    print("Transaction status updated.")
    
    # Create a logistic record.
    logistic_query = """
    INSERT INTO Logistics (fkShop, fkUserBuyer, fkTransaction, createDate, updateDate, isDelete)
    OUTPUT INSERTED.pkLogistic
    VALUES (?, ?, ?, GETDATE(), GETDATE(), 0);
    """
    logistic_result = query_mssql("INSERT", logistic_query, (fkShop, fkUserBuyer, transactionId))
    print("Logistic record created with ID:", logistic_result)
    return logistic_result

if __name__ == "__main__":
    sellerChangeTransactionAndCreateLogistic(1, "Shipped", 1, 1)

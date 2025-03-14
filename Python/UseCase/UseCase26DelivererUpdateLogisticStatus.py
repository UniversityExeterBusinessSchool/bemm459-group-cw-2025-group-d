import sys, os
from datetime import datetime
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from MSSQLConnection import query_mssql

def delivererUpdateLogisticStatus(logisticId, newStatus):
    """
    Update the logistic status in SQL.
    """
    update_query = """
    UPDATE LogisticStates
    SET logisticStatus = ?, updateDate = GETDATE()
    WHERE fkLogistic = ?;
    """
    result = query_mssql("UPDATE", update_query, (newStatus, logisticId))
    print("Logistic status updated for logistic ID:", logisticId)
    return result

if __name__ == "__main__":
    delivererUpdateLogisticStatus(1, "Delivered")

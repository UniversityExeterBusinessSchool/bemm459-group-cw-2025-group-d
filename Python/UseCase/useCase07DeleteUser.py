from datetime import datetime
import sys
import os
# regular expression
import re
# Object for mongodb
from bson.objectid import ObjectId
# # Add the parent directory (Project) to sys.path
# # Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))

from DatabaseConnection import getMongoConnection
def softDeleteUser(user_id: int) -> bool:
    try:
        # MSSQL: Update isDelete flag to 1
        mssql_query = f"UPDATE marketsync.Users SET isDelete = 1 WHERE pkUser = {user_id}"
        queryMSSQL("UPDATE", mssql_query)
        print("User soft deleted in MSSQL.")
        
        # MongoDB: Update isDelete flag to True
        client = getMongoConnection()
        collectionUsers = client['Users']
        result = collectionUsers.update_one(
            {"pkUser": user_id},
            {"$set": {"isDelete": True}}
        )
        
        if result.modified_count > 0:
            print("User soft deleted in MongoDB.")
        else:
            print("User not found or already soft deleted in MongoDB.")
            return False

        return True

    except Exception as error:
        print("Error soft deleting user:", str(error))
        return False

    finally:
        if client:
            client.close()

# Example usage
if __name__ == "__main__":
    user_id = 1  # Replace with the actual user ID
    softDeleteUser(user_id)
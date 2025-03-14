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

def hardDeleteUser(pkUser: int) -> bool:
    try:
        # MSSQL: Remove the user record
        mssql_query = f"DELETE FROM marketsync.Users WHERE pkUser = {pkUser}"
        queryMSSQL("DELETE", mssql_query)
        print("User hard deleted in MSSQL.")
        
        # MongoDB: Remove the user document
        client = getMongoConnection()
        collectionUsers = client['Users']
        result = collectionUsers.delete_one({"pkUser": pkUser})
        
        if result.deleted_count > 0:
            print("User hard deleted in MongoDB.")
        else:
            print("User not found in MongoDB.")
            return False

        return True

    except Exception as error:
        print("Error hard deleting user:", str(error))
        return False

    finally:
        if client:
            client.close()

# Example usage
if __name__ == "__main__":
    user_id = 1  # Replace with the actual user ID
    hardDeleteUser(user_id)

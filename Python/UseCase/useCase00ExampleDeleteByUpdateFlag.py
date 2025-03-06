import sys
import os
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import queryMSSQL
# ResultObject file

# Function to update a user
# Use case: Update the position of an existing user.
def deleteUserByFlag(user_id):
    query = f"UPDATE marketsync.users SET isDelete = 'FALSE' WHERE id = {user_id}"
    result = queryMSSQL("UPDATE", query)
    print(result)
    return result
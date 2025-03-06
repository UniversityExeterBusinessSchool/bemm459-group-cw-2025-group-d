import sys
import os
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import queryMSSQL

# Function to delete a user
# Use case: Delete an existing user from the users table.
def deleteUser(user_id):
    query = f"DELETE FROM marketsync.users WHERE id = {user_id}"
    result = queryMSSQL("DELETE", query)
    print(result)
    return result
import sys
import os
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import queryPostgreSQL, queryFunctionPostgreSQL
# ResultObject file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ResultObject')))
from resultObject00Example import Example00Query, Example00Result

# Function to delete a user
# Use case: Delete an existing user from the users table.
def deleteUser(user_id):
    query = f"DELETE FROM marketsync.users WHERE id = {user_id}"
    result = queryPostgreSQL("DELETE", query)
    print(result)
    return result
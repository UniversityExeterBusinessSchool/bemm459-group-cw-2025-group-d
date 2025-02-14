import sys
import os
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import queryPostgreSQL, queryFunctionPostgreSQL
# ResultObject file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ResultObject')))
from resultObject00Example import Example00Query, Example00Result

# Function to update a user
# Use case: Update the position of an existing user.
def deleteUserByFlag(user_id):
    query = f"UPDATE marketsync.users SET isDelete = 'FALSE' WHERE id = {user_id}"
    result = queryPostgreSQL("UPDATE", query)
    print(result)
    return result
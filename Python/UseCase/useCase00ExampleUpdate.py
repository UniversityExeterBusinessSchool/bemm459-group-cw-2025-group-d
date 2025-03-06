import sys
import os
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import queryMSSQL

# Function to update a user
# Use case: Update the email of an existing user.
def updateUser(user_id, email):
    query = f"UPDATE marketsync.users SET email = '{email}' WHERE id = {user_id}"
    result = queryMSSQL("UPDATE", query)
    print(result)
    return result
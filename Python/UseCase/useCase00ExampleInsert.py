import sys
import os
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import queryMSSQL

# Function to insert a user
# Use case: Add a new user to the users table.
def insertUser(user_id, name, position):
    query = f"INSERT INTO marketsync.users (id, name, position) VALUES ({user_id}, '{name}', '{position}')"
    result = queryMSSQL("INSERT", query)
    print(result)
    return result

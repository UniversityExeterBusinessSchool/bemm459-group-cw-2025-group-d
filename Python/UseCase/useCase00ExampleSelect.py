import sys
import os
# Add the parent directory (Project) to sys.path
# Env file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# import env file
import env
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import queryPostgreSQL, queryFunctionPostgreSQL, getMongoConnection
# ResultObject file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../ResultObject')))
from resultObject00Example import Example00Query, Example00Result

# at each function you need to descripe use case of that function 

# first way to get user
def getUser1():
    query = "SELECT * FROM marketsync.users"
    result = queryPostgreSQL("SELECT", query)
    print(result)
    return result

# second way to get user
def getUser2():
    # Object from ResultObject/resultObject00Example
    funcationParameter = Example00Query("SELECT * FROM marketsync.users")
    def functionQuery(cursor,postgres_connection,funcationParameter):
        cursor.execute(funcationParameter.query)
        # Commit the transaction
        records = cursor.fetchall()
        return records
    result = queryFunctionPostgreSQL(functionQuery,funcationParameter)
    print(result)
    return result

# run the function
# getUser1()
# getUser2()

def getUserMongo():
    client = getMongoConnection()
    db = client[env.mongoDB_database]
    collectionUsers = db['Users']
    # collectionProducts = db['Products']
    users = collectionUsers.find()  # Get all documents in the collection
    for user in users:
        print(user)
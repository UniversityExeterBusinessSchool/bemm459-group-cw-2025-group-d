# import connection from file in Python/Libary/DatabaseConnection
# from Library.DatabaseConnection import queryPostGreSQL, queryFunctionPostGreSQL
# import result object from file in Python/ResultObject/00_exampleObject.py
# from ResultObject.00_exampleObject import exampleObject

# at each function you need to descripe use case of that function 

# first way to get user
# def getUser1():
#     query = "SELECT * FROM marketsync.users"
#     result = queryPostGreSQL("SELECT", query)
#     print(result)
#     return result

# second way to get user
# def getUser2():
#     return null

# run the function
# getUser1()
# getUser2()

import sys
import os

# Add the parent directory (Project) to sys.path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Now, you can import your module
import env
import Library.DatabaseConnection



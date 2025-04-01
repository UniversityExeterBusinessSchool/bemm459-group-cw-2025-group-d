import sys
import os
# Add the parent directory (Project) to sys.path
# ENV file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
# MSSQL connection
import pyodbc
# MongoDB connection
from pymongo import MongoClient
from pymongo.database import Database as MongoDatabase
# import env file
import env
from typing import Literal

def queryMSSQL(operation: Literal["SELECT", "INSERT", "UPDATE", "DELETE"], query: str, params: tuple = ()):
    """
    Execute a SQL query on the MSSQL database.
    Args:
        operation (Literal["SELECT", "INSERT", "UPDATE", "DELETE"]): The type of SQL operation.
        query (str): The SQL query string.
        params (tuple, optional): Parameters for the SQL query. Defaults to ().
    Raises:
        Exception: If any error occurs during the database operation.
    Returns:
        list or None: The result of the query if it's a SELECT operation, otherwise None.
    """
    mssql_connection = None
    cursor = None
    try:
        mssql_connection = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=' + env.mssql_server + ',' + str(env.mssql_port) + ';'
            'DATABASE=' + env.mssql_database + ';'
            'UID=' + env.mssql_user + ';'
            'PWD=' + env.mssql_password
        )
        cursor = mssql_connection.cursor()
        cursor.execute(query, params)
        if operation == "SELECT":
            records = cursor.fetchall()
            return records
        elif operation == "INSERT":
            row = cursor.fetchone()
            mssql_connection.commit()
            return row
        elif operation == "INSERT_WITHOUT_FETCH":
            mssql_connection.commit()
        elif operation in ["UPDATE", "DELETE"]:
            mssql_connection.commit()
    except Exception as error:
        print("MSSQL Error:" + str(error))
        raise
    finally:
        if cursor is not None:
            cursor.close()
        if mssql_connection is not None:
            mssql_connection.close()

def queryFunctionMSSQL(functionQuery, functionParameter):
    """
    Execute a SQL function on the MSSQL database.
    Args:
        functionQuery (str): The SQL function query string.
        functionParameter (tuple, optional): Parameters for the SQL function.
    Raises:
        Exception: If any error occurs during the database operation.
    Returns:
        list or None: The result of the query if it's a SELECT operation, otherwise None.
    """
    try:
        mssql_connection = pyodbc.connect(
            'DRIVER={SQL Server};'
            'SERVER=' + env.mssql_server + ';'
            'DATABASE=' + env.mssql_database + ';'
            'UID=' + env.mssql_user + ';'
            'PWD=' + env.mssql_password
        )
        cursor = mssql_connection.cursor()
        result = functionQuery(cursor=cursor, mssql_connection=mssql_connection, functionParameter=functionParameter)
        return result
    except Exception as error:
        print("MSSQL Error:" + str(error))
        raise
    finally:
        # Closing the database connection
        if mssql_connection:
            cursor.close()
            mssql_connection.close()

# MongoDB connection
def getMongoConnection() -> MongoDatabase:
    """
    Establish a connection to the MongoDB database.
    Raises:
        Exception: If any error occurs during the database operation.
    Returns:
        MongoDatabase: The MongoDB database object.
    """
    try:
        mongo_connection = MongoClient(
            host = env.mongoDB_host,
            port = env.mongoDB_port,
            username = env.mongoDB_username,
            password = env.mongoDB_password
        )
        client = mongo_connection
        return client, env.mongoDB_database
    except Exception as error:
        print("MongoDB Error:" + str(error))
        raise
    finally:
        pass
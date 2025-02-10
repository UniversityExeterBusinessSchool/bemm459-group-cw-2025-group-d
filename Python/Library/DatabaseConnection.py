import sys
import os
# Add the parent directory (Project) to sys.path
# ENV file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# PostgreSQL connection
import psycopg2
# Redis connection
import redis
# MongoDB connection
# from pymongo import MongoClient
# ElasticSearch connection
# from elasticsearch import Elasticsearch
import env
from typing import Literal, Callable, Any

# PostgreSQL connection
def queryPostgreSQL(operation: Literal["SELECT", "INSERT", "UPDATE", "DELETE"], query: str):
    try:
        postgres_connection = psycopg2.connect(
            host=env.postgreSQL_host,
            port=env.postgreSQL_port,
            database=env.postgreSQL_database,
            user=env.postgreSQL_user,
            password=env.postgreSQL_password
        )
        cursor = postgres_connection.cursor()
        if operation == "SELECT":
            # Executing the SQL query
            cursor.execute(query)
            # Fetching all rows from the executed query
            records = cursor.fetchall()
            return records
        elif operation == "INSERT":
            # Execute insert query
            cursor.execute(query)
            # Fetch inserted data
            row = cursor.fetchone()
            # Commit the transaction
            postgres_connection.commit()
            return row
        elif operation == "UPDATE":
            # Execute update query
            cursor.execute(query)
            # Commit the transaction
            postgres_connection.commit()
        elif operation == "DELETE":
            # Execute delete query
            cursor.execute(query)
            # Commit the transaction
            postgres_connection.commit()
        else:
            raise ValueError("Invalid operation type")
            
    except Exception as error:
        print("PostgreSQL Error:" + str(error))
    finally:
        # Closing the database connection
        if postgres_connection:
            cursor.close()
            postgres_connection.close()
            print("PostgreSQL connection is closed")


def queryFunctionPostgreSQL(functionQuery,functionParameter):
    try:
        postgres_connection = psycopg2.connect(
            host=env.postgreSQL_host,
            port=env.postgreSQL_port,
            database=env.postgreSQL_database,
            user=env.postgreSQL_user,
            password=env.postgreSQL_password
        )
        cursor = postgres_connection.cursor()
        result = functionQuery(cursor = cursor,postgres_connection = postgres_connection,functionParameter = functionParameter)
        return result
    except Exception as error:
        print("PostgreSQL Error:" + str(error))
    finally:
        # Closing the database connection
        if postgres_connection:
            cursor.close()
            postgres_connection.close()
            print("PostgreSQL connection is closed")

# Redis connection
# redis_connection = redis.StrictRedis(
#     host='localhost',
#     port=10002,
#     password='marketsyncpassword',
#     decode_responses=True
# )
# print("Connected to Redis")

# MongoDB connection
# mongo_connection = MongoClient(
#     'localhost',
#     10003,
#     username='system_admin',
#     password='marketsyncpassword'
# )
# print("Connected to MongoDB")

# Elasticsearch connection
# es_connection = Elasticsearch(
#     ['http://localhost:10004'],
#     http_auth=('elastic', 'marketsyncpassword')
# )
# print("Connected to Elasticsearch")
from datetime import datetime
import sys
import os
# regular expression
import re
# Object for mongodb
from bson.objectid import ObjectId
# jwt
import jwt
import bcrypt
from datetime import datetime, timedelta
# Add the parent directory (Project) to sys.path
# ENV file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import env
# # Add the parent directory (Project) to sys.path
# # Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import getMongoConnection

SECRET_KEY = env.jwt_secret

def validateToken(email: str, token: str) -> bool:
    try:
        # Decode the token
        decoded = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        
        # Check if the email from the token matches the provided email
        if decoded['email'] != email:
            print("Email mismatch")
            return False
        
        # Establish MongoDB connection
        client = getMongoConnection()
        collectionUsers = client['Users']
        
        # Find the user by email
        user = collectionUsers.find_one({'email': email})
        if not user:
            print("User not found")
            return False
        
        # Check if the token from the frontend matches the token in the backend
        if user['loginToken'] != token:
            print("Token mismatch")
            return False
        
        # Check if the token has expired
        endDate = datetime.fromisoformat(decoded['endDate'])
        if endDate < datetime.utcnow():
            print("Token has expired")
            return False
        
        # Additional validation checks can be added here
        print("Token is valid")
        return True

    except jwt.ExpiredSignatureError:
        print("Token has expired")
        return False
    except jwt.InvalidTokenError:
        print("Invalid token")
        return False

    finally:
        client.close()

# Example usage
if __name__ == "__main__":
    email = "example@example.com"
    token = "your_jwt_token_here"
    isValid = validateToken(email, token)
    print("Is token valid?", isValid)
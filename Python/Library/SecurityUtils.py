
import sys
import os
# Hash Library
import hashlib
# JSON Web token
import jwt
# Datetime
from datetime import datetime, timedelta
# Add the parent directory (Project) to sys.path
# ENV file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
import env
SECRET_KEY = env.jwt_secret

def hashPassword(password):
    hashObject = hashlib.sha256()
    hashObject.update(password.encode('utf-8'))
    hashedPassword = hashObject.hexdigest()
    return hashedPassword

def comparePasswords(inputPassword, storedHashedPassword):
    hashedInputPassword = hashPassword(inputPassword)
    return hashedInputPassword == storedHashedPassword

class TokenExpiredError(Exception):
    pass

class InvalidTokenError(Exception):
    pass

def generateToken(email: str) -> str:
    createDate = datetime.now()
    endDate = createDate + timedelta(hours=1)
    payload = {
        'email': email,
        'createDate': createDate.isoformat(),
        'endDate': endDate.isoformat()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

def decodeAndValidateToken(token: str) -> str:
    try:
        # Decode the token
        decodedPayload = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
        # Extract the email and endDate
        email = decodedPayload.get('email')
        endDate = datetime.fromisoformat(decodedPayload.get('endDate'))
        # Check if the token is still valid
        if datetime.now() > endDate:
            raise TokenExpiredError("Token has expired")
        # Return the email if valid
        return email
    except jwt.ExpiredSignatureError:
        raise TokenExpiredError("Token signature has expired")
    except jwt.InvalidTokenError:
        raise InvalidTokenError("Invalid token")
    except Exception as e:
        raise InvalidTokenError(f"Token validation failed: {str(e)}")
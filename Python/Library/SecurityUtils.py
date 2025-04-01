
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

def hashPassword(password :str,salt :str):
    """
    Hashes a password using SHA256 with a salt.
    Args:
        password (str): The password to hash.
        salt (str): The salt to use for hashing.
    Returns:
        str: The hashed password.
    """
    saltedPassword = password + salt
    hashObject = hashlib.sha256()
    hashObject.update(saltedPassword.encode('utf-8'))
    hashedPassword = hashObject.hexdigest()
    return hashedPassword

def comparePasswords(inputPassword, storedHashedPassword, salt):
    """
    Compares an input password with a stored hashed password using a salt.
    Args:
        inputPassword (str): The password to compare.
        storedHashedPassword (str): The stored hashed password.
        salt (str): The salt used for hashing.
    Returns:
        bool: True if the passwords match, False otherwise.
    """
    hashedInputPassword = hashPassword(inputPassword, salt)
    return hashedInputPassword == storedHashedPassword

def generateToken(email: str) -> str:
    """
    Generates a JWT token for a given email.
    Args:
        email (str): The email to include in the token.
    Returns:
        str: The generated JWT token.
    """
    createDate = datetime.now()
    endDate = createDate + timedelta(hours=1)
    payload = {
        'email': email,
        'createDate': createDate.isoformat(),
        'endDate': endDate.isoformat()
    }
    token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')
    return token

class TokenExpiredError(Exception):
    """
    Exception raised when a token has expired.
    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="Token has expired"):
        self.message = message
        super().__init__(self.message)
        
    pass

class InvalidTokenError(Exception):
    """
    Exception raised when an invalid token is encountered.
    Attributes:
        message (str): Explanation of the error.
    """
    def __init__(self, message="Invalid token"):
        self.message = message
        super().__init__(self.message)

def decodeAndValidateToken(token: str) -> str:
    """
    Decodes and validates a JWT token.
    Args:
        token (str): The JWT token to decode and validate.
    Raises:
        TokenExpiredError: If the token has expired.
        InvalidTokenError: If the token is invalid.
    Returns:
        str: The email associated with the token if it's valid.
    """
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
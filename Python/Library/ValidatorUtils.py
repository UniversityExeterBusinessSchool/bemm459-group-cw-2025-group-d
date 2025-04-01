# Regular Expression
import re

def validateNotNull(value, fieldName):
    """
    Validates that a given value is not null or empty.
    Args:
        value: The value to validate.
        fieldName: The name of the field being validated.
    Raises:
        ValueError: If the value is null or empty.
    """
    if not value:
        raise ValueError(f"{fieldName} must not be null or empty.")

def validateMaxLength(value, fieldName, maxLength=200):
    """
    Validates that a given value does not exceed a specified maximum length.
    Args:
        value: The value to validate.
        fieldName: The name of the field being validated.
        maxLength: The maximum allowed length.
    Raises:
        ValueError: If the value exceeds the maximum length.
    """
    if len(value) > maxLength:
        raise ValueError(f"{fieldName} must not exceed {maxLength} characters.")

def validateEmail(email):
    """
    Validates that a given email address is in a valid format.
    Args:
        email (str): The email address to validate.
    Raises:
        ValueError: If the email is not in a valid format.
    """
    validateNotNull(email, "Email")
    validateMaxLength(email, "Email")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email address: {email}")

def validateCountryCode(countryCode):
    """
    Validates that a given country code is in a valid format.
    Args:
        countryCode (str): The country code to validate.
    Raises:
        ValueError: If the country code is not in a valid format.
    """
    validateNotNull(countryCode, "Country code")
    validateMaxLength(countryCode, "Country code")
    if not (countryCode.startswith("+") and countryCode[1:].isdigit() and 1 <= len(countryCode[1:]) <= 3):
        raise ValueError(f"Invalid country code: {countryCode}")

def validatePhoneNumber(phoneNumber):
    """
    Validates that a given phone number is in a valid format.
    Args:
        phoneNumber (str): The phone number to validate.
    Raises:
        ValueError: If the phone number is not in a valid format.
    """
    validateNotNull(phoneNumber, "Phone number")
    validateMaxLength(phoneNumber, "Phone number")
    if not phoneNumber.isdigit():
        raise ValueError(f"Invalid phone number: {phoneNumber}")

def validateString(string, fieldName):
    """
    Validates that a given string is in a valid format.
    Args:
        string (str): The string to validate.
        fieldName (str): The name of the field being validated.
    Raises:
        ValueError: If the string is not in a valid format.
    """
    validateNotNull(string, fieldName)
    validateMaxLength(string, fieldName)
    # pattern string can contain number
    pattern = r'^[a-zA-Z0-9\s]+$'
    if not re.match(pattern, string):
        raise ValueError(f"Invalid {fieldName}: {string}")
    
def validateSentence(string, fieldName):
    """
    Validates that a given sentence is in a valid format.
    Args:
        string (str): The sentence to validate.
        fieldName (str): The name of the field being validated.
    Raises:
        ValueError: If the sentence is not in a valid format.
    """
    validateNotNull(string, fieldName)
    validateMaxLength(string, fieldName)
    pattern = r'^[a-zA-Z0-9\s.,!?;:\'"-]+$'
    if not re.match(pattern, string):
        raise ValueError(f"Invalid {fieldName}: {string}")
    
def validateStringList(stringList, fieldName):
    """
    Validates that a given list of strings is in a valid format.
    Args:
        stringList (list): The list of strings to validate.
        fieldName (str): The name of the field being validated.
    Raises:
        ValueError: If the list or any of its strings are not in a valid format.
    """
    # Check if the list itself is not null
    validateNotNull(stringList, fieldName)
    # Ensure the input is a list
    if not isinstance(stringList, list):
        raise ValueError(f"{fieldName} must be a list of strings")
    # Iterate through the list and validate each string
    for index, item in enumerate(stringList):
        # Ensure each item is not null
        validateNotNull(item, f"{fieldName}[{index}]")
        # Ensure each item adheres to the maximum length
        validateMaxLength(item, f"{fieldName}[{index}]")
        # Ensure each item matches the pattern (sentence)
        pattern = r'^[a-zA-Z0-9\s.,!?;:\'"-]+$'
        if not re.match(pattern, item):
            raise ValueError(f"Invalid {fieldName}[{index}]: {item}")

def validateImagePath(productImagePath, fieldName="productImagePath"):
    """
    Validates that a given product image path is in a valid format.
    Args:
        productImagePath (str): The product image path to validate.
        fieldName (str): The name of the field being validated.
    Raises:
        ValueError: If the product image path is not in a valid format."""
    # Ensure the field is not null
    validateNotNull(productImagePath, fieldName)
    validateMaxLength(productImagePath, fieldName)
    if not isinstance(productImagePath, str):
        raise ValueError(f"Invalid {fieldName}: must be a string.")
    # Ensure the field is a string
    if not productImagePath.endswith(('.png', '.jpg', '.jpeg')):
        raise ValueError(f"Invalid {fieldName}: must be a png, jpg, or jpeg file.")
        

def validateImagePathList(productImagePath, fieldName="productImagePath"):
    """
    Validates that a given list of product image paths is in a valid format.
    Args:
        productImagePath (list): The list of product image paths to validate.
        fieldName (str): The name of the field being validated.
    Raises:
        ValueError: If the list or any of its product image paths are not in a valid format.
    """
    # Ensure the field is not null
    validateNotNull(productImagePath, fieldName)
    # Ensure the field is a list
    if not isinstance(productImagePath, list):
        raise ValueError(f"{fieldName} must be a list of strings.")
    # If the list is not empty, validate each item
    for index, item in enumerate(productImagePath):
        # Ensure each item is not null
        validateNotNull(item, f"{fieldName}[{index}]")
        # Ensure each item is a string
        if not isinstance(item, str):
            raise ValueError(f"Invalid {fieldName}[{index}]: must be a string.")
        # Ensure each item ends with a valid image extension
        if not item.endswith(('.png', '.jpg', '.jpeg')):
            raise ValueError(f"Invalid {fieldName}[{index}]: must be a png, jpg, or jpeg file.")
            

def validateGender(gender):
    """
    Validates that a given gender is in a valid format.
    Args:
        gender (str): The gender to validate.
    Raises:
        ValueError: If the gender is not in a valid format.
    """
    validateNotNull(gender, "Gender")
    validateMaxLength(gender, "Gender")
    if gender not in ['Male', 'Female', 'Unidentify']:
        raise ValueError(f"Invalid gender: {gender}")

def validatePassword(password):
    """
    Validates that a given password meets certain criteria.
    Args:
        password (str): The password to validate.
    Raises:
        ValueError: If the password does not meet the criteria.
    """
    validateNotNull(password, "Password")
    validateMaxLength(password, "Password")
    if len(password) < 8:
        raise ValueError("Password should be longer than 8 characters.")

def validateEmailConfirmationStatus(emailConfirmationStatus):
    """
    Validates that a given email confirmation status is in a valid format.
    Args:
        emailConfirmationStatus (str): The email confirmation status to validate.
    Raises:
        ValueError: If the email confirmation status is not in a valid format.
    """
    validateNotNull(emailConfirmationStatus, "EmailConfirmationStatus")
    validateMaxLength(emailConfirmationStatus, "EmailConfirmationStatus")
    if emailConfirmationStatus not in ['Confirmed', 'Unconfirmed']:
        raise ValueError(f"Invalid EmailConfirmationStatus: {emailConfirmationStatus}")
    
def validateBoolean(booleanData):
    """
    Validates that a given boolean value is in a valid format.
    Args:
        booleanData (bool): The boolean value to validate.
    Raises:
        ValueError: If the boolean value is not in a valid format.
    """
    if not isinstance(booleanData, bool):
        raise ValueError(f"Invalid boolean value: {booleanData}")
    
def validateFloatOrDouble(value, fieldName="value"):
    """
    Validates that a given value is a float or double.
    Args:
        value: The value to validate.
        fieldName: The name of the field being validated.
    Raises:
        ValueError: If the value is not a float or double.
    """
    # Check if the value is not null
    validateNotNull(value, fieldName)
    # Ensure the value is of type float or can be interpreted as a float
    if not isinstance(value, (float, int)):  # Allow int as it can also represent a valid float
        raise ValueError(f"{fieldName} must be a float or double.")
    # Optionally, add further constraints, such as a range
    if value < 0.0:  # Example: ensuring a non-negative value
        raise ValueError(f"{fieldName} must be greater than or equal to 0.0.")

def validateAddressList(addressList):
    """
    Validates that a given list of addresses is in a valid format.
    Args:
        addressList (list): The list of addresses to validate.
    Raises:
        ValueError: If the list or any of its addresses are not in a valid format.
    """
    # Define the expected structure
    expectedStructure = {
        "addressLine1": str,
        "addressLine2": str,
        "city": str,
        "state": str,
        "country": str,
        "zipCode": int,
    }
    errors = []
    for index, address in enumerate(addressList):
        if not isinstance(address, dict):
            errors.append(f"Item at index {index} is not a valid dictionary.")
            continue
        # Validate required keys and their types for each address
        for key, expected_type in expectedStructure.items():
            if key not in address:
                errors.append(f"Address at index {index}: Missing key: {key}")
            elif not isinstance(address[key], expected_type):
                errors.append(f"Address at index {index}: Key '{key}' should be of type {expected_type.__name__}, got {type(address[key]).__name__}.")
        # Additional checks for zipCode
        if "zipCode" in address and isinstance(address["zipCode"], int):
            if address["zipCode"] <= 0:
                errors.append(f"Address at index {index}: zipCode must be a positive integer.")
    # Raise an error if there are validation issues
    if errors:
        raise ValueError("Address validation failed with the following errors:\n" + "\n".join(errors))
    
def validateTransactionStatus(transactionStatus):
    """
    Validates that a given transaction status is in a valid format.
    Args:
        transactionStatus (str): The transaction status to validate.
    Raises:
        ValueError: If the transaction status is not in a valid format.
    """
    validateNotNull(transactionStatus, "TransactionStatus")
    validateMaxLength(transactionStatus, "TransactionStatus")
    if transactionStatus not in ['Processing', 'Wait for payment', 'Completed', 'Cancelled']:
        raise ValueError(f"Invalid TransactionStatus: {transactionStatus}")
        
def validateLogisticStatus(logisticStatus):
    """
    Validates that a given logistic status is in a valid format.
    Args:
        logisticStatus (str): The logistic status to validate.
    Raises:
        ValueError: If the logistic status is not in a valid format.
    """
    validateNotNull(logisticStatus, "LogisticStatus")
    validateMaxLength(logisticStatus, "LogisticStatus")
    if logisticStatus not in ['Processing', 'Shipping', 'Delivered', 'Cancelled']:
        raise ValueError(f"Invalid LogisticStatus: {logisticStatus}")
        
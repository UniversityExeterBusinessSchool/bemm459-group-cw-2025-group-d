# Regular Expression
import re

def validateNotNull(value, fieldName):
    if not value:
        raise ValueError(f"{fieldName} must not be null or empty.")

def validateMaxLength(value, fieldName, maxLength=200):
    if len(value) > maxLength:
        raise ValueError(f"{fieldName} must not exceed {maxLength} characters.")

def validateEmail(email):
    validateNotNull(email, "Email")
    validateMaxLength(email, "Email")
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    if not re.match(pattern, email):
        raise ValueError(f"Invalid email address: {email}")

def validateCountryCode(countryCode):
    validateNotNull(countryCode, "Country code")
    validateMaxLength(countryCode, "Country code")
    if not (countryCode.startswith("+") and countryCode[1:].isdigit() and 1 <= len(countryCode[1:]) <= 3):
        raise ValueError(f"Invalid country code: {countryCode}")

def validatePhoneNumber(phoneNumber):
    validateNotNull(phoneNumber, "Phone number")
    validateMaxLength(phoneNumber, "Phone number")
    if not phoneNumber.isdigit():
        raise ValueError(f"Invalid phone number: {phoneNumber}")

def validateString(string, fieldName):
    validateNotNull(string, fieldName)
    validateMaxLength(string, fieldName)
    # pattern string can contain number
    pattern = r'^[a-zA-Z0-9\s]+$'
    if not re.match(pattern, string):
        raise ValueError(f"Invalid {fieldName}: {string}")
    
def validateSentence(string, fieldName):
    validateNotNull(string, fieldName)
    validateMaxLength(string, fieldName)
    pattern = r'^[a-zA-Z0-9\s.,!?;:\'"-]+$'
    if not re.match(pattern, string):
        raise ValueError(f"Invalid {fieldName}: {string}")
    
def validateStringList(stringList, fieldName):
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
    validateNotNull(productImagePath, fieldName)
    validateMaxLength(productImagePath, fieldName)
    if not isinstance(productImagePath, str):
        raise ValueError(f"Invalid {fieldName}: must be a string.")

def validateImagePathList(productImagePath, fieldName="productImagePath"):
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

def validateGender(gender):
    validateNotNull(gender, "Gender")
    validateMaxLength(gender, "Gender")
    if gender not in ['Male', 'Female', 'Unidentify']:
        raise ValueError(f"Invalid gender: {gender}")

def validatePassword(password):
    validateNotNull(password, "Password")
    validateMaxLength(password, "Password")
    if len(password) < 8:
        raise ValueError("Password should be longer than 8 characters.")

def validateEmailConfirmationStatus(emailConfirmationStatus):
    validateNotNull(emailConfirmationStatus, "EmailConfirmationStatus")
    validateMaxLength(emailConfirmationStatus, "EmailConfirmationStatus")
    if emailConfirmationStatus not in ['Confirmed', 'Unconfirmed']:
        raise ValueError(f"Invalid EmailConfirmationStatus: {emailConfirmationStatus}")
    
def validateBoolean(booleanData):
    if not isinstance(booleanData, bool):
        raise ValueError(f"Invalid boolean value: {booleanData}")
    
def validateFloatOrDouble(value, fieldName="value"):
    # Check if the value is not null
    validateNotNull(value, fieldName)
    # Ensure the value is of type float or can be interpreted as a float
    if not isinstance(value, (float, int)):  # Allow int as it can also represent a valid float
        raise ValueError(f"{fieldName} must be a float or double.")
    # Optionally, add further constraints, such as a range
    if value < 0.0:  # Example: ensuring a non-negative value
        raise ValueError(f"{fieldName} must be greater than or equal to 0.0.")

def validateAddressList(addressList):
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
    for index, address in enumerate(address_list):
        if not isinstance(address, dict):
            errors.append(f"Item at index {index} is not a valid dictionary.")
            continue
        # Validate required keys and their types for each address
        for key, expected_type in expected_structure.items():
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
    validateNotNull(transactionStatus, "TransactionStatus")
    validateMaxLength(transactionStatus, "TransactionStatus")
    if transactionStatus not in ['Processing', 'Wait for payment', 'Completed', 'Cancelled']:
        raise ValueError(f"Invalid TransactionStatus: {transactionStatus}")
        
def validateLogisticStatus(logisticStatus):
    validateNotNull(logisticStatus, "LogisticStatus")
    validateMaxLength(logisticStatus, "LogisticStatus")
    if logisticStatus not in ['Processing', 'Shipping', 'Delivered', 'Cancelled']:
        raise ValueError(f"Invalid LogisticStatus: {logisticStatus}")
        
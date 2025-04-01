import logging
logging.basicConfig(filename='error.log', level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

def logError(**kwargs):
    """
    Logs an error message with detailed information.
    Args:
        **kwargs: Keyword arguments representing error details.
    """
    errorDetails = ', '.join(f"{key}={value}" for key, value in kwargs.items())
    print(errorDetails)
    logging.error(f"Error Details: {errorDetails}")
from datetime import datetime
import sys
import os
# Object for mongodb
from bson.objectid import ObjectId
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import queryMSSQL, getMongoConnection
from ValidatorUtils import validateTransactionStatus, validateLogisticStatus
from Logger import logError
from Product import validateProductGroupId, validatePKProduct
from User import validatePKUser

def validateTransactionPK(pkTransaction: int):
    """
    Validates if a transaction ID is valid.
    Args:
        pkTransaction: The ID of the transaction to validate.
    Raises:
        ValueError: If the transaction ID is invalid.
    """
    queryCheckPKTransaction =  "SELECT pkTransaction FROM marketsync.v_transactions WHERE pkTransaction = ?"
    transaction = queryMSSQL(operation="SELECT", query=queryCheckPKTransaction, params=(pkTransaction))
    if transaction is None:
        raise ValueError(f"Invalid pkTransaction: {pkTransaction}")
                         
def checkIsTransactionCompleted(pkTransaction: int):
    """
    Gets the transaction status.
    Args:
        pkTransaction: The ID of the transaction to check.
    Raises:
        ValueError: If the transaction ID is invalid.
    """
    # check if transaction is completed
    queryCheckPKTransaction =  "SELECT fkTransaction FROM marketsync.v_transactionstates WHERE fkTransaction = ? AND transactionStatus = ?"
    transaction = queryMSSQL(operation="SELECT", query=queryCheckPKTransaction, params=(pkTransaction, "Completed"))
    if transaction is None:
        raise ValueError(f"Transaction Status is not Completed.")

def getProductGroupTransactionHistory(productGroupId):
    """
    Gets the transaction history of a product group.
    Args:
        productGroupId (ObjectId): The ID of the product group to get the transaction history for.
    Returns:
        list: A list of transactions that the product group has been involved in.
    Raises:
        ValueError: If the product group ID is invalid.
        Exception: If there is an error getting the transaction history.
    """
    try:
        # validate product group id
        validateProductGroupId(productGroupId)
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        db = client[dbname]
        collection = db['Products']
        productGroup = collection.find_one({"_id": ObjectId(productGroupId)}, {"product": 1})
        if productGroup is None:
            raise ValueError(f"Invalid productGroupId: {productGroupId}")
        # use pkproduct to search product in transaction table in rdbms
        transactionHistory = []
        for product in productGroup["product"]:
            queryGetTransactionHistory = """
            SELECT t.pkTransaction, t.createDate, t.totalPrice, t.fkUserBuyer, tp.quantity, tp.price, p.productName
            FROM marketsync.Transactions t
            INNER JOIN marketsync.TransactionProducts tp ON t.pkTransaction = tp.fkTransaction
            INNER JOIN marketsync.Products p ON tp.fkProduct = p.pkProduct
            WHERE tp.fkProduct = ?
            """
            transactions = queryMSSQL(operation="SELECT", query=queryGetTransactionHistory, params=(product["pkProduct"]))
            if transactions is not None:
                for transaction in transactions:
                    transactionHistory.append(transaction)
        return transactionHistory
    except Exception as error:
        print("Fail to get product group transaction history:", error)
        logError(error=error, function=getProductGroupTransactionHistory.__name__, input= {
            "productGroupId": productGroupId
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getProductTransactionHistory(pkProduct):
    """
    Gets the transaction history of a product.
    Args:
        pkProduct (int): The ID of the product to get the transaction history for.
    Returns:
        list: A list of transactions that the product has been involved in.
    Raises:
        ValueError: If the product ID is invalid.
        Exception: If there is an error getting the transaction history.
    """
    try:
        # validate product id
        validatePKProduct(pkProduct)
        # Get data from rdbms database
        queryGetTransactionHistory = """
        SELECT t.pkTransaction, t.createDate, t.totalPrice, t.fkUserBuyer, tp.quantity, tp.price, p.productName
        FROM marketsync.Transactions t
        INNER JOIN marketsync.TransactionProducts tp ON t.pkTransaction = tp.fkTransaction
        INNER JOIN marketsync.Products p ON tp.fkProduct = p.pkProduct
        WHERE tp.fkProduct = ?
        """
        transactions = queryMSSQL(operation="SELECT", query=queryGetTransactionHistory, params=(pkProduct))
        return transactions
    except Exception as error:
        print("Fail to get product transaction history:", error)
        logError(error=error, function=getProductTransactionHistory.__name__, input= {
            "pkProduct": pkProduct
        })
            


def addProductToCart(fkUser: int, fkProduct: int, quantity: int):
    """
    Adds a product to a user's cart.
    Args:
        fkUser (int): The ID of the user to add the product to.
        fkProduct (int): The ID of the product to add.
        quantity (int): The quantity of the product to add.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error adding the product to the cart.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Check if product exist in rdbms database
        validatePKProduct(fkProduct)
        # Check if quantity is valid
        if quantity <= 0:
            raise ValueError(f"Invalid quantity: {quantity}")
        # Update data to mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        productExist = False
        for item in user["cart"]:
            if item["pkProduct"] == fkProduct:
                item["quantity"] += quantity
                productExist = True
                break
        if not productExist:
            # Get product price from mongodb
            collectionProduct = db['Products']
            product = collectionProduct.find_one({"product.pkProduct": fkProduct}, {"product.$": 1})
            if product is None:
                raise ValueError(f"Invalid fkProduct: {fkProduct}")
            price = product["product"][0]["productPrice"]
            # Add product to cart
            cartItem = {
                "productId": ObjectId(product["_id"]),
                "pkProduct": fkProduct,
                "quantity": quantity,
                "price": price
            }
            collectionUsers.update_one(
                {"pkUser": fkUser},
                {"$push": {"cart": cartItem}}
            )
        else:
            collectionUsers.update_one(
                {"pkUser": fkUser, "cart.pkProduct": fkProduct},
                {"$set": {"cart.$.quantity": item["quantity"]}}
            )
        print("Product added to cart.")
    except Exception as error:
        print("Fail to add product to cart:", error)
        logError(error=error, function=addProductToCart.__name__, input= {
            "fkUser": fkUser,
            "fkProduct": fkProduct,
            "quantity": quantity
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def removeProductFromCart(fkUser: int, fkProduct: int):
    """
    Removes a product from a user's cart.
    Args:
        fkUser (int): The ID of the user to remove the product from.
        fkProduct (int): The ID of the product to remove.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid or if the product is not found in the cart.
        Exception: If there is an error removing the product from the cart.
    """
    # remove product from cart in user.cart in mongodb
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Check if product exist in rdbms database
        validatePKProduct(fkProduct)
        # Update data to mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        productExist = False
        for item in user["cart"]:
            if item["pkProduct"] == fkProduct:
                productExist = True
                break
        if not productExist:
            raise ValueError(f"Product {fkProduct} not found in cart")
        collectionUsers.update_one(
            {"pkUser": fkUser},
            {"$pull": {"cart": {"pkProduct": fkProduct}}}
        )
        print("Product removed from cart.")
    except Exception as error:
        print("Fail to remove product from cart:", error)
        logError(error=error, function=removeProductFromCart.__name__, input= {
            "fkUser": fkUser,
            "fkProduct": fkProduct
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def editProductQuantityInCart(fkUser: int, fkProduct: int, quantity: int):
    """
    Edits the quantity of a product in a user's cart.
    Args:
        fkUser (int): The ID of the user whose cart to edit.
        fkProduct (int): The ID of the product to edit.
        quantity (int): The new quantity of the product.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid or if the product is not found in the cart.
        Exception: If there is an error editing the product quantity in the cart.
    """
    # edit product quantity in cart
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Check if product exist in rdbms database
        validatePKProduct(fkProduct)
        # Check if quantity is valid
        if quantity <= 0:
            raise ValueError(f"Invalid quantity: {quantity}")
        # Update data to mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        productExist = False
        for item in user["cart"]:
            if item["pkProduct"] == fkProduct:
                item["quantity"] = quantity
                productExist = True
                break
        if not productExist:
            raise ValueError(f"Product {fkProduct} not found in cart")
        collectionUsers.update_one(
            {"pkUser": fkUser, "cart.pkProduct": fkProduct},
            {"$set": {"cart.$.quantity": quantity}}
        )
        print("Product quantity updated in cart.")
    except Exception as error:
        print("Fail to update product quantity in cart:", error)
        logError(error=error, function=editProductQuantityInCart.__name__, input= {
            "fkUser": fkUser,
            "fkProduct": fkProduct,
            "quantity": quantity
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    
def getUserCart(fkUser: int):
    """
    Gets the cart of a user.
    Args:
        fkUser (int): The ID of the user to get the cart for.
    Returns:
        list: A list of products in the user's cart.
    Raises:
        ValueError: If the user ID is invalid.
        Exception: If there is an error getting the cart.
    """
    # get cart
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Get data from mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        return user["cart"]
    except Exception as error:
        print("Fail to get cart:", error)
        logError(error=error, function=getUserCart.__name__, input= {
            "fkUser": fkUser
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    
def clearCart(fkUser: int):
    """
    Clears the cart of a user.
    Args:
        fkUser (int): The ID of the user whose cart to clear.
    Returns:
        None
    Raises:
        ValueError: If the user ID is invalid.
        Exception: If there is an error clearing the cart.
    """
    # clear cart
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Update data to mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        collectionUsers.update_one(
            {"pkUser": fkUser},
            {"$set": {"cart": []}}
        )
        print("Cart cleared.")
    except Exception as error:
        print("Fail to clear cart:", error)
        logError(error=error, function=clearCart.__name__, input= {
            "fkUser": fkUser
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def cartToPayment(fkUser: int):
    """
    Converts a user's cart to a payment transaction.
    Args:
        fkUser (int): The ID of the user whose cart to convert.
    Returns:
        int: The ID of the newly created transaction.
    Raises:
        ValueError: If the user ID is invalid or if the cart is empty.
        Exception: If there is an error creating the transaction.
    """
    # use cart data in mongodb to create transaction in rdbms
    # then create transaction status in rdbms as well it start from 'Processing'
    # after that clear cart
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Get data from mongodb
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUsers = db['Users']
        # Check if product already in cart
        user = collectionUsers.find_one({"pkUser": fkUser}, {"cart": 1})
        if user is None:
            raise ValueError(f"Invalid fkUser: {fkUser}")
        if len(user["cart"]) == 0:
            raise ValueError(f"Cart is empty")
        # Validate fkProduct
        for item in user["cart"]:
            validatePKProduct(item["pkProduct"])
        # loop user["cart"] to get pkProduct then use it to create transaction, transactionproduct,transactionstatus "Processing"
        totalPrice = 0
        for item in user["cart"]:
            totalPrice += item["quantity"] * item["price"]
        # Insert data to rdbms database
        queryInsertTransaction = """
        SET NOCOUNT ON;
        DECLARE @InsertedTransaction TABLE (pkTransaction INT);
        INSERT INTO marketsync.Transactions (fkUserBuyer, totalPrice)
        OUTPUT Inserted.pkTransaction INTO @InsertedTransaction
        VALUES (?, ?);
        SELECT pkTransaction FROM @InsertedTransaction;
        """
        pkTransaction = queryMSSQL(operation="INSERT", query=queryInsertTransaction, params=(fkUser, totalPrice))[0]
        if pkTransaction is None:
            raise ValueError(f"Failed to create transaction for user: {fkUser}")
        # Insert transaction product
        for item in user["cart"]:
            # Get fkShop from first product
            queryInsertTransactionProduct = """
            INSERT INTO marketsync.TransactionProducts (fkTransaction, fkProduct, quantity, price)
            VALUES (?, ?, ?, ?);
            """
            queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertTransactionProduct, params=(pkTransaction, item["pkProduct"], item["quantity"], item["price"]))
        # Insert transaction status
        queryInsertTransactionStatus = """
        INSERT INTO marketsync.TransactionStates (fkTransaction, transactionStatus)
        VALUES (?, ?);
        """
        queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertTransactionStatus, params=(pkTransaction, "Processing"))
        # Clear cart
        clearCart(fkUser)
        print("Transaction created.")
        return pkTransaction
    except Exception as error:
        print("Fail to create transaction:", error)
        logError(error=error, function=cartToPayment.__name__, input= {
            "fkUser": fkUser
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def changeTransactionStatus(pkTransaction: int, transactionStatus: str):
    """
    Updates the status of a transaction.
    Args:
        pkTransaction (int): The ID of the transaction to update.
        transactionStatus (str): The new status of the transaction.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error updating the transaction status.
    """
    # change transaction status in SQL
    try:
        # Validate transaction pk
        validateTransactionPK(pkTransaction)
        # Validate transaction status
        validateTransactionStatus(transactionStatus)
        # Check if transaction exist in rdbms database
        queryCheckTransaction = """
        SELECT pkTransaction FROM marketsync.Transactions WHERE pkTransaction = ?
        """
        transaction = queryMSSQL(operation="SELECT", query=queryCheckTransaction, params=(pkTransaction))
        if transaction is None:
            raise ValueError(f"Invalid pkTransaction: {pkTransaction}")
        # Update data to rdbms database
        queryInsertTransactionStatus = """
        INSERT INTO marketsync.TransactionStates (fkTransaction, transactionStatus)
        VALUES (?, ?);
        """
        queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertTransactionStatus, params=(pkTransaction, transactionStatus))
        print("Transaction status updated.")
    except Exception as error:
        print("Fail to update transaction status:", error)
        logError(error=error, function=changeTransactionStatus.__name__, input= {
            "pkTransaction": pkTransaction,
            "transactionStatus": transactionStatus
        })
        
def updateSoldAmount(pkTransacion):
    """
    Updates the sold amount of products in MongoDB after a transaction is completed.
    Args:
        pkTransacion (int): The ID of the transaction to update the sold amount for.
    Returns:
        None
    Raises:
        ValueError: If the transaction ID is invalid or if the transaction is not completed.
        Exception: If there is an error updating the sold amount.
        
    """
    # create logistic with pktransaction also need to check that transaction is completed first
    try:
        # Get data from rdbms database
        queryGetTransactionProduct = """
        SELECT fkProduct, quantity
        FROM marketsync.TransactionProducts
        WHERE fkTransaction = ?
        """
        transactionProducts = queryMSSQL(operation="SELECT", query=queryGetTransactionProduct, params=(pkTransacion))
        if transactionProducts is None:
            raise ValueError(f"Invalid pkTransaction: {pkTransacion}")
        # Update data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        for transactionProduct in transactionProducts:
            pkProduct = transactionProduct[0]
            quantity = transactionProduct[1]
            productGroup = collection.find_one({"product.pkProduct": pkProduct}, {"product.$": 1})
            if productGroup is None:
                raise ValueError(f"Invalid pkProduct: {pkProduct}")
            result = collection.update_one(
                {"_id": ObjectId(productGroup["_id"])},
                {"$inc": {"soldAmount": quantity}}
            )
            print("Product sold amount updated. Matched:", result.matched_count, "Modified:", result.modified_count)
    except Exception as error:
        print("Fail to update sold amount:", error)
        logError(error=error, function=updateSoldAmount.__name__, input= {
            "pkTransacion": pkTransacion
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
def createLogistic(pkTransaction: int, deliveryDate: datetime):
    """
    Creates a new logistic for a transaction.
    Args:
        pkTransaction (int): The ID of the transaction to create the logistic for.
        deliveryDate (datetime): The expected delivery date of the logistic.
    Returns:
        int: The ID of the newly created logistic.
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error creating the logistic.
    """
    try:
        # Validate transaction pk
        validateTransactionPK(pkTransaction)
        # Check if transaction status is completed
        checkIsTransactionCompleted(pkTransaction)
        # Update sold amount
        updateSoldAmount(pkTransaction)
        # Insert data to rdbms database
        queryInsertLogistic = """
        SET NOCOUNT ON;
        DECLARE @InsertedLogistic TABLE (pkLogistic INT);
        INSERT INTO marketsync.Logistics (fkTransaction, expectedDeliveryDate)
        OUTPUT Inserted.pkLogistic INTO @InsertedLogistic
        VALUES (?, ?);
        SELECT pkLogistic FROM @InsertedLogistic;
        """
        pkLogistic = queryMSSQL(operation="INSERT", query=queryInsertLogistic, params=(pkTransaction, deliveryDate))[0]
        if pkLogistic is None:
            raise ValueError(f"Failed to create logistic for transaction: {pkTransaction}")
        # Insert logistic status
        queryInsertLogisticStatus = """
        INSERT INTO marketsync.LogisticStates (fkLogistic, logisticStatus)
        VALUES (?, ?);
        """
        queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertLogisticStatus, params=(pkLogistic, "Processing"))
        print("Logistic created.")
        return pkLogistic
    except Exception as error:
        print("Fail to create logistic:", error)
        logError(error=error, function=createLogistic.__name__, input= {
            "pkTransaction": pkTransaction,
            "deliveryDate": deliveryDate
        })
        
def changeLogisticStatus(pkLogistic: int, logisticStatus: str):
    """
    Updates the status of a logistic.
    Args:
        pkLogistic (int): The ID of the logistic to update.
        logisticStatus (str): The new status of the logistic.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error updating the logistic status.
    """
    # change logistic status in SQL
    try:
        # Validate logistic status
        validateLogisticStatus(logisticStatus)
        # Check if logistic exist in rdbms database
        queryCheckLogistic = """
        SELECT pkLogistic FROM marketsync.Logistics WHERE pkLogistic = ?
        """
        logistic = queryMSSQL(operation="SELECT", query=queryCheckLogistic, params=(pkLogistic))
        if logistic is None:
            raise ValueError(f"Invalid pkLogistic: {pkLogistic}")
        # Update data to rdbms database
        queryInsertLogisticStatus = """
        INSERT INTO marketsync.LogisticStates (fkLogistic, logisticStatus)
        VALUES (?, ?);
        """
        queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertLogisticStatus, params=(pkLogistic, logisticStatus))
        print("Logistic status updated.")
    except Exception as error:
        print("Fail to update logistic status:", error)
        logError(error=error, function=changeLogisticStatus.__name__, input= {
            "pkLogistic": pkLogistic,
            "logisticStatus": logisticStatus
        })
        
        
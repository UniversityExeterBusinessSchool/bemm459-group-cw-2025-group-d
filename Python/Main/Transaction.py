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
from Product import getfkShopfromProduct, validateProductGroupId, validatePKProduct
from User import validatePKUser

def validateTransactionPK(pkTransaction: int):
    queryCheckPKTransaction =  "SELECT pkTransaction FROM marketsync.v_transactions WHERE pkTransaction = ?"
    transaction = queryMSSQL(operation="SELECT", query=queryCheckPKTransaction, params=(pkTransaction))
    if transaction is None:
        raise ValueError(f"Invalid pkTransaction: {pkTransaction}")
                         
def checkIsTransactionCompleted(pkTransaction: int):
    # check if transaction is completed
    queryCheckPKTransaction =  "SELECT fkTransaction FROM marketsync.v_transactionstates WHERE fkTransaction = ? AND transactionStatus = ?"
    transaction = queryMSSQL(operation="SELECT", query=queryCheckPKTransaction, params=(pkTransaction, "Completed"))
    if transaction is None:
        raise ValueError(f"Transaction Status is not Completed.")

def getProductGroupTransactionHistory(productGroupId):
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
            SELECT t.pkTransaction, t.transactionDate, t.totalAmount, t.fkUser, t.fkShop, tp.quantity, tp.price
            FROM marketsync.Transactions t
            JOIN marketsync.TransactionProducts tp ON t.pkTransaction = tp.fkTransaction
            WHERE tp.fkProduct = ?
            """
            transactions = queryMSSQL(operation="SELECT", query=queryGetTransactionHistory, params=(product["pkProduct"]))
            if transactions is not None:
                for transaction in transactions:
                    transactionHistory.append(transaction)
        return transactionHistory
    except Exception as error:
        print("Fail to get product group transaction history:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getProductTransactionHistory(pkProduct):
    try:
        # validate product id
        validatePKProduct(pkProduct)
        # Get data from rdbms database
        queryGetTransactionHistory = """
        SELECT t.pkTransaction, t.transactionDate, t.totalAmount, t.fkUser, t.fkShop, tp.quantity, tp.price
        FROM marketsync.Transactions t
        JOIN marketsync.TransactionProducts tp ON t.pkTransaction = tp.fkTransaction
        WHERE tp.fkProduct = ?
        """
        transactions = queryMSSQL(operation="SELECT", query=queryGetTransactionHistory, params=(pkProduct))
        return transactions
    except Exception as error:
        print("Fail to get product transaction history:", error)


def addProductToCart(fkUser: int, fkProduct: int, quantity: int):
    # add product to cart in user.cart in mongodb
    # also check if duplicate add the quantity instead
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def removeProductFromCart(fkUser: int, fkProduct: int):
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def editProductQuantityInCart(fkUser: int, fkProduct: int, quantity: int):
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    
def getUserCart(fkUser: int):
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    
def clearCart(fkUser: int):
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def cartToPayment(fkUser: int):
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
            fkShop = getfkShopfromProduct(item["pkProduct"])
            queryInsertTransactionProduct = """
            INSERT INTO marketsync.TransactionProducts (fkTransaction, fkShop, fkProduct, quantity, price)
            VALUES (?, ?, ?, ?, ?);
            """
            queryMSSQL(operation="INSERT_WITHOUT_FETCH", query=queryInsertTransactionProduct, params=(pkTransaction, fkShop, item["pkProduct"], item["quantity"], item["price"]))
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
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            


def changeTransactionStatus(pkTransaction: int, transactionStatus: str):
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

def createLogistic(pkTransaction: int, deliveryDate: datetime):
    # create logistic with pktransaction also need to check that transaction is completed first
    try:
        # Validate transaction pk
        validateTransactionPK(pkTransaction)
        # Check if transaction status is completed
        checkIsTransactionCompleted(pkTransaction)
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
        
def changeLogisticStatus(pkLogistic: int, logisticStatus: str):
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
        
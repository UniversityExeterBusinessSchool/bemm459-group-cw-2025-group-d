import sys
import os
# # Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import queryMSSQL, getMongoConnection
from ValidatorUtils import validateString
from Logger import logError
from User import validatePKUser

def validatePKShop(pkShop: int):
    """
    Validates if a shop ID is valid.
    Args:
        pkShop: The ID of the shop to validate.
    Raises:
        ValueError: If the shop ID is invalid.
    """
    query =  "SELECT pkshop FROM marketsync.v_shops WHERE pkshop = ?"
    shop = queryMSSQL(operation="SELECT", query=query, params=(pkShop))
    if shop is None:
        raise ValueError(f"Invalid pkShop: {pkShop}")
    
def getShopNameWithPKShop(pkShop: int):
    """
    Gets the name of a shop from a shop ID.
    Args:
        pkShop: The ID of the shop.
    Returns:
        The name of the shop.
    Raises:
        ValueError: If the shop ID is invalid.
    """
    query =  "SELECT shopName FROM marketsync.v_shops WHERE pkshop = ?"
    shop = queryMSSQL(operation="SELECT", query=query, params=(pkShop))
    if shop is None:
        raise ValueError(f"Invalid pkShop: {pkShop}")
    return shop[0][0]

def createShop(fkUser: int,shopName):
    """
    Creates a new shop.
    Args:
        fkUser (int): The foreign key of the user who owns the shop.
        shopName (str): The name of the shop.
    Returns:
        int: The primary key of the newly created shop.
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error creating the shop.
    """
    try:
        # Check if user exist in rdbms database
        validatePKUser(fkUser)
        # Validate Value
        validateString(shopName, "Shop name")
        # Insert data to rdbms database
        queryInsertShop = """
        SET NOCOUNT ON;
        DECLARE @InsertedShop TABLE (pkShop INT);
        INSERT INTO marketsync.Shops (shopName, fkUser)
        OUTPUT Inserted.pkShop INTO @InsertedShop
        VALUES (?, ?);
        SELECT pkShop FROM @InsertedShop;
        """
        pkShop = queryMSSQL(operation = "INSERT", query = queryInsertShop, params=(shopName, fkUser))
        if pkShop is None:
            raise ValueError(f"Failed to create shop: {shopName} for user {fkUser}")
        print("Shop created successfully")
        return pkShop[0]
    except Exception as error:
        print("Fail to create shop:", error)
        logError(error=error, function=createShop.__name__, input= {
            "fkUser": fkUser,
            "shopName": shopName
        })
    
def updateShopName(pkShop: int, shopName):
    """
    Updates the name of an existing shop.
    Args:
        pkShop (int): The primary key of the shop to update.
        shopName (str): The new name for the shop.
    Returns:
        None
    Raises:
        ValueError: If any of the input values are invalid.
        Exception: If there is an error updating the shop name.
    """
    try:
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # Validate Value
        validateString(shopName, "Shop name")
        # Update shop name in rdbms database
        queryUpdateShop = "UPDATE marketsync.Shops SET shopName = ? WHERE pkShop = ?"
        queryMSSQL(operation="UPDATE", query=queryUpdateShop, params=(shopName,pkShop))
        if queryMSSQL(operation="SELECT", query="SELECT pkShop FROM marketsync.Shops WHERE pkShop = ? AND shopName = ?", params=(pkShop, shopName)) is None:
            raise ValueError(f"Failed to update shop: {shopName} for shop {pkShop}")
        print("Shop name updated in rdbms database.")
        # Update shop name in mongodb
        client,dbname = getMongoConnection()
        collectionProducts = client[dbname]['Products']
        updateResult = collectionProducts.update_many(
            {"pkShop": pkShop, "isDelete": False},
            {"$set": {"shopName": shopName}}
        )
        if updateResult.modified_count > 0:
            print(f"Updated {updateResult.modified_count} product group shop names in MongoDB.")
        else:
            print("No product group shop names were updated in MongoDB.")
        print("Shop updated successfully")
    except Exception as error:
        print("Fail to update shop:", error)
        logError(error=error, function=updateShopName.__name__, input= {
            "pkShop": pkShop,
            "shopName": shopName
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            

def softDeleteShop(pkShop: int):
    """
    Deletes a shop by setting its isDelete flag to True.
    Args:
        pkShop (int): The primary key of the shop to delete.
    Returns:
        None
    Raises:
        ValueError: If the shop ID is invalid.
        Exception: If there is an error deleting the shop.
    """
    try:
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # soft delete shop in rdbms database
        queryUpdateShop = "UPDATE marketsync.Shops SET isDelete = 1 WHERE pkShop = ?"
        queryMSSQL(operation="UPDATE", query=queryUpdateShop, params=(pkShop))
        print("Shop soft deleted in rdbms database.")
        # Get all product relate to shop in mongodb
        client,dbname = getMongoConnection()
        collectionProducts = client[dbname]['Products']
        products = collectionProducts.find({"pkShop": pkShop, "isDelete": False})
        # update product isDelete
        for product in products:
            for productItem in product["product"]:
                queryUpdateProduct = "UPDATE marketsync.Products SET isDelete = 1 WHERE pkProduct = ?"
                queryMSSQL(operation="UPDATE", query=queryUpdateProduct, params=(productItem["pkProduct"]))
                print("Product soft deleted in rdbms database.")
        # delete shop in mongodb
        updateResult = collectionProducts.update_many(
            {"pkShop": pkShop, "isDelete": False},
            {"$set": {"isDelete": True}}
        )
        if updateResult.modified_count > 0:
            print(f"Deleted {updateResult.modified_count} every product group with pkshop " + str(pkShop) + " in MongoDB.")
        else:
            print("No product group shop names were updated in MongoDB.")
        print("Shop deleted successfully")
    except Exception as error:
        print("Fail to delete shop:", error)
        logError(error=error, function=softDeleteShop.__name__, input= {
            "pkShop": pkShop
        })
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
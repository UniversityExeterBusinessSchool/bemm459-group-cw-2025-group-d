import sys
import os
# # Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import queryMSSQL, getMongoConnection
from ValidatorUtils import validateString
from User import validatePKUser

def validatePKShop(pkShop: int):
    query =  "SELECT pkshop FROM marketsync.v_shops WHERE pkshop = ?"
    shop = queryMSSQL(operation="SELECT", query=query, params=(pkShop))
    if shop is None:
        raise ValueError(f"Invalid pkShop: {pkShop}")
    
def getShopNameWithPKShop(pkShop: int):
    query =  "SELECT shopName FROM marketsync.v_shops WHERE pkshop = ?"
    shop = queryMSSQL(operation="SELECT", query=query, params=(pkShop))
    if shop is None:
        raise ValueError(f"Invalid pkShop: {pkShop}")
    return shop[0][0]

def createShop(fkUser: int,shopName):
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
        return None
    
def updateShopName(pkShop: int, shopName):
    try:
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # Validate Value
        validateString(shopName, "Shop name")
        # Update shop name in rdbms database
        queryUpdateShop = "UPDATE Shops SET shopName = ? WHERE pkShop = ?"
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

def softDeleteShop(pkShop: int):
    try:
        # Check if shop exist in rdbms database
        validatePKShop(pkShop)
        # soft delete shop in rdbms database
        queryUpdateShop = "UPDATE Shops SET isDelete = 1 WHERE pkShop = ?"
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
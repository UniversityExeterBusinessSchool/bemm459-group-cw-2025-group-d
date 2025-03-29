from datetime import datetime
import sys
import os
# Object for mongodb
from bson.objectid import ObjectId
# Add the parent directory (Project) to sys.path
# Library file
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from DatabaseConnection import queryMSSQL, getMongoConnection
from ValidatorUtils import validateString, validateSentence, validateStringList, validateImagePath, validateFloatOrDouble
from Shop import validatePKShop, getShopNameWithPKShop
from User import validatePKUser

def validateProductGroupId(productGroupId) -> bool:
    try:
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        productGroup = collection.find_one({"_id": ObjectId(productGroupId)}, {"_id": 0})
        if productGroup is None:
            raise ValueError(f"Invalid productGroupId: {productGroupId}")
    except Exception as error:
        raise
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
def getfkShopFromProductGroup(productGroupId):
    try:
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        productGroup = collection.find_one({"_id": ObjectId(productGroupId)}, {"pkShop": 1})
        if productGroup is None:
            raise ValueError(f"Invalid productGroupId: {productGroupId}")
        return productGroup["pkShop"]
    except Exception as error:
        print("Fail to get fkShop from product group:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def getfkShopfromProduct(pkProduct: int):
    query =  "SELECT fkShop FROM marketsync.v_products WHERE pkProduct = ?"
    shop = queryMSSQL(operation="SELECT", query=query, params=(pkProduct))
    if shop is None:
        raise ValueError(f"Invalid pkProduct: {pkProduct}")
    return shop[0][0]

def validatePKProduct(pkProduct):
    try:        
        # Get data from rdbms database
        queryCheckPKProduct =  "SELECT pkproduct FROM marketsync.v_products WHERE pkproduct = ?"
        product = queryMSSQL(operation="SELECT", query=queryCheckPKProduct, params=(pkProduct))
        if product is None:
            raise ValueError(f"Invalid productId: {pkProduct}")
    except Exception as error:
        raise
            

def createProductGroup(fkShop: int, groupName, groupDescription, productImagePath, productCategory, isDelete = False):
    try:
        # Check if shop exist in rdbms database
        validatePKShop(fkShop)
        # Validate Value
        validateSentence(groupName, "Group name")
        validateSentence(groupDescription, "Group description")
        validateImagePath(productImagePath, "Product image path")
        validateStringList(productCategory, "Product category")
        # Get shop name
        shopName = getShopNameWithPKShop(fkShop)
        # Insert data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        productGroup = {
            "pkShop": fkShop,
            "shopName": shopName,
            "productName": groupName,
            "productDescription": groupDescription,
            "productImagePath": productImagePath,
            "productCategory": productCategory,
            "soldAmount": 0,
            "product": [],
            "reviews": [],
            "createDate": datetime.now(),
            "updateDate": datetime.now(),
            "isDelete": isDelete
        }
        result = collection.insert_one(productGroup)
        return result.inserted_id
    except Exception as error:
        print("Fail to create ProductGroup:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def updateProductGroup(productGroupId, groupName, groupDescription, productImagePath, productCategory):
    try:
        # Validate Value
        validateSentence(groupName, "Group name")
        validateSentence(groupDescription, "Group description")
        validateString(productImagePath, "Product image path")
        validateStringList(productCategory, "Product category")
        # Update data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        updatedFields = {
            "productName": groupName,
            "productDescription": groupDescription,
            "productImagePath": productImagePath,
            "productCategory": productCategory,
            "updateDate": datetime.now()
        }
        result = collection.update_one({"_id": ObjectId(productGroupId)}, {"$set": updatedFields})
        print("Product group updated. Matched:", result.matched_count, "Modified:", result.modified_count)
        return result.modified_count
    except Exception as error:
        print("Fail to update product group:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
def deleteProductGroup(productGroupId):
    try:
        # Delete data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        result = collection.update_one(
            {"_id": ObjectId(productGroupId)},
            {"$set": {"isDelete": True, "updateDate": datetime.now()}}
        )
        print("Product group soft-deleted. Matched:", result.matched_count, "Modified:", result.modified_count)
        return result.modified_count
    except Exception as error:
        print("Fail to delete product group:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def createProductToProductGroup(productGroupId, productName, productDescription, productImagePath, productPrice):
    try:
        # validate product group id
        validateProductGroupId(productGroupId)
        # get fkshop from product group
        fkShop = getfkShopFromProductGroup(productGroupId)
        # Validate Value
        validateSentence(productName, "Product name")
        validateSentence(productDescription, "Product description")
        validateImagePath(productImagePath, "Product image path")
        validateFloatOrDouble(productPrice, "Product price")
        # Insert product data to rdbms
        queryInsertProduct = """
        SET NOCOUNT ON;
        DECLARE @InsertedProducts TABLE (pkProduct INT);
        INSERT INTO marketsync.Products (productName,fkShop)
        OUTPUT Inserted.pkProduct INTO @InsertedProducts
        VALUES (?,?)
        SELECT pkProduct FROM @InsertedProducts;
        """
        pkProduct = queryMSSQL(operation="INSERT", query=queryInsertProduct, params=(productName,fkShop))[0]
        if pkProduct is None:
            raise ValueError(f"Failed to create product: {productName}")
        # Update data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        product = {
            "pkProduct": int(pkProduct),
            "productName": productName,
            "productDescription": productDescription,
            "productImagePath": productImagePath,
            "productPrice": productPrice,
            "createDate": datetime.now(),
            "updateDate": datetime.now(),
            "isDelete": False
        }
        result = collection.update_one(
            {"_id": ObjectId(productGroupId)},
            {"$push": {"product": product}}
        )
        print("Product added to group. Matched:", result.matched_count, "Modified:", result.modified_count)
        return pkProduct
    except Exception as error:
        print("Fail to add product to group:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
    

def updateProductToProductGroup(productGroupId, fkProduct, productName, productDescription, productImagePath, productPrice):
    try:
        # validate product group id
        validateProductGroupId(productGroupId)
        # validate product id
        validatePKProduct(fkProduct)
        # Validate Value
        validateString(productName, "Product name")
        validateString(productDescription, "Product description")
        validateImagePathList(productImagePath, "Product image path")
        validateFloatOrDouble(productPrice, "Product price")
        # Update product name to rdbms dataabase
        queryUpdateProduct = "UPDATE marketsync.Products SET productName = ? WHERE pkProduct = ?"
        queryMSSQL(operation="UPDATE", query=queryUpdateProduct, params=(productName,fkProduct))
        if queryMSSQL(operation="SELECT", query="SELECT pkProduct FROM marketsync.Products WHERE pkProduct = ? AND productName = ?", params=(fkProduct, productName)) is None:
            raise ValueError(f"Failed to update product: {productName}")
        # Check if product exist in product group
        productGroup = collection.find_one({"_id": ObjectId(productGroupId)}, {"product": 1})
        if productGroup is None:
            raise ValueError(f"Invalid productGroupId: {productGroupId}")
        productExist = False
        for product in productGroup["product"]:
            if product["pkProduct"] == fkProduct:
                productExist = True
                break
        if not productExist:
            raise ValueError(f"Product {fkProduct} not found in product group {productGroupId}")
        # Update product data to mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        updatedFields = {
            "product.$.productName": productName,
            "product.$.productDescription": productDescription,
            "product.$.productImagePath": productImagePath,
            "product.$.productPrice": productPrice,
            "product.$.updateDate": datetime.now()
        }
        result = collection.update_one(
            {"_id": ObjectId(productGroupId), "product.pkProduct": fkProduct},
            {"$set": updatedFields}
        )
        print("Product updated in group. Matched:", result.matched_count, "Modified:", result.modified_count)
        return result.modified_count
    except Exception as error:
        print("Fail to update product in group:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
def deleteProductFromProductGroup(productGroupId, fkProduct):
    try:
        # validate product group id
        validateProductGroupId(productGroupId)
        # validate product id
        validatePKProduct(fkProduct)
        # Update product name to rdbms dataabase
        queryUpdateProduct = "UPDATE marketsync.Products SET isDelete = 1, updateDate = ? WHERE pkProduct = ?"
        queryMSSQL(operation="UPDATE", query=queryUpdateProduct, params=(datetime.now(),fkProduct))
        if queryMSSQL(operation="SELECT", query="SELECT pkProduct FROM marketsync.Products WHERE pkProduct = ? AND isDelete = 1", params=(fkProduct)) is None:
            raise ValueError(f"Failed to delete product: {fkProduct}")
        # Check if product exist in product group
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        productGroup = collection.find_one({"_id": ObjectId(productGroupId)}, {"product": 1})
        if productGroup is None:
            raise ValueError(f"Invalid productGroupId: {productGroupId}")
        productExist = False
        for product in productGroup["product"]:
            if product["pkProduct"] == fkProduct:
                productExist = True
                break
        if not productExist:
            raise ValueError(f"Product {fkProduct} not found in product group {productGroupId}")
        # Update product data to mongodb database
        result = collection.update_one(
            {"_id": ObjectId(productGroupId), "product.pkProduct": fkProduct},
            {"$set": {"product.$.isDelete": True, "product.$.updateDate": datetime.now()}}
        )
        print("Product soft-deleted in group. Matched:", result.matched_count, "Modified:", result.modified_count)
        return result.modified_count
    except Exception as error:
        print("Fail to delete product in group:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
        
def searchProduct(productName):
    # search productname, productdescription , product.productname or product.productdescription in mongdbo with wildcard
    try:
        # Validate Value
        validateString(productName, "Product name")
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        # Search product name or product description in product group
        productGroups = collection.find({
            "$or": [
                {"productName": {"$regex": productName, "$options": "i"}},
                {"productDescription": {"$regex": productName, "$options": "i"}},
                {"product.productName": {"$regex": productName, "$options": "i"}},
                {"product.productDescription": {"$regex": productName, "$options": "i"}}
            ],
            "isDelete": False
        })
        products = []
        for productGroup in productGroups:
            products.append(productGroup)
        return products
    except Exception as error:
        print("Fail to search product:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()

def searchProductWithCategory(productName,productCategory):
    # search productname, productdescription, productcategory , product.productname or product.productdescription in mongdbo with wildcard
    try:
        # Validate Value
        validateString(productName, "Product name")
        validateStringList(productCategory, "Product category")
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        collection = client[dbname]['Products']
        # Search product name or product description in product group
        productGroups = collection.find({
            "$and": [
                {
                    "$or": [
                        {"productName": {"$regex": productName, "$options": "i"}},
                        {"productDescription": {"$regex": productName, "$options": "i"}},
                        {"product.productName": {"$regex": productName, "$options": "i"}},
                        {"product.productDescription": {"$regex": productName, "$options": "i"}}
                    ]
                },
                {"productCategory": {"$in": productCategory}},
                {"isDelete": False}
            ]
        })
        products = []
        for productGroup in productGroups:
            products.append(productGroup)
        return products
    except Exception as error:
        print("Fail to search product:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
            
def getUserRecommendations(pkUser,size):
    # get most popular product with from user latest 5 user.searchHistory.keyword
    # size is total number of item need to be return
    # if user doesn't have at least 5 keyword fill it with all his/her keyword
    # if user doesn't have any keyword fill it with most popular product without keyword
    try:
        # Check if user exist in rdbms database
        validatePKUser(pkUser)
        # Validate Value
        if size <= 0:
            raise ValueError(f"Invalid size: {size}")
        # Get data from mongodb database
        client,dbname = getMongoConnection()
        db = client[dbname]
        collectionUser = db['Users']
        collectionProduct = db['Products']
        # Get user search history
        user = collectionUser.find_one({"pkUser": pkUser}, {"searchHistory": 1})
        if user is None:
            raise ValueError(f"Invalid pkUser: {pkUser}")
        # Get user search history keyword
        keywords = []
        if "searchHistory" in user:
            for searchHistory in user["searchHistory"]:
                keywords.append(searchHistory["keyword"])
        # Get most popular product with keyword
        products = []
        if len(keywords) > 0:
            for keyword in keywords:
                productGroups = collectionProduct.find({
                    "$or": [
                        {"productName": {"$regex": keyword, "$options": "i"}},
                        {"productDescription": {"$regex": keyword, "$options": "i"}},
                        {"product.productName": {"$regex": keyword, "$options": "i"}},
                        {"product.productDescription": {"$regex": keyword, "$options": "i"}}
                    ],
                    "isDelete": False
                }).sort("soldAmount", -1).limit(size)
                for productGroup in productGroups:
                    products.append(productGroup)
        # Get most popular product without keyword
        if len(products) < size:
            productGroups = collectionProduct.find({"isDelete": False}).sort("soldAmount", -1).limit(size - len(products))
            for productGroup in productGroups:
                products.append(productGroup)
        return products
    except Exception as error:
        print("Fail to get user recommendations:", error)
    finally:
        if 'client' in locals() and client is not None:  # Check if client exists
            client.close()
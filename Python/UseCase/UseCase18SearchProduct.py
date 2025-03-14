import sys, os, re
from pymongo import ASCENDING, DESCENDING
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def searchProduct(keyword, sort_by="date", page=1, page_size=10):
    """
    Search product groups matching a keyword in productName, productDescription, or shopName.
    Supports sorting by:
      - "date"      : uses createDate (descending)
      - "price"     : sorts by computed avgPrice (ascending)
      - "popularity": sorts by soldAmount (descending)
      - "rating"    : sorts by computed avgRating (descending)
    And supports pagination.
    """
    client = getMongoConnection()
    db = client["marketsync"]
    collection = db["Products"]

    regex = re.compile(keyword, re.IGNORECASE)
    match_stage = {
        "$match": {
            "isDelete": False,
            "$or": [
                {"productName": {"$regex": regex}},
                {"productDescription": {"$regex": regex}},
                {"shopName": {"$regex": regex}}
            ]
        }
    }
    # Compute average rating from reviews (if available) and average price from embedded products.
    add_fields_stage = {
        "$addFields": {
            "avgRating": {"$cond": {
                "if": {"$gt": [{"$size": "$reviews"}, 0]},
                "then": {"$avg": "$reviews.star"},
                "else": 0
            }},
            "avgPrice": {"$cond": {
                "if": {"$gt": [{"$size": "$product"}, 0]},
                "then": {"$avg": "$product.productPrice"},
                "else": 0
            }}
        }
    }
    # Determine sort field and order.
    if sort_by == "date":
        sort_field, sort_order = "createDate", DESCENDING
    elif sort_by == "price":
        sort_field, sort_order = "avgPrice", ASCENDING
    elif sort_by == "popularity":
        sort_field, sort_order = "soldAmount", DESCENDING
    elif sort_by == "rating":
        sort_field, sort_order = "avgRating", DESCENDING
    else:
        sort_field, sort_order = "createDate", DESCENDING

    sort_stage = {"$sort": {sort_field: sort_order}}
    skip_stage = {"$skip": (page - 1) * page_size}
    limit_stage = {"$limit": page_size}

    pipeline = [match_stage, add_fields_stage, sort_stage, skip_stage, limit_stage]
    results = list(collection.aggregate(pipeline))
    return results

if __name__ == "__main__":
    results = searchProduct("phone", sort_by="price", page=1, page_size=5)
    for product in results:
        print(product)

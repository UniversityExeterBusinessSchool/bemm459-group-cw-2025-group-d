import sys, os, re
from datetime import datetime
from pymongo import DESCENDING
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def getUserRecommendations(userEmail, limit=10):
    """
    Retrieve product recommendations for a user based on the most recent search keyword.
    """
    client = getMongoConnection()
    db = client["marketsync"]
    user_coll = db["Users"]
    prod_coll = db["Products"]

    user = user_coll.find_one({"email": userEmail})
    if not user or "searchHistory" not in user:
        print("User not found or no search history available.")
        return []

    # Use the most recent search keyword.
    search_history = sorted(user["searchHistory"], key=lambda x: x.get("createDate", datetime.min), reverse=True)
    if not search_history:
        print("No search keywords available.")
        return []
    keyword = search_history[0]["keyword"]
    regex = re.compile(keyword, re.IGNORECASE)

    query = {"isDelete": False, "$or": [
        {"productName": {"$regex": regex}},
        {"productDescription": {"$regex": regex}},
        {"shopName": {"$regex": regex}}
    ]}
    recommendations = list(prod_coll.find(query).sort("createDate", DESCENDING).limit(limit))
    return recommendations

if __name__ == "__main__":
    recs = getUserRecommendations("test3@gmail.com", limit=5)
    for rec in recs:
        print(rec)

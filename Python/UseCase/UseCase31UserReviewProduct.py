import sys, os, datetime
from bson.objectid import ObjectId
from pymongo import ReturnDocument

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../Library')))
from databaseConnection import getMongoConnection

def setReviewProduct(productGroupId, pkUser, new_comment, new_star):
    """
    Updates the review for a product group.
      - If a review by the user exists, update the comment and star rating.
      - Otherwise, add a new review entry.
    """
    client = getMongoConnection()
    db = client["marketsync"]
    products_coll = db["Products"]
    current_time = datetime.datetime.now()
    
    # Attempt to update an existing review.
    result = products_coll.update_one(
        {"_id": ObjectId(productGroupId), "reviews.pkUser": pkUser},
        {"$set": {"reviews.$.comment": new_comment,
                  "reviews.$.star": new_star,
                  "reviews.$.updateDate": current_time}}
    )
    if result.modified_count == 0:
        # No review found; add a new review.
        new_review = {
            "pkUser": pkUser,
            "star": new_star,
            "comment": new_comment,
            "createDate": current_time,
            "updateDate": current_time
        }
        result = products_coll.update_one(
            {"_id": ObjectId(productGroupId)},
            {"$push": {"reviews": new_review}}
        )
        print("New review added.")
    else:
        print("Review updated.")
    return result.modified_count

if __name__ == "__main__":
    # Example usage: replace productGroupId with a valid ObjectId string.
    product_group_id = "60d5f4832f8fb814b56fa181"
    setReviewProduct(product_group_id, pkUser=1, new_comment="Great product!", new_star=4.5)

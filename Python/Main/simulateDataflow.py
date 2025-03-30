from datetime import datetime, timedelta
from User import createUser
from Shop import createShop
from Product import createProductGroup, createProductToProductGroup
from Transaction import addProductToCart,cartToPayment, changeTransactionStatus,createLogistic, changeLogisticStatus
from Message import sendUserMessageToShop, sendShopMessageToUser, getMessageBetweenUserAndShop
from initialProductData import productData
def simulate():
    # create 20 user and store it in user[]
    users = []
    for i in range(20):
        # use index to create ascii a-z for name
        firstName = 'firstname'+chr(ord('A') + i % 26)
        lastName = 'lastname'+chr(ord('a') + i % 26)
        user = createUser(f"user{i}@example001.com", "+44", f"0777777777{i}", firstName, lastName, "Male", "password123")
        users.append(user)
    # create 5 shop and store it in shop[]
    shops = []
    for i in range(5):
        shop = createShop(users[i], f"Shop{i}")
        shops.append(shop)
    # create product group using productData and store it in productGroup[]
    # use productData.customise to create product
    productGroups = []
    products = []
    for i in range(len(productData)):
        productGroup = createProductGroup(shops[i % 5], productData[i]["name"], productData[i]["description"], "image.png", [productData[i]["category"]])
        print(productGroup)
        productGroups.append(productGroup)
        for customize in productData[i]["customize"]:
            product = createProductToProductGroup(productGroup, f"{productData[i]['name']} - {customize}", f"{productData[i]['description']} - {customize}", "image1.jpg", productData[i]["price"])
            products.append(product)
    print(products)
    # add 5 product to 1 user cart
    addProductToCart(users[0], products[0], 1)
    addProductToCart(users[0], products[1], 2)
    addProductToCart(users[0], products[2], 3)
    addProductToCart(users[0], products[3], 4)
    addProductToCart(users[0], products[4], 5)
    # use cart to make transaction and save pktransaction
    pkTransaction = cartToPayment(users[0])
    print(pkTransaction)
    # use pktransaction change transaction status to complete
    changeTransactionStatus(pkTransaction, "Wait for payment")
    changeTransactionStatus(pkTransaction, "Completed")
    # create logistic
    deliveryDate = datetime.now() + timedelta(days=7)
    pkLogistic = createLogistic(pkTransaction, deliveryDate)
    # change logistic status to 'complete'
    changeLogisticStatus(pkLogistic, "Shipping")
    changeLogisticStatus(pkLogistic, "Delivered")
    # create message between user1 and shop1 10 message
    for i in range(10):
        if i % 2 == 0:
            sendUserMessageToShop(users[0], shops[0], f"Hello Shop1, this is user1 message {i}")
        else:
            sendShopMessageToUser(users[0], shops[0], f"Hello User1, this is shop1 message {i}")
    # get message
    message = getMessageBetweenUserAndShop(users[0], shops[0])
    print(message)

simulate()
# if __name__ == "__main__":
#     # Code inside this block runs only when the file is executed directly
#     simulate()

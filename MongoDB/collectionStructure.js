{
    Users : {
        id: int, // key for this collection
        pkUser: int, // key from RDBMS
        email: String, // check email format as well
        password: String, // hash
        firstName: String,
        lastName: String,
        fullName: String,
        phoneCountryCode: int,
        phoneNumber: int,
        gender: String, // Male, Female, Unidentify
        address : [
            {
                addressLine1: String,
                addressLine2: String,
                city: String,
                state: String,
                country: String,
                zipCode: int
            }
        ],
        cart: [
            {
                productId: int, // id from mongodb product collection
                pkProduct: int, // key from RDBMS
                quantity: int,
                price: double
            }
        ],
        searchHistory: [
            {
                keyword: String,
                createDate: Datetime
            }
        ],
        emailConfirmationStatus: String, // "Confirmed", "Unconfirmed"
        loginToken : String,
        loginDate: Datetime,
        createDate: Datetime,
        updateDate: Datetime,
        isDelete: Boolean, // True = deactive, False = active
    }
},
{
    Products : {
        id: int, // key for this collection
        pkShop: int, // key from RDBMS
        shopName: String,
        productName: String,
        productDescription: String,
        productImagePath: String,
        productCategory: String[],
        soldAmount: int,
        product: [
            {
                pkProduct: int, // key from RDBMS
                productName: String,
                productDescription: String,
                productImagePath: String[],
                productPrice: double,
                stock: int,
                soldAmount: int,
                createDate: Datetime,
                updateDate: Datetime,
                isDelete: Boolean, // True = deactive, False = active
            }
        ],
        reviews: [
            {
                pkUser: int, // key from RDBMS
                star: float,
                comment: String,
            }
        ],
        createDate: Datetime,
        updateDate: Datetime,
        isDelete: Boolean, // True = deactive, False = active
    }
},
{
    Messages: {
        id: int, // key for this collection
        pkUserBuyer: int, // key from RDBMS
        pkShop: int, // key from RDBMS
        chat: [
            {
                message: String,
                createDate: Datetime,
                updateDate: Datetime,
                isDelete: Boolean, // True = deactive, False = active
            }
        ]
    }
}


use marketsync
// Create Users collection
db.createCollection("Users", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["id", "pkUser", "email", "password", "firstName", "lastName", "fullName", "phoneCountryCode", "phoneNumber", "gender", "address", "cart", "emailConfirmationStatus", "loginToken", "createDate", "updateDate", "isDelete"],
            properties: {
                id: { bsonType: "int", description: "key for this collection" },
                pkUser: { bsonType: "int", description: "key from RDBMS" },
                email: { bsonType: "string", pattern: "^[^\s@]+@[^\s@]+\.[^\s@]+$", description: "must be a valid email format" },
                password: { bsonType: "string", description: "hashed password" },
                firstName: { bsonType: "string" },
                lastName: { bsonType: "string" },
                fullName: { bsonType: "string" },
                phoneCountryCode: { bsonType: "int" },
                phoneNumber: { bsonType: "int" },
                gender: { enum: ["Male", "Female", "Unidentify"] },
                address: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["addressLine1", "city", "state", "country", "zipCode"],
                        properties: {
                            addressLine1: { bsonType: "string" },
                            addressLine2: { bsonType: "string" },
                            city: { bsonType: "string" },
                            state: { bsonType: "string" },
                            country: { bsonType: "string" },
                            zipCode: { bsonType: "int" }
                        }
                    }
                },
                cart: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["productId", "pkProduct", "quantity", "price"],
                        properties: {
                            productId: { bsonType: "int" },
                            pkProduct: { bsonType: "int" },
                            quantity: { bsonType: "int" },
                            price: { bsonType: "double" }
                        }
                    }
                },
                searchHistory: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["keyword", "createDate"],
                        properties: {
                            keyword: { bsonType: "string" },
                            createDate: { bsonType: "date" }
                        }
                    }
                },
                emailConfirmationStatus: { enum: ["Confirmed", "Unconfirmed"] },
                loginToken: { bsonType: "string" },
                createDate: { bsonType: "date" },
                updateDate: { bsonType: "date" },
                isDelete: { bsonType: "bool" }
            }
        }
    }
});

// Create Products collection
db.createCollection("Products", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["id", "pkShop", "shopName", "productName", "productDescription", "productImagePath", "productCategory", "soldAmount", "product", "reviews", "createDate", "updateDate", "isDelete"],
            properties: {
                id: { bsonType: "int", description: "key for this collection" },
                pkShop: { bsonType: "int", description: "key from RDBMS" },
                shopName: { bsonType: "string" },
                productName: { bsonType: "string" },
                productDescription: { bsonType: "string" },
                productImagePath: { bsonType: "string" },
                productCategory: {
                    bsonType: "array",
                    items: { bsonType: "string" }
                },
                soldAmount: { bsonType: "int" },
                product: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["pkProduct", "productName", "productDescription", "productImagePath", "productPrice", "stock", "soldAmount", "createDate", "updateDate", "isDelete"],
                        properties: {
                            pkProduct: { bsonType: "int", description: "key from RDBMS" },
                            productName: { bsonType: "string" },
                            productDescription: { bsonType: "string" },
                            productImagePath: {
                                bsonType: "array",
                                items: { bsonType: "string" }
                            },
                            productPrice: { bsonType: "double" },
                            stock: { bsonType: "int" },
                            soldAmount: { bsonType: "int" },
                            createDate: { bsonType: "date" },
                            updateDate: { bsonType: "date" },
                            isDelete: { bsonType: "bool" }
                        }
                    }
                },
                reviews: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["pkUser", "star", "comment"],
                        properties: {
                            pkUser: { bsonType: "int", description: "key from RDBMS" },
                            star: { bsonType: "double" },
                            comment: { bsonType: "string" }
                        }
                    }
                },
                createDate: { bsonType: "date" },
                updateDate: { bsonType: "date" },
                isDelete: { bsonType: "bool" }
            }
        }
    }
});

// Create Messages collection
db.createCollection("Messages", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["id", "pkUserBuyer", "pkShop", "chat"],
            properties: {
                id: { bsonType: "int", description: "key for this collection" },
                pkUserBuyer: { bsonType: "int", description: "key from RDBMS" },
                pkShop: { bsonType: "int", description: "key from RDBMS" },
                chat: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["message", "createDate", "updateDate", "isDelete"],
                        properties: {
                            message: { bsonType: "string" },
                            createDate: { bsonType: "date" },
                            updateDate: { bsonType: "date" },
                            isDelete: { bsonType: "bool" }
                        }
                    }
                }
            }
        }
    }
});

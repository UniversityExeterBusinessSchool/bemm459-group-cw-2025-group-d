use ("marketsync");

// Create Users collection
db.createCollection("Users", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["pkUser", "email", "password", "firstName", "lastName", "fullName", "phoneCountryCode", "phoneNumber", "gender", "address", "cart", "emailConfirmationStatus", "loginToken", "createDate", "updateDate", "isDelete"],
            properties: {
                pkUser: { bsonType: "int", description: "key from RDBMS" },
                email: { bsonType: "string", pattern: "^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\\.[a-zA-Z]{2,}$", description: "must be a valid email format" },
                password: { bsonType: "string", description: "hashed password" },
                firstName: { bsonType: "string" },
                lastName: { bsonType: "string" },
                fullName: { bsonType: "string" },
                phoneCountryCode: { bsonType: "string" },
                phoneNumber: { bsonType: "string" },
                gender: { bsonType: "string", enum: ["Male", "Female", "Unidentify"] },
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
                            productId: { bsonType: "objectId" },
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
                emailConfirmationStatus: { bsonType: "string", enum: ["Confirmed", "Unconfirmed"] },
                loginToken: { bsonType: "string" },
                createDate: { bsonType: "date" },
                updateDate: { bsonType: "date" },
                isDelete: { bsonType: "bool" }
            }
        }
    }
});
db.Users.createIndex({ pkUser: 1 }, { name: "pkUserIndex", unique: true });
db.Users.createIndex({ email: 1 }, { name: "emailIndex" });
db.Users.createIndex({ phoneNumber: 1 }, { name: "phoneNumberIndex" });

// Create Products collection
db.createCollection("Products", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["pkShop", "shopName", "productName", "productDescription", "productImagePath", "productCategory", "soldAmount", "reviews", "createDate", "updateDate", "isDelete"],
            properties: {
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
db.Products.createIndex({ pkShop: 1 }, { name: "pkShopIndex" });
db.Products.createIndex({ shopName: 1 }, { name: "shopNameIndex" });
db.Products.createIndex({ productName: 1 }, { name: "productNameIndex" });
db.Products.createIndex({ productDescription: 1 }, { name: "productDescriptionIndex" });

// Create Messages collection
db.createCollection("Messages", {
    validator: {
        $jsonSchema: {
            bsonType: "object",
            required: ["pkUserBuyer", "pkShop", "chat"],
            properties: {
                pkUserBuyer: { bsonType: "int", description: "key from RDBMS" },
                pkShop: { bsonType: "int", description: "key from RDBMS" },
                chat: {
                    bsonType: "array",
                    items: {
                        bsonType: "object",
                        required: ["message", "sender", "createDate", "updateDate", "isDelete"],
                        properties: {
                            message: { bsonType: "string" },
                            sender: { bsonType: "string" },
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
db.Messages.createIndex({ pkUserBuyer: 1 }, { name: "pkUserBuyerIndex" });
db.Messages.createIndex({ pkShop: 1 }, { name: "pkShopIndex" });

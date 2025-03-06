-- Insert Trigger for Users table
CREATE OR ALTER TRIGGER trgUsersInsert
ON marketsync.Users
INSTEAD OF INSERT
AS
BEGIN
    INSERT INTO marketsync.Users (email, createDate, updateDate, isDelete) 
    SELECT email, GETDATE(), GETDATE(), 0
    FROM inserted;
END;
GO

-- Insert Trigger for Shops table
CREATE OR ALTER TRIGGER trgShopsInsert
ON marketsync.Shops
INSTEAD OF INSERT
AS
BEGIN
    INSERT INTO marketsync.Shops (shopName, fkUser, createDate, updateDate, isDelete) 
    SELECT shopName, fkUser, GETDATE(), GETDATE(), 0
    FROM inserted;
END;
GO

-- Insert Trigger for Products table
CREATE OR ALTER TRIGGER trgProductsInsert
ON marketsync.Products
INSTEAD OF INSERT
AS
BEGIN
    INSERT INTO marketsync.Products (productName, fkShop, createDate, updateDate, isDelete) 
    SELECT productName, fkShop, GETDATE(), GETDATE(), 0
    FROM inserted;
END;
GO

-- Insert Trigger for Transactions table
CREATE OR ALTER TRIGGER trgTransactionsInsert
ON marketsync.Transactions
INSTEAD OF INSERT
AS
BEGIN
    INSERT INTO marketsync.Transactions (price, currency, fkUserBuyer, fkShop, createDate, updateDate, isDelete) 
    SELECT price, currency, fkUserBuyer, fkShop, GETDATE(), GETDATE(), 0
    FROM inserted;
END;
GO

-- Insert Trigger for TransactionStates table
CREATE OR ALTER TRIGGER trgTransactionStatesInsert
ON marketsync.TransactionStates
INSTEAD OF INSERT
AS
BEGIN
    INSERT INTO marketsync.TransactionStates (fkTransaction, transactionStatus, createDate, updateDate, isDelete) 
    SELECT fkTransaction, transactionStatus, GETDATE(), GETDATE(), 0
    FROM inserted;
END;
GO

-- Insert Trigger for Logistics table
CREATE OR ALTER TRIGGER trgLogisticsInsert
ON marketsync.Logistics
INSTEAD OF INSERT
AS
BEGIN
    INSERT INTO marketsync.Logistics (fkShop, fkUserBuyer, fkTransaction, createDate, updateDate, isDelete) 
    SELECT fkShop, fkUserBuyer, fkTransaction, GETDATE(), GETDATE(), 0
    FROM inserted;
END;
GO

-- Insert Trigger for LogisticStates table
CREATE OR ALTER TRIGGER trgLogisticStatesInsert
ON marketsync.LogisticStates
INSTEAD OF INSERT
AS
BEGIN
    INSERT INTO marketsync.LogisticStates (fkLogistic, logisticStatus, createDate, updateDate, isDelete) 
    SELECT fkLogistic, logisticStatus, GETDATE(), GETDATE(), 0
    FROM inserted;
END;
GO

-- Update Trigger for Users table
CREATE OR ALTER TRIGGER trgUsersUpdate
ON marketsync.Users
INSTEAD OF UPDATE
AS
BEGIN
    UPDATE marketsync.Users
    SET updateDate = GETDATE(),
        email = i.email,
        isDelete = i.isDelete
    FROM marketsync.Users u
    JOIN inserted i ON u.pkUser = i.pkUser;
END;
GO

-- Update Trigger for Shops table
CREATE OR ALTER TRIGGER trgShopsUpdate
ON marketsync.Shops
INSTEAD OF UPDATE
AS
BEGIN
    UPDATE marketsync.Shops
    SET updateDate = GETDATE(),
        shopName = i.shopName,
        fkUser = i.fkUser,
        isDelete = i.isDelete
    FROM marketsync.Shops s
    JOIN inserted i ON s.pkShop = i.pkShop;
END;
GO

-- Update Trigger for Products table
CREATE OR ALTER TRIGGER trgProductsUpdate
ON marketsync.Products
INSTEAD OF UPDATE
AS
BEGIN
    UPDATE marketsync.Products
    SET updateDate = GETDATE(),
        productName = i.productName,
        fkShop = i.fkShop,
        isDelete = i.isDelete
    FROM marketsync.Products p
    JOIN inserted i ON p.pkProduct = i.pkProduct;
END;
GO

-- Update Trigger for Transactions table
CREATE OR ALTER TRIGGER trgTransactionsUpdate
ON marketsync.Transactions
INSTEAD OF UPDATE
AS
BEGIN
    UPDATE marketsync.Transactions
    SET updateDate = GETDATE(),
        price = i.price,
        currency = i.currency,
        fkUserBuyer = i.fkUserBuyer,
        fkShop = i.fkShop,
        isDelete = i.isDelete
    FROM marketsync.Transactions t
    JOIN inserted i ON t.pkTransaction = i.pkTransaction;
END;
GO

-- Update Trigger for TransactionStates table
CREATE OR ALTER TRIGGER trgTransactionStatesUpdate
ON marketsync.TransactionStates
INSTEAD OF UPDATE
AS
BEGIN
    UPDATE marketsync.TransactionStates
    SET updateDate = GETDATE(),
        fkTransaction = i.fkTransaction,
        transactionStatus = i.transactionStatus,
        isDelete = i.isDelete
    FROM marketsync.TransactionStates ts
    JOIN inserted i ON ts.pkTransactionState = i.pkTransactionState;
END;
GO

-- Update Trigger for Logistics table
CREATE OR ALTER TRIGGER trgLogisticsUpdate
ON marketsync.Logistics
INSTEAD OF UPDATE
AS
BEGIN
    UPDATE marketsync.Logistics
    SET updateDate = GETDATE(),
        fkShop = i.fkShop,
        fkUserBuyer = i.fkUserBuyer,
        fkTransaction = i.fkTransaction,
        isDelete = i.isDelete
    FROM marketsync.Logistics l
    JOIN inserted i ON l.pkLogistic = i.pkLogistic;
END;
GO

-- Update Trigger for LogisticStates table
CREATE OR ALTER TRIGGER trgLogisticStatesUpdate
ON marketsync.LogisticStates
INSTEAD OF UPDATE
AS
BEGIN
    UPDATE marketsync.LogisticStates
    SET updateDate = GETDATE(),
        fkLogistic = i.fkLogistic,
        logisticStatus = i.logisticStatus,
        isDelete = i.isDelete
    FROM marketsync.LogisticStates ls
    JOIN inserted i ON ls.pkLogisticState = i.pkLogisticState;
END;
GO

-- Select database
USE marketsync;
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
        fkUserBuyer = i.fkUserBuyer,
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

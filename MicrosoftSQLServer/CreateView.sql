-- Create view for the Users table
CREATE VIEW marketsync.V_Users AS
SELECT * 
FROM marketsync.Users
WHERE isDelete = 0;
GO

-- Create view for the Shops table
CREATE VIEW marketsync.V_Shops AS
SELECT * 
FROM marketsync.Shops
WHERE isDelete = 0;
GO

-- Create view for the Products table
CREATE VIEW marketsync.V_Products AS
SELECT * 
FROM marketsync.Products
WHERE isDelete = 0;
GO

-- Create view for the Transactions table
CREATE VIEW marketsync.V_Transactions AS
SELECT * 
FROM marketsync.Transactions
WHERE isDelete = 0;
GO

-- Create view for the TransactionStates table
CREATE VIEW marketsync.V_TransactionStates AS
SELECT * 
FROM marketsync.TransactionStates
WHERE isDelete = 0;
GO

-- Create view for the Logistics table
CREATE VIEW marketsync.V_Logistics AS
SELECT * 
FROM marketsync.Logistics
WHERE isDelete = 0;
GO

-- Create view for the LogisticStates table
CREATE VIEW marketsync.V_LogisticStates AS
SELECT * 
FROM marketsync.LogisticStates
WHERE isDelete = 0;
GO

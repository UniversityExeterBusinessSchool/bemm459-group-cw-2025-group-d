-- Create view for the User table
CREATE VIEW marketsync.V_User AS
SELECT * FROM marketsync.User
WHERE isDelete = FALSE;

-- Create view for the Shop table
CREATE VIEW marketsync.V_Shop AS
SELECT * FROM marketsync.Shop
WHERE isDelete = FALSE;

-- Create view for the Product table
CREATE VIEW marketsync.V_Product AS
SELECT * FROM marketsync.Product
WHERE isDelete = FALSE;

-- Create view for the Transaction table
CREATE VIEW marketsync.V_Transaction AS
SELECT * FROM marketsync.Transaction
WHERE isDelete = FALSE;

-- Create view for the TransactionState table
CREATE VIEW marketsync.V_TransactionState AS
SELECT * FROM marketsync.TransactionState
WHERE isDelete = FALSE;

-- Create view for the Logistic table
CREATE VIEW marketsync.V_Logistic AS
SELECT * FROM marketsync.Logistic
WHERE isDelete = FALSE;

-- Create view for the LogisticState table
CREATE VIEW marketsync.V_LogisticState AS
SELECT * FROM marketsync.LogisticState
WHERE isDelete = FALSE;

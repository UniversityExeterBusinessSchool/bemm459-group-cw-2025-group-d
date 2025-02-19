-- Function to handle INSERT operations
CREATE OR REPLACE FUNCTION setCreateFields()
RETURNS TRIGGER AS $$
BEGIN
    NEW.createDate = NOW();
    NEW.updateDate = NOW();
    NEW.isDelete = FALSE;
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Function to handle UPDATE operations
CREATE OR REPLACE FUNCTION setUpdateFields()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updateDate = NOW();
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

-- Triggers for Users table
CREATE TRIGGER trgUsersInsert
BEFORE INSERT ON marketsync.Users
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgUsersUpdate
BEFORE UPDATE ON marketsync.Users
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for Shops table
CREATE TRIGGER trgShopsInsert
BEFORE INSERT ON marketsync.Shops
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgShopsUpdate
BEFORE UPDATE ON marketsync.Shops
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for Products table
CREATE TRIGGER trgProductsInsert
BEFORE INSERT ON marketsync.Products
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgProductsUpdate
BEFORE UPDATE ON marketsync.Products
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for Transactions table
CREATE TRIGGER trgTransactionsInsert
BEFORE INSERT ON marketsync.Transactions
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgTransactionsUpdate
BEFORE UPDATE ON marketsync.Transactions
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for TransactionStates table
CREATE TRIGGER trgTransactionStatesInsert
BEFORE INSERT ON marketsync.TransactionStates
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgTransactionStatesUpdate
BEFORE UPDATE ON marketsync.TransactionStates
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for Logistics table
CREATE TRIGGER trgLogisticsInsert
BEFORE INSERT ON marketsync.Logistics
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgLogisticsUpdate
BEFORE UPDATE ON marketsync.Logistics
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for LogisticStates table
CREATE TRIGGER trgLogisticStatesInsert
BEFORE INSERT ON marketsync.LogisticStates
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgLogisticStatesUpdate
BEFORE UPDATE ON marketsync.LogisticStates
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

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

-- Triggers for User table
CREATE TRIGGER trgUserInsert
BEFORE INSERT ON marketsync.User
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgUserUpdate
BEFORE UPDATE ON marketsync.User
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for Shop table
CREATE TRIGGER trgShopInsert
BEFORE INSERT ON marketsync.Shop
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgShopUpdate
BEFORE UPDATE ON marketsync.Shop
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for Product table
CREATE TRIGGER trgProductInsert
BEFORE INSERT ON marketsync.Product
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgProductUpdate
BEFORE UPDATE ON marketsync.Product
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for Transaction table
CREATE TRIGGER trgTransactionInsert
BEFORE INSERT ON marketsync.Transaction
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgTransactionUpdate
BEFORE UPDATE ON marketsync.Transaction
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for TransactionState table
CREATE TRIGGER trgTransactionStateInsert
BEFORE INSERT ON marketsync.TransactionState
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgTransactionStateUpdate
BEFORE UPDATE ON marketsync.TransactionState
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for Logistic table
CREATE TRIGGER trgLogisticInsert
BEFORE INSERT ON marketsync.Logistic
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgLogisticUpdate
BEFORE UPDATE ON marketsync.Logistic
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();

-- Triggers for LogisticState table
CREATE TRIGGER trgLogisticStateInsert
BEFORE INSERT ON marketsync.LogisticState
FOR EACH ROW
EXECUTE FUNCTION setCreateFields();

CREATE TRIGGER trgLogisticStateUpdate
BEFORE UPDATE ON marketsync.LogisticState
FOR EACH ROW
EXECUTE FUNCTION setUpdateFields();
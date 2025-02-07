-- Create the schema marketsync
CREATE SCHEMA marketsync;

-- Create the User table
CREATE TABLE marketsync.User (
  pkUser SERIAL PRIMARY KEY,
  email VARCHAR(200) NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL
);

-- Create the Shop table
CREATE TABLE marketsync.Shop (
  pkShop SERIAL PRIMARY KEY,
  shopName VARCHAR(200) NOT NULL,
  fkUser INT NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkUser) REFERENCES marketsync.User(pkUser)
);

-- Create the Product table
CREATE TABLE marketsync.Product (
  pkProduct SERIAL PRIMARY KEY,
  productName VARCHAR(200) NOT NULL,
  fkShop INT NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkShop) REFERENCES marketsync.Shop(pkShop)
);

-- Create the Transaction table
CREATE TABLE marketsync.Transaction (
  pkTransaction SERIAL PRIMARY KEY,
  price FLOAT NOT NULL,
  currency VARCHAR(200) NOT NULL,
  fkUserBuyer INT NOT NULL,
  fkShop INT NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkUserBuyer) REFERENCES marketsync.User(pkUser),
  FOREIGN KEY (fkShop) REFERENCES marketsync.Shop(pkShop)
);

-- Create the TransactionState table
CREATE TABLE marketsync.TransactionState (
  pkTransactionState SERIAL PRIMARY KEY,
  fkTransaction INT NOT NULL,
  transactionStatus VARCHAR(200) NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkTransaction) REFERENCES marketsync.Transaction(pkTransaction)
);

-- Create the Logistic table
CREATE TABLE marketsync.Logistic (
  pkLogistic SERIAL PRIMARY KEY,
  fkShop INT NOT NULL,
  fkUserBuyer INT NOT NULL,
  fkTransaction INT NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkShop) REFERENCES marketsync.Shop(pkShop),
  FOREIGN KEY (fkUserBuyer) REFERENCES marketsync.User(pkUser),
  FOREIGN KEY (fkTransaction) REFERENCES marketsync.Transaction(pkTransaction)
);

-- Create the LogisticState table
CREATE TABLE marketsync.LogisticState (
  pkLogisticState SERIAL PRIMARY KEY,
  fkLogistic INT NOT NULL,
  logisticStatus VARCHAR(200) NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkLogistic) REFERENCES marketsync.Logistic(pkLogistic)
);

-- Create the Currency table (MasterData)
-- CREATE TABLE marketsync.Currency (
--   pkCurrency SERIAL PRIMARY KEY,
--   currency VARCHAR(200) NOT NULL
-- );

-- Create the TransactionStatus table (MasterData)
-- CREATE TABLE marketsync.TransactionStatus (
--   pkTransactionStatus SERIAL PRIMARY KEY,
--   transactionStatus VARCHAR(200) NOT NULL
-- );

-- Create the LogisticStatus table (MasterData)
-- CREATE TABLE marketsync.LogisticStatus (
--   pkLogisticStatus SERIAL PRIMARY KEY,
--   logisticStatus VARCHAR(200) NOT NULL
-- );

-- Create the ProductCategory table (MasterData)
-- CREATE TABLE marketsync.ProductCategory (
--   pkProductCategory SERIAL PRIMARY KEY,
--   productCategory VARCHAR(200) NOT NULL
-- );
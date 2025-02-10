-- Create the schema marketsync
CREATE SCHEMA marketsync;

-- Create the Users table
CREATE TABLE marketsync.Users (
  pkUser SERIAL PRIMARY KEY,
  email VARCHAR(200) NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL
);

-- Create the Shops table
CREATE TABLE marketsync.Shops (
  pkShop SERIAL PRIMARY KEY,
  shopName VARCHAR(200) NOT NULL,
  fkUser INT NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkUser) REFERENCES marketsync.Users(pkUser)
);

-- Create the Products table
CREATE TABLE marketsync.Products (
  pkProduct SERIAL PRIMARY KEY,
  productName VARCHAR(200) NOT NULL,
  fkShop INT NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkShop) REFERENCES marketsync.Shops(pkShop)
);

-- Create the Transactions table
CREATE TABLE marketsync.Transactions (
  pkTransaction SERIAL PRIMARY KEY,
  price FLOAT NOT NULL,
  currency VARCHAR(200) NOT NULL,
  fkUserBuyer INT NOT NULL,
  fkShop INT NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkUserBuyer) REFERENCES marketsync.Users(pkUser),
  FOREIGN KEY (fkShop) REFERENCES marketsync.Shops(pkShop)
);

-- Create the TransactionStates table
CREATE TABLE marketsync.TransactionStates (
  pkTransactionState SERIAL PRIMARY KEY,
  fkTransaction INT NOT NULL,
  transactionStatus VARCHAR(200) NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkTransaction) REFERENCES marketsync.Transactions(pkTransaction)
);

-- Create the Logistics table
CREATE TABLE marketsync.Logistics (
  pkLogistic SERIAL PRIMARY KEY,
  fkShop INT NOT NULL,
  fkUserBuyer INT NOT NULL,
  fkTransaction INT NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkShop) REFERENCES marketsync.Shops(pkShop),
  FOREIGN KEY (fkUserBuyer) REFERENCES marketsync.Users(pkUser),
  FOREIGN KEY (fkTransaction) REFERENCES marketsync.Transactions(pkTransaction)
);

-- Create the LogisticStates table
CREATE TABLE marketsync.LogisticStates (
  pkLogisticState SERIAL PRIMARY KEY,
  fkLogistic INT NOT NULL,
  logisticStatus VARCHAR(200) NOT NULL,
  createDate TIMESTAMP NOT NULL,
  updateDate TIMESTAMP NOT NULL,
  isDelete BOOLEAN NOT NULL,
  FOREIGN KEY (fkLogistic) REFERENCES marketsync.Logistics(pkLogistic)
);

-- Create the Currencies table (MasterData)
-- CREATE TABLE marketsync.Currencies (
--   pkCurrency SERIAL PRIMARY KEY,
--   currency VARCHAR(200) NOT NULL
-- );

-- Create the TransactionStatuses table (MasterData)
-- CREATE TABLE marketsync.TransactionStatuses (
--   pkTransactionStatus SERIAL PRIMARY KEY,
--   transactionStatus VARCHAR(200) NOT NULL
-- );

-- Create the LogisticStatuses table (MasterData)
-- CREATE TABLE marketsync.LogisticStatuses (
--   pkLogisticStatus SERIAL PRIMARY KEY,
--   logisticStatus VARCHAR(200) NOT NULL
-- );

-- Create the ProductCategories table (MasterData)
-- CREATE TABLE marketsync.ProductCategories (
--   pkProductCategory SERIAL PRIMARY KEY,
--   productCategory VARCHAR(200) NOT NULL
-- );

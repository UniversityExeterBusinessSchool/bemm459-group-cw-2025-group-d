-- Create the schema marketsync
CREATE SCHEMA marketsync;
GO

-- Create the Users table
CREATE TABLE marketsync.Users (
  pkUser INT IDENTITY(1,1) PRIMARY KEY,
  email VARCHAR(200) NOT NULL,
  createDate DATETIME NOT NULL,
  updateDate DATETIME NOT NULL,
  isDelete BIT NOT NULL
);
GO

-- Create the Shops table
CREATE TABLE marketsync.Shops (
  pkShop INT IDENTITY(1,1) PRIMARY KEY,
  shopName VARCHAR(200) NOT NULL,
  fkUser INT NOT NULL,
  createDate DATETIME NOT NULL,
  updateDate DATETIME NOT NULL,
  isDelete BIT NOT NULL,
  FOREIGN KEY (fkUser) REFERENCES marketsync.Users(pkUser)
);
GO

-- Create the Products table
CREATE TABLE marketsync.Products (
  pkProduct INT IDENTITY(1,1) PRIMARY KEY,
  productName VARCHAR(200) NOT NULL,
  fkShop INT NOT NULL,
  createDate DATETIME NOT NULL,
  updateDate DATETIME NOT NULL,
  isDelete BIT NOT NULL,
  FOREIGN KEY (fkShop) REFERENCES marketsync.Shops(pkShop)
);
GO

-- Create the Transactions table
CREATE TABLE marketsync.Transactions (
  pkTransaction INT IDENTITY(1,1) PRIMARY KEY,
  price FLOAT NOT NULL,
  currency VARCHAR(200) NOT NULL,
  fkUserBuyer INT NOT NULL,
  fkShop INT NOT NULL,
  createDate DATETIME NOT NULL,
  updateDate DATETIME NOT NULL,
  isDelete BIT NOT NULL,
  FOREIGN KEY (fkUserBuyer) REFERENCES marketsync.Users(pkUser),
  FOREIGN KEY (fkShop) REFERENCES marketsync.Shops(pkShop)
);
GO

-- Create the TransactionStates table
CREATE TABLE marketsync.TransactionStates (
  pkTransactionState INT IDENTITY(1,1) PRIMARY KEY,
  fkTransaction INT NOT NULL,
  transactionStatus VARCHAR(200) NOT NULL,
  createDate DATETIME NOT NULL,
  updateDate DATETIME NOT NULL,
  isDelete BIT NOT NULL,
  FOREIGN KEY (fkTransaction) REFERENCES marketsync.Transactions(pkTransaction)
);
GO

-- Create the Logistics table
CREATE TABLE marketsync.Logistics (
  pkLogistic INT IDENTITY(1,1) PRIMARY KEY,
  fkShop INT NOT NULL,
  fkUserBuyer INT NOT NULL,
  fkTransaction INT NOT NULL,
  createDate DATETIME NOT NULL,
  updateDate DATETIME NOT NULL,
  isDelete BIT NOT NULL,
  FOREIGN KEY (fkShop) REFERENCES marketsync.Shops(pkShop),
  FOREIGN KEY (fkUserBuyer) REFERENCES marketsync.Users(pkUser),
  FOREIGN KEY (fkTransaction) REFERENCES marketsync.Transactions(pkTransaction)
);
GO

-- Create the LogisticStates table
CREATE TABLE marketsync.LogisticStates (
  pkLogisticState INT IDENTITY(1,1) PRIMARY KEY,
  fkLogistic INT NOT NULL,
  logisticStatus VARCHAR(200) NOT NULL,
  createDate DATETIME NOT NULL,
  updateDate DATETIME NOT NULL,
  isDelete BIT NOT NULL,
  FOREIGN KEY (fkLogistic) REFERENCES marketsync.Logistics(pkLogistic)
);
GO

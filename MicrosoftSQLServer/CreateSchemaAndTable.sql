-- Select database
USE marketsync;
GO

-- Create the schema marketsync
CREATE SCHEMA marketsync;
GO

-- Create the Users table
CREATE TABLE marketsync.Users (
  pkUser INT IDENTITY(1,1) PRIMARY KEY,
  email VARCHAR(200) NOT NULL,
  createDate DATETIME NOT NULL DEFAULT GETDATE(),
  updateDate DATETIME NOT NULL DEFAULT GETDATE(),
  isDelete BIT NOT NULL DEFAULT 0
);
GO

-- Create the Shops table
CREATE TABLE marketsync.Shops (
  pkShop INT IDENTITY(1,1) PRIMARY KEY,
  shopName VARCHAR(200) NOT NULL,
  fkUser INT NOT NULL,
  createDate DATETIME NOT NULL DEFAULT GETDATE(),
  updateDate DATETIME NOT NULL DEFAULT GETDATE(),
  isDelete BIT NOT NULL DEFAULT 0,
  FOREIGN KEY (fkUser) REFERENCES marketsync.Users(pkUser)
);
GO

-- Create the Products table
CREATE TABLE marketsync.Products (
  pkProduct INT IDENTITY(1,1) PRIMARY KEY,
  productName VARCHAR(200) NOT NULL,
  fkShop INT NOT NULL,
  createDate DATETIME NOT NULL DEFAULT GETDATE(),
  updateDate DATETIME NOT NULL DEFAULT GETDATE(),
  isDelete BIT NOT NULL DEFAULT 0,
  FOREIGN KEY (fkShop) REFERENCES marketsync.Shops(pkShop)
);
GO

-- Create the Transactions table
CREATE TABLE marketsync.Transactions (
  pkTransaction INT IDENTITY(1,1) PRIMARY KEY,
  fkUserBuyer INT NOT NULL,
  totalPrice FLOAT NOT NULL,
  createDate DATETIME NOT NULL DEFAULT GETDATE(),
  updateDate DATETIME NOT NULL DEFAULT GETDATE(),
  isDelete BIT NOT NULL DEFAULT 0,
  FOREIGN KEY (fkUserBuyer) REFERENCES marketsync.Users(pkUser),
);
GO

-- Create the TransactionProdcut table
CREATE TABLE marketsync.TransactionProducts (
  pkTransactionProduct INT IDENTITY(1,1) PRIMARY KEY,
  fkTransaction INT NOT NULL,
  fkProduct INT NOT NULL,
  quantity INT NOT NULL,
  price FLOAT NOT NULL,
  createDate DATETIME NOT NULL DEFAULT GETDATE(),
  updateDate DATETIME NOT NULL DEFAULT GETDATE(),
  isDelete BIT NOT NULL DEFAULT 0,
  FOREIGN KEY (fkTransaction) REFERENCES marketsync.Transactions(pkTransaction),
  FOREIGN KEY (fkProduct) REFERENCES marketsync.Products(pkProduct)
);
GO

-- Create the TransactionStates table
CREATE TABLE marketsync.TransactionStates (
  pkTransactionState INT IDENTITY(1,1) PRIMARY KEY,
  fkTransaction INT NOT NULL,
  transactionStatus VARCHAR(200) NOT NULL,
  createDate DATETIME NOT NULL DEFAULT GETDATE(),
  updateDate DATETIME NOT NULL DEFAULT GETDATE(),
  isDelete BIT NOT NULL DEFAULT 0,
  FOREIGN KEY (fkTransaction) REFERENCES marketsync.Transactions(pkTransaction)
);
GO

-- Create the Logistics table
CREATE TABLE marketsync.Logistics (
  pkLogistic INT IDENTITY(1,1) PRIMARY KEY,
  fkTransaction INT NOT NULL,
  expectedDeliveryDate DATETIME NOT NULL,
  createDate DATETIME NOT NULL DEFAULT GETDATE(),
  updateDate DATETIME NOT NULL DEFAULT GETDATE(),
  isDelete BIT NOT NULL DEFAULT 0,
  FOREIGN KEY (fkTransaction) REFERENCES marketsync.Transactions(pkTransaction)
);
GO

-- Create the LogisticStates table
CREATE TABLE marketsync.LogisticStates (
  pkLogisticState INT IDENTITY(1,1) PRIMARY KEY,
  fkLogistic INT NOT NULL,
  logisticStatus VARCHAR(200) NOT NULL,
  createDate DATETIME NOT NULL DEFAULT GETDATE(),
  updateDate DATETIME NOT NULL DEFAULT GETDATE(),
  isDelete BIT NOT NULL DEFAULT 0,
  FOREIGN KEY (fkLogistic) REFERENCES marketsync.Logistics(pkLogistic)
);
GO

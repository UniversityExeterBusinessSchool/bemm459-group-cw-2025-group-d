-- Insert data into Users table
INSERT INTO marketsync.Users (email, createDate, updateDate, isDelete) VALUES
('user1@example.com', GETDATE(), GETDATE(), 0),
('user2@example.com', GETDATE(), GETDATE(), 0),
('user3@example.com', GETDATE(), GETDATE(), 0),
('user4@example.com', GETDATE(), GETDATE(), 0),
('user5@example.com', GETDATE(), GETDATE(), 0),
('user6@example.com', GETDATE(), GETDATE(), 0),
('user7@example.com', GETDATE(), GETDATE(), 0),
('user8@example.com', GETDATE(), GETDATE(), 0),
('user9@example.com', GETDATE(), GETDATE(), 0),
('user10@example.com', GETDATE(), GETDATE(), 0),
('user11@example.com', GETDATE(), GETDATE(), 0),
('user12@example.com', GETDATE(), GETDATE(), 0),
('user13@example.com', GETDATE(), GETDATE(), 0),
('user14@example.com', GETDATE(), GETDATE(), 0),
('user15@example.com', GETDATE(), GETDATE(), 0),
('user16@example.com', GETDATE(), GETDATE(), 0),
('user17@example.com', GETDATE(), GETDATE(), 0),
('user18@example.com', GETDATE(), GETDATE(), 0),
('user19@example.com', GETDATE(), GETDATE(), 0),
('user20@example.com', GETDATE(), GETDATE(), 0);
GO

-- Insert data into Shops table
INSERT INTO marketsync.Shops (shopName, fkUser, createDate, updateDate, isDelete) VALUES
('Shop1', 1, GETDATE(), GETDATE(), 0),
('Shop2', 2, GETDATE(), GETDATE(), 0),
('Shop3', 3, GETDATE(), GETDATE(), 0),
('Shop4', 4, GETDATE(), GETDATE(), 0),
('Shop5', 5, GETDATE(), GETDATE(), 0),
('Shop6', 6, GETDATE(), GETDATE(), 0),
('Shop7', 7, GETDATE(), GETDATE(), 0),
('Shop8', 8, GETDATE(), GETDATE(), 0),
('Shop9', 9, GETDATE(), GETDATE(), 0),
('Shop10', 10, GETDATE(), GETDATE(), 0),
('Shop11', 11, GETDATE(), GETDATE(), 0),
('Shop12', 12, GETDATE(), GETDATE(), 0),
('Shop13', 13, GETDATE(), GETDATE(), 0),
('Shop14', 14, GETDATE(), GETDATE(), 0),
('Shop15', 15, GETDATE(), GETDATE(), 0),
('Shop16', 16, GETDATE(), GETDATE(), 0),
('Shop17', 17, GETDATE(), GETDATE(), 0),
('Shop18', 18, GETDATE(), GETDATE(), 0),
('Shop19', 19, GETDATE(), GETDATE(), 0),
('Shop20', 20, GETDATE(), GETDATE(), 0);
GO

-- Insert data into Products table
INSERT INTO marketsync.Products (productName, fkShop, createDate, updateDate, isDelete) VALUES
('Product1', 1, GETDATE(), GETDATE(), 0),
('Product2', 2, GETDATE(), GETDATE(), 0),
('Product3', 3, GETDATE(), GETDATE(), 0),
('Product4', 4, GETDATE(), GETDATE(), 0),
('Product5', 5, GETDATE(), GETDATE(), 0),
('Product6', 6, GETDATE(), GETDATE(), 0),
('Product7', 7, GETDATE(), GETDATE(), 0),
('Product8', 8, GETDATE(), GETDATE(), 0),
('Product9', 9, GETDATE(), GETDATE(), 0),
('Product10', 10, GETDATE(), GETDATE(), 0),
('Product11', 11, GETDATE(), GETDATE(), 0),
('Product12', 12, GETDATE(), GETDATE(), 0),
('Product13', 13, GETDATE(), GETDATE(), 0),
('Product14', 14, GETDATE(), GETDATE(), 0),
('Product15', 15, GETDATE(), GETDATE(), 0),
('Product16', 16, GETDATE(), GETDATE(), 0),
('Product17', 17, GETDATE(), GETDATE(), 0),
('Product18', 18, GETDATE(), GETDATE(), 0),
('Product19', 19, GETDATE(), GETDATE(), 0),
('Product20', 20, GETDATE(), GETDATE(), 0);
GO

-- Insert data into Transactions table
INSERT INTO marketsync.Transactions (price, currency, fkUserBuyer, fkShop, createDate, updateDate, isDelete) VALUES
(100.0, 'USD', 1, 1, GETDATE(), GETDATE(), 0),
(200.0, 'USD', 2, 2, GETDATE(), GETDATE(), 0),
(300.0, 'USD', 3, 3, GETDATE(), GETDATE(), 0),
(400.0, 'USD', 4, 4, GETDATE(), GETDATE(), 0),
(500.0, 'USD', 5, 5, GETDATE(), GETDATE(), 0),
(600.0, 'USD', 6, 6, GETDATE(), GETDATE(), 0),
(700.0, 'USD', 7, 7, GETDATE(), GETDATE(), 0),
(800.0, 'USD', 8, 8, GETDATE(), GETDATE(), 0),
(900.0, 'USD', 9, 9, GETDATE(), GETDATE(), 0),
(1000.0, 'USD', 10, 10, GETDATE(), GETDATE(), 0),
(1100.0, 'USD', 11, 11, GETDATE(), GETDATE(), 0),
(1200.0, 'USD', 12, 12, GETDATE(), GETDATE(), 0),
(1300.0, 'USD', 13, 13, GETDATE(), GETDATE(), 0),
(1400.0, 'USD', 14, 14, GETDATE(), GETDATE(), 0),
(1500.0, 'USD', 15, 15, GETDATE(), GETDATE(), 0),
(1600.0, 'USD', 16, 16, GETDATE(), GETDATE(), 0),
(1700.0, 'USD', 17, 17, GETDATE(), GETDATE(), 0),
(1800.0, 'USD', 18, 18, GETDATE(), GETDATE(), 0),
(1900.0, 'USD', 19, 19, GETDATE(), GETDATE(), 0),
(2000.0, 'USD', 20, 20, GETDATE(), GETDATE(), 0);
GO

-- Insert data into TransactionStates table
INSERT INTO marketsync.TransactionStates (fkTransaction, transactionStatus, createDate, updateDate, isDelete) VALUES
(1, 'Pending', GETDATE(), GETDATE(), 0),
(2, 'Completed', GETDATE(), GETDATE(), 0),
(3, 'Cancelled', GETDATE(), GETDATE(), 0),
(4, 'Pending', GETDATE(), GETDATE(), 0),
(5, 'Completed', GETDATE(), GETDATE(), 0),
(6, 'Cancelled', GETDATE(), GETDATE(), 0),
(7, 'Pending', GETDATE(), GETDATE(), 0),
(8, 'Completed', GETDATE(), GETDATE(), 0),
(9, 'Cancelled', GETDATE(), GETDATE(), 0),
(10, 'Pending', GETDATE(), GETDATE(), 0),
(11, 'Completed', GETDATE(), GETDATE(), 0),
(12, 'Cancelled', GETDATE(), GETDATE(), 0),
(13, 'Pending', GETDATE(), GETDATE(), 0),
(14, 'Completed', GETDATE(), GETDATE(), 0),
(15, 'Cancelled', GETDATE(), GETDATE(), 0),
(16, 'Pending', GETDATE(), GETDATE(), 0),
(17, 'Completed', GETDATE(), GETDATE(), 0),
(18, 'Cancelled', GETDATE(), GETDATE(), 0),
(19, 'Pending', GETDATE(), GETDATE(), 0),
(20, 'Completed', GETDATE(), GETDATE(), 0);
GO

-- Insert data into Logistics table (continued)
INSERT INTO marketsync.Logistics (fkShop, fkUserBuyer, fkTransaction, createDate, updateDate, isDelete) VALUES
(5, 5, 5, GETDATE(), GETDATE(), 0),
(6, 6, 6, GETDATE(), GETDATE(), 0),
(7, 7, 7, GETDATE(), GETDATE(), 0),
(8, 8, 8, GETDATE(), GETDATE(), 0),
(9, 9, 9, GETDATE(), GETDATE(), 0),
(10, 10, 10, GETDATE(), GETDATE(), 0),
(11, 11, 11, GETDATE(), GETDATE(), 0),
(12, 12, 12, GETDATE(), GETDATE(), 0),
(13, 13, 13, GETDATE(), GETDATE(), 0),
(14, 14, 14, GETDATE(), GETDATE(), 0),
(15, 15, 15, GETDATE(), GETDATE(), 0),
(16, 16, 16, GETDATE(), GETDATE(), 0),
(17, 17, 17, GETDATE(), GETDATE(), 0),
(18, 18, 18, GETDATE(), GETDATE(), 0),
(19, 19, 19, GETDATE(), GETDATE(), 0),
(20, 20, 20, GETDATE(), GETDATE(), 0);
GO

-- Insert data into LogisticStates table
INSERT INTO marketsync.LogisticStates (fkLogistic, logisticStatus, createDate, updateDate, isDelete) VALUES
(1, 'In Transit', GETDATE(), GETDATE(), 0),
(2, 'Delivered', GETDATE(), GETDATE(), 0),
(3, 'Cancelled', GETDATE(), GETDATE(), 0),
(4, 'In Transit', GETDATE(), GETDATE(), 0),
(5, 'Delivered', GETDATE(), GETDATE(), 0),
(6, 'Cancelled', GETDATE(), GETDATE(), 0),
(7, 'In Transit', GETDATE(), GETDATE(), 0),
(8, 'Delivered', GETDATE(), GETDATE(), 0),
(9, 'Cancelled', GETDATE(), GETDATE(), 0),
(10, 'In Transit', GETDATE(), GETDATE(), 0),
(11, 'Delivered', GETDATE(), GETDATE(), 0),
(12, 'Cancelled', GETDATE(), GETDATE(), 0),
(13, 'In Transit', GETDATE(), GETDATE(), 0),
(14, 'Delivered', GETDATE(), GETDATE(), 0),
(15, 'Cancelled', GETDATE(), GETDATE(), 0),
(16, 'In Transit', GETDATE(), GETDATE(), 0),
(17, 'Delivered', GETDATE(), GETDATE(), 0),
(18, 'Cancelled', GETDATE(), GETDATE(), 0),
(19, 'In Transit', GETDATE(), GETDATE(), 0),
(20, 'Delivered', GETDATE(), GETDATE(), 0);
GO

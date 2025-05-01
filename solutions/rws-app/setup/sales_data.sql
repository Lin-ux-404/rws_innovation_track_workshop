-- Sample Sales Data schema and data

-- Create SalesRegions table
CREATE TABLE SalesRegions (
    RegionID INT PRIMARY KEY,
    RegionName NVARCHAR(50) NOT NULL,
    RegionManager NVARCHAR(100) NULL,
    HeadquartersLocation NVARCHAR(100) NULL
);

-- Create Products table
CREATE TABLE Products (
    ProductID INT PRIMARY KEY,
    ProductName NVARCHAR(100) NOT NULL,
    ProductCategory NVARCHAR(50) NOT NULL,
    UnitPrice DECIMAL(10, 2) NOT NULL,
    ProductLine NVARCHAR(50) NULL,
    LaunchDate DATE NULL
);

-- Create Customers table
CREATE TABLE Customers (
    CustomerID INT PRIMARY KEY,
    CustomerName NVARCHAR(100) NOT NULL,
    ContactName NVARCHAR(100) NULL,
    CustomerType NVARCHAR(50) NOT NULL,
    RegionID INT NOT NULL,
    Country NVARCHAR(50) NOT NULL,
    City NVARCHAR(50) NULL,
    FOREIGN KEY (RegionID) REFERENCES SalesRegions(RegionID)
);

-- Create SalesData table
CREATE TABLE SalesData (
    SalesID INT PRIMARY KEY,
    ProductID INT NOT NULL,
    CustomerID INT NOT NULL,
    SalesDate DATE NOT NULL,
    Quantity INT NOT NULL,
    UnitsSold INT NOT NULL,
    TotalAmount DECIMAL(15, 2) NOT NULL,
    DiscountApplied DECIMAL(5, 2) NULL,
    SalesChannel NVARCHAR(50) NULL,
    PromotionID INT NULL,
    FOREIGN KEY (ProductID) REFERENCES Products(ProductID),
    FOREIGN KEY (CustomerID) REFERENCES Customers(CustomerID)
);

-- Insert data into SalesRegions
INSERT INTO SalesRegions (RegionID, RegionName, RegionManager, HeadquartersLocation) VALUES
(1, 'Europe', 'Anna Müller', 'Amsterdam'),
(2, 'North America', 'John Smith', 'Chicago'),
(3, 'APAC', 'Li Wei', 'Singapore'),
(4, 'LATAM', 'Carlos Vega', 'Mexico City'),
(5, 'Middle East', 'Fatima Al-Saud', 'Dubai');

-- Insert data into Products
INSERT INTO Products (ProductID, ProductName, ProductCategory, UnitPrice, ProductLine, LaunchDate) VALUES
(101, 'Pepper Seeds XF-1', 'Seeds', 12.99, 'Vegetables', '2023-01-15'),
(102, 'Tomato Seeds TR-23', 'Seeds', 9.99, 'Vegetables', '2022-11-20'),
(103, 'Cucumber Seeds CX-5', 'Seeds', 8.50, 'Vegetables', '2023-03-10'),
(104, 'Lettuce Seeds LT-7', 'Seeds', 7.99, 'Vegetables', '2022-09-05'),
(105, 'Melon Seeds ML-9', 'Seeds', 15.75, 'Fruits', '2023-02-28'),
(106, 'Strawberry Seeds SB-3', 'Seeds', 18.25, 'Fruits', '2022-08-12'),
(107, 'Basil Seeds BS-1', 'Seeds', 6.50, 'Herbs', '2023-04-01'),
(108, 'Carrot Seeds CR-6', 'Seeds', 8.25, 'Vegetables', '2022-10-15'),
(109, 'Onion Seeds ON-4', 'Seeds', 7.75, 'Vegetables', '2023-01-30'),
(110, 'Spinach Seeds SP-8', 'Seeds', 6.99, 'Vegetables', '2022-12-10');

-- Insert data into Customers
INSERT INTO Customers (CustomerID, CustomerName, ContactName, CustomerType, RegionID, Country, City) VALUES
(1001, 'Green Fields Farm', 'Michael Johnson', 'Distributor', 1, 'Netherlands', 'Rotterdam'),
(1002, 'Sunshine Gardens', 'Sarah Williams', 'Direct Grower', 2, 'United States', 'California'),
(1003, 'Eastern Harvest Ltd', 'Hiroshi Tanaka', 'Distributor', 3, 'Japan', 'Tokyo'),
(1004, 'Fertile Grounds', 'Maria Rodriguez', 'Direct Grower', 4, 'Brazil', 'Sao Paulo'),
(1005, 'Desert Bloom Agricultural', 'Hassan Al-Farsi', 'Distributor', 5, 'UAE', 'Abu Dhabi'),
(1006, 'Northern Plantations', 'Emma Johansson', 'Direct Grower', 1, 'Sweden', 'Stockholm'),
(1007, 'Midwest Farmers Cooperative', 'Robert Brown', 'Cooperative', 2, 'United States', 'Illinois'),
(1008, 'Pacific Agro Solutions', 'James Wong', 'Distributor', 3, 'Australia', 'Sydney'),
(1009, 'Southern Crops', 'Alejandro Gomez', 'Direct Grower', 4, 'Argentina', 'Buenos Aires'),
(1010, 'Mediterranean Growers', 'Sofia Papas', 'Cooperative', 1, 'Greece', 'Athens');

-- Insert data into SalesData (past year)
INSERT INTO SalesData (SalesID, ProductID, CustomerID, SalesDate, Quantity, UnitsSold, TotalAmount, DiscountApplied, SalesChannel, PromotionID) VALUES
(10001, 101, 1001, '2023-06-15', 50, 500, 6495.00, 0.05, 'Direct', NULL),
(10002, 102, 1002, '2023-07-03', 30, 300, 2997.00, NULL, 'Online', NULL),
(10003, 103, 1003, '2023-08-12', 45, 450, 3825.00, NULL, 'Direct', NULL),
(10004, 104, 1004, '2023-09-05', 25, 250, 1997.50, NULL, 'Distributor', NULL),
(10005, 105, 1005, '2023-10-18', 40, 400, 6300.00, NULL, 'Direct', NULL),
(10006, 106, 1006, '2023-11-22', 35, 350, 6387.50, NULL, 'Online', 201),
(10007, 107, 1007, '2023-12-07', 60, 600, 3900.00, NULL, 'Direct', NULL),
(10008, 108, 1008, '2024-01-14', 55, 550, 4537.50, NULL, 'Distributor', NULL),
(10009, 109, 1009, '2024-02-03', 70, 700, 5425.00, NULL, 'Direct', 202),
(10010, 110, 1010, '2024-03-11', 65, 650, 4543.50, NULL, 'Online', NULL),
(10011, 101, 1002, '2024-03-28', 45, 450, 5845.50, NULL, 'Direct', NULL),
(10012, 102, 1003, '2024-04-09', 40, 400, 3996.00, NULL, 'Distributor', NULL),
(10013, 103, 1004, '2024-04-17', 50, 500, 4250.00, NULL, 'Online', 203),
(10014, 104, 1005, '2024-04-25', 35, 350, 2796.50, NULL, 'Direct', NULL),
(10015, 105, 1006, '2024-05-02', 55, 550, 8662.50, NULL, 'Distributor', NULL);
GO

-- Create a view for easy access to sales data with product and customer info
CREATE VIEW vw_SalesSummary AS
SELECT 
    s.SalesID,
    s.SalesDate,
    p.ProductName,
    p.ProductCategory,
    c.CustomerName,
    c.CustomerType,
    r.RegionName,
    c.Country,
    s.Quantity,
    s.UnitsSold,
    s.TotalAmount,
    s.SalesChannel
FROM 
    SalesData s
    JOIN Products p ON s.ProductID = p.ProductID
    JOIN Customers c ON s.CustomerID = c.CustomerID
    JOIN SalesRegions r ON c.RegionID = r.RegionID
GO
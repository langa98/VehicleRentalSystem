/*CREATE DATABASE VehicleRental;
GO
*/

USE VehicleRental;
GO

IF NOT EXISTS (
    SELECT *
    FROM sys.tables
    WHERE name = 'Customer'
)
BEGIN
CREATE TABLE Customer(
	CustomerID INT IDENTITY(1,1) PRIMARY KEY,
	FirtName NVARCHAR(50) NOT NULL,
	LastName NVARCHAR(50)NOT NULL,
	PhoneNumber NVARCHAR(20) ,
	Email NVARCHAR(50) UNIQUE NOT NULL,
	DriversLicenseNo NVARCHAR(30)
);
END;
GO


IF NOT EXISTS (
    SELECT *
    FROM sys.tables
    WHERE name = 'VehicleCategory'
)
BEGIN
CREATE TABLE VehicleCategory(
	CategoryID INT IDENTITY(1,1) PRIMARY KEY,
	CategoryName NVARCHAR(50) NOT NULL,
	DailyRate DECIMAL(10,2) NOT NULL CHECK (DailyRate>0)
);
END;
GO

IF NOT EXISTS (
    SELECT *
    FROM sys.tables
    WHERE name = 'Vehicle'
)
BEGIN
CREATE TABLE Vehicle(
	VehicleID INT IDENTITY(1,1) PRIMARY KEY,
	RegistrationNo NVARCHAR(20) UNIQUE NOT NULL,
	Make NVARCHAR(20) NOT NULL,
	Model NVARCHAR(30) NOT NULL,
	[Year]  INT NOT NULL,
	[Status] NVARCHAR(20) NOT NULL,
	CategoryID INT NOT NULL,
	FOREIGN KEY (CategoryID) 
		REFERENCES VehicleCategory(CategoryID)
	
);
END;
GO

IF NOT EXISTS (
    SELECT *
    FROM sys.tables
    WHERE name = 'Booking'
)
BEGIN
CREATE TABLE Booking(
	BookingID INT IDENTITY(1,1) PRIMARY KEY,
	StartDate DATE NOT NULL,
	EndDate DATE NOT NULL,
	BookingStatus VARCHAR(30) NOT NULL,
	CustomerID INT NOT NULL,
    VehicleID INT NOT NULL,
	FOREIGN KEY(CustomerID)
		REFERENCES Customer(CustomerID),
	FOREIGN KEY(VehicleID)
		REFERENCES Vehicle(VehicleID),

		CHECK (EndDate >= StartDate)
);
END;
GO

IF NOT EXISTS (
    SELECT *
    FROM sys.tables
    WHERE name = 'Payment'
)
BEGIN
CREATE TABLE Payment(
	PaymentID INT IDENTITY(1,1) PRIMARY KEY,
	Amount DECIMAL(10,2) NOT NULL CHECK(Amount>0),
	PaymentDate DATE NOT NULL,
	PaymentMethod NVARCHAR(30) NOT NULL,
	BookingID INT NOT NULL,
	FOREIGN KEY(BookingID)
		REFERENCES Booking(BookingID)
);
END;
GO

IF NOT EXISTS (
    SELECT *
    FROM sys.tables
    WHERE name = 'User'
)
BEGIN
CREATE TABLE [User](
	UserID INT IDENTITY(1,1) PRIMARY KEY,
	UserName NVARCHAR(50) ,
	PasswordHash NVARCHAR(100) NOT NULL,
	[Role] VARCHAR(15) NOT NULL,
	CustomerID INT NULL,
	FOREIGN KEY(CustomerID)
		REFERENCES Customer(CustomerID),
		
		CHECK ([Role] IN ('Admin', 'Customer'))
);
END;
GO
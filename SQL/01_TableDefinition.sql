
IF DB_ID('VehicleRental') IS NULL
BEGIN
    CREATE DATABASE VehicleRental;
END;
GO

USE VehicleRental;
GO

IF NOT EXISTS (
    SELECT *
    FROM sys.schemas
    WHERE name = 'Rental'
)
BEGIN
    EXEC('CREATE SCHEMA Rental');
END;
GO


IF NOT EXISTS (
    SELECT *
    FROM sys.tables t
    INNER JOIN sys.schemas s
        ON t.schema_id = s.schema_id
    WHERE t.name = 'Customer'
      AND s.name = 'Rental'
)
BEGIN

    CREATE TABLE Rental.Customer
    (
        CustomerID INT IDENTITY(1,1) PRIMARY KEY,

        FirstName NVARCHAR(50) NOT NULL,

        LastName NVARCHAR(50) NOT NULL,

		IDNumber CHAR(13) NOT NULL UNIQUE,

        PhoneNumber NVARCHAR(20),

        Email NVARCHAR(100) UNIQUE NOT NULL,

        DriversLicenseNo NVARCHAR(30) UNIQUE,

		CONSTRAINT CK_Customer_IDNumber_Digits
        CHECK (IDNumber NOT LIKE '%[^0-9]%')
    );

END;
GO

IF NOT EXISTS (
    SELECT *
    FROM sys.tables t
    INNER JOIN sys.schemas s
        ON t.schema_id = s.schema_id
    WHERE t.name = 'VehicleCategory'
      AND s.name = 'Rental'
)
BEGIN

    CREATE TABLE Rental.VehicleCategory
    (
        CategoryID INT IDENTITY(1,1) PRIMARY KEY,

        CategoryName NVARCHAR(50) NOT NULL UNIQUE,

        DailyRate DECIMAL(10,2) NOT NULL
            CHECK (DailyRate > 0)
    );

END;
GO

IF NOT EXISTS (
    SELECT *
    FROM sys.tables t
    INNER JOIN sys.schemas s
        ON t.schema_id = s.schema_id
    WHERE t.name = 'Vehicle'
      AND s.name = 'Rental'
)
BEGIN

    CREATE TABLE Rental.Vehicle
    (
        VehicleID INT IDENTITY(1,1) PRIMARY KEY,

        RegistrationNo NVARCHAR(20) UNIQUE NOT NULL,

        Make NVARCHAR(20) NOT NULL,

        Model NVARCHAR(30) NOT NULL,

        [Year] INT NOT NULL,

        [Status] NVARCHAR(20) NOT NULL,

        CategoryID INT NOT NULL,

        FOREIGN KEY (CategoryID)
            REFERENCES Rental.VehicleCategory(CategoryID),

		CONSTRAINT CK_Vehicle_Status
			CHECK ([Status] IN ('Available', 'Rented', 'Maintenance'))
    );

END;
GO

IF NOT EXISTS (
    SELECT *
    FROM sys.tables t
    INNER JOIN sys.schemas s
        ON t.schema_id = s.schema_id
    WHERE t.name = 'Booking'
      AND s.name = 'Rental'
)
BEGIN

    CREATE TABLE Rental.Booking
    (
        BookingID INT IDENTITY(1,1) PRIMARY KEY,

        CustomerID INT NOT NULL,

        VehicleID INT NOT NULL,

        StartDate DATE NOT NULL,

        EndDate DATE NOT NULL,

        BookingStatus VARCHAR(30) NOT NULL,

        FOREIGN KEY (CustomerID)
            REFERENCES Rental.Customer(CustomerID),

        FOREIGN KEY (VehicleID)
            REFERENCES Rental.Vehicle(VehicleID),

        CHECK (EndDate >= StartDate),

		CONSTRAINT CK_Booking_Status
			CHECK (BookingStatus IN ('Pending', 'Confirmed', 'Completed', 'Cancelled'))
    );

END;
GO

IF NOT EXISTS (
    SELECT *
    FROM sys.tables t
    INNER JOIN sys.schemas s
        ON t.schema_id = s.schema_id
    WHERE t.name = 'Payment'
      AND s.name = 'Rental'
)
BEGIN

    CREATE TABLE Rental.Payment
    (
        PaymentID INT IDENTITY(1,1) PRIMARY KEY,

        Amount DECIMAL(10,2) NOT NULL
            CHECK (Amount > 0),

        PaymentDate DATE NOT NULL,

        PaymentMethod NVARCHAR(30) NOT NULL,

        BookingID INT NOT NULL,

        FOREIGN KEY (BookingID)
            REFERENCES Rental.Booking(BookingID),

		CONSTRAINT CK_Payment_Method
			CHECK (PaymentMethod IN ('Cash', 'Card', 'EFT'))
 );
END;
GO


IF NOT EXISTS (
    SELECT *
    FROM sys.tables t
    INNER JOIN sys.schemas s
        ON t.schema_id = s.schema_id
    WHERE t.name = 'User'
      AND s.name = 'Rental'
)
BEGIN

    CREATE TABLE Rental.[User]
    (
        UserID INT IDENTITY(1,1) PRIMARY KEY,

        Username NVARCHAR(50) NOT NULL UNIQUE,

        PasswordHash NVARCHAR(100) NOT NULL,

        [Role] VARCHAR(15) NOT NULL,

        CustomerID INT NULL,

        FOREIGN KEY (CustomerID)
            REFERENCES Rental.Customer(CustomerID),

        CONSTRAINT CK_User_Role
			CHECK ([Role] IN ('Admin', 'Customer'))
    );
END;
GO


SELECT
    s.name AS SchemaName,
    t.name AS TableName
FROM sys.tables t
INNER JOIN sys.schemas s
    ON t.schema_id = s.schema_id
WHERE s.name = 'Rental'
ORDER BY t.name;
GO

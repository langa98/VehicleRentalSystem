/* VehicleRental - full setup in one script.
   Safe to run more than once: sample data is loaded only the first time, so customers/vehicles you delete stay deleted. Run it in SSMS / VS Code (SQL Server extension) as a whole.
   PART 1 builds everything (tables, sample data, indexes, views, demo logins).
   PART 2 runs the reports and login lookups (read-only). */


/* ======================================================================
   PART 1A - TABLES (was 01_TableDefinition.sql)
   ====================================================================== */
IF DB_ID('VehicleRental') IS NULL
BEGIN
    CREATE DATABASE VehicleRental;
END;
GO

USE VehicleRental;
GO
-- A database that already has its tables is treated as already set up, so sample data is never re-added.
IF OBJECT_ID('Rental.Customer', 'U') IS NOT NULL AND NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'SampleDataLoaded')
    EXEC sp_addextendedproperty @name = N'SampleDataLoaded', @value = N'1';
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
			CHECK ([Role] IN ('Admin', 'Staff', 'Customer'))
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

/* ======================================================================
   PART 1B - SAMPLE DATA + CONSTRAINT NOTES (was 02_SampleData_Testing.sql)
   ====================================================================== */
USE VehicleRental;
GO


-- CUSTOMER SAMPLE DATA

IF NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'SampleDataLoaded')
INSERT INTO Rental.Customer
    (FirstName, LastName, IDNumber, PhoneNumber, Email, DriversLicenseNo)
SELECT
    v.FirstName,
    v.LastName,
    v.IDNumber,
    v.PhoneNumber,
    v.Email,
    v.DriversLicenseNo
FROM
(
    VALUES
        ('Thabo', 'Mokoena', '9001015009087', '0821234567', 'thabo.mokoena@email.com', 'DL10001'),
        ('Lerato', 'Molefe', '9505050123086', '0832345678', 'lerato.molefe@email.com', 'DL10002'),
        ('Daniel', 'Smith', '8807125012084', '0713456789', 'daniel.smith@email.com', 'DL10003'),
        ('Naledi', 'Dlamini', '0102030087089', '0794567890', 'naledi.dlamini@email.com', 'DL10004'),
        ('James', 'Williams', '9209095065081', '0765678901', 'james.williams@email.com', 'DL10005')
) AS v(FirstName, LastName, IDNumber, PhoneNumber, Email, DriversLicenseNo)
WHERE NOT EXISTS
(
    SELECT 1
    FROM Rental.Customer AS c
    WHERE c.IDNumber = v.IDNumber
);
GO

SELECT *
FROM Rental.Customer;
GO



-- VEHICLE CATEGORY SAMPLE DATA

IF NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'SampleDataLoaded')
INSERT INTO Rental.VehicleCategory
    (CategoryName, DailyRate)
SELECT
    v.CategoryName,
    v.DailyRate
FROM
(
    VALUES
        ('Economy', 350.00),
        ('Sedan', 500.00),
        ('SUV', 750.00),
        ('Luxury', 1200.00)
) AS v(CategoryName, DailyRate)
WHERE NOT EXISTS
(
    SELECT 1
    FROM Rental.VehicleCategory AS vc
    WHERE vc.CategoryName = v.CategoryName
);
GO

SELECT *
FROM Rental.VehicleCategory;
GO



-- VEHICLE SAMPLE DATA

IF NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'SampleDataLoaded')
INSERT INTO Rental.Vehicle
    (RegistrationNo, Make, Model, [Year], [Status], CategoryID)
SELECT
    v.RegistrationNo,
    v.Make,
    v.Model,
    v.[Year],
    v.[Status],
    vc.CategoryID
FROM
(
    VALUES
        ('CA123456', 'Toyota', 'Starlet', 2023, 'Available', 'Economy'),
        ('GP456789', 'Volkswagen', 'Polo', 2022, 'Available', 'Economy'),
        ('NW789012', 'Toyota', 'Corolla', 2024, 'Rented', 'Sedan'),
        ('EC234567', 'BMW', '3 Series', 2023, 'Available', 'Sedan'),
        ('FS567890', 'Toyota', 'Fortuner', 2024, 'Available', 'SUV'),
        ('KZN345678', 'Ford', 'Everest', 2023, 'Maintenance', 'SUV'),
        ('GP678901', 'Mercedes-Benz', 'C-Class', 2024, 'Available', 'Luxury')
) AS v(RegistrationNo, Make, Model, [Year], [Status], CategoryName)

INNER JOIN Rental.VehicleCategory AS vc
    ON vc.CategoryName = v.CategoryName

WHERE NOT EXISTS
(
    SELECT 1
    FROM Rental.Vehicle AS existingVehicle
    WHERE existingVehicle.RegistrationNo = v.RegistrationNo
);
GO

SELECT *
FROM Rental.Vehicle;
GO


-- BOOKING SAMPLE DATA

IF NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'SampleDataLoaded')
INSERT INTO Rental.Booking
    (CustomerID, VehicleID, StartDate, EndDate, BookingStatus)

SELECT
    c.CustomerID,
    v.VehicleID,
    b.StartDate,
    b.EndDate,
    b.BookingStatus

FROM
(
    VALUES
        ('9001015009087', 'CA123456', '2026-09-05', '2026-09-08', 'Confirmed'),
        ('9505050123086', 'NW789012', '2026-08-20', '2026-08-23', 'Completed'),
        ('8807125012084', 'FS567890', '2026-09-10', '2026-09-15', 'Pending'),
        ('0102030087089', 'EC234567', '2026-08-25', '2026-08-28', 'Completed'),
        ('9209095065081', 'GP678901', '2026-09-20', '2026-09-25', 'Cancelled')
) AS b(IDNumber, RegistrationNo, StartDate, EndDate, BookingStatus)

INNER JOIN Rental.Customer AS c
    ON c.IDNumber = b.IDNumber

INNER JOIN Rental.Vehicle AS v
    ON v.RegistrationNo = b.RegistrationNo

WHERE NOT EXISTS
(
    SELECT 1
    FROM Rental.Booking AS existingBooking
    WHERE existingBooking.CustomerID = c.CustomerID
      AND existingBooking.VehicleID = v.VehicleID
      AND existingBooking.StartDate = b.StartDate
      AND existingBooking.EndDate = b.EndDate
);
GO

SELECT *
FROM Rental.Booking;
GO


-- PAYMENT SAMPLE DATA

IF NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'SampleDataLoaded')
INSERT INTO Rental.Payment
    (Amount, PaymentDate, PaymentMethod, BookingID)

SELECT
    p.Amount,
    p.PaymentDate,
    p.PaymentMethod,
    b.BookingID

FROM
(
    VALUES
        ('9001015009087', 'CA123456', '2026-09-05', '2026-09-08',
         1050.00, '2026-09-01', 'Card'),

        ('9505050123086', 'NW789012', '2026-08-20', '2026-08-23',
         1500.00, '2026-08-20', 'EFT'),

        ('0102030087089', 'EC234567', '2026-08-25', '2026-08-28',
         1500.00, '2026-08-25', 'Cash')
) AS p(IDNumber, RegistrationNo, StartDate, EndDate,
       Amount, PaymentDate, PaymentMethod)

INNER JOIN Rental.Customer AS c
    ON c.IDNumber = p.IDNumber

INNER JOIN Rental.Vehicle AS v
    ON v.RegistrationNo = p.RegistrationNo

INNER JOIN Rental.Booking AS b
    ON b.CustomerID = c.CustomerID
   AND b.VehicleID = v.VehicleID
   AND b.StartDate = p.StartDate
   AND b.EndDate = p.EndDate

WHERE NOT EXISTS
(
    SELECT 1
    FROM Rental.Payment AS existingPayment
    WHERE existingPayment.BookingID = b.BookingID
      AND existingPayment.Amount = p.Amount
      AND existingPayment.PaymentDate = p.PaymentDate
      AND existingPayment.PaymentMethod = p.PaymentMethod
);
GO

SELECT *
FROM Rental.Payment;
GO


-- USER SAMPLE DATA

IF NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'SampleDataLoaded')
INSERT INTO Rental.[User]
    (Username, PasswordHash, [Role], CustomerID)
SELECT
    'admin',
    'HASH_ADMIN',
    'Admin',
    NULL
WHERE NOT EXISTS
(
    SELECT 1
    FROM Rental.[User]
    WHERE Username = 'admin'
);
GO


IF NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'SampleDataLoaded')
INSERT INTO Rental.[User]
    (Username, PasswordHash, [Role], CustomerID)

SELECT
    u.Username,
    u.PasswordHash,
    'Customer',
    c.CustomerID

FROM
(
    VALUES
        ('thabo', 'HASH_THABO', '9001015009087'),
        ('lerato', 'HASH_LERATO', '9505050123086'),
        ('daniel', 'HASH_DANIEL', '8807125012084'),
        ('naledi', 'HASH_NALEDI', '0102030087089'),
        ('james', 'HASH_JAMES', '9209095065081')
) AS u(Username, PasswordHash, IDNumber)

INNER JOIN Rental.Customer AS c
    ON c.IDNumber = u.IDNumber

WHERE NOT EXISTS
(
    SELECT 1
    FROM Rental.[User] AS existingUser
    WHERE existingUser.Username = u.Username
);
GO


-- Staff account

IF NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'SampleDataLoaded')
INSERT INTO Rental.[User]
    (Username, PasswordHash, [Role], CustomerID)
SELECT
    'staff01',
    'HASH_STAFF01',
    'Staff',
    NULL
WHERE NOT EXISTS
(
    SELECT 1
    FROM Rental.[User]
    WHERE Username = 'staff01'
);
GO

SELECT *
FROM Rental.[User];
GO


-- Sample data is loaded only ONCE. After this, rows deleted on the website stay deleted when the script is re-run.
IF NOT EXISTS (SELECT 1 FROM sys.extended_properties WHERE class = 0 AND name = N'SampleDataLoaded')
    EXEC sp_addextendedproperty @name = N'SampleDataLoaded', @value = N'1';
GO

/*
--====================================
--Testing the constraints
--====================================

TEST 1 - ID NUMBER (I DEFINED IT TO NOT CONTAIN A-Z)
    INSERT INTO Rental.Customer
        (FirstName, LastName, IDNumber, PhoneNumber, Email, DriversLicenseNo)
    VALUES
        ('Test', 'Person', '90010150090AB', '0800000000',
        'test@email.com', 'DL99999');

THIS TEST WORKS, output im getting is:
The INSERT statement conflicted with the CHECK constraint "CK_Customer_IDNumber_Digits".
The conflict occurred in database "VehicleRental", table "Rental.Customer", column 'IDNumber'.


TEST 2 - Vehicle Status (should be either, 'Available', 'Rented', 'Maintenance' )

    INSERT INTO Rental.Vehicle
        (RegistrationNo, Make, Model, [Year], [Status], CategoryID)
    VALUES
        ('TEST123', 'Toyota', 'Yaris', 2024, 'Broken', 1);

THIS TEST WORKS, output im getting is:
The INSERT statement conflicted with the CHECK constraint "CK_Vehicle_Status".
The conflict occurred in database "VehicleRental", table "Rental.Vehicle", column 'Status'.


TEST 3 - Booking Status
Should be: Pending, Confirmed, Completed, or Cancelled

    INSERT INTO Rental.Booking
        (CustomerID, VehicleID, StartDate, EndDate, BookingStatus)
    VALUES
        (1, 1, '2026-10-01', '2026-10-05', 'Rejected');

THIS TEST WORKS, output im getting is:
The INSERT statement conflicted with the CHECK constraint "CK_Booking_Status".
The conflict occurred in database "VehicleRental", table "Rental.Booking", column 'BookingStatus'.


TEST 4 - Booking Dates
EndDate should be equal to or later than StartDate

    INSERT INTO Rental.Booking
        (CustomerID, VehicleID, StartDate, EndDate, BookingStatus)
    VALUES
        (1, 1, '2026-10-10', '2026-10-05', 'Confirmed');

THIS TEST WORKS, output im getting is:
The INSERT statement conflicted with the CHECK constraint "CK__Booking__571DF1D5".
The conflict occurred in database "VehicleRental", table "Rental.Booking"


TEST 5 - Payment Method
Should be: Cash, Card, or EFT

    INSERT INTO Rental.Payment
        (Amount, PaymentDate, PaymentMethod, BookingID)
    VALUES
        (1000.00, '2026-09-02', 'Cheque', 1);

THIS TEST WORKS, output im getting is:
The INSERT statement conflicted with the CHECK constraint "CK_Payment_Method".
The conflict occurred in database "VehicleRental", table "Rental.Payment", column 'PaymentMethod'.


TEST 6 - User Role
Should be: Admin, Staff, or Customer

INSERT INTO Rental.[User]
    (Username, PasswordHash, [Role], CustomerID)
VALUES
    ('testuser', 'HASH_TEST', 'Manager', NULL);

THIS TEST WORKS, output im getting is:
The INSERT statement conflicted with the CHECK constraint "CK_User_Role".
The conflict occurred in database "VehicleRental", table "Rental.User", column 'Role'.
*/

/* ======================================================================
   PART 1C - INDEXES AND VIEWS (was 04_Indexes_Views.sql)
   ====================================================================== */
USE VehicleRental;
Go

--Indexing for quicker retrieval in Cstomer Id column

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_Booking_CustomerID'
      AND object_id = OBJECT_ID('Rental.Booking')
)
BEGIN
    CREATE INDEX IX_Booking_CustomerID
    ON Rental.Booking(CustomerID);
END;
GO

-- Indexing Booking.VehicleID

IF NOT EXISTS
(
    SELECT 1
    FROM sys.indexes
    WHERE name = 'IX_Booking_VehicleID'
      AND object_id = OBJECT_ID('Rental.Booking')
)
BEGIN
    CREATE INDEX IX_Booking_VehicleID
    ON Rental.Booking(VehicleID);
END;
GO

--======================================
-- VIEWS (im gonna use them for Reports)
--======================================

-- View 1: Customer Booking Details 
--(Since im gonna have many cutomers i dont want to rewrite this Multi JOIN query i'll just use this VIEW)
--This View combines 3 Tables as one big output and I can tell the whole story in one select

CREATE OR ALTER VIEW Rental.vw_CustomerBookingDetails
AS
SELECT
    c.CustomerID,
    c.FirstName,
    c.LastName,
    v.RegistrationNo,
    v.Make,
    v.Model,
    b.BookingID,
    b.StartDate,
    b.EndDate,
    b.BookingStatus
FROM Rental.Customer AS c
INNER JOIN Rental.Booking AS b
    ON c.CustomerID = b.CustomerID
INNER JOIN Rental.Vehicle AS v
    ON b.VehicleID = v.VehicleID;
GO

SELECT *
FROM Rental.vw_CustomerBookingDetails;
GO

-- View 2 Payment Details
--This also combines 3 tables but the output is about payments


CREATE OR ALTER VIEW Rental.vw_PaymentDetails
AS
SELECT
    p.PaymentID,
    p.Amount,
    p.PaymentDate,
    p.PaymentMethod,
    b.BookingID,
    c.CustomerID,
    c.FirstName,
    c.LastName,
    b.BookingStatus
FROM Rental.Payment AS p
INNER JOIN Rental.Booking AS b
    ON p.BookingID = b.BookingID
INNER JOIN Rental.Customer AS c
    ON b.CustomerID = c.CustomerID;
GO

SELECT *
FROM Rental.vw_PaymentDetails;
GO


-- View 3: Vehicle Availability
-- (note to myself) - on tkinter there should be an option to Show available cars,
-- and that procces need multi join 

CREATE OR ALTER VIEW Rental.vw_VehicleAvailability
AS
SELECT
    v.VehicleID,
    v.RegistrationNo,
    v.Make,
    v.Model,
    v.[Year],
    v.[Status],
    vc.CategoryName,
    vc.DailyRate
FROM Rental.Vehicle AS v
INNER JOIN Rental.VehicleCategory AS vc
    ON v.CategoryID = vc.CategoryID;
GO

SELECT *
FROM Rental.vw_VehicleAvailability;
GO

/* ======================================================================
   PART 1D - DEMO LOGIN PASSWORDS (new)
   The sample users had placeholder hashes (HASH_ADMIN etc.), which nobody can log in with.
   This sets real hashes only where a placeholder is still in place.
   admin / Admin1    staff01 / Staff1234    thabo, lerato, daniel, naledi, james / Customer1
   Change these before showing the site to anyone else.
   ====================================================================== */
USE VehicleRental;
GO
UPDATE Rental.[User] SET PasswordHash = 'NzNVNKcQSoWFBLMQi65Fdw==:tB5JC7GnfZWn5hQfD2vBaUC5xdew0FmTdUFmNoK90hk=' WHERE Username = 'admin' AND PasswordHash LIKE 'HASH[_]%';
UPDATE Rental.[User] SET PasswordHash = 'thSx5nR6/xFzq68oEMbbdg==:Nj7pecbFgBqP7Xcu4jA8wgkVK5M85TzVAG2T00nIS/E=' WHERE Username = 'staff01' AND PasswordHash LIKE 'HASH[_]%';
UPDATE Rental.[User] SET PasswordHash = 'EBmfSQS2VAWPBHud09KSoQ==:NuY0Sznu/2ioIMfM1WD1FwhD27XE8K00Hs0qu0iCbBg=' WHERE Username = 'thabo' AND PasswordHash LIKE 'HASH[_]%';
UPDATE Rental.[User] SET PasswordHash = '4ownyyA1nXpQY/VqBjo8/w==:DVzpnaMjYJXDGFmZpvfjls/J1gz7R/g3vDD0AHJC8ik=' WHERE Username = 'lerato' AND PasswordHash LIKE 'HASH[_]%';
UPDATE Rental.[User] SET PasswordHash = 'KY/g/tsoxGClHkJu1vhohw==:RjewkxBfczBEwA22xNjbSVk1sL2JX9hSGDMKDOCNB+k=' WHERE Username = 'daniel' AND PasswordHash LIKE 'HASH[_]%';
UPDATE Rental.[User] SET PasswordHash = '0lQkMjRytdXFhzarNt0Eiw==:3BMwtVP4zVJ6n1h5O6+hNXcTquW2E0JDttLoYus9CwQ=' WHERE Username = 'naledi' AND PasswordHash LIKE 'HASH[_]%';
UPDATE Rental.[User] SET PasswordHash = 'pJGwI/GQxQ9qKztBUIr4Ow==:GCGDNq4WQFxKhxGL7C/h9A/wTsxG3N8RVl21uZy95yY=' WHERE Username = 'james' AND PasswordHash LIKE 'HASH[_]%';
GO

/* ======================================================================
   PART 2A - REPORTS (was 05_Reports.sql)
   ====================================================================== */
USE VehicleRental;
GO


-- REPORT 1: AVAILABLE VEHICLES (I can use the same Report just Changing Satus and get 2 more )

SELECT
    RegistrationNo,
    Make,
    Model,
    [Year],
    CategoryName,
    DailyRate
FROM Rental.vw_VehicleAvailability
WHERE [Status] = 'Available'
ORDER BY CategoryName, DailyRate;
GO


-- REPORT 2 - CUSTOMER BOOKING HISTORY
SELECT
    CustomerID,
    FirstName,
    LastName,
    BookingID,
    RegistrationNo,
    Make,
    Model,
    StartDate,
    EndDate,
    BookingStatus
FROM Rental.vw_CustomerBookingDetails
ORDER BY CustomerID, StartDate;
GO


-- REPORT 3: PAYMENT / REVENUE SUMMARY

SELECT
    PaymentMethod,
    COUNT(PaymentID) AS NumberOfPayments,
    SUM(Amount) AS TotalRevenue
FROM Rental.Payment
GROUP BY PaymentMethod
ORDER BY TotalRevenue DESC;
GO


-- REPORT 4: BOOKING STATUS SUMMARY

SELECT
    BookingStatus,
    COUNT(BookingID) AS NumberOfBookings
FROM Rental.Booking
GROUP BY BookingStatus
ORDER BY NumberOfBookings DESC;
GO

-- REPORT 5: RUNNING REVENUE

SELECT
    PaymentID,
    PaymentDate,
    PaymentMethod,
    Amount,
    SUM(Amount) OVER (
        ORDER BY PaymentDate, PaymentID
    ) AS RunningRevenue
FROM Rental.Payment
ORDER BY PaymentDate, PaymentID;
GO


-- REPORT 6: PAYMENT CHANGE USING LAG

SELECT
    PaymentID,
    PaymentDate,
    PaymentMethod,
    Amount,

    LAG(Amount) OVER (
        ORDER BY PaymentDate, PaymentID
    ) AS PreviousPayment,

    Amount - LAG(Amount) OVER (
        ORDER BY PaymentDate, PaymentID
    ) AS PaymentChange

FROM Rental.Payment
ORDER BY PaymentDate, PaymentID;
GO

-- REPORT 7: CUSTOMER BOOKING PERFORMANCE

WITH CustomerBookingStats AS
(
    SELECT
        c.CustomerID,
        c.FirstName,
        c.LastName,
        COUNT(b.BookingID) AS TotalBookings
    FROM Rental.Customer AS c
    LEFT JOIN Rental.Booking AS b
        ON c.CustomerID = b.CustomerID
    GROUP BY
        c.CustomerID,
        c.FirstName,
        c.LastName
)

SELECT
    CustomerID,
    FirstName,
    LastName,
    TotalBookings,

    CASE
        WHEN TotalBookings = 0 THEN 'No Bookings'
        WHEN TotalBookings = 1 THEN 'Single Booking'
        ELSE 'Regular Customer'
    END AS CustomerType,

    RANK() OVER (
        ORDER BY TotalBookings DESC
    ) AS BookingRank

FROM CustomerBookingStats
ORDER BY BookingRank, LastName;
GO

/* ======================================================================
   PART 2B - LOGIN LOOKUPS (was 06_Authentication.sql)
   ====================================================================== */
USE VehicleRental;
GO

-- ==========================================
-- AUTHENTICATION
-- ==========================================

-- Login lookup
-- im gonna use Python to supply the aparameter 
-- The query returns the information needed
-- to authenticate the user and determine their role.

-- Login lookup
-- Python will supply the username as a parameter.

DECLARE @Username NVARCHAR(50) = 'thabo';

SELECT
    UserID,
    Username,
    PasswordHash,
    [Role],
    CustomerID
FROM Rental.[User]
WHERE Username = @Username;
GO


-- ==========================================
-- AUTHENTICATION TESTS
-- ==========================================

-- Test 1 - Existing Customer
SELECT
    UserID,
    Username,
    PasswordHash,
    [Role],
    CustomerID
FROM Rental.[User]
WHERE Username = 'thabo';
GO


-- Test 2 - Existing Admin

SELECT
    UserID,
    Username,
    PasswordHash,
    [Role],
    CustomerID
FROM Rental.[User]
WHERE Username = 'admin';
GO


-- Test 3 - Non-existent User

SELECT
    UserID,
    Username,
    PasswordHash,
    [Role],
    CustomerID
FROM Rental.[User]
WHERE Username = 'does_not_exist';
GO


-- Test 3: Existing Staff
SELECT
    UserID,
    Username,
    PasswordHash,
    [Role],
    CustomerID
FROM Rental.[User]
WHERE Username = 'staff01';
GO
GO

USE VehicleRental;
GO
/*
WE ARE DOING TEST FOR DATA MANAGEMENT 
THAT IS ALLA BOUT THE CRUD
*/

--C which is Create(INSERT) 

INSERT INTO Rental.Customer
    (FirstName, LastName, IDNumber, PhoneNumber, Email, DriversLicenseNo)
VALUES
    ('Sipho', 'Nkosi', '9801015009087', '0812345678',
     'sipho.nkosi@email.com', 'DL10006');
GO

--R which is Read(SELECT)
SELECT *
FROM Rental.Customer;
GO

SELECT
    CustomerID,
    FirstName,
    LastName,
    Email
FROM Rental.Customer;
GO

--Note to myself (Create VIEWS) For Reports after you are done with all the Testing and Staging

--U which is Update
UPDATE Rental.Customer
SET PhoneNumber = '0829999999'
WHERE CustomerID = 7;
GO

SELECT PhoneNumber
FROM Rental.Customer
WHERE CustomerID=7;
GO

--D which is Delete
DELETE 
FROM Rental.Customer
WHERE CustomerID=7;

SELECT *
FROM Rental.Customer;
GO


--====================================
-- VEHICLE CRUD
--====================================

-- CREATE / INSERT

INSERT INTO Rental.Vehicle
    (RegistrationNo, Make, Model, [Year], [Status], CategoryID)
VALUES
    ('CRUD001', 'Hyundai', 'i20', 2025, 'Available', 1);
GO

SELECT *
FROM Rental.Vehicle
WHERE RegistrationNo = 'CRUD001';
GO

-- UPDATE

UPDATE Rental.Vehicle
SET [Status] = 'Maintenance'
WHERE VehicleID = 9;
GO

SELECT *
FROM Rental.Vehicle
WHERE VehicleID = 9;
GO

-- DELETE

DELETE FROM Rental.Vehicle
WHERE VehicleID = 9;
GO

SELECT *
FROM Rental.Vehicle
WHERE VehicleID = 9;
GO

--====================================
-- BOOKING CRUD
--====================================

-- CREATE / INSERT

INSERT INTO Rental.Booking
    (CustomerID, VehicleID, StartDate, EndDate, BookingStatus)
VALUES
    (1, 1, '2026-10-10', '2026-10-15', 'Pending');
GO

SELECT *
FROM Rental.Booking
WHERE CustomerID = 1
  AND VehicleID = 1
  AND StartDate = '2026-10-10';
GO

-- UPDATE

UPDATE Rental.Booking
SET BookingStatus = 'Confirmed'
WHERE BookingID = 8;
GO

SELECT *
FROM Rental.Booking
WHERE BookingID = 8;
GO

-- DELETE

DELETE FROM Rental.Booking
WHERE BookingID = 8;
GO

SELECT *
FROM Rental.Booking
WHERE BookingID = 8;
GO

--====================================
-- PAYMENT CRUD
--====================================

-- CREATE / INSERT

INSERT INTO Rental.Payment
    (Amount, PaymentDate, PaymentMethod, BookingID)
VALUES
    (3750.00, '2026-09-02', 'Card', 3);
GO

SELECT *
FROM Rental.Payment
WHERE BookingID = 3
  AND Amount = 3750.00;
GO

--Update 

UPDATE Rental.Payment
SET PaymentMethod = 'EFT'
WHERE PaymentID = 5;
GO

SELECT *
FROM Rental.Payment
WHERE PaymentID = 5;
GO

--Delete 

DELETE FROM Rental.Payment
WHERE PaymentID = 5;
GO

SELECT *
FROM Rental.Payment
WHERE PaymentID = 5;
GO

--====================================
-- VEHICLE CATEGORY CRUD
--====================================

-- CREATE / INSERT

INSERT INTO Rental.VehicleCategory
    (CategoryName, DailyRate)
VALUES
    ('Compact', 400.00);
GO

SELECT *
FROM Rental.VehicleCategory
WHERE CategoryName = 'Compact';
GO

--UPDATE

UPDATE Rental.VehicleCategory
SET DailyRate = 450.00
WHERE CategoryID = 5;
GO

SELECT *
FROM Rental.VehicleCategory
WHERE CategoryID = 5;
GO

--Delete
DELETE FROM Rental.VehicleCategory
WHERE CategoryID = 5;
GO

SELECT *
FROM Rental.VehicleCategory
WHERE CategoryID = 5;
GO

--====================================
-- USER CRUD
--====================================

-- CREATE / INSERT

INSERT INTO Rental.[User]
    (Username, PasswordHash, [Role], CustomerID)
VALUES
    ('crud_test', 'HASH_CRUD_TEST', 'Customer', 1);
GO

SELECT *
FROM Rental.[User]
WHERE Username = 'crud_test';
GO

--Update

UPDATE Rental.[User]
SET Username = 'crud_test_updated'
WHERE UserID = 8;
GO

SELECT *
FROM Rental.[User]
WHERE UserID = 8;
GO

--Delete
DELETE FROM Rental.[User]
WHERE UserID = 8;
GO

SELECT *
FROM Rental.[User]
WHERE UserID = 8;
GO
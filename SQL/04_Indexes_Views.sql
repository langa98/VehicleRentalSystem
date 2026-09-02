
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


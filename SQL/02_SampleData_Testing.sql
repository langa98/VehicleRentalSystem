USE VehicleRental;
GO


-- CUSTOMER SAMPLE DATA

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


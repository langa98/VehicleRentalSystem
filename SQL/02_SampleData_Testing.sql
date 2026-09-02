USE VehicleRental;
GO

INSERT INTO Rental.Customer
    (FirstName, LastName, IDNumber, PhoneNumber, Email, DriversLicenseNo)
VALUES
    ('Thabo', 'Mokoena', '9001015009087', '0821234567', 'thabo.mokoena@email.com', 'DL10001'),
    ('Lerato', 'Molefe', '9505050123086', '0832345678', 'lerato.molefe@email.com', 'DL10002'),
    ('Daniel', 'Smith', '8807125012084', '0713456789', 'daniel.smith@email.com', 'DL10003'),
    ('Naledi', 'Dlamini', '0102030087089', '0794567890', 'naledi.dlamini@email.com', 'DL10004'),
    ('James', 'Williams', '9209095065081', '0765678901', 'james.williams@email.com', 'DL10005');
GO

SELECT *
FROM Rental.Customer;
GO

INSERT INTO Rental.VehicleCategory
    (CategoryName, DailyRate)
VALUES
    ('Economy', 350.00),
    ('Sedan', 500.00),
    ('SUV', 750.00),
    ('Luxury', 1200.00);
GO

SELECT *
FROM Rental.VehicleCategory;
GO

INSERT INTO Rental.Vehicle
    (RegistrationNo, Make, Model, [Year], [Status], CategoryID)
VALUES
    ('CA123456', 'Toyota', 'Starlet', 2023, 'Available', 1),
    ('GP456789', 'Volkswagen', 'Polo', 2022, 'Available', 1),
    ('NW789012', 'Toyota', 'Corolla', 2024, 'Rented', 2),
    ('EC234567', 'BMW', '3 Series', 2023, 'Available', 2),
    ('FS567890', 'Toyota', 'Fortuner', 2024, 'Available', 3),
    ('KZN345678', 'Ford', 'Everest', 2023, 'Maintenance', 3),
    ('GP678901', 'Mercedes-Benz', 'C-Class', 2024, 'Available', 4);
GO

SELECT *
FROM Rental.Vehicle;
GO

INSERT INTO Rental.Booking
    (CustomerID, VehicleID, StartDate, EndDate, BookingStatus)
VALUES
    (1, 1, '2026-09-05', '2026-09-08', 'Confirmed'),
    (2, 3, '2026-08-20', '2026-08-23', 'Completed'),
    (3, 5, '2026-09-10', '2026-09-15', 'Pending'),
    (4, 4, '2026-08-25', '2026-08-28', 'Completed'),
    (5, 7, '2026-09-20', '2026-09-25', 'Cancelled');
GO

SELECT *
FROM Rental.Booking;
GO

INSERT INTO Rental.Payment
    (Amount, PaymentDate, PaymentMethod, BookingID)
VALUES
    (1050.00, '2026-09-01', 'Card', 1),
    (1500.00, '2026-08-20', 'EFT', 2),
    (1500.00, '2026-08-25', 'Cash', 4);
GO

SELECT *
FROM Rental.Payment;
GO

INSERT INTO Rental.[User]
    (Username, PasswordHash, [Role], CustomerID)
VALUES
    ('admin', 'HASH_ADMIN', 'Admin', NULL),
    ('thabo', 'HASH_THABO', 'Customer', 1),
    ('lerato', 'HASH_LERATO', 'Customer', 2),
    ('daniel', 'HASH_DANIEL', 'Customer', 3),
    ('naledi', 'HASH_NALEDI', 'Customer', 4),
    ('james', 'HASH_JAMES', 'Customer', 5);
GO

SELECT *
FROM Rental.[User];
GO

/*
--====================================
--Testing the contraints
--====================================

TEST 1 - ID NUMBER (I DEFINED IT TO NOT CONTAINT A-Z)
	INSERT INTO Rental.Customer
		(FirstName, LastName, IDNumber, PhoneNumber, Email, DriversLicenseNo)
	VALUES
		('Test', 'Person', '90010150090AB', '0800000000',
		'test@email.com', 'DL99999');

THIS TEST WORKS, output im getting is:
The INSERT statement conflicted with the CHECK constraint "CK_Customer_IDNumber_Digits".
The conflict occurred in database "VehicleRental", table "Rental.Customer", column 'IDNumber'.'


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
Should be: Admin or Customer

INSERT INTO Rental.[User]
    (Username, PasswordHash, [Role], CustomerID)
VALUES
    ('testuser', 'HASH_TEST', 'Manager', NULL);

THIS TEST WORKS, output im getting is:
The INSERT statement conflicted with the CHECK constraint "CK_User_Role".
The conflict occurred in database "VehicleRental", table "Rental.User", column 'Role'.

*/
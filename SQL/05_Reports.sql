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

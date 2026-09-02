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
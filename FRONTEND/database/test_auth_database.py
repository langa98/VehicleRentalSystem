from connection import get_connection
from password import verify_password


username = "staff01"
password = "Staff123"


connection = get_connection()
cursor = connection.cursor()

cursor.execute("""
    SELECT UserID, Username, PasswordHash, [Role], CustomerID
    FROM Rental.[User]
    WHERE Username = ?
""", (username,))

user = cursor.fetchone()

if user is None:
    print("User not found.")

else:
    user_id = user.UserID
    username = user.Username
    stored_hash = user.PasswordHash
    role = user.Role
    customer_id = user.CustomerID

    print("User found:")
    print("UserID:", user_id)
    print("Username:", username)
    print("Role:", role)
    print("CustomerID:", customer_id)

    print()
    print("Password verification:")
    print(verify_password(password, stored_hash))


connection.close()
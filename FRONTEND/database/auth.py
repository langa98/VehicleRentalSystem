from database.connection import get_connection
from database.password import verify_password


def authenticate_user(username, password):

    connection = get_connection()
    cursor = connection.cursor()

    cursor.execute("""
        SELECT UserID, Username, PasswordHash, [Role], CustomerID
        FROM Rental.[User]
        WHERE Username = ?
    """, (username,))

    user = cursor.fetchone()

    connection.close()

    if user is None:
        return None

    if not verify_password(password, user.PasswordHash):
        return None

    return {
        "UserID": user.UserID,
        "Username": user.Username,
        "Role": user.Role,
        "CustomerID": user.CustomerID
    }
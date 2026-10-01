from auth import authenticate_user


print("Testing correct Admin password:")

user = authenticate_user("admin", "Admin123")

if user is None:
    print("Login failed.")
else:
    print("Login successful.")
    print("Username:", user["Username"])
    print("Role:", user["Role"])
    print("CustomerID:", user["CustomerID"])


print()
print("Testing wrong Admin password:")

user = authenticate_user("admin", "WrongPassword")

if user is None:
    print("Login correctly rejected.")
else:
    print("ERROR: Wrong password was accepted.")
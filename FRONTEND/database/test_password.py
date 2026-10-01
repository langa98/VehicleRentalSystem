from password import hash_password, verify_password


password = "Admin123"

stored_hash = hash_password(password)

print("Stored hash:")
print(stored_hash)

print()

print("Correct password:")
print(verify_password("Admin123", stored_hash))

print()

print("Wrong password:")
print(verify_password("WrongPassword", stored_hash))
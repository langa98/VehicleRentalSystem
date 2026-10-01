from password import hash_password


password = "Admin123"

stored_hash = hash_password(password)

print(stored_hash)
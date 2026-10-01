from password import verify_password


stored_hash = "H5+dLgv5NjTksV47dWBAyw==:t5h0Q7l/NJ+sZxlm1QlIAHfZTXKCKVpT+lpUk+jfSEE="


print("Correct password:")
print(verify_password("Admin123", stored_hash))

print()

print("Wrong password:")
print(verify_password("WrongPassword", stored_hash))
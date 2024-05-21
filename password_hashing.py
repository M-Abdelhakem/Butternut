import bcrypt


# Function to hash a password with salt
def hash_password(password):
    # Generate a salt
    salt = bcrypt.gensalt()
    # Hash the password with the salt
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    # Return the hashed password and salt
    return hashed_password, salt


# Function to verify a password
def verify_password(password, stored_hashed_password, salt):
    # Hash the entered password with the stored salt
    hashed_password = bcrypt.hashpw(password.encode("utf-8"), salt)
    # Compare the hashed password with the stored hashed password
    return hashed_password == stored_hashed_password

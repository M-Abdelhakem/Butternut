from pymongo import MongoClient, ASCENDING
from utils.password_hashing import hash_password, verify_password


class DBManager:
    def __init__(self):
        self.client = MongoClient("mongodb://localhost:27017/")
        self.db = self.client["ButternutDB"]
        self.clients_collection = self.db["clients"]
        self.clients_uploads_collection = self.db["clients_uploads"]

        self.clients_collection.create_index([("username", ASCENDING)], unique=True)
        self.clients_uploads_collection.create_index(
            [("user_id", ASCENDING)], unique=False
        )

    def check_user(self, username):
        return self.clients_collection.find_one(username)

    def insert_user(self, user):
        hashed_password = hash_password(user["password"])
        self.clients_collection.insert_one(
            {"username": user["username"], "password": hashed_password, "logged-in": False}
        )

    def validate_user(self, user):
        user_record = self.clients_collection.find_one({"username": user["username"]})
        if user_record:
            stored_hashed_password = user_record["password"]
            if verify_password(user["password"], stored_hashed_password):
                # self.clients_collection.update_one(
                #     {"username": user["username"]},
                #     {"$set": {"logged-in": True}}
                # )
                return user_record

    def save_business_context(self, username, context):
        self.clients_collection.update_one(
            {"username": username},
            {"$set": {"business_context": context}}
        )

    def insert_upload_record(self, data):
        return self.clients_uploads_collection.insert_one(data)

    def retrieve_uploaded_data(self, username):
        # Query the database to retrieve uploaded data for the specified username
        uploaded_data = self.clients_uploads_collection.find(
            {"user_id": username},
            {"_id": 0, "file_name": 1, "upload_date": 1, "upload_id": 1},
        )
        return list(uploaded_data)

    def delete_uploaded_data(self, upload_id):
        # Delete the uploaded data with the specified upload_id
        self.clients_uploads_collection.delete_one({"upload_id": upload_id})

    def retrieve_data_as_table(self, upload_id):
        # Query the database to retrieve uploaded data for the specified upload_id
        uploaded_data = self.clients_uploads_collection.find_one(
            {"upload_id": upload_id},
            {"_id": 0, "file_data": 1},  # Assuming "file_data" contains the data
        )
        return uploaded_data.get("file_data") if uploaded_data else None

    def update_clients_add_customers(self, client_username, new_customers):
        # Fetch the current customers for the client
        client = self.clients_collection.find_one(
            {"username": client_username}, {"customers": 1}
        )

        if not client or "customers" not in client:
            current_customers = []
        else:
            current_customers = client["customers"]

        # Extract the emails of the current customers into a dictionary for fast lookup
        current_customer_dict = {
            customer["email"]: customer for customer in current_customers
        }

        # Lists to hold new customers and updates
        unique_new_customers = []
        customers_to_update = []

        for new_customer in new_customers:
            email = new_customer["email"]
            if email in current_customer_dict:
                # Existing customer: update the profile if necessary
                current_customer = current_customer_dict[email]
                if current_customer != new_customer:  # Check if the profile has changed
                    customers_to_update.append(new_customer)
            else:
                # New customer
                unique_new_customers.append(new_customer)

        # Merge new and existing customers with updates into a single list
        merged_customers = current_customers
        for customer in unique_new_customers:
            merged_customers.append(customer)
        for customer in customers_to_update:
            # Find the index of the customer to update
            index = next(
                (
                    i
                    for i, c in enumerate(merged_customers)
                    if c["email"] == customer["email"]
                ),
                None,
            )
            if index is not None:
                merged_customers[index] = customer

        # Update the clients collection with the merged customers list
        self.clients_collection.update_one(
            {"username": client_username}, {"$set": {"customers": merged_customers}}
        )


    def get_business_context(self, username):
        result = self.clients_collection.find_one(
            {"username": username},
            {"_id": 0, "business_context": 1}
        )
        if result:
            business_context = result.get('business_context')
            if business_context:
                return business_context
        return None
    


    def save_password_reset_token(self, username, token):
        self.clients_collection.update_one({"username": username}, {"$set": {"reset_token": token}})
    
    def get_username_by_token(self, token):
        user = self.clients_collection.find_one({"reset_token": token})
        return user["username"] if user else None

    def delete_password_reset_token(self, token):
        self.clients_collection.update_one({"reset_token": token}, {"$unset": {"reset_token": ""}})
    
    def update_password(self, username, hashed_password):
        self.clients_collection.update_one({"username": username}, {"$set": {"password": hashed_password}})



    def update_user_profile(self, username: str, profile_info: dict):
        # Logic to update the user's profile information in the database
        self.clients_collection.update_one({"username": username}, {"$set": profile_info})
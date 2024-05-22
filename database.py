from pymongo import MongoClient, ASCENDING
from password_hashing import hash_password, verify_password


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
        hashed_password, salt = hash_password(user["password"])
        self.clients_collection.insert_one(
            {"username": user["username"], "password": [hashed_password, salt]}
        )

    def validate_user(self, user):

        user_record = self.clients_collection.find_one({"username": user["username"]})
        if user_record:
            stored_hashed_password = user_record["password"][0]
            stored_salt = user_record["password"][1]
            if verify_password(user["password"], stored_hashed_password, stored_salt):
                return user_record

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
        client = self.clients_collection.find_one({"username": client_username}, {"customers": 1})
        
        if "customers" not in client:
            current_customers = []
        else:
            current_customers = client["customers"]
        
        # Extract the emails of the current customers into a dictionary for fast lookup
        current_customer_dict = {customer["email"]: customer for customer in current_customers}
        
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

        if unique_new_customers:
            # Update the clients collection to append only the unique new customers
            self.clients_collection.update_one(
                {"username": client_username},
                {"$push": {"customers": {"$each": unique_new_customers}}},
            )
        
        if customers_to_update:
            # Update the existing customers
            for updated_customer in customers_to_update:
                self.clients_collection.update_one(
                    {"username": client_username},
                    {"$set": {"customers.$": updated_customer}}
                )
# , "customers.email": updated_customer["email"] --> line 96
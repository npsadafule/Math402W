import numpy as np
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB URI and Client Setup
uri = 'mongodb+srv://USERNAME:PASSWORD@cluster0.lxrcibg.mongodb.net/'
client = MongoClient(uri, server_api=ServerApi('1'))

# Database and Collection
db = client["healthcare"]  # Use your database name
patients_col = db["patients"]  # Use your collection name

# Generate 1000 patients with random lambda values between 0.25 and 2
patients = [
    {"patient_id": i, "lambda": np.random.uniform(0.25, 2)}
    for i in range(1000)
]

# Insert patients into MongoDB
result = patients_col.insert_many(patients)
print(f"Inserted {len(result.inserted_ids)} patients into MongoDB.")

# Close the connection
client.close()
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from credentials import USERNAME, PASSWORD

# Load the data from Excel
excel_file_path = 'Appointments.xlsx'  
df = pd.read_excel(excel_file_path, usecols=['PID', 'Clinician'])

# Group each patient by their corresponding MRP and remove duplicates
grouped = df.groupby('Clinician')['PID'].apply(lambda x: list(set(x))).reset_index(name='Patients')

# MongoDB connection details
uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.lxrcibg.mongodb.net/"
client = MongoClient(uri, server_api=ServerApi('1'))

# Specify the database and collection
db = client["healthcare"]
mrp_col = db["MRP"]

# Store each MRP and their associated patients in the MongoDB collection
for index, row in grouped.iterrows():
    # Here we are creating a document for each MRP with a unique list of patient IDs they see
    mrp_col.update_one(
        {'Clinician': row['Clinician']},
        {'$set': {'Patients': row['Patients']}},
        upsert=True
    )

print("MRP data has been updated in the MongoDB database.")
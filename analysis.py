import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

# Load the data from Excel
excel_file_path = 'Appointments.xlsx'  # Update this path as necessary
df = pd.read_excel(excel_file_path, usecols=['PID', 'AppointmentDate'])

# Convert dates to datetime objects and ensure they're in the correct format
df['AppointmentDate'] = pd.to_datetime(df['AppointmentDate'])

# Calculate the total number of months covered in the data
start_date = datetime(2021, 4, 1)
end_date = datetime(2024, 1, 4)
total_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month

# Calculate lambda for each patient
lambdas = df.groupby('PID').size() / total_months
lambdas = lambdas.reset_index(name='lambda')  # Use 'lambda' to match the second script

# MongoDB connection details
uri = "mongodb+srv://USERNAME:PASSWORD@cluster0.lxrcibg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Specify the database and collection to match the second script
db = client['healthcare']
collection = db['patients']  # Use 'patients' to match the second script

# Convert the DataFrame to a list of dictionaries for insertion
lambda_dicts = lambdas.to_dict('records')

# Update the database
for patient in lambda_dicts:
    collection.update_one(
        {'PID': patient['PID']},
        {'$set': patient},  # Update to set the entire patient document
        upsert=True
    )

print("Lambda values have been updated in the database.")
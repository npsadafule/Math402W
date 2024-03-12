import pandas as pd
from pymongo import MongoClient, ServerApi
from datetime import datetime

uri = "mongodb+srv://USERNAME:PASSWORD@cluster0.lxrcibg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Connect to the 'healthcare' database and 'patients' collection
db = client['healthcare']
patients_col = db['patients']

# Load the Excel file into a pandas DataFrame
df = pd.read_excel('Appointments.xlsx', usecols=['PID', 'ApptBookedDate'])

# Convert 'ApptBookedDate' to datetime
df['ApptBookedDate'] = pd.to_datetime(df['ApptBookedDate'])

# Calculate the number of months covered in the data for lambda calculation
start_date = df['ApptBookedDate'].min()
end_date = df['ApptBookedDate'].max()
total_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month + 1

# Calculate lambda (rate of booking an appointment per month) for each patient
lambdas = df.groupby('PID').size() / total_months

# Update MongoDB with lambda values for each patient
for pid, lambda_val in lambdas.iteritems():
    # Update if exists, insert if doesn't exist (upsert=True)
    patients_col.update_one({'PID': pid}, {'$set': {'lambda': lambda_val}}, upsert=True)

print("Lambda values updated in MongoDB.")
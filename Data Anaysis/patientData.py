import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime

# Load the lambda data from Excel
lambda_excel_file_path = 'Appointments.xlsx'  # Update this path as necessary
df_lambda = pd.read_excel(lambda_excel_file_path, usecols=['PID', 'ApptBookedDate'])

# Convert dates to datetime objects for lambda data
df_lambda['ApptBookedDate'] = pd.to_datetime(df_lambda['ApptBookedDate'])

# Calculate the total number of months covered in the lambda data
start_date = datetime(2021, 4, 1)
end_date = datetime(2024, 1, 4)
total_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month

# Calculate lambda for each patient
lambdas = df_lambda.groupby('PID').size() / total_months
lambdas = lambdas.reset_index(name='Lambda')

# Load the CSI data from the other Excel file
csi_excel_file_path = 'CSI data.xlsx'  # Update this path as necessary
df_csi = pd.read_excel(csi_excel_file_path, usecols=['PID', 'CSI_Score_0.1'])

# Calculate the average CSI score for each patient
avg_csi_scores = df_csi.groupby('PID')['CSI_Score_0.1'].mean()
avg_csi_scores = avg_csi_scores.reset_index(name='CSI')

# MongoDB connection details
uri = "mongodb+srv://USERNAME:PASSWORD@cluster0.lxrcibg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Specify the database and collection
db = client['healthcare']
patients_col = db['patients']

# Update lambda values in the database
for patient in lambdas.to_dict('records'):
    patients_col.update_one(
        {'PID': patient['PID']},
        {'$set': {'Lambda': patient['Lambda']}},
        upsert=True
    )

# Update the database with average CSI scores
for patient in avg_csi_scores.to_dict('records'):
    patients_col.update_one(
        {'PID': patient['PID']},
        {'$set': {'CSI': patient['CSI']}},
        upsert=True
    )

client.close()  

print("Database has been updated with Lambda and CSI values.")
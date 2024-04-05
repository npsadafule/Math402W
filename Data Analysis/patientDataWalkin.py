import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from datetime import datetime
from credentials import USERNAME, PASSWORD

# Load the lambda data from Excel
lambda_excel_file_path = 'Appointments.xlsx'  # Update this path as necessary
df_lambda = pd.read_excel(lambda_excel_file_path, usecols=['PID', 'ApptBookedDate', 'ApptTypeDesc'])

# Convert dates to datetime objects for lambda data
df_lambda['ApptBookedDate'] = pd.to_datetime(df_lambda['ApptBookedDate'])

# List of appointment types to be excluded
exclude_appt_types = [
    "Team 2 Booked", "Case Management", "Phone call from clinician to client", "Team 1 and Team 2 Booked", "Video", 
    "Team 2 Phone call from clinician to client", "Tobacco Dependency Clinic", "Clinical Chart Time", 
    "Team 1 Phone call from clinician to client", "Virtual Care", "Follow-up", "Home Visit", "External Activity", 
    "myoActivation", "Program Screening", "Team 2 Outreach Visit", "Pap Testing", "Counselling",  
    "Team 1 Care Coordination", "Care Coordination", "Video Conferencing", "Interdisciplinary Consult", 
    "Internal Medicine", "OAT Visit - In Office", "Break", "OAT Visit - Outreach", "Letter", "Team 2 Care Coordination", 
    "Specialist", "OAT Visit - Phone", "Team 1 Outreach Visit", "Bridging Only", "Specimen Collection", 
    "Trans Clinic", "Mental Health Note", "Fibroscan", "Group Visit", "IUC Insertion", "Outreach Visit", "Psychiatrist", "Hep C Visit", "Intake", "Methadone/SUBOXONE", "Methadone Assessment", "Urgent (Same Day Visit)", "New Assessment",  "Addiction Services", "Pharmacy", "Social Worker",
]

# Filter out the excluded appointment types
df_lambda_filtered = df_lambda[~df_lambda['ApptTypeDesc'].isin(exclude_appt_types)]

# Calculate the total number of months covered in the lambda data
start_date = datetime(2021, 4, 1)
end_date = datetime(2024, 1, 4)
total_months = (end_date.year - start_date.year) * 12 + end_date.month - start_date.month

# Calculate lambda for each patient with the filtered data
lambdas = df_lambda_filtered.groupby('PID').size() / total_months
lambdas = lambdas.reset_index(name='Lambda')

# Load CSI data and calculate average, ensuring it's only for relevant PIDs
csi_excel_file_path = 'CSI data.xlsx'  # Update this path as necessary
df_csi = pd.read_excel(csi_excel_file_path, usecols=['PID', 'CSI_Score_0.1'])

# Filter CSI data to include only PIDs present in df_lambda_filtered
df_csi_filtered = df_csi[df_csi['PID'].isin(df_lambda_filtered['PID'].unique())]
avg_csi_scores = df_csi_filtered.groupby('PID')['CSI_Score_0.1'].mean().reset_index(name='CSI')

# MongoDB connection details - replace USERNAME and PASSWORD
uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.lxrcibg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Specify the database and collection
db = client['healthcare']
patients_col = db['patients(walkin)']

# Update lambda values in the database for relevant PIDs only
for patient in lambdas.to_dict('records'):
    patients_col.update_one(
        {'PID': patient['PID']},
        {'$set': {'Lambda': patient['Lambda']}},
        upsert=True
    )

# Update the database with average CSI scores for relevant PIDs only
for patient in avg_csi_scores.to_dict('records'):
    patients_col.update_one(
        {'PID': patient['PID']},
        {'$set': {'CSI': patient['CSI']}},
        upsert=True
    )

client.close()
print("Database has been updated with Lambda and CSI values.")
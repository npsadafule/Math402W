import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load the data from Excel
excel_file_path = 'Appointments.xlsx'
df = pd.read_excel(excel_file_path, usecols=['PID', 'is_visit', 'ApptTypeDesc'])

# Define a list of ApptTypeDesc to exclude from the show rate calculation
excluded_appt_types = [
    "Team 2 Booked", "Case Management", "Phone call from clinician to client", "Team 1 and Team 2 Booked", "Video", 
    "Team 2 Phone call from clinician to client", "Tobacco Dependency Clinic", "Clinical Chart Time", 
    "Team 1 Phone call from clinician to client", "Virtual Care", "Follow-up", "Home Visit", "External Activity", 
    "myoActivation", "Program Screening", "Team 2 Outreach Visit", "Pap Testing", "Counselling",  
    "Team 1 Care Coordination", "Care Coordination", "Video Conferencing", "Interdisciplinary Consult", 
    "Internal Medicine", "OAT Visit - In Office", "Break", "OAT Visit - Outreach", "Letter", "Team 2 Care Coordination", 
    "Specialist", "OAT Visit - Phone", "Team 1 Outreach Visit", "Bridging Only", "Specimen Collection", 
    "Trans Clinic", "Mental Health Note", "Fibroscan", "Group Visit", "IUC Insertion", "Outreach Visit", "Psychiatrist", "Hep C Visit", "Intake", "Methadone/SUBOXONE", "Methadone Assessment", "Urgent (Same Day Visit)", "New Assessment",  "Addiction Services", "Pharmacy", "Social Worker",
]

# Filter out appointments based on ApptTypeDesc
df_filtered = df[~df['ApptTypeDesc'].isin(excluded_appt_types)]

# Calculate the show rate for each PID
# Group by PID and calculate mean of 'is_visit' directly as the show rate
df_show_rate = df_filtered.groupby('PID')['is_visit'].mean().reset_index()
df_show_rate.rename(columns={'is_visit': 'ShowRate'}, inplace=True)

# MongoDB connection details
uri = "mongodb+srv://USERNAME:PASSWORD@cluster0.lxrcibg.mongodb.net/"
client = MongoClient(uri, server_api=ServerApi('1'))

# Specify the database and collection
db = client['healthcare']
patients_col = db['patients(walk-in)']

# Update the database with the show rates and remove NoShowRate
for index, row in df_show_rate.iterrows():
    # Update (or insert) ShowRate value
    patients_col.update_one(
        {'PID': row['PID']},
        {'$set': {'ShowRate': row['ShowRate']},
         '$unset': {'NoShowRate': ""}},  # This removes the NoShowRate key
        upsert=False
    )

print("Database has been updated with Show rates.")

# Close the MongoDB connection
client.close()
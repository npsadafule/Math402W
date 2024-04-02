import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load the data from Excel
excel_file_path = 'Appointments.xlsx'
df = pd.read_excel(excel_file_path, usecols=['PID', 'is_visit', 'ApptTypeDesc'])

# Define a list of ApptTypeDesc to exclude from the show rate calculation
excluded_appt_types = [
    "Phone call FROM CLIENT to clinician", "Team 1 Walk-In", "Team 1 and Team 2 Walk In",
    "Do Not Book", "Routine Visit", "Team 2 Walk-In", "Hep C Visit",
    "Intake", "Admin Note", "Outreach Visit", "Psychiatrist",
    "Walk In", "Phone Call", "Team 1 Phone call FROM CLIENT to clinician",
    "Methadone/SUBOXONE", "Methadone Assessment", "Team 2 Phone call FROM CLIENT to clinician",
    "Addiction Services", "Urgent (Same Day Visit)", "Ambulatory Care", "Pharmacy", "Nursing", "New Assessment",
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
patients_col = db['patients(booked)']

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
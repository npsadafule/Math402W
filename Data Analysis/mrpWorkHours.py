from pymongo.mongo_client import MongoClient
from pymongo.server_api import ServerApi
import pandas as pd
from credentials import USERNAME, PASSWORD

# MongoDB URI and connection
uri = "mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.lxrcibg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
client = MongoClient(uri, server_api=ServerApi('1'))

# Load data from Excel file
df_appointments = pd.read_excel("Appointments.xlsx")

# Convert the ApptBookedDate to datetime
df_appointments["ApptBookedDate"] = pd.to_datetime(df_appointments["ApptBookedDate"])

# Each appointment lasts for 30 minutes.
# Calculate the average hours worked per week for each clinician
weeks_covered = (df_appointments["ApptBookedDate"].max() - df_appointments["ApptBookedDate"].min()).days / 7
appointment_counts = df_appointments["Clinician"].value_counts()
total_hours_per_clinician = (appointment_counts * 30 / 60)
avg_hours_per_week = total_hours_per_clinician / weeks_covered

# Prepare data for MongoDB
data_for_mongodb = [{"Clinician": clinician, "AvgHoursPerWeek": avg_hours} for clinician, avg_hours in avg_hours_per_week.items()]

# Insert into MongoDB
db = client.healthcare
collection = db["MRP-Work-Hours"]
collection.insert_many(data_for_mongodb)

print("Data inserted into MongoDB.")

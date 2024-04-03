import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Function to fetch Lambda and CSI data from MongoDB
def fetch_lambda_csi_data():
    # MongoDB connection details - replace USERNAME and PASSWORD
    uri = "mongodb+srv://USERNAME:PASSWORD@cluster0.lxrcibg.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0"
    client = MongoClient(uri, server_api=ServerApi('1'))

    db = client['healthcare']
    patients_col = db['patients(booked)']

    # Fetch Lambda and CSI values for all patients
    data = list(patients_col.find({}, {"_id": 0, "Lambda": 1, "CSI": 1}))

    client.close()
    return pd.DataFrame(data)

# Fetch data
df = fetch_lambda_csi_data()

# Plotting
plt.figure(figsize=(24, 13.5))
plt.scatter(df['Lambda'], df['CSI'], alpha=0.5, c='blue', edgecolors='w', label='Patient Data')
plt.title('Relationship between Lambda (Booking Rate) and CSI (Complexity Score Index) for Booked Appointments Only')
plt.xlabel('Lambda (Rate of Booking Appointments per Month)')
plt.ylabel('CSI (Complexity Score Index)')
plt.grid(True)
plt.show()

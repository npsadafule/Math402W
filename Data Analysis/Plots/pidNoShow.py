import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from credentials import USERNAME, PASSWORD

def fetch_show_rates():
    # MongoDB connection details - replace with your actual credentials
    uri = f"mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.lxrcibg.mongodb.net/"
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    # Specify the database and collection
    db = client['healthcare']
    patients_col = db['patients(booked)']
    
    # Fetch ShowRate values for all patients
    data = list(patients_col.find({}, {"_id": 0, "ShowRate": 1}))
    client.close()
    
    # Convert the data into a pandas DataFrame
    df_show_rate = pd.DataFrame(data)
    return df_show_rate

# Fetch data
df_show_rate = fetch_show_rates()

# Calculate the weights for each data point to represent their percentage of the total
weights = [1.0 / len(df_show_rate)] * len(df_show_rate)

# Plotting the histogram of show rates with percentages
plt.figure(figsize=(24, 13.5))
plt.hist(df_show_rate['ShowRate'], bins=50, color='skyblue', edgecolor='black', weights=weights)
plt.title('Distribution of Patient Show Rates (Booked Appointments)')
plt.xlabel('Show Rate')
plt.ylabel('Percentage of Patients')
plt.grid(True)

# Adjust y-axis to show percentages
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(xmax=1))

plt.show()

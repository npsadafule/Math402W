import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def fetch_show_rates():
    # MongoDB connection details - replace with your actual credentials
    uri = "mongodb+srv://USERNAME:PASSWORD@cluster0.lxrcibg.mongodb.net/"
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    # Specify the database and collection
    db = client['healthcare']
    patients_col = db['patients']
    
    # Fetch ShowRate values for all patients
    data = list(patients_col.find({}, {"_id": 0, "ShowRate": 1}))
    client.close()
    
    # Convert the data into a pandas DataFrame
    df_show_rate = pd.DataFrame(data)
    return df_show_rate

# Fetch data
df_show_rate = fetch_show_rates()

# Plotting the histogram of show rates
plt.figure(figsize=(10, 6))
plt.hist(df_show_rate['ShowRate'], bins=50, color='skyblue', edgecolor='black')
plt.title('Distribution of Patient Show Rates')
plt.xlabel('Show Rate')
plt.ylabel('Number of Patients')
plt.grid(True)
plt.show()

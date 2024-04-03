import matplotlib.pyplot as plt
import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def fetch_lambda_values():
    # MongoDB connection details - replace with your actual credentials
    uri = "mongodb+srv://USERNAME:PASSWORD@cluster0.lxrcibg.mongodb.net/"
    client = MongoClient(uri, server_api=ServerApi('1'))
    
    # Specify the database and collection
    db = client['healthcare']
    patients_col = db['patients(walkin)']
    
    # Fetch Lambda values for all patients
    data = list(patients_col.find({}, {"_id": 0, "Lambda": 1}))
    client.close()
    
    # Convert the data into a pandas DataFrame
    df_lambda = pd.DataFrame(data)
    return df_lambda

# Fetch lambda data
df_lambda = fetch_lambda_values()

# Calculate the weights for each data point to represent their percentage of the total
weights = [1.0 / len(df_lambda)] * len(df_lambda)

# Plotting the histogram of lambda values with percentages
plt.figure(figsize=(24, 13.5))
plt.hist(df_lambda['Lambda'], bins=50, color='skyblue', edgecolor='black', weights=weights)
plt.title('Distribution of Rate of Walk-in Appointment (λ) for Patients (Walk-in Appointments)')
plt.xlabel('λ (Average Walk-ins per Month)')
plt.ylabel('Percentage of Patients')
plt.grid(True)

# Adjust y-axis to show percentages
plt.gca().yaxis.set_major_formatter(plt.matplotlib.ticker.PercentFormatter(xmax=1))

plt.show()

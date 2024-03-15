import pandas as pd
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# Load the data from Excel
excel_file_path = 'Appointments.xlsx'
df = pd.read_excel(excel_file_path, usecols=['PID', 'is_visit'])

# Calculate the no-show rate for each PID
# Group by PID and calculate mean of 'is_visit' where 1 is show and 0 is no-show
# So, the no-show rate will be 1 - mean('is_visit') because mean gives us the show rate
df_no_show = df.groupby('PID')['is_visit'].mean().reset_index()
df_no_show['NoShowRate'] = 1 - df_no_show['is_visit']
df_no_show = df_no_show.drop(columns=['is_visit'])

# MongoDB connection details
uri = "mongodb+srv://USERNAME:PASSWORD@cluster0.lxrcibg.mongodb.net/"
client = MongoClient(uri, server_api=ServerApi('1'))

# Specify the database and collection
db = client['healthcare']
patients_col = db['patients']

# Update the database with the no-show rates
for index, row in df_no_show.iterrows():
    patients_col.update_one(
        {'PID': row['PID']},
        {'$set': {'NoShowRate': row['NoShowRate']}},
        upsert=False  # We only want to update existing documents
    )

print("No-show rates have been updated in the database.")

# Close the MongoDB connection
client.close()
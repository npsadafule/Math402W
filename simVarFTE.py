import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from pymongo.server_api import ServerApi

# MongoDB connection details
uri = 'mongodb+srv://npsadafule:zbbc4445@cluster0.lxrcibg.mongodb.net/'
client = MongoClient(uri, server_api=ServerApi('1'))

# Database and Collection
db = client["healthcare"]
patients_col = db["patients(booked)"]

# Fetch lambda values and ShowRates for all patients
patients_data = list(patients_col.find({}, {"_id": 0, "Lambda": 1, "ShowRate": 1}))

# Close the database connection
client.close()

# Process fetched data
lambdas = [patient["Lambda"] for patient in patients_data]
show_rates = [patient.get("ShowRate", 0) for patient in patients_data]

# Desired wait time input from the user
desired_wait_time = float(input("Enter the desired average wait time (in weeks): "))

# Define the simulation parameters
weeks = 52  # Simulate over 52 weeks (1 year)

# Adjusted simulation function to calculate wait times including ShowRate
def simulate_panel_size(panel_size, lambdas, show_rates, total_slots):
    total_requested_appointments = 0
    for i in range(panel_size):
        adjusted_lambda = lambdas[i] * show_rates[i]  # Adjust lambda by ShowRate
        patient_appointments = np.sum(np.random.poisson(adjusted_lambda, weeks))
        total_requested_appointments += patient_appointments
    
    overflow = total_requested_appointments - total_slots
    if overflow > 0:
        wait_time = overflow / panel_size
    else:
        wait_time = 0
    return wait_time

# Function to find optimal panel size for a given FTE
def find_optimal_panel_size_for_fte(fte):
    hours_per_week = fte * 37.5 / 2  # MRP's availability for booked appointments
    slots_per_week = hours_per_week * 2  # 30 mins per appointment
    total_slots = slots_per_week * weeks
    for size in range(len(lambdas), 0, -1):
        wait_time = simulate_panel_size(size, lambdas, show_rates, total_slots)
        if wait_time <= desired_wait_time:
            return size
    return None

# Iterate over FTE values and find optimal panel sizes
fte_values = np.arange(0.5, 1.3, 0.1)
optimal_panel_sizes = []

for fte in fte_values:
    optimal_size = find_optimal_panel_size_for_fte(fte)
    optimal_panel_sizes.append(optimal_size)

# Plotting FTE values against optimal panel sizes
plt.figure(figsize=(16, 9))
plt.plot(fte_values, optimal_panel_sizes, marker='o', linestyle='-', color='blue')
plt.title('Optimal Panel Size vs. FTE')
plt.xlabel('FTE')
plt.ylabel('Optimal Panel Size')
plt.grid(True)
plt.tight_layout()
plt.show()

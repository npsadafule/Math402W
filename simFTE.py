import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from credentials import USERNAME, PASSWORD

# Desired wait time input from the user
desired_wait_time = float(input("Enter the desired average wait time (in weeks): "))
fte = float(input("Enter the FTE: "))

# MongoDB connection details
uri = f'mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.lxrcibg.mongodb.net/'
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

# Assuming a default ShowRate of 0 for patients without a ShowRate value
show_rates = [patient.get("ShowRate", 0) for patient in patients_data]


# Define the simulation parameters
hours_per_week = fte * 37.5 / 2  # MRP's availability for booked appointments
slots_per_week = hours_per_week * 2  # 30 mins per appointment
weeks = 52  # Simulate over 52 weeks (1 year)
total_slots = slots_per_week * weeks

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

# Find optimal panel size including ShowRate in the calculation
panel_sizes = []
average_wait_times = []
optimal_panel_size = None

for size in range(len(lambdas), 0, -1):
    wait_time = simulate_panel_size(size, lambdas, show_rates, total_slots)
    panel_sizes.append(size)
    average_wait_times.append(wait_time)
    if wait_time <= desired_wait_time and optimal_panel_size is None:
        optimal_panel_size = size

# Reverse lists to plot them from smaller to larger panel sizes
panel_sizes.reverse()
average_wait_times.reverse()

# Plotting
plt.figure(figsize=(16, 9))
plt.plot(panel_sizes, average_wait_times, marker='o', linestyle='-', color='blue')
plt.axhline(y=desired_wait_time, color='r', linestyle='--', label=f'Desired Wait Time = {desired_wait_time} weeks')
if optimal_panel_size is not None:
    plt.axvline(x=optimal_panel_size, color='g', linestyle='--', label=f'Optimal Panel Size = {optimal_panel_size}')
plt.title('Panel Size vs. Average Wait Time (including ShowRate)')
plt.xlabel('Panel Size')
plt.ylabel('Average Wait Time (weeks)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

if optimal_panel_size is not None:
    print(f"The optimal panel size to achieve a desired wait time of {desired_wait_time} weeks or less is: {optimal_panel_size}")
else:
    print("No panel size can achieve the desired wait time.")

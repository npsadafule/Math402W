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

# Database and Collection for booked and walk-in patients
db = client["healthcare"]
patients_booked_col = db["patients(booked)"]
patients_walkin_col = db["patients(walkin)"]

# Fetch lambda values and ShowRates for booked and walk-in patients
patients_booked_data = list(patients_booked_col.find({}, {"_id": 0, "Lambda": 1, "ShowRate": 1}))
patients_walkin_data = list(patients_walkin_col.find({}, {"_id": 0, "Lambda": 1, "ShowRate": 1}))

# Close the database connection
client.close()

# Process fetched data for booked and walk-in patients
lambdas_booked = [patient["Lambda"] for patient in patients_booked_data]
show_rates_booked = [patient.get("ShowRate", 0) for patient in patients_booked_data]  # Default ShowRate to 0 for booked
lambdas_walkin = [patient["Lambda"] for patient in patients_walkin_data]
show_rates_walkin = [patient.get("ShowRate", 1) for patient in patients_walkin_data]  # Default ShowRate to 1 for walk-in

# Combine lambdas and show rates for total panel
lambdas_total = lambdas_booked + lambdas_walkin
show_rates_total = show_rates_booked + show_rates_walkin

# Simulation parameters adjusted for combined appointments
hours_per_week = fte * 37.5  # Total weekly hours
slots_per_week = hours_per_week * 2  # Assuming 30 mins per appointment
weeks = 52
total_slots = slots_per_week * weeks

# Adjusted simulation function
def simulate_panel_size(panel_size, lambdas, show_rates, total_slots):
    total_requested_appointments = 0
    for i in range(panel_size):
        adjusted_lambda = lambdas[i] * show_rates[i]
        patient_appointments = np.sum(np.random.poisson(adjusted_lambda, weeks))
        total_requested_appointments += patient_appointments
    
    overflow = total_requested_appointments - total_slots
    return overflow / panel_size if overflow > 0 else 0

# Finding the optimal panel size
panel_sizes = list(range(1, len(lambdas_total) + 1))
average_wait_times = []

for size in panel_sizes:
    wait_time = simulate_panel_size(size, lambdas_total, show_rates_total, total_slots)
    average_wait_times.append(wait_time)

# Adjust the method to find the optimal panel size to get the largest panel size that meets the desired wait time
optimal_panel_size = None
for size, wait_time in reversed(list(zip(panel_sizes, average_wait_times))):
    if wait_time <= desired_wait_time:
        optimal_panel_size = size
        break

# Plotting
plt.figure(figsize=(16, 9))
plt.plot(panel_sizes, average_wait_times, marker='o', linestyle='-', color='blue')
plt.axhline(y=desired_wait_time, color='r', linestyle='--', label=f'Desired Wait Time = {desired_wait_time} weeks')
if optimal_panel_size:
    plt.axvline(x=optimal_panel_size, color='g', linestyle='--', label=f'Optimal Panel Size = {optimal_panel_size}')
plt.title('Panel Size vs. Average Wait Time (Booked and walk-in)')
plt.xlabel('Panel Size')
plt.ylabel('Average Wait Time (weeks)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

if optimal_panel_size:
    print(f"The optimal panel size to achieve a desired wait time of {desired_wait_time} weeks or less is: {optimal_panel_size}")
else:
    print("It is not possible to achieve the desired wait time with the available slots.")

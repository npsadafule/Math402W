import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from credentials import USERNAME, PASSWORD

# Desired wait time input from the user
desired_wait_time = float(input("Enter the desired average wait time (in weeks): "))

# MongoDB connection details
uri = f'mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.lxrcibg.mongodb.net/'
client = MongoClient(uri, server_api=ServerApi('1'))

# Database and Collection
db = client["healthcare"]
patients_col = db["patients"]

# Fetch lambda values for all patients
patients_lambdas = list(patients_col.find({}, {"_id": 0, "Lambda": 1}))

# Close the database connection
client.close()

# Convert lambda values to a list of floats
lambdas = [patient["Lambda"] for patient in patients_lambdas]

# Define the simulation parameters
hours_per_week = 6 * 2  # MRP's availability: 6 hours/day, 2 days/week
slots_per_week = hours_per_week * 2  # 30 mins per appointment
weeks = 16  # Simulate over 16 weeks (4 months)
total_slots = slots_per_week * weeks

# Adjusted simulation function to calculate wait times
def simulate_panel_size(panel_size, lambdas, total_slots):
    total_requested_appointments = 0
    for lam in lambdas[:panel_size]:
        patient_appointments = np.sum(np.random.poisson(lam, weeks))
        total_requested_appointments += patient_appointments
    
    overflow = total_requested_appointments - total_slots
    if overflow > 0:
        wait_time = overflow / panel_size
    else:
        wait_time = 0
    return wait_time

# Find optimal panel size
panel_sizes = []
average_wait_times = []
optimal_panel_size = None

for size in range(len(lambdas), 0, -1):
    wait_time = simulate_panel_size(size, lambdas, total_slots)
    panel_sizes.append(size)
    average_wait_times.append(wait_time)
    if wait_time <= desired_wait_time and optimal_panel_size is None:
        optimal_panel_size = size

# Reverse lists to plot them from smaller to larger panel sizes
panel_sizes.reverse()
average_wait_times.reverse()

# Plotting
plt.figure(figsize=(10, 6))
plt.plot(panel_sizes, average_wait_times, marker='o', linestyle='-', color='blue')
plt.axhline(y=desired_wait_time, color='r', linestyle='--', label=f'Desired Wait Time = {desired_wait_time} weeks')
if optimal_panel_size is not None:
    plt.axvline(x=optimal_panel_size, color='g', linestyle='--', label=f'Optimal Panel Size = {optimal_panel_size}')
plt.title('Panel Size vs. Average Wait Time')
plt.xlabel('Panel Size')
plt.ylabel('Average Wait Time (weeks)')
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.show()

# Output the optimal panel size
if optimal_panel_size is not None:
    print(f"The optimal panel size to achieve a desired wait time of {desired_wait_time} weeks or less is: {optimal_panel_size}")
else:
    print("No panel size can achieve the desired wait time.")

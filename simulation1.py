import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from pymongo.server_api import ServerApi

def simulate_panel_size(panel_size, lambdas, show_rates, total_slots, weeks):
    total_requested_appointments = 0
    for i in range(panel_size):
        # Adjust for the scenario where panel size exceeds the number of patients
        index = i % len(lambdas)  # Use modulo for cyclic access to lambda and show rates
        adjusted_lambda = lambdas[index] * show_rates[index]
        patient_appointments = np.sum(np.random.poisson(adjusted_lambda, weeks))
        total_requested_appointments += patient_appointments
    
    overflow = total_requested_appointments - total_slots
    return overflow / panel_size if overflow > 0 else 0

def run_simulation(desired_wait_time, lambdas, show_rates, total_slots, weeks, extra_patients=100):
    optimal_panel_size = None
    # Extend simulation to include extra 100 patients beyond the actual patient count
    for size in range(1, len(lambdas) + extra_patients + 1):
        wait_time = simulate_panel_size(size, lambdas, show_rates, total_slots, weeks)
        if wait_time <= desired_wait_time:
            optimal_panel_size = size
        else:
            # Continue for extra 100 patients even after exceeding the desired wait time
            if size >= len(lambdas) + extra_patients:
                break
    return optimal_panel_size

def fetch_patient_data():
    # MongoDB connection details
    uri = 'mongodb+srv://USERNAME:PASSWORD@cluster0.lxrcibg.mongodb.net/'
    client = MongoClient(uri, server_api=ServerApi('1'))
    db = client["healthcare"]
    patients_col = db["patients"]
    patients_data = list(patients_col.find({}, {"_id": 0, "Lambda": 1, "ShowRate": 1}))
    client.close()

    lambdas = [patient["Lambda"] for patient in patients_data]
    show_rates = [patient.get("ShowRate", 1) for patient in patients_data]  # Default show rate to 1 if not present
    return lambdas, show_rates

# Simulation parameters
desired_wait_time = float(input("Enter the desired average wait time (in weeks): "))
lambdas, show_rates = fetch_patient_data()
hours_per_week = 6 * 2
slots_per_week = hours_per_week * 2
weeks = 16
total_slots = slots_per_week * weeks

num_runs = 10  # Define the number of simulation runs
optimal_panel_sizes = []

for run in range(num_runs):
    optimal_size = run_simulation(desired_wait_time, lambdas, show_rates, total_slots, weeks, extra_patients=50)
    optimal_panel_sizes.append(optimal_size)
    print(f"Run {run+1}: Optimal Panel Size = {optimal_size}")

# Plot the optimal panel sizes from each simulation run
plt.figure(figsize=(10, 6))
plt.hist(optimal_panel_sizes, bins=range(min(optimal_panel_sizes), max(optimal_panel_sizes) + 1, 1), alpha=0.7, edgecolor='black')
plt.title('Distribution of Optimal Panel Sizes Across Simulation Runs')
plt.xlabel('Optimal Panel Size')
plt.ylabel('Frequency')
plt.grid(axis='y', alpha=0.75)
plt.show()

# Calculate and display the mean and median of the optimal panel sizes
if optimal_panel_sizes:
    print(f"Mean Optimal Panel Size: {np.mean(optimal_panel_sizes)}")
    print(f"Median Optimal Panel Size: {np.median(optimal_panel_sizes)}")
else:
    print("Unable to achieve the desired wait time in any simulation run.")

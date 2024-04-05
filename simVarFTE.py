import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from credentials import USERNAME, PASSWORD

desired_wait_time = float(input("Enter the desired average wait time (in weeks): "))
# MongoDB connection details - replace USERNAME and PASSWORD with your MongoDB credentials
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

# Desired wait time input from the user (static values for demonstration)

# Weeks of simulation
weeks = 52

# Simulation function
def simulate_panel_size(panel_size, lambdas, show_rates, total_slots):
    total_requested_appointments = 0
    for i in range(min(panel_size, len(lambdas))):  # Ensure we do not exceed list bounds
        adjusted_lambda = lambdas[i] * show_rates[i]
        patient_appointments = np.sum(np.random.poisson(adjusted_lambda, weeks))
        total_requested_appointments += patient_appointments
    
    overflow = total_requested_appointments - total_slots
    return overflow / panel_size if overflow > 0 else 0

# Function to find the optimal panel size for each FTE value
def find_optimal_panel_size(desired_wait_time, fte_range, lambdas_total, show_rates_total, weeks=52):
    optimal_sizes = {}
    for fte in fte_range:
        hours_per_week = fte * 37.5  # Total weekly hours available for appointments
        slots_per_week = hours_per_week * 2  # Assuming 30 mins per appointment
        total_slots = slots_per_week * weeks
        first_met_criteria = None  # To store the first panel size that meets the criteria
        # Extend search beyond the initial criteria meeting size
        for size in range(1, len(lambdas_total) + 51):  
            if size > len(lambdas_total):
                # Ensuring not to exceed the total number of patients in the simulation
                optimal_sizes[fte] = first_met_criteria if first_met_criteria else "Not achievable"
                break
            wait_time = simulate_panel_size(size, lambdas_total, show_rates_total, total_slots)
            if wait_time <= desired_wait_time:
                if first_met_criteria is None:
                    first_met_criteria = size
                last_met_criteria = size  # Update this each time the criteria is met
            elif first_met_criteria is not None:
                # If we've found at least one size meeting the criteria and then find one that doesn't, break
                optimal_sizes[fte] = last_met_criteria
                break
        else:
            # If loop completes without break, ensure we capture the last size meeting criteria
            if first_met_criteria is not None:
                optimal_sizes[fte] = last_met_criteria
    return optimal_sizes

# Range of FTE values to simulate
fte_range = np.arange(0.3, 1.2, 0.1)

# Finding the optimal panel size for each FTE value
optimal_panel_sizes = find_optimal_panel_size(desired_wait_time, fte_range, lambdas_total, show_rates_total)

# Plotting
plt.figure(figsize=(16, 9))
plt.plot(list(optimal_panel_sizes.keys()), list(optimal_panel_sizes.values()), marker='o', linestyle='-', color='blue')
plt.title('Optimal Panel Size vs. FTE for Desired Wait Time')
plt.xlabel('FTE')
plt.ylabel('Optimal Panel Size')
plt.grid(True)
plt.tight_layout()
plt.show()

import numpy as np
import matplotlib.pyplot as plt
from pymongo import MongoClient
from pymongo.server_api import ServerApi
from credentials import USERNAME, PASSWORD

# MongoDB URI and Client Setup
uri = 'mongodb+srv://{USERNAME}:{PASSWORD}@cluster0.lxrcibg.mongodb.net/'
client = MongoClient(uri, server_api=ServerApi('1'))

# Database and Collection
db = client["healthcare"]
patients_col = db["patients"]

# Fetch the lambda values for all patients
patients_lambdas = list(patients_col.find({}, {"_id": 0, "lambda": 1}))

# Close the database connection
client.close()

def can_all_book_within_limit(lambda_values, slots_per_week, weeks_limit):
    patients = len(lambda_values)
    appointment_booked = [False] * patients
    week = 0

    while not all(appointment_booked) and week < weeks_limit:
        week += 1
        appointments_this_week = 0

        for i, patient in enumerate(lambda_values):
            if not appointment_booked[i]:
                if np.random.rand() < patient["lambda"]:
                    appointment_booked[i] = True
                    appointments_this_week += 1
                    if appointments_this_week == slots_per_week:
                        break

    return all(appointment_booked)

def find_optimal_number_of_patients(lambda_values, slots_per_week, weeks_limit):
    optimal_patient_count = 0
    for patient_count in range(len(lambda_values), 0, -1):
        if can_all_book_within_limit(lambda_values[:patient_count], slots_per_week, weeks_limit):
            optimal_patient_count = patient_count
            break

    return optimal_patient_count

# Fixed parameters
slots_per_week = 12  # Fixed number of slots
weeks_limit = 52  # Maximum number of weeks to find the optimal number of patients

# Finding the optimal number of patients
optimal_patient_count = find_optimal_number_of_patients(patients_lambdas, slots_per_week, weeks_limit)
print(f"Optimal number of patients that can be accommodated: {optimal_patient_count}")

# Optional: Plotting the simulation result for the optimal number of patients
# To visualize, you may run a simulation with the optimal_patient_count and plot the weekly bookings.
import numpy as np
import matplotlib.pyplot as plt

def simulate_appointments_equal_lambda(lambda_, patients=1000, slots_per_week=12, weeks_limit=1000):
    # Using a uniform lambda for all patients.
    print(f"Using a uniform lambda of {lambda_} for all patients.")

    # Initialize tracking variables
    appointment_booked = [False] * patients
    total_appointments_booked = 0
    week = 0
    weekly_bookings = []

    # Simulation loop
    while not all(appointment_booked) and week < weeks_limit:
        week += 1
        expected_requests = lambda_ * patients
        actual_requests = np.random.poisson(expected_requests)
        appointments_this_week = min(actual_requests, slots_per_week)
        
        # Book appointments for this week
        bookings_count = 0
        for _ in range(appointments_this_week):
            for i in range(patients):
                if not appointment_booked[i]:
                    appointment_booked[i] = True
                    total_appointments_booked += 1
                    bookings_count += 1
                    break

        weekly_bookings.append(bookings_count)

        if all(appointment_booked):
            print(f"All patients have booked an appointment by week {week}.")
            break
    else:
        print(f"Not all patients could book an appointment within {weeks_limit} weeks.")

    return week, weekly_bookings

# Example usage
lambda_ = 0.25  # Adjust lambda as needed
week, weekly_bookings = simulate_appointments_equal_lambda(lambda_)

# Plotting the result
plt.figure(figsize=(10, 6))
plt.plot(range(1, week + 1), weekly_bookings, marker='o', linestyle='-', color='b')
plt.title('Weekly Bookings Over Time')
plt.xlabel('Week')
plt.ylabel('Number of Bookings')
plt.grid(True)
plt.show()
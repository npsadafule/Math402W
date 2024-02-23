import numpy as np

def simulate_appointments_equal_lambda(lambda_, patients=1000, slots_per_week=6, weeks_limit=1000):
    # Print initial setup details
    print(f"Using a uniform lambda of {lambda_} for all patients.")

    # Initialize a list to track whether each patient has booked an appointment
    appointment_booked = [False] * patients
    
    # Initialize the total number of appointments booked
    total_appointments_booked = 0

    # Initialize a counter for the number of weeks
    week = 0

    # Continue simulation until all patients have booked or reached the week limit
    while not all(appointment_booked) and week < weeks_limit:
        week += 1
        
        # The expected number of requests is the product of lambda and the patient count
        expected_requests = lambda_ * patients
        
        # Calculate the actual number of requests based on the Poisson distribution
        actual_requests = np.random.poisson(expected_requests)
        
        # Determine the number of appointments that can be booked, capped by the slots available
        appointments_this_week = min(actual_requests, slots_per_week)
        
        # Update the appointments booked
        for _ in range(appointments_this_week):
            for i in range(patients):
                if not appointment_booked[i]:
                    appointment_booked[i] = True
                    total_appointments_booked += 1
                    break

        # Check if all appointments have been booked
        if all(appointment_booked):
            print(f"All patients have booked an appointment by week {week}.")
            break
    else:
        print(f"Not all patients could book an appointment within {weeks_limit} weeks.")
        
# Example usage
lambda_ = 0.25  # Adjust lambda as needed
simulate_appointments_equal_lambda(lambda_)
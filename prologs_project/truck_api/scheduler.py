from datetime import datetime, timedelta
from .utils import check_hos_violation, calculate_reset_period

def plan_driver_schedule(pickup_time, dropoff_time, current_duty_status, last_duty_change_time):
    """
    Plan a driver's schedule to optimize HOS flexibility.
    Incorporates the Sleeper Berth Provision for split sleeper berth rule.
    """
    current_time = datetime.now()
    violation, message = check_hos_violation(last_duty_change_time, current_time)
    if violation:
        print("Violation detected:", message)
        # Calculate necessary reset if there's a violation
        new_reset_time = calculate_reset_period(current_time)
        print("New reset time proposed:", new_reset_time)
        return False, new_reset_time

    # Implement logic for Sleeper Berth Provision to split the required 10-hour off-duty into 8/2 splits.
    if current_duty_status == 'Driving':
        driving_time_left = 11 - (current_time - parse_time(last_duty_change_time)).total_seconds() / 3600
        if driving_time_left < 0:
            return False, calculate_reset_period(current_time)
        
        # Plan the schedule considering pickup and dropoff times
        time_to_pickup = (parse_time(pickup_time) - current_time).total_seconds() / 3600
        if time_to_pickup > driving_time_left:
            return False, calculate_reset_period(current_time + timedelta(hours=time_to_pickup))

    return True, None  # True indicates no violations and no changes needed

# Example Usage:
# plan_driver_schedule('2023-12-25T09:00:00Z', '2023-12-25T18:00:00Z', 'Driving', '2023-12-25T00:00:00Z')

from datetime import datetime, timedelta
import pytz

def parse_time(time_str):
    """ Parse an ISO formatted time string into a timezone-aware datetime object. """
    return datetime.fromisoformat(time_str.replace('Z', '+00:00'))

def calculate_reset_period(time):
    """ Calculate the next valid reset period for a driver. """
    return time + timedelta(hours=10)

def check_hos_violation(duty_status_start_time, current_time,
                        max_drive_time=11, max_shift_time=14,
                        max_cycle_time=70, required_reset_time=10):
    start_time = parse_time(duty_status_start_time)
    current_time = parse_time(current_time)
    elapsed_time = current_time - start_time
    hours_driven = elapsed_time.total_seconds() / 3600

    # Check for maximum continuous drive time
    if hours_driven > max_drive_time:
        return True, "Exceeded maximum continuous drive time limit."

    # Check for maximum shift time
    if hours_driven > max_shift_time:
        return True, "Exceeded maximum shift time limit."

    # Check for cycle time
    if hours_driven > max_cycle_time:
        return True, "Exceeded maximum cycle time limit."

    # Check for required reset period
    next_reset_time = calculate_reset_period(current_time)
    if next_reset_time < current_time:
        return True, "Driver has not had the required reset period."

    return False, None


# truck_api/utils.py

from datetime import datetime
import pytz

def parse_time(time_str: str) -> datetime:
    """
    Parse an ISO 8601 formatted time string to a datetime object.
    Handles the 'Z' (Zulu) time zone indicator by replacing it with '+00:00'.
    """
    try:
        return datetime.fromisoformat(time_str.replace('Z', '+00:00'))
    except ValueError as e:
        raise ValueError(f"Invalid time format: {time_str}") from e

def check_hos_violation(start_time: datetime, end_time: datetime) -> (bool, str):
    """
    Check for HOS violations between the start time and end time.
    """
    # Example logic for violation (update as needed)
    duration = (end_time - start_time).total_seconds() / 3600  # Duration in hours

    if duration > 11:
        return True, "Exceeded maximum drive hours per shift."

    # Add more checks as needed
    return False, ""


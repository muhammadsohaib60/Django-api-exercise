from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from datetime import datetime, timedelta
import pytz
from django.shortcuts import render
from .api_utils import fetch_api_data

def evaluate_hos_conditions(pickup_time_str: str, dropoff_time_str: str, duty_status: str, duty_status_start_time_str: str, cycle_work_minutes: float) -> dict:
    """
    Evaluate HOS conditions based on FMCSA regulations.
    """
    violations = []

    # Parse the datetime strings
    pickup_time = datetime.fromisoformat(pickup_time_str.replace('Z', '+00:00'))
    dropoff_time = datetime.fromisoformat(dropoff_time_str.replace('Z', '+00:00'))
    duty_status_start_time = datetime.fromisoformat(duty_status_start_time_str.replace('Z', '+00:00'))

    # 11-Hour Driving Limit
    max_drive_hours = 11
    total_drive_hours = (dropoff_time - pickup_time).total_seconds() / 3600
    if total_drive_hours > max_drive_hours:
        violations.append("Exceeded maximum drive hours per shift.")

    # 14-Hour Driving Window
    max_on_duty_hours = 14
    total_on_duty_hours = (dropoff_time - pickup_time).total_seconds() / 3600
    if total_on_duty_hours > max_on_duty_hours:
        violations.append("Exceeded maximum on-duty hours per shift.")

    # 30-Minute Break
    max_continuous_drive_hours = 8
    if total_drive_hours > max_continuous_drive_hours and duty_status not in ['OFF', 'SB']:
        violations.append("Failed to take a 30-minute break after 8 hours of driving.")

    # 60/70-Hour Duty Limit (Assuming a 7-day cycle for simplicity)
    max_weekly_on_duty_hours = 60
    cycle_on_duty_hours = cycle_work_minutes / 60
    if cycle_on_duty_hours > max_weekly_on_duty_hours:
        violations.append("Exceeded maximum on-duty hours in a 7-day period.")

    # Sleeper Berth Provision
    if duty_status == 'SB':
        sleeper_berth_hours = 8
        if (dropoff_time - duty_status_start_time).total_seconds() / 3600 < sleeper_berth_hours:
            violations.append("Failed to take 8 consecutive hours in the sleeper berth.")

    return {
        "violation": bool(violations),
        "message": "; ".join(violations)
    }


def calculate_optimal_schedule(driver_data, pickup_datetime):
    """
    Calculate the optimal schedule for the driver based on HOS rules.
    """
    # Extract relevant data from driver_data
    shift_drive_minutes = driver_data['shiftDriveMinutes']
    max_shift_drive_minutes = driver_data['maxShiftDriveMinutes']
    duty_status_start_time = datetime.fromisoformat(driver_data['dutyStatusStartTime'].replace('Z', '+00:00'))
    
    # Initialize variables for optimal schedule calculation
    remaining_drive_minutes = max_shift_drive_minutes - shift_drive_minutes
    
    rules_applied = []

    # Implement Sleeper Berth Provision logic
    if driver_data['dutyStatus'] == 'SB':
        remaining_drive_minutes += 120  # Add 2 hours for Sleeper Berth Provision
        rules_applied.append('Sleeper Berth Provision applied: +2 hours')

    # Calculate optimal dropoff time based on remaining drive minutes
    dropoff_datetime = pickup_datetime + timedelta(minutes=remaining_drive_minutes)
    
    return pickup_datetime, dropoff_datetime, rules_applied

@require_http_methods(["GET"])
def home(request):
    """
    Home page view that includes a list of drivers.
    """
    try:
        drivers_data = fetch_api_data('drivers')
    except Exception as e:
        drivers_data = []
    return render(request, 'home.html', {'drivers': drivers_data})

@require_http_methods(["GET"])
def get_trucks(request):
    """
    Endpoint to get truck data.
    """
    try:
        trucks_data = fetch_api_data('trucks')
    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch truck data: {str(e)}"}, status=500)
    
    return JsonResponse(trucks_data, safe=False)

@require_http_methods(["GET"])
def check_truck_hos(request):
    """
    Endpoint to check HOS violations for trucks.
    """
    try:
        trucks_data = fetch_api_data('trucks')
    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch truck data: {str(e)}"}, status=500)
    
    violations = []
    utc = pytz.UTC
    current_time = datetime.now(utc)
    
    for truck in trucks_data:
        truck_time = datetime.fromisoformat(truck['timeStamp'].replace('Z', '+00:00'))
        if truck_time.tzinfo is None:
            truck_time = utc.localize(truck_time)
        
        hours_driven = (current_time - truck_time).total_seconds() / 3600

        if hours_driven > 11:
            violations.append({
                "truck_name": truck['name'],
                "violation_message": "Exceeded maximum continuous drive time limit."
            })
        elif hours_driven < 0:
            violations.append({
                "truck_name": truck['name'],
                "violation_message": "Invalid timestamp (in the future)."
            })
    
    return JsonResponse({"violations": violations})

@require_http_methods(["GET"])
def get_drivers(request):
    """
    Endpoint to get driver data.
    """
    try:
        drivers_data = fetch_api_data('drivers')
    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch driver data: {str(e)}"}, status=500)
    
    return JsonResponse(drivers_data, safe=False)

@require_http_methods(["GET"])
def check_driver_hos(request):
    """
    Endpoint to check driver HOS violations.
    """
    try:
        drivers_data = fetch_api_data('drivers')  # Function to fetch driver data from API
    except Exception as e:
        return JsonResponse({"error": f"Failed to fetch driver data: {str(e)}"}, status=500)

    violations = []
    current_time = datetime.utcnow().replace(tzinfo=pytz.UTC)

    for driver in drivers_data:
        duty_start_time = driver.get('dutyStatusStartTime')
        shift_hours = driver.get('shiftDriveMinutes', 0) / 60

        if shift_hours > 11:
            violations.append({
                "driver_id": driver.get('driverId'),
                "violation_message": "Exceeded maximum drive hours per shift."
            })

        # Additional HOS checks
        schedule_evaluation = evaluate_hos_conditions(
            pickup_time_str=duty_start_time,
            dropoff_time_str=str(current_time),
            duty_status=driver.get('dutyStatus'),
            duty_status_start_time_str=duty_start_time,
            cycle_work_minutes=driver.get('cycleWorkMinutes', 0)
        )
        if schedule_evaluation['violation']:
            violations.append({
                "driver_id": driver.get('driverId'),
                "violation_message": schedule_evaluation['message']
            })

    return JsonResponse({"violations": violations})

@require_http_methods(["GET"])
def plan_optimal_schedule(request):
    """
    Endpoint to plan an optimal schedule for a driver.
    """
    driver_id = request.GET.get('driver_id').strip()
    
    try:
        drivers_data = fetch_api_data('drivers')
    except Exception as e:
        return JsonResponse({'error': f"Failed to fetch driver data: {str(e)}"}, status=500)
    
    driver_data = next((driver for driver in drivers_data if driver['driverId'] == driver_id), None)
    
    if not driver_data:
        return JsonResponse({'error': 'Driver ID not found'}, status=404)

    try:
        # Use current time as pickup time for the sake of optimization
        pickup_datetime = datetime.now(pytz.UTC)
        pickup_datetime, dropoff_datetime, rules_applied = calculate_optimal_schedule(driver_data, pickup_datetime)
    except Exception as e:
        return JsonResponse({'error': f"Failed to calculate dropoff time: {str(e)}"}, status=500)

    schedule_evaluation = evaluate_hos_conditions(
        pickup_time_str=pickup_datetime.isoformat(),
        dropoff_time_str=dropoff_datetime.isoformat(),
        duty_status=driver_data.get('dutyStatus', ''),
        duty_status_start_time_str=driver_data.get('dutyStatusStartTime', ''),
        cycle_work_minutes=driver_data.get('cycleWorkMinutes', 0)
    )
    
    schedule = {
        'driverId': driver_id,
        'pickup': pickup_datetime.isoformat(),
        'dropoff': dropoff_datetime.isoformat()
    }

    return JsonResponse({
        'schedule': schedule,
        'hos_violations': schedule_evaluation,
        'rules_applied': rules_applied
    })


@require_http_methods(["GET"])
def check_hos_with_conditions(request):
    """
    Endpoint to check HOS conditions based on provided pickup and dropoff times, and duty status.
    """
    driver_id = request.GET.get('driver_id').strip()
    pickup_time = request.GET.get('pickup_time')
    dropoff_time = request.GET.get('dropoff_time')

    try:
        pickup_datetime = datetime.strptime(pickup_time, '%Y-%m-%dT%H:%M').replace(tzinfo=pytz.UTC)
        dropoff_datetime = datetime.strptime(dropoff_time, '%Y-%m-%dT%H:%M').replace(tzinfo=pytz.UTC)
    except ValueError as e:
        return JsonResponse({'error': str(e)}, status=400)

    try:
        drivers_data = fetch_api_data('drivers')
    except Exception as e:
        return JsonResponse({'error': f"Failed to fetch driver data: {str(e)}"}, status=500)
    
    driver_data = next((driver for driver in drivers_data if driver['driverId'] == driver_id), None)
    
    if not driver_data:
        return JsonResponse({'error': 'Driver ID not found'}, status=404)

    schedule_evaluation = evaluate_hos_conditions(
        pickup_time_str=pickup_datetime.isoformat(),
        dropoff_time_str=dropoff_datetime.isoformat(),
        duty_status=driver_data.get('dutyStatus', ''),
        duty_status_start_time_str=driver_data.get('dutyStatusStartTime', ''),
        cycle_work_minutes=driver_data.get('cycleWorkMinutes', 0)
    )

    return JsonResponse({
        'hos_violations': schedule_evaluation
    })

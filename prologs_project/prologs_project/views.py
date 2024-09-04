from django.shortcuts import render
from truck_api.api_utils import fetch_api_data  # Adjust the import according to your project structure

def home(request):
    drivers_data = fetch_api_data('drivers')
    return render(request, 'home.html', {'drivers': drivers_data})

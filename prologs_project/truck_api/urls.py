from django.urls import path
from .views import get_trucks, check_truck_hos, get_drivers, check_driver_hos, plan_optimal_schedule,check_hos_with_conditions

urlpatterns = [
    path('trucks/', get_trucks, name='get_trucks'),
    path('check_truck_hos/', check_truck_hos, name='check_truck_hos'),
    path('drivers/', get_drivers, name='get_drivers'),
    path('check_driver_hos/', check_driver_hos, name='check_driver_hos'),
    path('schedule/', plan_optimal_schedule, name='plan_schedule'),
    path('check_hos_with_conditions/', check_hos_with_conditions, name='check_hos_with_conditions'),
]


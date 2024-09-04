from django.db import models

# Create your models here.
from django.db import models

class DriverSchedule(models.Model):
    driver_id = models.CharField(max_length=100)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    status = models.CharField(max_length=100)  # 'driving', 'rest', 'on-duty', etc.

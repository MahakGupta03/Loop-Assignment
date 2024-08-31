from django.db import models

class Store(models.Model):
    store_id = models.CharField(max_length=50)
    status = models.CharField(max_length=10)
    timestamp_utc = models.DateTimeField()

class BusinessHours(models.Model):
    store_id = models.CharField(max_length=50)
    day = models.IntegerField()  # 0 = Monday, 6 = Sunday
    start_time_local = models.TimeField()
    end_time_local = models.TimeField()

class StoreTimezones(models.Model):
    store_id = models.CharField(max_length=50)
    timezone_str = models.CharField(max_length=50, default='America/Chicago')

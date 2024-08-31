import csv
from django.core.management.base import BaseCommand
from monitor.models import Store, BusinessHours, StoreTimezones
from datetime import datetime,timedelta
import pytz
import time
import functools
import pandas as pd


class Command(BaseCommand):
    help = 'Load CSV data into the database'

    def handle(self, *args, **kwargs):
        # Import data from CSVs
        batch_size = 10000
        stores_csv = pd.read_csv('../store_monitoring/store.csv', chunksize=10000)
        business_hours_csv = pd.read_csv('../store_monitoring/business hours.csv', chunksize=batch_size)
        timezones_csv = pd.read_csv('../store_monitoring/timezone.csv', chunksize=batch_size)

        # Define timezone dictionary
        timezone_dict = {}
        for _, row in pd.concat(timezones_csv).iterrows():
            timezone_dict[row['store_id']] = pytz.timezone(row['timezone_str'])

        for business_hours_df in business_hours_csv:
            business_hours_objects = []
            for i,row in business_hours_df.iterrows():
                start_time = pd.to_datetime(row['start_time_local']).time()
                end_time = pd.to_datetime(row['end_time_local']).time()
                business_hours_objects.append(
                    BusinessHours(
                        store_id=row['store_id'],
                        day=int(row['day']),
                        start_time_local=start_time,
                        end_time_local=end_time
                    )
                )

            BusinessHours.objects.bulk_create(business_hours_objects)


        for timezones_df in timezones_csv:
            store_timezone_objects = []
            for i, row in timezones_df.iterrows():
                store_timezone_objects.append(
                    StoreTimezones(
                        store_id=row['store_id'],
                        timezone_str=row['timezone_str']
                    )
                )

            StoreTimezones.objects.bulk_create(store_timezone_objects, batch_size=batch_size)


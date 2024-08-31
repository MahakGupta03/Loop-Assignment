import json
import pytz
from monitor.models import Store, BusinessHours, StoreTimezones
from datetime import datetime, timedelta


def get_store_uptime_downtime(store_id, start_date, end_date):
    """
    Computes the uptime and downtime for a given store within a given time range.
    """
    store=Store.objects.values_list('store_id', flat=True).distinct()

    timezone_str = StoreTimezones.objects.get(store_id=store_id).timezone_str
    timezone = pytz.timezone(timezone_str)

    # Compute business hours in local timezone for each day within the given time range
    business_hours = {}
    for day_offset in range((end_date - start_date).days + 1):
        date = start_date + timedelta(days=day_offset)
        day_of_week = date.weekday()
        local_start_time = datetime.combine(date, BusinessHours.objects.get(store_id=store_id, day=day_of_week).start_time_local)
        local_end_time = datetime.combine(date, BusinessHours.objects.get(store_id=store_id, day=day_of_week).end_time_local)
        business_hours[date] = (local_start_time.astimezone(timezone), local_end_time.astimezone(timezone))

    # Retrieve store status changes within the given time range
    status_changes = Store.objects.filter(store_id=store_id, timestamp_utc__range=(start_date, end_date)).order_by('timestamp_utc')
    # Initialize counters for uptime and downtime
    uptime = timedelta()
    downtime = timedelta()

    # Compute uptime and downtime based on status changes and business hours
    last_status = None
    for i, status_change in enumerate(status_changes):
        if i == 0:
            last_status = status_change.status
            continue

        time_diff = status_change.timestamp_utc - status_changes[i - 1].timestamp_utc

        if last_status == "open":
            # Compute downtime during non-business hours
            for j in range((status_changes[i - 1].timestamp_utc.date() - start_date).days, (status_change.timestamp_utc.date() - start_date).days):
                date = start_date + timedelta(days=j)
                if business_hours[date][1] < business_hours[date][0]:
                    downtime += timedelta(hours=24) - (business_hours[date][1] - business_hours[date][0])
                else:
                    downtime += max(timedelta(), business_hours[date][0] - business_hours[date][1])
            uptime += time_diff
        else:
            # Compute uptime during business hours
            for j in range((status_changes[i - 1].timestamp_utc.date() - start_date).days, (status_change.timestamp_utc.date() - start_date).days):
                date = start_date + timedelta(days=j)
                if business_hours[date][1] < business_hours[date][0]:
                    uptime += timedelta(hours=24) - (business_hours[date][1] - business_hours[date][0])
                else:
                    uptime += max(timedelta(), business_hours[date][1] - business_hours[date][0])
            downtime += time_diff

        last_status = status_change.status

    # Compute uptime and downtime for the last status change to the end of the time range
    if last_status == "open":
        for j in range((status_changes[-1].timestamp_utc.date() - start_date).days, (end_date - start_date).days + 1):
            date = start_date + timedelta(days=j)
            if business_hours[date][1] is not None:
                downtime += business_hours[date][1] - business_hours[date][0]

    else:
        for j in range((status_changes[-1].timestamp_utc.date() - start_date).days, (end_date - start_date).days + 1):
            date = start_date + timedelta(days=j)
            if business_hours[date][0] is not None:
                uptime += business_hours[date][1] - business_hours[date][0]

    return uptime, downtime




# def generate_report():

#     # Generate report data
#     report_data = []

#     # Fetch all stores and their statuses in a single query
#     stores = Store.objects.values('store_id').distinct()
#     store_statuses = Store.objects.filter(store_id__in=[store['store_id'] for store in stores]).values('store_id', 'status')

#      # Create a dictionary to map store_id to its status
#     store_status_map = {store['store_id']: store['status'] for store in store_statuses}

#     for store in stores:
#         store_id = store['store_id']
#         status = store_status_map.get(store_id)

#         # uptime, downtime = compute_uptime(store.store_id)
#         uptime, downtime = compute_uptime(store)
#         report_data.append({
#             'store_id': store,
#             'status': status,
#             'uptime': round(uptime, 2),
#             'downtime': round(downtime, 2)
#         })


#     return report_data



def generate_report():
    report_data = []

    # Fetch all stores and their statuses in a single query
    stores = Store.objects.values('store_id').distinct()
    store_statuses = Store.objects.filter(store_id__in=[store['store_id'] for store in stores]).values('store_id', 'status')

    # Create a dictionary to map store_id to its status
    store_status_map = {store['store_id']: store['status'] for store in store_statuses}

    for store in stores:
        store_id = store['store_id']
        status = store_status_map.get(store_id)

        # Compute uptime and downtime for different periods
        uptime_last_hour, downtime_last_hour = compute_uptime(store_id, timedelta(hours=1))
        uptime_last_day, downtime_last_day = compute_uptime(store_id, timedelta(days=1))
        uptime_last_week, downtime_last_week = compute_uptime(store_id, timedelta(weeks=1))

        report_data.append({
            'store_id': store_id,
            'uptime_last_hour': round(uptime_last_hour, 2),
            'uptime_last_day': round(uptime_last_day, 2),
            'uptime_last_week': round(uptime_last_week, 2),
            'downtime_last_hour': round(downtime_last_hour, 2),
            'downtime_last_day': round(downtime_last_day, 2),
            'downtime_last_week': round(downtime_last_week, 2)
        })

    return report_data




# def compute_uptime(store_id, start_date=None, end_date=None):
#     if not start_date:
#         start_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0)
#     if not end_date:
#         end_date = datetime.utcnow().replace(hour=0, minute=0, second=0, microsecond=0) + timedelta(days=1)
#     timezone = get_store_timezone(store_id)
    
#     start_date = pytz.utc.localize(start_date).astimezone(timezone)
#     end_date = pytz.utc.localize(end_date).astimezone(timezone)
    
#     business_hours = get_store_business_hours(store_id)
#     hours_open = compute_business_hours_overlap(business_hours, timezone, start_date, end_date)
#     uptime = hours_open / timedelta(hours=24) * 100
#     downtime = 100 - uptime

#     return uptime, downtime



def compute_uptime(store_id, period):
    end_date = datetime.utcnow()
    start_date = end_date - period
    timezone = get_store_timezone(store_id)
    
    start_date = pytz.utc.localize(start_date).astimezone(timezone)
    end_date = pytz.utc.localize(end_date).astimezone(timezone)
    
    business_hours = get_store_business_hours(store_id)
    
    # Placeholder logic to compute uptime and downtime
    # Replace this with actual logic to compute uptime and downtime for the given period
    uptime = 0
    downtime = 0
    
    # Example logic (to be replaced with actual computation)
    for hour in range(int(period.total_seconds() // 3600)):
        uptime += 50  # Example: 50 minutes of uptime per hour
        downtime += 10  # Example: 10 minutes of downtime per hour
    
    return uptime, downtime





def get_store_timezone(store_id):
    timezone = StoreTimezones.objects.filter(store_id=store_id).first()
    if timezone is None:
        return pytz.timezone('America/Chicago')
    return pytz.timezone(timezone.timezone_str)


def get_store_business_hours(store_id):
    business_hours = BusinessHours.objects.filter(store_id=store_id)
    return [(bh.day, bh.start_time_local, bh.end_time_local) for bh in business_hours]


def compute_business_hours_overlap(business_hours, timezone, start_date, end_date):
    total_overlap = timedelta()
    for day, start_time, end_time in business_hours:
        start_time_utc = timezone.localize(datetime.combine(start_date.date(), start_time)).astimezone(pytz.utc)
        end_time_utc = timezone.localize(datetime.combine(end_date.date(), end_time)).astimezone(pytz.utc)
        if start_time_utc >= end_time_utc:
            end_time_utc += timedelta(days=1)
        business_day_start = max(start_date, start_time_utc)
        business_day_end = min(end_date, end_time_utc)
        overlap = (business_day_end - business_day_start).total_seconds() / 3600
        overlap = max(overlap, 0)
        total_overlap += timedelta(hours=overlap)
    return total_overlap


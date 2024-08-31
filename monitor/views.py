from django.shortcuts import render
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from monitor.report_generator import generate_report
import uuid
import pandas as pd

report_store = {}
@csrf_exempt
def trigger_report(request):
    report_id = str(uuid.uuid4())
    report_store[report_id] = "Running"
    
    # Trigger the report generation in the background
    report_data = generate_report()
    
    # Store the result
    report_store[report_id] = report_data
    return JsonResponse({"report_id": report_id})

def get_report(request, report_id):
    if report_id not in report_store:
        return JsonResponse({"error": "Invalid report_id"}, status=404)
    
    report_data = report_store[report_id]
    if report_data == "Running":
        return JsonResponse({"status": "Running"})
    
    df = pd.DataFrame(report_data)
    
    # Save DataFrame to a CSV file
    csv_file_path = f'report_{report_id}.csv'
    df.to_csv(csv_file_path, index=False)
    
    return JsonResponse({
        "status": "Complete",
        "data": report_data
    })
from django.shortcuts import render

# Create your views here.
# views.py
import os
import pandas as pd
import matplotlib.pyplot as plt
import json
from django.http import JsonResponse
from rest_framework.decorators import api_view
from invoice.models import Invoice
from .utils import load_data_from_db, format_invoice_date, product_analysis

# Set Matplotlib to use 'Agg' backend
plt.switch_backend('Agg')

@api_view(['POST'])
def generate_product_analysis(request):
    try:
        user_id = request.data.get('user_id')
        if not user_id:
            return JsonResponse({'error': 'user_id is required'}, status=400)

        invoices = Invoice.objects.filter(recipient=user_id)
        data = load_data_from_db(invoices)
        data = format_invoice_date(data)
        top_selling, price_analysis = product_analysis(data)

        response_data = {
            'top_selling': format_chart_data(top_selling),
            'price_analysis': format_chart_data(price_analysis),
        }

        return JsonResponse(response_data, status=200)
    except Exception as e:
        print(f"Error in generate_product_analysis: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def get_product_pie_chart(request, year):
    try:
        file_name = f'static/charts/product_pie_chart_{year}.png'
        if not os.path.exists(file_name):
            return JsonResponse({'error': 'Pie chart image not found for the specified year'}, status=404)

        top_selling, _ = product_analysis(load_data_from_db(Invoice.objects.all()))  # Load data to get actual values
        top_selling_year = top_selling.get(year)

        response_data = {
            "labels": list(top_selling_year.index) if top_selling_year else [],
            "data": list(top_selling_year.values) if top_selling_year else [],
            "backgroundColor": ["#FF6384", "#36A2EB", "#FFCE56"],
            "downloadUrl": request.build_absolute_uri(file_name),
        }
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Error in get_product_pie_chart: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

@api_view(['GET'])
def get_product_bar_chart(request, year):
    try:
        file_name = f'static/charts/product_bar_chart_{year}.png'
        if not os.path.exists(file_name):
            return JsonResponse({'error': 'Bar chart image not found for the specified year'}, status=404)

        _, price_analysis = product_analysis(load_data_from_db(Invoice.objects.all()))  # Load data to get actual values
        price_analysis_year = price_analysis.get(year)

        response_data = {
            "labels": list(price_analysis_year.index) if price_analysis_year else [],
            "data": list(price_analysis_year.values) if price_analysis_year else [],
            "downloadUrl": request.build_absolute_uri(file_name),
        }
        return JsonResponse(response_data)
    except Exception as e:
        print(f"Error in get_product_bar_chart: {str(e)}")
        return JsonResponse({'error': str(e)}, status=500)

def format_chart_data(chart_data):
    response = []
    for year, data in chart_data.items():
        formatted_data = {
            'year': int(year),
            'labels': list(data.index),
            'data': [int(value) for value in data.values],
        }
        response.append(formatted_data)
    return response
 
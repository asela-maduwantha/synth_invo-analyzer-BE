from django.urls import path
from .views import generate_product_analysis, get_product_pie_chart, get_product_bar_chart

urlpatterns = [
    path('generate-product-analysis/', generate_product_analysis, name='generate_product_analysis'),
    path('get-product-pie-chart/<int:year>/', get_product_pie_chart, name='get_product_pie_chart'),
    path('get-product-bar-chart/<int:year>/', get_product_bar_chart, name='get_product_bar_chart'),
]
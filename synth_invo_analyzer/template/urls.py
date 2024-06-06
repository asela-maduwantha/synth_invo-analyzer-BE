from django.urls import path
from . import views  

urlpatterns = [
    path('upload-internal-invoice-format/', views.store_internal_format, name='upload-internal-invoice-format'),  
    path('upload_invoice_template/', views.upload_invoice_template, name='uplod-template'),
    path('get_template_keys/<str:template_id>/', views.get_template_keys, name='get-template-keys'),
    path('get-internal-keys/', views.get_internal_format_attributes, name="get-internal"),
    path('save_template_mapping/', views.save_template_mapping, name='save-maps'),
    path('get-template-by-supplier/', views.get_template_by_supplier, name='get-template'),
    path('get-mapping-by-id/', views.get_mapping_by_supplier, name='get_mapping_by_supplier'),
]


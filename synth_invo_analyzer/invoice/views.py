from rest_framework.response import Response
from rest_framework.decorators import api_view
import json
from .models import Invoice
from .utils import convert_invoice
from .serializers import InvoiceSerializer
from rest_framework import status
from search.elasticsearch_utils import index_invoice

@api_view(['POST'])
def create_invoice(request):
    try:
        if 'source_invoice' in request.FILES:
            source_invoice_file = request.FILES['source_invoice']
            source_invoice = json.load(source_invoice_file)
        else:
            source_invoice = json.loads(request.data.get('source_invoice'))

    
        supplier_id = request.data.get("supplier_id")
        organization_id = request.data.get("organization_id")
        converted_invoice = convert_invoice(source_invoice, supplier_id)
       
        

        invoice_data = {
            'issuer': supplier_id,
            'recipient': organization_id,
            'source_format': json.dumps(source_invoice),  
            'internal_format': json.dumps(converted_invoice),  
        }

        serializer = InvoiceSerializer(data=invoice_data)
        

        if serializer.is_valid():
            serializer.save()
            
            
            invoice_instance = serializer.instance  # Access the saved instance

            # Index the invoice in Elasticsearch
            index_invoice(invoice_instance)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        else:
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    except Exception as e:
        print(e)
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def supplier_invoice_view(request):
    try:
        supplier_id = request.query_params.get('user_id')
        
        invoices = Invoice.objects.filter(issuer=supplier_id)
        

        serializer = InvoiceSerializer(invoices, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
def organization_invoice_view(request):
    try:
        organization_id = request.query_params.get('user_id')
        
        invoices = Invoice.objects.filter(recipient=organization_id)
        

        serializer = InvoiceSerializer(invoices, many=True)
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        print(e)
        return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
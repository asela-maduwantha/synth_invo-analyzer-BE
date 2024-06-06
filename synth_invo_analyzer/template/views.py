from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import InternalInvoiceFormat, TemplateMapping, InvoiceTemplate
from .serializers import InternalInvoiceFormatSerializer, InvoiceTemplateSerializer
from .utils import extract_keys
from authentication.models import SystemAdmin
import json
import uuid

@api_view(['POST'])
def store_internal_format(request):
    invoice_file = request.FILES.get('internal')
    system_admin_id = request.data.get("uploaded_user")
    
    if not invoice_file:
        return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

    # Check if an internal invoice format already exists
    if InternalInvoiceFormat.objects.exists():
        return Response({"error": "An internal invoice format already exists."}, status=status.HTTP_400_BAD_REQUEST)

    internal_invoice = invoice_file.read().decode("utf-8")
    
    try:
        internal_invoice_json = json.loads(internal_invoice)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format."}, status=status.HTTP_400_BAD_REQUEST)
    
    extracted_attributes = extract_keys(internal_invoice_json)
    
    system_admin = SystemAdmin.objects.filter(admin_id=system_admin_id)
    if not system_admin.exists():
        return Response({"error": "System Admin not found."}, status=status.HTTP_404_NOT_FOUND)

    internal_format_data = {
        "uploaded_user": system_admin_id,
        "internal_format": internal_invoice,
        "attributes": extracted_attributes
    }

    serializer = InternalInvoiceFormatSerializer(data=internal_format_data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def upload_invoice_template(request):
    try:
        supplier = request.data.get('uploaded_user')

        # Check if an invoice template already exists for the supplier
        if InvoiceTemplate.objects.filter(supplier=supplier).exists():
            return Response({"error": "An invoice template for this supplier already exists."}, status=status.HTTP_400_BAD_REQUEST)

        invoice_file = request.FILES.get('invoice_template')
        if not invoice_file:
            return Response({"error": "No file provided."}, status=status.HTTP_400_BAD_REQUEST)

        template_content = invoice_file.read().decode('utf-8')

        try:
            template_content_json = json.loads(template_content)
        except json.JSONDecodeError:
            return Response({"error": "Invalid JSON content."}, status=status.HTTP_400_BAD_REQUEST)

        template_content = json.dumps(template_content_json)

        invoice_template = InvoiceTemplate(
            supplier=supplier,
            template_name=invoice_file.name,
            template_content=template_content
        )
        invoice_template.save()
        return Response({"template_id": str(invoice_template.id)}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['POST'])
def save_template_mapping(request):
    try:
        template_id = request.data.get('template_id')
        supplier_id = request.data.get('user_id')
        mapping_data = request.data.get("mapping")

        if not template_id:
            return Response({"error": "Template ID is required."}, status=status.HTTP_400_BAD_REQUEST)

        if not mapping_data:
            return Response({"error": "Mapping data is required."}, status=status.HTTP_400_BAD_REQUEST)

        # Check if a mapping already exists for the supplier
        if TemplateMapping.objects.filter(supplier=supplier_id).exists():
            return Response({"error": "A mapping for this supplier already exists."}, status=status.HTTP_400_BAD_REQUEST)

        mapping_json = json.dumps(mapping_data)
        
        template_mapping = TemplateMapping(
            template_id=template_id,
            supplier=supplier_id,
            mapping=mapping_json
        )
        template_mapping.save()

        return Response({"success": "Mapping saved successfully"}, status=status.HTTP_201_CREATED)
    except Exception as e:
        return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_internal_format_attributes(request):
    all_internal_invoices = InternalInvoiceFormat.objects.all()
    unique_attributes = set()
    for invoice in all_internal_invoices:
        if invoice.attributes:
            unique_attributes.update(invoice.attributes)

    return Response({"attributes": list(unique_attributes)}, status=status.HTTP_200_OK)


@api_view(['GET'])
def get_template_keys(request, template_id):
    try:
        template = InvoiceTemplate.objects.get(id=template_id)
        json_content = json.loads(template.template_content)
        extracted_keys = list(extract_keys(json_content))
        return Response({"keys": extracted_keys}, status=status.HTTP_200_OK)
    except InvoiceTemplate.DoesNotExist:
        return Response({"error": "Template not found."}, status=status.HTTP_404_NOT_FOUND)
    except json.JSONDecodeError:
        return Response({"error": "Invalid JSON format."}, status=status.HTTP_400_BAD_REQUEST)


@api_view(['GET'])
def get_template_by_supplier(request):
    try:
        supplier_id = request.query_params.get('user_id')
        if not supplier_id:
            return Response({'error': 'supplier_id is required'}, status=status.HTTP_400_BAD_REQUEST)

        template = InvoiceTemplate.objects.filter(supplier=supplier_id)
        
        if not template.exists():
            return Response({'error': 'Template not found for the given supplier_id'}, status=status.HTTP_404_NOT_FOUND)
        
        serializer = InvoiceTemplateSerializer(template, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


@api_view(['GET'])
def get_mapping_by_supplier(request):
    try:
        supplier_id = request.query_params.get('user_id')
        
        template_mapping = TemplateMapping.objects.get(supplier=supplier_id)
        
        return Response(template_mapping.mapping, status=status.HTTP_200_OK)
    except TemplateMapping.DoesNotExist:
        return Response({'error': 'Template not found for the given supplier_id'}, status=status.HTTP_404_NOT_FOUND)
    except Exception as e:
        return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

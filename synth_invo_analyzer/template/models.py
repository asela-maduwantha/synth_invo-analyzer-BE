from cassandra.cqlengine import columns
from django_cassandra_engine.models import DjangoCassandraModel
import uuid
from datetime import datetime
import json

class InternalInvoiceFormat(DjangoCassandraModel):
    id = columns.UUID(default=uuid.uuid4)  
    uploaded_user = columns.Integer()  # systemadmin
    internal_format = columns.Text(primary_key=True)  
    uploaded_at = columns.DateTime(default=datetime.now)  
    attributes = columns.List(columns.Text)
    
class InvoiceTemplate(DjangoCassandraModel):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    supplier = columns.Integer()  # Supplier
    template_name = columns.Text()  
    template_content = columns.Text()  # Store JSON content as text
    attributes = columns.List(columns.Text)  # If you need attributes
    uploaded_at = columns.DateTime(default=datetime.now)

class TemplateMapping(DjangoCassandraModel):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    template_id = columns.UUID()
    supplier = columns.Integer()
    mapping = columns.Text()  # Store mapping as text
    created_at = columns.DateTime(default=datetime.now)

    @property
    def mapping_dict(self):
        return json.loads(self.mapping) if self.mapping else {}

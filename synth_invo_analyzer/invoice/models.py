from django_cassandra_engine.models import DjangoCassandraModel
from cassandra.cqlengine import columns
import uuid
from datetime import datetime

class Invoice(DjangoCassandraModel):
    id = columns.UUID(primary_key=True, default=uuid.uuid4)
    issuer = columns.Integer()
    recipient = columns.Integer()
    source_format = columns.Text()  
    internal_format = columns.Text()  #json format and use for search
    created_at = columns.DateTime(default=datetime.now)

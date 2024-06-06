import json
from template.models import TemplateMapping, InternalInvoiceFormat

def convert_invoice(source_invoice, supplier_id):

    template_mapping = TemplateMapping.objects.get(supplier = supplier_id)
    mappings = json.loads(template_mapping.mapping)
  

    internal = InternalInvoiceFormat.objects().first()
  
    
    target = json.loads(internal.internal_format)


    for source_key, target_key in mappings.items():
        if '[]' in source_key:
           
            source_prefix, source_field = source_key.split('[]')
            target_prefix, target_field = target_key.split('[]')
            if source_prefix in source_invoice:
                target_list = []
                for item in source_invoice[source_prefix]:
                    target_item = {}
                    for sub_source_key, sub_target_key in mappings.items():
                        if sub_source_key.startswith(source_prefix + '[]'):
                            sub_source_field = sub_source_key.split('[]')[1][1:]
                            sub_target_field = sub_target_key.split('[]')[1][1:]
                            if sub_source_field in item:
                                set_value(target_item, sub_target_field, item[sub_source_field])
                    target_list.append(target_item)
                set_value(target, target_prefix, target_list)
        else:
            source_parts = source_key.split('.')
            value = source_invoice
            for part in source_parts:
                if value and part in value:
                    value = value.get(part)
                else:
                    value = None
                    break
            if value is not None:
                set_value(target, target_key, value)

    return target

def set_value(target_dict, key_path, value):
        keys = key_path.split('.')
        for key in keys[:-1]:
            if key not in target_dict:
                target_dict[key] = {}
            target_dict = target_dict[key]
        target_dict[keys[-1]] = value
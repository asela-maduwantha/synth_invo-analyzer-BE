def extract_keys(json_obj, parent_key=''):
    keys = []
    if isinstance(json_obj, dict):
        for key, value in json_obj.items():
            new_key = f"{parent_key}.{key}" if parent_key else key
            if isinstance(value, dict):
                keys.extend(extract_keys(value, new_key))
            elif isinstance(value, list) and value:
                if isinstance(value[0], dict):
                    keys.extend(extract_keys(value[0], f"{new_key}[]"))
                else:
                    keys.append(new_key + '[]')
            else:
                keys.append(new_key)
    return keys

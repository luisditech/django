def set_nested(data, path, value):
    keys = path.split(".")
    d = data
    for i, key in enumerate(keys[:-1]):
        try:
            key_int = int(key)
            while len(d) <= key_int:
                d.append({})
            d = d[key_int]
        except (ValueError, TypeError):
            if key not in d or not isinstance(d[key], (dict, list)):
                d[key] = {}
            d = d[key]
    final_key = keys[-1]
    try:
        final_index = int(final_key)
        while len(d) <= final_index:
            d.append({})
        d[final_index] = value
    except (ValueError, TypeError):
        d[final_key] = value

def append_nested(data, path, value):
    keys = path.split(".")
    d = data
    for k in keys[:-1]:
        d = d.setdefault(k, {})
    if keys[-1] not in d or not isinstance(d[keys[-1]], list):
        d[keys[-1]] = []
    d[keys[-1]].append(value)

def delete_nested(data, path):
    keys = path.split(".")
    d = data
    for k in keys[:-1]:
        d = d.get(k, {})
    d.pop(keys[-1], None)
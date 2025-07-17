import re
import json

def normalize_payload(data):
    if isinstance(data, dict):
        return [data]
    elif isinstance(data, list):
        return data
    elif isinstance(data, str):
        try:
            parsed = json.loads(data)
            if isinstance(parsed, list):
                return parsed
            else:
                return [parsed]
        except json.JSONDecodeError:
            return [data]  # caso raro: string normal, no es JSON
    else:
        raise ValueError(f"Unsupported data format for PostgreSQL insert: {type(data)}")

def extract_value_from_path(data, path):
    keys = re.split(r'\.(?![^\[]*\])', path)
    current = data
    try:
        for key in keys:
            if '[' in key and ']' in key:
                key_name, index = key[:-1].split('[')
                current = current[key_name][int(index)]
            else:
                current = current[key]
        return current
    except (KeyError, IndexError, TypeError):
        return None

def set_value_at_path(output, path, value):
    keys = path.split('.')
    current = output
    for key in keys[:-1]:
        if key not in current or not isinstance(current[key], dict):
            current[key] = {}
        current = current[key]
    current[keys[-1]] = value

def get_nested(data, path):
    keys = path.split(".")
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return None
    return data

def apply_mapping_to_dataset(dataset, mapping: dict):
    def map_record(record):
        new_record = {}
        for target_field, source_field in mapping.items():
            # 🔹 Constante explícita
            if isinstance(source_field, str) and source_field.startswith("$const:"):
                value = source_field.replace("$const:", "")

            # 🔹 Plantilla tipo ext_{ID_BOOKING}
            elif isinstance(source_field, str) and "{" in source_field and "}" in source_field:
                value = re.sub(r"\{(.*?)\}", lambda m: str(get_nested(record, m.group(1)) or ""), source_field)

            # 🔹 Valor normal desde el registro
            else:
                value = get_nested(record, source_field)

            if value is not None:
                set_value_at_path(new_record, target_field, value)

        return new_record

    if isinstance(dataset, list):
        return [map_record(record) for record in dataset]
    elif isinstance(dataset, dict):
        return map_record(dataset)
    return dataset
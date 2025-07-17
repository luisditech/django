def get_nested_value(data, key_path):
    keys = key_path.split(".")
    for key in keys:
        if isinstance(data, dict):
            data = data.get(key)
        else:
            return None
    return data

def match_conditions(entry, conditions):
    for condition in conditions:
        key = condition.get("key")
        op = condition.get("op")
        value = condition.get("value")
        actual = get_nested_value(entry, key)

        if op == "==" and actual != value:
            return False
        elif op == "!=" and actual == value:
            return False
        elif op == ">" and not (isinstance(actual, (int, float)) and actual > value):
            return False
        elif op == "<" and not (isinstance(actual, (int, float)) and actual < value):
            return False
        elif op == ">=" and not (isinstance(actual, (int, float)) and actual >= value):
            return False
        elif op == "<=" and not (isinstance(actual, (int, float)) and actual <= value):
            return False
        elif op == "in" and actual not in value:
            return False
        elif op == "not_in" and actual in value:
            return False

    return True

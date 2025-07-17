# transforms/apply.py

from .utils import set_nested, delete_nested, append_nested

def apply_transformation_rules(data, rules: list):
    if isinstance(data, list):
        return [apply_transformation_rules(item, rules) for item in data]

    result = data.copy()

    for rule in rules:
        if not rule.is_active:
            continue
        config = rule.get_config()
        transform_type = config.get("type")
        fields = config.get("fields", {})

        if transform_type == "set":
            for path, value in fields.items():
                set_nested(result, path, value)
        elif transform_type == "delete":
            for path in fields:
                delete_nested(result, path)
        elif transform_type == "put":
            for path, value in fields.items():
                set_nested(result, path, value)

    return result


def apply_rules_to_dataset(dataset, rules):
    if isinstance(dataset, list):
        return [apply_transformation_rules(r, rules) for r in dataset]
    elif isinstance(dataset, dict):
        return apply_transformation_rules(dataset, rules)
    return dataset

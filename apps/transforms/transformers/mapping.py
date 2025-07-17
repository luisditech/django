def transform_mapping(value, mapping_dict, default=None):
    return mapping_dict.get(value, default or value)
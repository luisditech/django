from datetime import datetime

def transform_date(value, input_format, output_format):
    try:
        return datetime.strptime(value, input_format).strftime(output_format)
    except (ValueError, TypeError):
        return None

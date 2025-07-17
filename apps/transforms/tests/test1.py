# tests/test_date.py
from transforms.transformers.date import transform_date

def test_transform_date():
    assert transform_date("25/04/2025", "%d/%m/%Y", "%Y-%m-%d") == "2025-04-25"
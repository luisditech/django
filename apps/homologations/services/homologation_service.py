import csv
from io import StringIO
import logging

logger = logging.getLogger(__name__)


def load_homologation_dict(csv_file_path: str) -> dict:
    """
    Carga un archivo CSV separado por punto y coma (;) y construye un dict {clave: valor}
    usando las primeras dos columnas.
    """
    d = {}
    with open(csv_file_path, newline='', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames
        if not fieldnames or len(fieldnames) < 2:
            raise ValueError("El archivo CSV debe tener al menos dos columnas.")
        key_col, value_col = fieldnames[0], fieldnames[1]
        for row in reader:
            key = row.get(key_col)
            val = row.get(value_col)
            if key is not None and val is not None:
                d[key.strip()] = val.strip()
    return d


def _get_nested(data: dict, path: str):
    """Devuelve el valor en data según la ruta 'a.b.c' o una clave simple."""
    if path in data:
        return data[path]

    cur = data
    for key in path.split("."):
        if not isinstance(cur, dict) or key not in cur:
            return None
        cur = cur[key]
    return cur


def _set_nested(data: dict, path: str, value):
    """Asigna value en data en la ruta 'a.b.c', creando dicts intermedios si faltan."""
    if path in data:
        data[path] = value
        return

    parts = path.split(".")
    cur = data
    for key in parts[:-1]:
        if key not in cur or not isinstance(cur[key], dict):
            cur[key] = {}
        cur = cur[key]
    cur[parts[-1]] = value


def apply_homologation_to_properties(data, homologation_dict, property_map):
    """
    Aplica homologaciones a una lista de diccionarios o un solo diccionario.

    data: list[dict] o dict
    homologation_dict: {'Switzerland': 'Switzerland2', …}
    property_map: {'custrecordmercadodeorigen.text': 'custrecordmercadodeorigen.text', …}
    """
    is_single = isinstance(data, dict)
    rows = [data] if is_single else data

    for idx, row in enumerate(rows):
        for source_path, target_path in property_map.items():
            original = _get_nested(row, source_path)
            if original is None:
                continue

            new_value = homologation_dict.get(original)
            if new_value is None:
                continue

            _set_nested(row, target_path, new_value)


    return data if not is_single else rows[0]

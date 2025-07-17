"""utils.py

Funciones utilitarias para transformar un payload de Shopify (u otra fuente
similar) en un objeto estructurado según un mapping declarativo.

El mapping soporta:
- Claves simples -> ruta de origen (con notación punto), "$const:valor" o "SO-{campo}" (formato dinámico)
- Claves de listas -> {"source": "ruta.lista", "fields": { ... }}
    * Dentro de "fields" puedes usar:
      - rutas (con puntos) para obtener el valor
      - "$const:valor" para constantes
      - "$index" para el índice (1-based) del elemento en la lista

La función principal `map_payload` devuelve SIEMPRE una lista de objetos.
"""

from typing import Any, Dict, List, Union

__all__ = ["map_payload"]


def _get_nested(data: Dict[str, Any], dotted: Any) -> Any:
    if not isinstance(dotted, str):
        return None
    for key in dotted.split('.'):
        if not isinstance(data, dict):
            return None
        data = data.get(key)
    return data


def _set_nested(dst: Dict[str, Any], dotted: str, value: Any) -> None:
    keys = dotted.split('.')
    for k in keys[:-1]:
        dst = dst.setdefault(k, {})
    dst[keys[-1]] = value


def _convert_const(val: str) -> Any:
    """Convierte strings como '1' -> int, 'true' -> bool, etc."""
    if val.lower() == "true":
        return True
    if val.lower() == "false":
        return False
    if val.isdigit():
        return int(val)
    try:
        return float(val)
    except ValueError:
        return val


def _map_list(item_list: List[Dict[str, Any]], spec: Dict[str, str]) -> List[Dict[str, Any]]:
    result: List[Dict[str, Any]] = []
    for idx, raw in enumerate(item_list, start=1):
        out: Dict[str, Any] = {}
        for dst, src in spec.items():
            if src == "$index":
                val = idx
            elif isinstance(src, str) and src.startswith("$const:"):
                val = _convert_const(src.split(":", 1)[1])
            else:
                val = _get_nested(raw, src)

            # Defaults
            if val in (None, ""):
                if dst.endswith("Phone"):
                    val = "000000000"
                elif dst.endswith("HouseNumber"):
                    val = "1"

            _set_nested(out, dst, val)
        result.append(out)
    return result


def map_payload(mapping: Dict[str, Any], src: Union[Dict, List]) -> List[Dict]:
    def _map_one(obj: Dict[str, Any]) -> Dict[str, Any]:
        out: Dict[str, Any] = {}
        for dst, spec in mapping.items():
            if isinstance(spec, dict) and "source" in spec and "fields" in spec:
                raw_list = _get_nested(obj, spec["source"]) or []
                if not isinstance(raw_list, list):
                    raw_list = []
                out[dst] = _map_list(raw_list, spec["fields"])
                continue

            if isinstance(spec, str) and spec.startswith("$const:"):
                val = _convert_const(spec.split(":", 1)[1])
                _set_nested(out, dst, val)
                continue

            val = _get_nested(obj, spec)

            # Aplica format() si corresponde
            if isinstance(spec, str) and "{" in spec and "}" in spec:
                try:
                    val = spec.format(**obj)
                except Exception:
                    pass

            # Defaults
            if val in (None, ""):
                if dst.endswith("Phone"):
                    val = "000000000"
                elif dst.endswith("HouseNumber"):
                    val = "1"

            _set_nested(out, dst, val)
        return out

    if isinstance(src, list):
        return [_map_one(o) for o in src]
    elif isinstance(src, dict):
        return [_map_one(src)]
    raise TypeError(f"Tipo de origen no soportado: {type(src)}")

# --- evaluador generico ------------------------------

def evaluate_branching(config: Dict[str, Any], order: Dict[str, Any]) -> str:
    """
    Lee `config` (como el JSON que pegaste en el campo Config)
    y devuelve el nombre del work siguiente.
    """
    cond = config.get("condition", {})
    field_path = cond.get("field")
    operator   = cond.get("operator", "equals")
    target     = cond.get("value")

    current_val = _get_nested(order, field_path)

    match_ok = False
    if operator == "equals":
        match_ok = current_val == target
    elif operator == "in":
        match_ok = current_val in target
    else:
        raise ValueError(f"Operador no soportado: {operator}")

    if match_ok:
        return config["if_true"]["next_work"]
    return config["if_false"]["next_work"]
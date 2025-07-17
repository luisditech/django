import requests
from urllib.parse import urlparse, urljoin
import logging
import base64

logger = logging.getLogger(__name__)

def http_request_data(connection, configuration, method=None, data=None, path_override=None):
    url = None
    if connection.type.lower() == "shopify":
        shop_url = connection.config.get("shop_url", "").replace("https://", "").rstrip("/")
        password = connection.config.get("password")
        api_version = connection.config.get("api_version", "2023-10")

        if not all([shop_url, api_version, password]):
            raise ValueError("Shopify config is incomplete.")

        base_url = f"https://{shop_url}/admin/api/{api_version}"
        auth = None
        headers = {
            "X-Shopify-Access-Token": password,
            "Content-Type": "application/json"
        }
        params = configuration.get("params", {})
        url = base_url+path_override

    else:
        base_url = connection.config.get("base_url")
        if not base_url:
            raise ValueError(f"Missing {connection.type.lower()} 'base_url' in connection config.")
        headers = connection.config.get("headers", {})

        custom_headers = connection.config.get("custom_headers", {})

        if connection.config.get("auth_type").lower() == "basic":
            username = connection.config.get("auth_username")
            password = connection.config.get("auth_password")

            # 1. Combina usuario y contraseña
            user_pass = f"{username}:{password}"
            token = base64.b64encode(user_pass.encode()).decode()
            headers["Authorization"] = f"Basic {token}"

        # Si custom_headers viene como string tipo "key:value", lo parseamos
        if isinstance(custom_headers, str):
            try:
                key, value = custom_headers.split(":", 1)
                custom_headers = {key.strip(): value.strip()}
            except ValueError:
                raise ValueError("Invalid format for 'custom_headers'. Expected 'key:value' or a dict.")

        # Actualizar los headers finales
        if isinstance(custom_headers, dict):
            headers.update(custom_headers)
        else:
            raise ValueError("'custom_headers' must be a dict or a 'key:value' string")
        
        params = configuration.get("params", {})
        auth = None  # default auth
        url = urljoin(base_url.rstrip("/") + "/", path_override or "")

    method = (method or connection.config.get("method") or "get").lower()

    try:
        response = requests.request(
            method=method,
            url=url,
            headers=headers,
            auth=auth,
            params=params if method == "get" else None,
            json=data if method in ["post", "put"] else None
        )
        response.raise_for_status()
        return response.json() if "application/json" in response.headers.get("Content-Type", "") else response.text

    except requests.RequestException as e:
        raise ValueError(f"HTTP request failed: {e}")
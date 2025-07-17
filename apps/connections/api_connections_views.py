import requests
import psycopg2
import paramiko
from ftplib import FTP
import time
import uuid
import hmac
import hashlib
import base64
from urllib.parse import quote, urlencode
import logging


logger = logging.getLogger(__name__)


def test_connection_logic(connection):
    cfg = connection.config
    ctype = connection.type.lower()
    print(cfg)
    if ctype == "postgresql":
        try:
            conn = psycopg2.connect(
                dbname=cfg["dbname"],
                user=cfg.get("user"),
                password=cfg["password"],
                host=cfg["host"],
                port=cfg.get("port", 5432),
                connect_timeout=5
            )
            conn.close()
            return {"status": 200, "ok": True, "message": "PostgreSQL connection OK"}
        except Exception as e:
            return {"status": 500, "ok": False, "message": f"❌ PostgreSQL error: {e}"}

    elif ctype == "rest":
        url = cfg.get("base_url")
        if not url:
            raise ValueError("Missing base_url in config")

        headers = {}
        auth_type = cfg.get("auth_type")

        if auth_type == "bearer":
            headers["Authorization"] = f"Bearer {cfg.get('auth_token')}"
        elif auth_type == "api_key":
            headers[cfg.get("api_key_header_name", "Authorization")] = cfg.get("api_key_value")
        elif auth_type == "basic":
            response = requests.get(url, auth=(cfg.get("auth_username"), cfg.get("auth_password")), timeout=5)
            return {"status": response.status_code, "ok": response.ok, "message": "REST (basic auth) tested"}

        custom_headers = cfg.get("custom_headers")
        if isinstance(custom_headers, str):
            for h in custom_headers.split(";"):
                if ":" in h:
                    k, v = h.split(":", 1)
                    headers[k.strip()] = v.strip()
        elif isinstance(custom_headers, dict):
            headers.update(custom_headers)

        response = requests.get(url, headers=headers, timeout=5)
        return {"status": response.status_code, "ok": response.ok, "message": "REST connection tested"}

    elif ctype == "shopify":
        shop_url = cfg.get("shop_url", "").replace("https://", "").rstrip("/")
        password = cfg.get("password")
        api_version = cfg.get("api_version", "2023-10")

        if not shop_url or not password:
            raise ValueError("Missing shop_url or password for Shopify")

        base_url = f"https://{shop_url}/admin/api/{api_version}/orders.json"
        headers = {
            "X-Shopify-Access-Token": password,
            "Content-Type": "application/json"
        }

        response = requests.get(base_url, headers=headers, timeout=5)
        response.raise_for_status()
        order_count = len(response.json().get("orders", []))

        return {
            "status": response.status_code,
            "ok": response.ok,
            "message": f"✅ Shopify connection OK — {order_count} orders found"
        }

    elif ctype == "ftp":
        try:
            ftp = FTP()
            ftp.connect(host=cfg.get("host"), port=cfg.get("port", 21), timeout=5)
            ftp.login(user=cfg.get("username"), passwd=cfg.get("password"))
            ftp.quit()
            return {"status": 200, "ok": True, "message": "FTP connection OK"}
        except Exception as e:
            return {"status": 500, "ok": False, "message": f"❌ FTP error: {e}"}

    elif ctype == "sftp":
        # Extract SFTP credentials and test connection only
        host = cfg.get("host")
        port = int(cfg.get("port", 22))
        username = cfg.get("username")
        password = cfg.get("password")

        try:
            transport = paramiko.Transport((host, port))
            transport.connect(username=username, password=password)
            transport.close()
            return {"status": 200, "ok": True, "message": "SFTP connection OK"}
        except Exception as e:
            return {"status": 500, "ok": False, "message": f"❌ SFTP error: {e}"}

    elif ctype == "restlet":
        import uuid, time, hmac, hashlib, base64, requests
        from urllib.parse import quote, urlencode

        if not cfg or not isinstance(cfg, dict):
            raise ValueError("❌ NetSuite config is missing or invalid")

        required_keys = [
            "consumer_key", "consumer_secret", "token_id",
            "account_id", "restlet_url", "token_secret"
        ]
        missing = [k for k in required_keys if not cfg.get(k)]
        if missing:
            raise ValueError(f"❌ Missing NetSuite config keys: {', '.join(missing)}")

        # 🔐 Credenciales
        consumer_key = cfg["consumer_key"]
        consumer_secret = cfg["consumer_secret"]
        token_key = cfg["token_id"]
        account_id = cfg["account_id"]
        restlet_url = cfg["restlet_url"]
        token_secret = cfg["token_secret"]

        # 🚨 URL fija del Restlet
        base_url = "https://6938861-sb1.restlets.api.netsuite.com/app/site/hosting/restlet.nl?script=580&deploy=1"

        # 🕒 Parámetros OAuth
        oauth_nonce = uuid.uuid4().hex
        oauth_timestamp = str(int(time.time()))
        oauth_params = {
            "oauth_consumer_key": consumer_key,
            "oauth_token": token_key,
            "oauth_signature_method": "HMAC-SHA256",
            "oauth_timestamp": oauth_timestamp,
            "oauth_nonce": oauth_nonce,
            "oauth_version": "1.0"
        }

        def generate_signature(method, url, params, consumer_secret, token_secret):
            sorted_params = sorted((quote(k, safe=''), quote(v, safe='')) for k, v in params.items())
            encoded_params = urlencode(sorted_params)
            base_string = '&'.join([
                method.upper(),
                quote(url, safe=''),
                quote(encoded_params, safe='')
            ])
            signing_key = f"{quote(consumer_secret)}&{quote(token_secret)}"
            hashed = hmac.new(signing_key.encode(), base_string.encode(), hashlib.sha256)
            return base64.b64encode(hashed.digest()).decode()

        signature = generate_signature("POST", base_url, oauth_params, consumer_secret, token_secret)
        oauth_params["oauth_signature"] = signature

        headers = {
            "Authorization": "OAuth " + ", ".join(
                [f'realm="{quote(account_id)}"'] +
                [f'{k}="{quote(v)}"' for k, v in oauth_params.items()]
            ),
            "Content-Type": "application/json"
        }

        # 📤 Payload de prueba (como en Postman)
        test_payload = [
            {
                "action": "create",
                "recordType": "customrecordvoucher",
                "customform": { "text": "Stayforlong Voucher Form" },
                "custrecord2": "1234",
                "custrecord5": "Afiliado",
                "custrecord4": "321654987",
                "custrecordcheckin": { "text": "04/03/2025" },
                "custrecordcheckoutdate": { "text": "14/03/2025" },
                "custrecorddivisadecompra": { "text": "GBP" },
                "custrecorddivisadeventa": { "text": "EUR" },
                "custrecordmercadodeorigen": { "text": "United Kingdom" },
                "custrecordpaymentdate": { "text": "02/03/2025" },
                "custrecordprovider": { "text": "avoris" },
                "custrecordtarifavoucher": { "text": "SFL" },
                "name": "321654789",
                "externalid": "ext_1234"
            }
        ]

        try:
            response = requests.post(
                base_url,
                headers=headers,
                json=test_payload,
                timeout=10
            )
            response.raise_for_status()
            return {
                "status": response.status_code,
                "ok": True,
                "message": f"NetSuite POST success — {response.text}",
                "data": response.json() if response.content else None
            }

        except requests.RequestException as e:
            response_text = None
            try:
                response_text = e.response.text if e.response else None
            except Exception:
                pass


            return {
                "status": getattr(e.response, "status_code", 500),
                "ok": False,
                "message": f"❌ NetSuite error: {str(e)}",
                "response": response_text
            }
    else:
        return {"status": 400, "ok": False, "message": f"❌ Unsupported connection type: {ctype}"}

import requests, time, uuid, hmac, hashlib, base64, json
from urllib.parse import quote, urlencode
from apps.workExecution.models import WorkExecution
import logging

logger = logging.getLogger(__name__)

def send_to_netsuite(cfg: dict, conn, payload: dict, work=None):
    """
    Envía un payload al Restlet de NetSuite usando POST con OAuth1 HMAC-SHA256.
    Además imprime un CURL equivalente para debug.
    NO usa cfg para la URL; toda la info está en conn.config.
    """
    # 1) Obtener la URL completa del Restlet (ya incluye ?script=…&deploy=…)
    restlet_full = conn.config.get("restlet_url")
    if not restlet_full or "?" not in restlet_full:
        raise ValueError("❌ 'restlet_url' en conn.config debe incluir '?script=…&deploy=…'")
    # Separa base y parámetros fijos
    base_url, query = restlet_full.split("?", 1)
    fixed_params = dict(p.split("=", 1) for p in query.split("&"))
    # 2) Credenciales en conn.config
    cc = conn.config
    for key in ("consumer_key","consumer_secret","token_id","account_id","restlet_url","token_secret"):
        if not cc.get(key):
            raise ValueError(f"❌ Falta la clave '{key}' en conn.config")

    consumer_key    = cc["consumer_key"]
    consumer_secret = cc["consumer_secret"]
    token_key       = cc["token_id"]
    account_id      = cc["account_id"]
    token_secret    = cc["token_secret"]

    # 3) Parámetros OAuth básicos
    ts    = str(int(time.time()))
    nonce = uuid.uuid4().hex
    oauth = {
        "oauth_consumer_key":     consumer_key,
        "oauth_token":            token_key,
        "oauth_signature_method": "HMAC-SHA256",
        "oauth_timestamp":        ts,
        "oauth_nonce":            nonce,
        "oauth_version":          "1.0",
    }

    # 4) Generar signature incluyendo script&deploy en la base string
    sig_params = {**fixed_params, **oauth}
    def gen_sig(method, url, params, cs, tscr):
        items = sorted((quote(k, safe=""), quote(v, safe="")) for k,v in params.items())
        enc   = urlencode(items)
        base  = "&".join([method.upper(), quote(url, safe=""), quote(enc, safe="")])
        key   = f"{quote(cs)}&{quote(tscr)}"
        dig   = hmac.new(key.encode(), base.encode(), hashlib.sha256).digest()
        return base64.b64encode(dig).decode()

    oauth["oauth_signature"] = gen_sig("POST", base_url, sig_params, consumer_secret, token_secret)

    # 5) Armar Authorization header
    auth_parts = [f'realm="{quote(account_id)}"']
    auth_parts += [f'{k}="{quote(v)}"' for k,v in oauth.items()]
    auth_header = "OAuth " + ",".join(auth_parts)
    headers = {
        "Authorization": auth_header,
        "Content-Type":  "application/json",
    }

    # 6) Asegurar que el payload siempre sea una lista
    body = payload if isinstance(payload, list) else [payload]


    # 7) Enviar la petición
    try:
        resp = requests.post(restlet_full, headers=headers, json=body, timeout=15)
        resp.raise_for_status()
        return {
            "status_code": resp.status_code,
            "ok": True,
            "message": f"✅ NetSuite POST success — {resp.text}",
            "data": resp.json() if resp.content else None
        }
    except requests.RequestException as e:
        err = f"❌ NetSuite error: {e}"
        logger.error(err)
        if work:
            WorkExecution.objects.create(
                work=work,
                status="error",
                message=err,
                response=json.dumps({"payload": body, "headers": headers})
            )
        return {
            "status_code": getattr(e.response, "status_code", 500),
            "ok": False,
            "message": err
        }
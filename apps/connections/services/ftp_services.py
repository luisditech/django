from ftplib import FTP
import paramiko
from io import BytesIO
import re


def read_from_ftp_or_sftp(connection, config):
    cfg = connection.config
    host = cfg.get("host")
    username = cfg.get("username")
    password = cfg.get("password")
    path = str(cfg.get("path", "")).replace("\\", "/").strip()
    port = int(cfg.get("port") or (22 if connection.type == "sftp" else 21))

    if not all([host, username, password]):
        raise ValueError("❌ Missing connection credentials (host, username, password)")

    if connection.type == "sftp":
        if "filename" in config:
            return _read_from_sftp(host, port, username, password, path, config["filename"])
        elif "suffix" in config:
            return _read_latest_file_from_sftp(host, port, username, password, path, config["suffix"])
        else:
            raise ValueError("❌ Config must contain either 'filename' or 'suffix' for SFTP")

    elif connection.type == "ftp":
        if "filename" in config:
            return _read_from_ftp(host, port, username, password, path, config["filename"])
        else:
            raise ValueError("❌ FTP only supports exact 'filename'")
    
    else:
        raise ValueError(f"❌ Unsupported connection type: '{connection.type}'")

def write_to_ftp_or_sftp(connection, content: str, filename: str):
    cfg = connection.config
    host = cfg.get("host")
    username = cfg.get("username")
    password = cfg.get("password")
    path = str(cfg.get("path", "")).replace("\\", "/").strip()
    port = int(cfg.get("port") or (22 if connection.type == "sftp" else 21))

    if not all([host, username, password]):
        raise ValueError("❌ Missing connection credentials (host, username, password)")

    if connection.type == "sftp":
        return _write_to_sftp(host, port, username, password, path, filename, content)
    elif connection.type == "ftp":
        return _write_to_ftp(host, port, username, password, path, filename, content)
    else:
        raise ValueError(f"❌ Unsupported connection type: '{connection.type}'")


def _read_from_sftp(host, port, username, password, path, filename):
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        if path:
            sftp.chdir(path)

        with sftp.file(filename, "rb") as remote_file:
            content = remote_file.read()
        return BytesIO(content)

    finally:
        sftp.close()
        transport.close()

def _read_latest_file_from_sftp(host, port, username, password, path, pattern_suffix):
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        if path:
            sftp.chdir(path)

        # Listar archivos y filtrar por patrón
        files = sftp.listdir()
        # intentar coincidencia exacta por sufijo
        matched_files = [f for f in files if f.endswith(pattern_suffix)]
        if not matched_files:
            # si no hay coincidencias, intentar por prefijo (inicia con)
            matched_files = [f for f in files if f.startswith(pattern_suffix)]
        if not matched_files:
            raise FileNotFoundError(f"No se encontraron archivos con sufijo o prefijo '{pattern_suffix}'")

        # Ordenar por fecha en el nombre del archivo
        def extract_date(f):
            # match 14-digit timestamp (ddmmyyyyHHMMSS) or fallback to 8-digit date (ddmmyyy)
            match = re.search(r'(\d{14})', f) or re.search(r'(\d{8})', f)
            return match.group(1) if match else ''

        matched_files.sort(key=extract_date, reverse=True)
        latest_file = matched_files[0]

        # Leer contenido del archivo más reciente
        with sftp.file(latest_file, "rb") as remote_file:
            content = remote_file.read()
        return BytesIO(content)

    finally:
        sftp.close()
        transport.close()


def _write_to_sftp(host, port, username, password, path, filename, content: str):
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    try:
        if path:
            try:
                sftp.chdir(path)
            except IOError:
                raise ValueError(f"❌ Path '{path}' does not exist on SFTP server")

        remote_path = f"{path}/{filename}" if path else filename

        with sftp.file(remote_path, "w") as remote_file:
            remote_file.write(content.encode("utf-8"))

    finally:
        sftp.close()
        transport.close()


def _read_from_ftp(host, port, username, password, path, filename):
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login(user=username, passwd=password)

    try:
        if path:
            ftp.cwd(path)

        buffer = BytesIO()
        ftp.retrbinary(f"RETR {filename}", buffer.write)
        buffer.seek(0)
        return buffer

    finally:
        ftp.quit()


def _write_to_ftp(host, port, username, password, path, filename, content: str):
    ftp = FTP()
    ftp.connect(host, port)
    ftp.login(user=username, passwd=password)

    try:
        if path:
            ftp.cwd(path)

        buffer = BytesIO(content.encode("utf-8"))
        ftp.storbinary(f"STOR {filename}", buffer)

    finally:
        ftp.quit()

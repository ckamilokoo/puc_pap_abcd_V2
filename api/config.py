import os 
from dotenv import load_dotenv
import base64


# Cargar las variables de entorno desde el archivo .env
load_dotenv()

certificate_base64 = os.getenv("CERTIFICATE_BASE64")
cert_bytes = base64.b64decode(certificate_base64)

# Almacena el certificado en un archivo temporal
with open("/tmp/certificate.crt", "wb") as cert_file:
    cert_file.write(cert_bytes)


class ServerConfig:

    SECRET_KEY = os.getenv('SECRET_KEY', 'default_secret_key')
    SQLALCHEMY_DATABASE_URI = os.getenv('SQLALCHEMY_DATABASE_URI')
    SQLALCHEMY_TRACK_MODIFICATIONS = False



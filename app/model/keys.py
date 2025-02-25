import os, base64
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.backends import default_backend
from app.app_config.config import ConfigClass as Config

def get_jwt_private_key():
    required_key = os.path.join(os.getcwd(), Config.jwt_private_key_path)
    with open(required_key, "rb") as f:
        private_key = serialization.load_pem_private_key(
            f.read(),
            password=Config.jwt_private_key_password.encode(),
            backend=default_backend()
        )
    return private_key

def get_jwt_certificate():
    required_certificate = os.path.join(os.getcwd(), Config.jwt_certificate_path)
    with open(required_certificate, "rb") as f:
        certificate = f.read()
    base64_encoded = base64.b64encode(certificate).decode("utf-8")
    return base64_encoded

def get_jwt_ca_certificate():
    required_certificate_ca = os.path.join(os.getcwd(), Config.jwt_ca_certificate_path)
    with open(required_certificate_ca, "rb") as f:
        ca_certificate = f.read()
    base64_encoded = base64.b64encode(ca_certificate).decode("utf-8")
    return base64_encoded

"""Gera chaves VAPID e imprime as variáveis para o .env"""
from py_vapid import Vapid
import base64

v = Vapid.from_file("private_key.pem")

# Public key — formato não comprimido (65 bytes) em base64url
from cryptography.hazmat.primitives.serialization import Encoding, PublicFormat, PrivateFormat, NoEncryption
pub_bytes = v.public_key.public_bytes(Encoding.X962, PublicFormat.UncompressedPoint)
pub_b64 = base64.urlsafe_b64encode(pub_bytes).rstrip(b"=").decode()

# Private key — DER/PKCS8 em base64url (formato que pywebpush espera)
priv_bytes = v.private_key.private_bytes(Encoding.DER, PrivateFormat.PKCS8, NoEncryption())
priv_b64 = base64.urlsafe_b64encode(priv_bytes).rstrip(b"=").decode()

print(f"VAPID_PUBLIC_KEY={pub_b64}")
print(f"VAPID_PRIVATE_KEY={priv_b64}")
print(f"\nCole essas duas linhas no seu .env")

from cryptography.fernet import Fernet
import os

fernet_key = os.environ["FERNET_KEY"]
fernet = Fernet(fernet_key)

def encrypt_secret(secret: str) -> str:
    return fernet.encrypt(secret.encode()).decode()

def decrypt_secret(token: str) -> str:
    return fernet.decrypt(token.encode()).decode()

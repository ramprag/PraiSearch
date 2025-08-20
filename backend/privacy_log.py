from cryptography.fernet import Fernet
import os

key = Fernet.generate_key()
cipher = Fernet(key)

def log_query(query):
    encrypted_query = cipher.encrypt(query.encode())
    with open("query_log.txt", "ab") as f:
        f.write(encrypted_query + b"\n")
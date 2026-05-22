import os
from dotenv import load_dotenv
import libsql

load_dotenv()
TURSO_URL = os.getenv("TURSO_DB")
TURSO_TOKEN = os.getenv("TURSO_TOKEN")

def get_connection():
    conn = libsql.connect(
        database = TURSO_URL,
        auth_token = TURSO_TOKEN)
    return conn

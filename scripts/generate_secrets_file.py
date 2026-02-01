import base64
import os

def file_to_base64(path):
    with open(path, "rb") as f:
        return base64.b64encode(f.read()).decode('utf-8')

try:
    p12_b64 = file_to_base64("ios_certs_2026/certificate.p12")
    profile_b64 = file_to_base64("ios_certs_2026/profile.mobileprovision")

    content = f"""
!!! ЭТИ ДАННЫЕ НУЖНО ОБНОВИТЬ В CODEMAGIC !!!
(Раздел Environment variables)

1. CM_CERTIFICATE
--------------------------------------------------
{p12_b64}
--------------------------------------------------

2. CM_PROVISIONING_PROFILE
--------------------------------------------------
{profile_b64}
--------------------------------------------------

3. CM_CERTIFICATE_PASSWORD
--------------------------------------------------
12345
--------------------------------------------------
"""
    with open("CODEMAGIC_NEW_SECRETS.txt", "w", encoding="utf-8") as f:
        f.write(content)
    print("File CODEMAGIC_NEW_SECRETS.txt created successfully.")

except Exception as e:
    print(f"Error: {e}")

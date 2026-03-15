import base64
import os
import sys
import glob

# Настройка кодировки для Windows
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# Get the directory where this script is located
script_dir = os.path.dirname(os.path.abspath(__file__))

# Determine which .p8 file to use
p8_file = None

# Option 1: Check command line argument
if len(sys.argv) > 1:
    p8_file = sys.argv[1]
    if not os.path.isabs(p8_file):
        p8_file = os.path.join(script_dir, p8_file)
else:
    # Option 2: Find all .p8 files in the script directory
    p8_files = glob.glob(os.path.join(script_dir, 'AuthKey_*.p8'))
    
    if len(p8_files) == 0:
        print("[ERROR] No .p8 files found in the script directory!")
        print(f"   Directory: {script_dir}")
        print("\n[USAGE] Usage:")
        print("   python encode_key.py [path_to_key.p8]")
        print("\n   Or place AuthKey_<KEY_ID>.p8 file in the same directory as this script.")
        sys.exit(1)
    elif len(p8_files) == 1:
        p8_file = p8_files[0]
        print(f"[OK] Found key file: {os.path.basename(p8_file)}")
    else:
        print("[WARN] Multiple .p8 files found. Please specify which one to use:")
        for i, f in enumerate(p8_files, 1):
            print(f"   {i}. {os.path.basename(f)}")
        print("\n[USAGE] Usage:")
        print("   python encode_key.py AuthKey_<KEY_ID>.p8")
        sys.exit(1)

# Verify file exists
if not os.path.exists(p8_file):
    print(f"[ERROR] File not found: {p8_file}")
    sys.exit(1)

# Read the .p8 file
print(f"[READ] Reading key file: {os.path.basename(p8_file)}")
try:
    with open(p8_file, 'rb') as f:
        key_content = f.read()
except Exception as e:
    print(f"[ERROR] Error reading file: {e}")
    sys.exit(1)

# Verify it's a valid PEM key
if b'BEGIN PRIVATE KEY' not in key_content:
    print("[WARN] Warning: File doesn't seem to contain a valid PEM private key")
    print("   (should start with '-----BEGIN PRIVATE KEY-----')")
    response = input("   Continue anyway? (y/n): ")
    if response.lower() != 'y':
        sys.exit(1)

# Encode to Base64
print("[ENCODE] Encoding to Base64...")
key_base64 = base64.b64encode(key_content).decode('ascii')

# Write to file
output_path = os.path.join(script_dir, 'key_base64.txt')
with open(output_path, 'w') as f:
    f.write(key_base64)

# Extract Key ID from filename
key_id = os.path.basename(p8_file).replace('AuthKey_', '').replace('.p8', '')

print("\n" + "="*70)
print("[OK] Key encoded successfully!")
print("="*70)
print(f"\n[INFO] Key Information:")
print(f"   - Key ID: {key_id}")
print(f"   - Base64 length: {len(key_base64)} characters")
print(f"   - Output file: {os.path.basename(output_path)}")
print(f"\n[VARS] Codemagic Environment Variables:")
print(f"   - APP_STORE_KEY_ID = {key_id}")
print(f"   - APP_STORE_ISSUER_ID = <Get from App Store Connect>")
print(f"   - APP_STORE_PRIVATE_KEY = <Copy Base64 string below>")
print("\n" + "="*70)
print("[COPY] Copy this ENTIRE string (without line breaks) to APP_STORE_PRIVATE_KEY:")
print("="*70)
print(key_base64)
print("="*70)
print("\n[TIP] The Base64 string is also saved to 'key_base64.txt'")

import httpx
import os
from dotenv import load_dotenv

load_dotenv()

url = os.environ.get('SUPABASE_URL')
key = os.environ.get('SUPABASE_KEY')

if not url or not key:
    print("Missing env vars")
    exit(1)

url = url.strip().rstrip('/')
if not url.startswith('https://'):
    url = 'https://' + url

print(f"Testing connection to: {url}")

try:
    with httpx.Client() as client:
        # Test basic rest endpoint
        res = client.get(f"{url}/rest/v1/", headers={"apikey": key})
        print(f"Rest Status: {res.status_code}")
        
        # Test storage endpoint
        res = client.get(f"{url}/storage/v1/bucket", headers={"Authorization": f"Bearer {key}"})
        print(f"Storage Status: {res.status_code}")
        print(f"Storage Body: {res.text[:100]}")
except Exception as e:
    print(f"Error: {e}")
    import traceback
    traceback.print_exc()

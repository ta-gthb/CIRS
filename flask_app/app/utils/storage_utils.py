import os
import uuid
import traceback
import requests
from flask import current_app
from supabase import create_client, Client

def get_supabase_client():
    url = current_app.config.get('SUPABASE_URL')
    key = current_app.config.get('SUPABASE_KEY')
    if not url or not key:
        print("CRITICAL: SUPABASE_URL or SUPABASE_KEY not configured.")
        return None
    
    key = key.strip()
    
    # Sanitize URL: Remove trailing slashes and ensure https://
    url = url.strip().rstrip('/')
    if not url.startswith('https://') and not url.startswith('http://'):
        url = 'https://' + url
    
    print(f"DEBUG: Using Supabase URL: {url}")
    
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"CRITICAL: Failed to create Supabase client: {e}")
        return None

def upload_file(file, folder="civic_issue"):
    """
    Uploads a file to Supabase Storage bucket using requests.
    """
    try:
        url = current_app.config.get('SUPABASE_URL').strip().rstrip('/')
        if not url.startswith('https://') and not url.startswith('http://'):
            url = 'https://' + url
            
        key = current_app.config.get('SUPABASE_KEY').strip()
        bucket_name = current_app.config.get('SUPABASE_BUCKET', 'cirs-uploads')
        
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = f"{folder}/{filename}"
        
        # Determine content type
        content_type = getattr(file, 'content_type', 'application/octet-stream')
        
        # Read file content
        file_content = file.read()
        file.seek(0)
        
        upload_url = f"{url}/storage/v1/object/{bucket_name}/{file_path}"
        
        headers = {
            "Authorization": f"Bearer {key}",
            "apikey": key,
            "Content-Type": content_type
        }
        
        print(f"Attempting Supabase upload via requests to: {upload_url}")
        
        response = requests.post(upload_url, headers=headers, data=file_content)
        
        if response.status_code != 200:
            print(f"Upload failed with status {response.status_code}: {response.text}")
            raise Exception(f"Supabase upload failed: {response.text}")
            
        # Get public URL
        # We can construct it manually if get_public_url also fails, 
        # but let's try the client first as it's a GET request.
        try:
            supabase = get_supabase_client()
            public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
            if not isinstance(public_url, str):
                if hasattr(public_url, 'public_url'):
                    public_url = public_url.public_url
                elif isinstance(public_url, dict):
                    public_url = public_url.get('publicURL') or public_url.get('url')
        except:
            # Manual construction as fallback
            public_url = f"{url}/storage/v1/object/public/{bucket_name}/{file_path}"
            
        print(f"Supabase upload successful. Public URL: {public_url}")
            
        return public_url, filename
        
    except Exception as e:
        print(f"Supabase Upload Error for {file.filename if hasattr(file, 'filename') else 'unknown'}: {e}")
        traceback.print_exc()
        raise Exception(f"Failed to upload file to Supabase: {e}")

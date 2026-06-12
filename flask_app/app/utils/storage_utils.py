import os
import uuid
import traceback
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
        traceback.print_exc()
        return None

def upload_file(file, folder="civic_issue"):
    """
    Uploads a file to Supabase Storage bucket.
    """
    try:
        supabase: Client = get_supabase_client()
        
        # Generate unique filename
        ext = os.path.splitext(file.filename)[1]
        filename = f"{uuid.uuid4().hex}{ext}"
        file_path = f"{folder}/{filename}"

        if not supabase:
            raise Exception("Supabase client not initialized. Cannot upload file.")

        bucket_name = current_app.config.get('SUPABASE_BUCKET', 'cirs-uploads')
        
        # Read file content
        file_content = file.read()
        # Reset file pointer just in case it's needed elsewhere
        file.seek(0)
        
        # Determine content type
        content_type = getattr(file, 'content_type', 'application/octet-stream')
        
        print(f"Attempting Supabase upload to bucket '{bucket_name}', path '{file_path}'...")
        print(f"Content Type: {content_type}, Content Length: {len(file_content)} bytes")
        
        # Upload to Supabase
        res = supabase.storage.from_(bucket_name).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        
        if not isinstance(public_url, str):
            if hasattr(public_url, 'public_url'):
                public_url = public_url.public_url
            elif isinstance(public_url, dict):
                public_url = public_url.get('publicURL') or public_url.get('url')
        
        print(f"Supabase upload successful. Public URL: {public_url}")
            
        return public_url, filename
        
    except Exception as e:
        print(f"Supabase Upload Error for {file.filename if hasattr(file, 'filename') else 'unknown'}: {e}")
        traceback.print_exc()
        raise Exception(f"Failed to upload file to Supabase: {e}")

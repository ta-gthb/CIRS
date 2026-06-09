import os
import uuid
from flask import current_app
from supabase import create_client, Client

def get_supabase_client():
    url = current_app.config.get('SUPABASE_URL')
    key = current_app.config.get('SUPABASE_KEY')
    if not url or not key:
        print("CRITICAL: SUPABASE_URL or SUPABASE_KEY not configured.")
        return None
    try:
        return create_client(url, key)
    except Exception as e:
        print(f"CRITICAL: Failed to create Supabase client: {e}")
        return None

def upload_file(file, folder="civic_issue"):
    """
    Uploads a file to Supabase Storage bucket.
    """
    supabase: Client = get_supabase_client()
    
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = f"{folder}/{filename}"

    if not supabase:
        print(f"Warning: Supabase client not initialized, falling back to local storage for {filename}.")
        return upload_file_local(file, folder)

    bucket_name = current_app.config.get('SUPABASE_BUCKET', 'cirs-uploads')
    
    try:
        # Read file content
        file_content = file.read()
        # Reset file pointer just in case it's needed elsewhere
        file.seek(0)
        
        # Determine content type
        content_type = getattr(file, 'content_type', 'application/octet-stream')
        
        print(f"Attempting Supabase upload to bucket '{bucket_name}', path '{file_path}'...")
        
        # Upload to Supabase
        # In supabase-py v2, this returns a response object or raises an exception
        res = supabase.storage.from_(bucket_name).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": content_type}
        )
        
        # Get public URL
        # In modern supabase-py (v2.x), get_public_url usually returns a string directly
        # but in some sub-versions it might return an object with a public_url attribute.
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        
        if not isinstance(public_url, str):
            if hasattr(public_url, 'public_url'):
                public_url = public_url.public_url
            elif isinstance(public_url, dict):
                public_url = public_url.get('publicURL') or public_url.get('url')
        
        print(f"Supabase upload successful. Public URL: {public_url}")
            
        return public_url, filename
        
    except Exception as e:
        print(f"Supabase Upload Error for {filename}: {e}")
        # Log more details if available
        if hasattr(e, 'message'):
            print(f"Error Message: {e.message}")
            
        print("Falling back to local storage due to upload error.")
        return upload_file_local(file, folder)

def upload_file_local(file, folder="civic_issue"):
    # Ensure folder structure exists in static/uploads
    safe_folder = folder.replace('/', os.sep)
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', safe_folder)
    
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    full_path = os.path.join(upload_dir, filename)
    
    file.save(full_path)
    
    from flask import url_for
    url_path = f'uploads/{folder}/{filename}'.replace('\\', '/')
    local_url = url_for('static', filename=url_path)
    
    return local_url, f"local_{filename}"

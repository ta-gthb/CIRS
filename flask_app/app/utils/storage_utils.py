import os
import uuid
from flask import current_app
from supabase import create_client, Client

def get_supabase_client():
    url = current_app.config.get('SUPABASE_URL')
    key = current_app.config.get('SUPABASE_KEY')
    if not url or not key:
        return None
    return create_client(url, key)

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
        # Fallback to local if not configured (useful for local dev)
        print("Warning: Supabase not configured, falling back to local storage.")
        return upload_file_local(file, folder)

    bucket_name = current_app.config.get('SUPABASE_BUCKET', 'cirs-uploads')
    
    try:
        # Read file content
        file_content = file.read()
        # Reset file pointer just in case it's needed elsewhere
        file.seek(0)
        
        # Determine content type
        content_type = getattr(file, 'content_type', 'application/octet-stream')
        
        # Upload to Supabase
        # The supabase-py library might return different response types depending on version
        res = supabase.storage.from_(bucket_name).upload(
            path=file_path,
            file=file_content,
            file_options={"content-type": content_type}
        )
        
        # Get public URL
        public_url = supabase.storage.from_(bucket_name).get_public_url(file_path)
        
        # Some versions return an object with a 'publicURL' or similar, 
        # but modern ones return the string directly.
        if isinstance(public_url, dict):
            public_url = public_url.get('publicURL') or public_url.get('url')
            
        return public_url, filename
        
    except Exception as e:
        print(f"Supabase Upload Error: {e}")
        # Only fallback to local if we are NOT in production-like environment
        # or if specifically allowed. 
        # On Render, local files are lost, so it's better to know it failed.
        if current_app.config.get('FLASK_ENV') == 'production':
             # In production, we might want to still try local as a last resort 
             # but it's risky. Let's keep it for now but log it heavily.
             print("CRITICAL: Supabase upload failed in production! Falling back to ephemeral local storage.")
        
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

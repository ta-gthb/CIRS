import os
import uuid
from flask import current_app, url_for

def upload_file(file, folder="civic_issue"):
    """
    Saves a file to the local filesystem in the static/uploads directory.
    Note: On platforms like Render, local files are ephemeral and will be 
    deleted when the service restarts.
    """
    # Ensure folder structure exists in static/uploads
    # Replace slashes in folder for local path compatibility
    safe_folder = folder.replace('/', os.sep)
    upload_dir = os.path.join(current_app.root_path, 'static', 'uploads', safe_folder)
    
    if not os.path.exists(upload_dir):
        os.makedirs(upload_dir, exist_ok=True)
    
    # Generate unique filename
    ext = os.path.splitext(file.filename)[1]
    filename = f"{uuid.uuid4().hex}{ext}"
    file_path = os.path.join(upload_dir, filename)
    
    file.save(file_path)
    
    # Return local URL (relative to static)
    # Using forward slashes for URL path
    url_path = f'uploads/{folder}/{filename}'.replace('\\', '/')
    local_url = url_for('static', filename=url_path)
    
    return local_url, f"local_{filename}"

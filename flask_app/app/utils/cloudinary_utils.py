import os
import uuid
import cloudinary
import cloudinary.uploader
from flask import current_app, url_for

def upload_to_cloudinary(file, folder="civic_issue"):
    # Check if Cloudinary is configured with non-placeholder values
    cloud_name = current_app.config.get('CLOUDINARY_NAME')
    api_key = current_app.config.get('CLOUDINARY_API_KEY')
    api_secret = current_app.config.get('CLOUDINARY_API_SECRET')

    is_configured = all([
        cloud_name and 'YOUR_CLOUDINARY_NAME' not in cloud_name,
        api_key and 'YOUR_CLOUDINARY_API_KEY' not in api_key,
        api_secret and 'YOUR_CLOUDINARY_API_SECRET' not in api_secret
    ])

    if is_configured:
        try:
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret
            )
            result = cloudinary.uploader.upload(file, folder=folder)
            return result.get('secure_url'), result.get('public_id')
        except Exception as e:
            # If Cloudinary is configured but fails (e.g., network error), fallback to local
            pass
    
    # Local Storage Fallback
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

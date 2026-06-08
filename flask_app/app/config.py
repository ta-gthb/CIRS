import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Supabase Configuration
    SUPABASE_URL = os.environ.get('SUPABASE_URL')
    SUPABASE_KEY = os.environ.get('SUPABASE_KEY') # Use Service Role Key for uploads
    SUPABASE_BUCKET = os.environ.get('SUPABASE_BUCKET', 'cirs-uploads')

    # Firebase Configuration
    FIREBASE_SERVICE_ACCOUNT_PATH = os.environ.get('FIREBASE_SERVICE_ACCOUNT_PATH')
    # These are needed for the frontend (passing to template)
    FIREBASE_API_KEY = os.environ.get('FIREBASE_API_KEY')
    FIREBASE_AUTH_DOMAIN = os.environ.get('FIREBASE_AUTH_DOMAIN')
    FIREBASE_PROJECT_ID = os.environ.get('FIREBASE_PROJECT_ID')
    FIREBASE_STORAGE_BUCKET = os.environ.get('FIREBASE_STORAGE_BUCKET')
    FIREBASE_MESSAGING_SENDER_ID = os.environ.get('FIREBASE_MESSAGING_SENDER_ID')
    FIREBASE_APP_ID = os.environ.get('FIREBASE_APP_ID')

    # Supabase/Postgres URI handling
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///civic_issue.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    LANGUAGES = {
        'en': 'English',
        'hi': 'हिन्दी (Hindi)',
        'bn': 'বাংলা (Bengali)',
        'te': 'తెలుగు (Telugu)',
        'mr': 'मराठी (Marathi)',
        'ta': 'தமிழ் (Tamil)',
        'gu': 'ગુજરાતી (Gujarati)',
        'kn': 'ಕನ್ನಡ (Kannada)',
        'ml': 'മലയാളം (Malayalam)',
        'pa': 'ਪੰਜਾਬੀ (Punjabi)',
        'or': 'ଓଡ଼ିଆ (Odia)',
        'as': 'অসমীয়া (Assamese)',
        'ks': 'کأشُر (Kashmiri)',
        'sd': 'سنڌي (Sindhi)',
        'sa': 'संस्कृतम् (Sanskrit)',
        'ur': 'اردو (Urdu)'
    }

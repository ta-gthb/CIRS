import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'you-will-never-guess'
    
    # Supabase/Postgres URI handling
    db_url = os.environ.get('DATABASE_URL')
    if db_url and db_url.startswith("postgres://"):
        db_url = db_url.replace("postgres://", "postgresql://", 1)
    
    SQLALCHEMY_DATABASE_URI = db_url or 'sqlite:///civic_issue.db'
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    CLOUDINARY_NAME = os.environ.get('CLOUDINARY_NAME')
    CLOUDINARY_API_KEY = os.environ.get('CLOUDINARY_API_KEY')
    CLOUDINARY_API_SECRET = os.environ.get('CLOUDINARY_API_SECRET')
    
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

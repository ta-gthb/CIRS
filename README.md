# Civic Issue Reporting System

A Flask-based platform for citizens to report civic issues and for authorities to manage them in real-time.

## Features
- **Citizen Portal:** Submit reports with images and voice notes.
- **Admin Dashboard:** Manage and track the status of reported issues.
- **Real-time Updates:** Powered by Flask-SocketIO.
- **Cloud Integration:** Uses Cloudinary for image and audio storage.
- **Maps:** Google Maps integration for location-based reporting.

## Prerequisites
- Python 3.8+
- pip (Python package manager)

## Installation

1. **Clone the repository:**
   ```bash
   git clone https://github.com/Uday142006/Civic-Issue.git
   cd Civic-Issue
   ```

2. **Set up a Virtual Environment (Recommended):**
   ```bash
   python -m venv venv
   # On Windows:
   venv\Scripts\activate
   # On macOS/Linux:
   source venv/bin/activate
   ```

3. **Install Dependencies:**
   ```bash
   pip install -r flask_app/requirements.txt
   ```

## Configuration

1. Navigate to the `flask_app` directory:
   ```bash
   cd flask_app
   ```
2. Create or update the `.env` file with your credentials:
   ```env
   SECRET_KEY=yoursecretkey
   DATABASE_URL=sqlite:///civic_issue.db
   GOOGLE_MAPS_API_KEY=YOUR_API_KEY
   CLOUDINARY_NAME=YOUR_CLOUDINARY_NAME
   CLOUDINARY_API_KEY=YOUR_CLOUDINARY_API_KEY
   CLOUDINARY_API_SECRET=YOUR_CLOUDINARY_API_SECRET
   ```

## Database Setup

Initialize the database and seed the default admin account:
```bash
python setup_db.py
```
*Note: This creates a default admin with phone number `9876543210`.*

## Running the Application

Start the server:
```bash
python run.py
```
The application will be available at `http://127.0.0.1:5000`.

## Project Structure
- `flask_app/app/`: Core application logic (models, routes, static, templates).
- `flask_app/run.py`: Application entry point.
- `flask_app/setup_db.py`: Database initialization script.
- `flask_app/requirements.txt`: Python dependencies.

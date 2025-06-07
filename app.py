from flask import Flask, jsonify, render_template, request, flash, redirect, url_for
from dotenv import load_dotenv
import os
import csv
import requests
from typing import List, Dict, Optional
import time
from werkzeug.utils import secure_filename
import tempfile

# Load environment variables
load_dotenv()

app = Flask(__name__)
app.secret_key = os.getenv('SECRET_KEY', 'dev-key-please-change')  # Required for flash messages

# Configure upload settings
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'csv'}

# Create uploads directory if it doesn't exist
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB max file size

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Get the Google API key from environment variables
GOOGLE_API_KEY = os.getenv('GOOGLE_API_KEY')

def get_street_view_url(lat: float, lng: float, width: int = 600, height: int = 400, heading: int = 0, pitch: int = 0, fov: int = 90) -> Optional[str]:
    """
    Generate a Google Street View static image URL for the given coordinates.
    
    Args:
        lat (float): Latitude
        lng (float): Longitude
        width (int): Image width in pixels (default: 600)
        height (int): Image height in pixels (default: 400)
        heading (int): Camera heading in degrees (default: 0)
        pitch (int): Camera pitch in degrees (default: 0)
        fov (int): Field of view in degrees (default: 90)
        
    Returns:
        Optional[str]: URL to the Street View image, or None if parameters are invalid
    """
    try:
        # Validate parameters
        if not (-90 <= lat <= 90) or not (-180 <= lng <= 180):
            print("Invalid coordinates")
            return None
            
        if not (1 <= width <= 2048) or not (1 <= height <= 2048):
            print("Invalid image dimensions")
            return None
            
        if not (0 <= heading <= 360):
            print("Invalid heading")
            return None
            
        if not (-90 <= pitch <= 90):
            print("Invalid pitch")
            return None
            
        if not (0 <= fov <= 120):
            print("Invalid field of view")
            return None
        
        # Construct the URL
        base_url = "https://maps.googleapis.com/maps/api/streetview"
        params = {
            'size': f"{width}x{height}",
            'location': f"{lat},{lng}",
            'heading': heading,
            'pitch': pitch,
            'fov': fov,
            'key': GOOGLE_API_KEY
        }
        
        # Build the URL with parameters
        url = f"{base_url}?{'&'.join(f'{k}={v}' for k, v in params.items())}"
        return url
        
    except Exception as e:
        print(f"Error generating Street View URL: {str(e)}")
        return None

def geocode_addresses(csv_path: str) -> List[Dict]:
    """
    Read addresses from a CSV file and geocode them using Google's Geocoding API.
    
    Args:
        csv_path (str): Path to the CSV file containing addresses
        
    Returns:
        List[Dict]: List of dictionaries containing address, latitude, and longitude
    """
    results = []
    
    try:
        with open(csv_path, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            
            for row in reader:
                address = row.get('address')
                if not address:
                    continue
                
                # Prepare the API request
                params = {
                    'address': address,
                    'key': GOOGLE_API_KEY
                }
                
                # Make the API request
                response = requests.get(
                    'https://maps.googleapis.com/maps/api/geocode/json',
                    params=params
                )
                
                if response.status_code == 200:
                    data = response.json()
                    
                    if data['status'] == 'OK':
                        location = data['results'][0]['geometry']['location']
                        results.append({
                            'address': address,
                            'lat': location['lat'],
                            'lng': location['lng']
                        })
                    else:
                        print(f"Geocoding failed for address: {address}. Status: {data['status']}")
                
                # Add a small delay to respect API rate limits
                time.sleep(0.2)
                
    except Exception as e:
        print(f"Error processing CSV file: {str(e)}")
        return []
    
    return results

@app.route('/', methods=['GET', 'POST'])
def home():
    properties = []
    error = None
    
    if request.method == 'POST':
        # Check if a file was uploaded
        if 'file' not in request.files:
            flash('No file selected')
            return redirect(request.url)
            
        file = request.files['file']
        
        if file.filename == '':
            flash('No file selected')
            return redirect(request.url)
            
        if file and allowed_file(file.filename):
            # Create a temporary file to store the upload
            with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as temp_file:
                file.save(temp_file.name)
                
                # Process the uploaded file
                properties = geocode_addresses(temp_file.name)
                
                # Add Street View URLs to each property
                for property in properties:
                    property['street_view_url'] = get_street_view_url(
                        lat=property['lat'],
                        lng=property['lng'],
                        width=800,
                        height=400
                    )
                
                # Clean up the temporary file
                os.unlink(temp_file.name)
                
                if not properties:
                    flash('No valid addresses found in the file')
                else:
                    flash(f'Successfully processed {len(properties)} addresses')
        else:
            flash('Invalid file type. Please upload a CSV file')
            return redirect(request.url)
    
    return render_template('index.html', 
                         properties=properties,
                         google_api_key=GOOGLE_API_KEY)

@app.route('/api-key-status')
def api_key_status():
    if GOOGLE_API_KEY:
        return jsonify({
            'status': 'success',
            'message': 'Google API key is configured',
            'key_exists': True
        })
    return jsonify({
        'status': 'warning',
        'message': 'Google API key is not configured',
        'key_exists': False
    })

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5001))  # Changed default port to 5001
    app.run(host='0.0.0.0', port=port, debug=True) 
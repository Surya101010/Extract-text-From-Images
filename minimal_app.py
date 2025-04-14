import os
from flask import Flask, render_template, request, jsonify, redirect, url_for

# Initialize Flask app
app = Flask(__name__)
app.config['SECRET_KEY'] = 'ocr-chatbot-secret-key'
app.config['UPLOAD_FOLDER'] = 'uploads'
app.config['ALLOWED_EXTENSIONS'] = {'png', 'jpg', 'jpeg', 'gif'}

# Ensure upload directory exists
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)

# Check for required packages
missing_packages = []
tesseract_found = False

# Try to import required packages
try:
    import pytesseract
    # Try to find Tesseract in common installation paths
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        '/usr/bin/tesseract',  # Linux path
        '/usr/local/bin/tesseract'  # macOS path
    ]

    for path in tesseract_paths:
        if os.path.exists(path):
            pytesseract.pytesseract.tesseract_cmd = path
            tesseract_found = True
            break
except ImportError:
    missing_packages.append("pytesseract")
    pytesseract = None

try:
    import cv2
    import numpy as np
except ImportError:
    missing_packages.append("opencv-python and numpy")

try:
    from flask_sqlalchemy import SQLAlchemy
except ImportError:
    missing_packages.append("flask-sqlalchemy")

try:
    from Levenshtein import ratio
except ImportError:
    missing_packages.append("python-Levenshtein")

# Routes
@app.route('/')
def index():
    return render_template('index.html', missing_packages=missing_packages, tesseract_found=tesseract_found)

@app.route('/install-info')
def install_info():
    return render_template('install_info.html', missing_packages=missing_packages, tesseract_found=tesseract_found)

@app.route('/upload', methods=['POST'])
def upload_file():
    if missing_packages or not tesseract_found:
        return jsonify({
            'result': {
                'extracted_text': "ERROR: Missing dependencies. Please install the required packages and Tesseract OCR.",
                'original_image': None,
                'processed_image': None,
                'accuracy': None,
                'precision': None
            }
        })
    
    return jsonify({
        'result': {
            'extracted_text': "The OCR functionality is not available in this minimal version. Please install all dependencies.",
            'original_image': None,
            'processed_image': None,
            'accuracy': None,
            'precision': None
        }
    })

@app.route('/chat', methods=['POST'])
def chat():
    data = request.get_json()
    user_message = data.get('message', '')
    
    if not user_message:
        return jsonify({'error': 'No message provided'}), 400
    
    # Simple response for the minimal version
    if 'install' in user_message.lower() or 'setup' in user_message.lower():
        response = "To set up the OCR Chatbot, you need to install:\n1. Python packages: pip install -r requirements.txt\n2. Tesseract OCR: https://github.com/UB-Mannheim/tesseract/wiki"
    else:
        response = "This is a minimal version of the OCR Chatbot. Please install all dependencies to access full functionality."
    
    return jsonify({'response': response})

@app.route('/chat_history')
def chat_history():
    return render_template('chat_history.html', messages=[], error="Database functionality is not available in minimal version")

@app.route('/ocr_results')
def ocr_results():
    return render_template('ocr_results.html', results=[], error="Database functionality is not available in minimal version")

@app.errorhandler(404)
def page_not_found(e):
    return render_template('error.html', error="Page not found"), 404

@app.errorhandler(500)
def server_error(e):
    return render_template('error.html', error="Internal server error"), 500

if __name__ == '__main__':
    print("Starting minimal OCR Chatbot web application...")
    if missing_packages:
        print(f"Warning: Some packages are missing: {', '.join(missing_packages)}")
        print("The application will run with limited functionality.")
        print("Visit /install-info for installation instructions.")
    
    if not tesseract_found and pytesseract is not None:
        print("Warning: Tesseract OCR not found in common installation paths.")
        print("OCR functionality will be limited.")
        print("Visit /install-info for installation instructions.")
    
    app.run(debug=True)

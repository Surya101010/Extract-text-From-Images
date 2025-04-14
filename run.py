import os
import sys
import subprocess
import webbrowser
from time import sleep

def check_tesseract():
    """Check if Tesseract is installed and update the path in app.py if needed."""
    print("Checking Tesseract installation...")
    
    # Try to find Tesseract in common installation paths
    tesseract_paths = [
        r'C:\Program Files\Tesseract-OCR\tesseract.exe',
        r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        # Add more potential paths if needed
    ]
    
    tesseract_path = None
    for path in tesseract_paths:
        if os.path.exists(path):
            tesseract_path = path
            print(f"Found Tesseract at: {path}")
            break
    
    if not tesseract_path:
        print("Tesseract not found in common installation paths.")
        print("Please install Tesseract OCR from: https://github.com/UB-Mannheim/tesseract/wiki")
        print("After installation, update the tesseract_cmd path in app.py")
        return False
    
    # Update the path in app.py if needed
    with open('app.py', 'r') as f:
        content = f.read()
    
    if "pytesseract.pytesseract.tesseract_cmd = " in content:
        # Replace the path
        new_content = content.replace(
            "pytesseract.pytesseract.tesseract_cmd = r'C:\\Program Files\\Tesseract-OCR\\tesseract.exe'", 
            f"pytesseract.pytesseract.tesseract_cmd = r'{tesseract_path}'"
        )
        
        with open('app.py', 'w') as f:
            f.write(new_content)
        
        print("Updated Tesseract path in app.py")
    
    return True

def install_requirements():
    """Install required Python packages."""
    print("Installing required packages...")
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
    print("All packages installed successfully!")

def run_app():
    """Run the Flask application."""
    print("Starting OCR Chatbot web application...")
    print("Opening browser in 3 seconds...")
    sleep(3)
    webbrowser.open('http://localhost:5000')
    
    # Run the Flask app
    os.environ['FLASK_APP'] = 'app.py'
    os.environ['FLASK_ENV'] = 'development'
    subprocess.call([sys.executable, "app.py"])

if __name__ == "__main__":
    print("=" * 50)
    print("OCR Chatbot Setup and Run Script")
    print("=" * 50)
    
    if check_tesseract():
        try:
            install_requirements()
            run_app()
        except Exception as e:
            print(f"Error: {e}")
            print("Setup failed. Please check the error message above.")
    else:
        print("Setup incomplete. Please install Tesseract OCR and try again.")

from flask import Flask, render_template

# Initialize Flask app
app = Flask(__name__)

# Routes
@app.route('/')
def index():
    missing_packages = ["pytesseract", "opencv-python", "flask-sqlalchemy", "python-Levenshtein"]
    tesseract_found = False
    return render_template('index.html', missing_packages=missing_packages, tesseract_found=tesseract_found)

@app.route('/install-info')
def install_info():
    missing_packages = ["pytesseract", "opencv-python", "flask-sqlalchemy", "python-Levenshtein"]
    tesseract_found = False
    return render_template('install_info.html', missing_packages=missing_packages, tesseract_found=tesseract_found)

if __name__ == '__main__':
    print("Starting simple OCR Chatbot web application...")
    print("This is a minimal version that only shows installation instructions.")
    app.run(debug=True)

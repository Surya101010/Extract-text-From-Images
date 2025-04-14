# OCR Chatbot Web Application

A Flask-based web application that extracts text from images using Optical Character Recognition (OCR) and provides a chatbot interface for user interaction. The application supports both English and Tamil languages.

## Features

- **OCR Functionality**: Extract text from uploaded images using Tesseract OCR
- **Image Preprocessing**: Improve OCR accuracy with skew correction, denoising, and adaptive thresholding
- **Multilingual Support**: English and Tamil language recognition
- **Chatbot Interface**: Interactive assistant to help with OCR tasks
- **Database Integration**: Store OCR results and chat history
- **Metrics Calculation**: Evaluate OCR accuracy when ground truth is provided

## Installation Requirements

### 1. Python Packages

Install the required Python packages using pip:

```bash
pip install -r requirements.txt
```

The requirements.txt file includes:
- flask==2.0.1
- pytesseract==0.3.10
- opencv-python==4.5.3.56
- numpy==1.21.2
- Pillow==8.3.2
- python-Levenshtein==0.12.2
- flask-sqlalchemy==2.5.1

### 2. Tesseract OCR Installation

#### Windows
1. Download the installer from [UB Mannheim's Tesseract page](https://github.com/UB-Mannheim/tesseract/wiki)
2. Run the installer and follow the instructions
3. Make sure to check "Add to PATH" during installation
4. Optionally, select additional language data (including Tamil) if needed

#### macOS
Using Homebrew:
```bash
brew install tesseract
brew install tesseract-lang  # For additional languages
```

#### Linux
Ubuntu/Debian:
```bash
sudo apt-get install tesseract-ocr
sudo apt-get install tesseract-ocr-tam  # For Tamil language support
```

Fedora/RHEL/CentOS:
```bash
sudo dnf install tesseract
sudo dnf install tesseract-langpack-tam  # For Tamil language support
```

## Running the Application

After installing all dependencies:

```bash
python app.py
```

The application will start on http://localhost:5000

## Troubleshooting

### Missing Dependencies
If you encounter errors related to missing dependencies:
1. Make sure all required Python packages are installed
2. Verify that Tesseract OCR is installed and added to your PATH
3. Check the application logs for specific error messages

### OCR Issues
If text extraction is not working properly:
1. Ensure the image has clear, readable text
2. Try preprocessing the image with an external tool
3. Check if the appropriate language data is installed for Tesseract

## Project Structure

- `app.py`: Main application file
- `templates/`: HTML templates for the web interface
- `uploads/`: Directory for storing uploaded and processed images
- `requirements.txt`: List of Python dependencies

## Future Enhancements

- Improved image preprocessing techniques
- Support for additional languages
- Advanced chatbot capabilities with NLP
- User authentication and personalized history

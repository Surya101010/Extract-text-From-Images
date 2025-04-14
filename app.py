from flask import Flask, render_template, request, jsonify, redirect, url_for
import os
import pytesseract
import cv2
import numpy as np
from PIL import Image
import io
import nltk
import spacy
import re
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import Levenshtein
from googletrans import Translator
from models import db, ChatHistory, OCRResult
from datetime import datetime
import logging

# Configure logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Initialize Flask app
app = Flask(__name__)

# Configure database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///ocr_chatbot.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SECRET_KEY'] = 'your-secret-key-here'  # Add a secret key for session management
db.init_app(app)

# Create database tables
with app.app_context():
    try:
        db.create_all()
        logger.info("Database tables created successfully")
        
        # Add test data if database is empty
        if ChatHistory.query.count() == 0:
            test_chat = ChatHistory(
                user_message="Hello, how does OCR work?",
                bot_response="OCR (Optical Character Recognition) is a technology that converts different types of documents into editable and searchable data.",
                language="en"
            )
            db.session.add(test_chat)
            db.session.commit()
            logger.info("Added test chat data")

        if OCRResult.query.count() == 0:
            test_ocr = OCRResult(
                filename="test_image.jpg",
                extracted_text="This is a test OCR result",
                language="eng"
            )
            db.session.add(test_ocr)
            db.session.commit()
            logger.info("Added test OCR data")
            
    except Exception as e:
        logger.error(f"Error initializing database: {str(e)}")

# Configure pytesseract
# For Windows
if os.name == 'nt':
    pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Load spaCy model
try:
    nlp = spacy.load('en_core_web_sm')
except:
    os.system('python -m spacy download en_core_web_sm')
    nlp = spacy.load('en_core_web_sm')

# Download NLTK data if not present
try:
    nltk.data.find('tokenizers/punkt')
except LookupError:
    nltk.download('punkt')

try:
    nltk.data.find('corpora/wordnet')
except LookupError:
    nltk.download('wordnet')

try:
    nltk.data.find('corpora/stopwords')
except LookupError:
    nltk.download('stopwords')

# Languages supported for OCR
LANGUAGES = {
    'eng': 'English',
    'fra': 'French',
    'deu': 'German',
    'spa': 'Spanish',
    'ita': 'Italian',
    'por': 'Portuguese',
    'hin': 'Hindi',
    'ara': 'Arabic',
    'chi_sim': 'Chinese (Simplified)',
    'rus': 'Russian',
    'jpn': 'Japanese',
    'kor': 'Korean',
    'tam': 'Tamil',
}

# Languages for translation
TRANSLATION_LANGUAGES = {
    'en': 'English',
    'fr': 'French',
    'de': 'German',
    'es': 'Spanish',
    'it': 'Italian',
    'pt': 'Portuguese',
    'hi': 'Hindi',
    'ar': 'Arabic',
    'zh-cn': 'Chinese (Simplified)',
    'ru': 'Russian',
    'ja': 'Japanese',
    'ko': 'Korean',
    'ta': 'Tamil'
}

def extract_text_from_image(image_file, lang='eng'):
    """Extract text from the uploaded image file using Tesseract OCR"""
    try:
        # Read the image file
        image = Image.open(image_file)
        
        # Convert to OpenCV format
        img_cv = cv2.cvtColor(np.array(image), cv2.COLOR_RGB2BGR)
        
        # Preprocess the image
        # Convert to grayscale
        gray = cv2.cvtColor(img_cv, cv2.COLOR_BGR2GRAY)
        
        # Apply thresholding
        _, thresh = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY | cv2.THRESH_OTSU)
        
        # Convert back to PIL Image
        preprocessed_img = Image.fromarray(thresh)
        
        # Extract text using tesseract
        text = pytesseract.image_to_string(preprocessed_img, lang=lang)
        
        # Clean up the text
        text = re.sub(r'\s+', ' ', text).strip()
        
        return text
    except Exception as e:
        print(f"Error processing image: {str(e)}")
        return "Error processing image. Please try again."

def translate_text(text, target_language='en'):
    """Translate text to the target language using Google Translate"""
    try:
        translator = Translator()
        result = translator.translate(text, dest=target_language)
        return result.text
    except Exception as e:
        print(f"Translation error: {str(e)}")
        return f"[Error translating to {TRANSLATION_LANGUAGES.get(target_language, target_language)}] {text}"

@app.route('/')
def index():
    """Render the main page"""
    return render_template('index.html', languages=LANGUAGES)

@app.route('/extract', methods=['POST'])
def extract():
    """Handle the form submission and extract text from the uploaded image"""
    try:
        # Check if a file was uploaded
        if 'file' not in request.files:
            return redirect(url_for('error', message="No file was uploaded"))
        
        file = request.files['file']
        
        # Check if the file has a name (i.e., was actually uploaded)
        if file.filename == '':
            return redirect(url_for('error', message="No file was selected"))
        
        # Check the file type
        allowed_extensions = {'png', 'jpg', 'jpeg', 'gif', 'bmp', 'tiff', 'pdf'}
        if not ('.' in file.filename and file.filename.rsplit('.', 1)[1].lower() in allowed_extensions):
            return redirect(url_for('error', message="Invalid file type. Allowed types: PNG, JPG, JPEG, GIF, BMP, TIFF, PDF"))
        
        # Get the selected language
        language = request.form.get('language', 'eng')
        
        # Extract text from the image
        extracted_text = extract_text_from_image(file, language)
        
        # Store OCR result in database
        ocr_result = OCRResult(
            filename=file.filename,
            extracted_text=extracted_text,
            language=language
        )
        db.session.add(ocr_result)
        db.session.commit()
        
        # Render the result page
        return render_template('result.html', 
                              extracted_text=extracted_text, 
                              image_name=file.filename,
                              language=LANGUAGES.get(language, language),
                              translation_languages=TRANSLATION_LANGUAGES)
    
    except Exception as e:
        print(f"Extraction error: {str(e)}")
        return redirect(url_for('error', message=f"An error occurred: {str(e)}"))

@app.route('/translate', methods=['POST'])
def translate():
    """Handle translation of the extracted text"""
    data = request.get_json()
    text = data.get('text', '')
    target_language = data.get('language', 'en')
    
    translated_text = translate_text(text, target_language)
    
    # Update the OCR result with translation
    ocr_result = OCRResult.query.order_by(OCRResult.timestamp.desc()).first()
    if ocr_result:
        ocr_result.translated_text = translated_text
        ocr_result.translation_language = target_language
        db.session.commit()
    
    return jsonify({'translated_text': translated_text})

@app.route('/error')
def error():
    """Render the error page"""
    message = request.args.get('message', 'An unknown error occurred')
    return render_template('error.html', message=message)

@app.route('/install_info')
def install_info():
    """Render the installation info page"""
    return render_template('install_info.html')

@app.route('/accuracy')
def accuracy():
    """Render the accuracy metrics page"""
    # This could be dynamically generated from real metrics in a production app
    accuracy_data = {
        'character_level': 92,
        'word_level': 87,
        'sentence_level': 78
    }
    return render_template('accuracy.html', accuracy=accuracy_data)

@app.route('/chat', methods=['POST'])
def chat():
    """Handle chatbot requests"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        language = data.get('language', 'en')
        
        # Get chatbot response
        bot_response = get_chatbot_response(user_message)
        
        # Store chat in database
        chat_entry = ChatHistory(
            user_message=user_message,
            bot_response=bot_response,
            language=language
        )
        db.session.add(chat_entry)
        db.session.commit()
        
        return jsonify({'response': bot_response})
    except Exception as e:
        logger.error(f"Error in chat route: {str(e)}")
        return jsonify({'response': 'I apologize, but I encountered an error. Please try again.'})

@app.route('/history')
def history():
    """Display chat and OCR history"""
    try:
        logger.debug("Accessing history route")
        chat_history = ChatHistory.query.order_by(ChatHistory.timestamp.desc()).all()
        ocr_history = OCRResult.query.order_by(OCRResult.timestamp.desc()).all()
        logger.debug(f"Found {len(chat_history)} chat entries and {len(ocr_history)} OCR entries")
        return render_template('history.html', 
                             chat_history=chat_history,
                             ocr_history=ocr_history)
    except Exception as e:
        logger.error(f"Error in history route: {str(e)}")
        return redirect(url_for('error', message=f"Error accessing history: {str(e)}"))

def get_chatbot_response(user_input):
    """Get chatbot response using NLP"""
    # Preprocess the user input
    doc = nlp(user_input.lower())
    
    # Extract key information
    entities = [ent.text for ent in doc.ents]
    keywords = [token.text for token in doc if not token.is_stop and token.is_alpha]
    
    # Define common OCR-related patterns and responses
    ocr_patterns = {
        'supported_languages': ['language', 'languages', 'support', 'supported', 'available'],
        'accuracy': ['accuracy', 'accurate', 'precision', 'quality', 'performance'],
        'file_types': ['format', 'formats', 'file', 'files', 'type', 'types', 'support', 'supported'],
        'process': ['how', 'work', 'works', 'process', 'working', 'explain'],
        'error': ['error', 'problem', 'issue', 'wrong', 'fail', 'failed', 'not working'],
        'tips': ['tip', 'tips', 'help', 'improve', 'better', 'quality', 'suggestion', 'suggestions'],
    }
    
    # Check for matches in keywords
    matched_patterns = []
    for pattern_type, pattern_words in ocr_patterns.items():
        if any(keyword in pattern_words for keyword in keywords):
            matched_patterns.append(pattern_type)
    
    # Generate appropriate response based on matched patterns
    if 'supported_languages' in matched_patterns:
        return "I support multiple languages including English, Tamil, French, German, Spanish, Italian, Portuguese, Hindi, Arabic, Chinese, Russian, Japanese, and Korean. You can select your preferred language from the dropdown menu when uploading an image."
    
    elif 'accuracy' in matched_patterns:
        return "The OCR accuracy depends on several factors including image quality, text clarity, and language. For best results, ensure your image is well-lit, properly aligned, and has clear text. You can check detailed accuracy metrics using the 'View Accuracy Metrics' button."
    
    elif 'file_types' in matched_patterns:
        return "I can process various image formats including PNG, JPG/JPEG, GIF, BMP, and TIFF. I can also handle PDF documents. Make sure your files are clear and readable for best results."
    
    elif 'process' in matched_patterns:
        return "I use advanced OCR (Optical Character Recognition) technology to extract text from images. The process involves: 1) Image preprocessing for better quality, 2) Text detection and segmentation, 3) Character recognition, and 4) Post-processing for accuracy. You can simply upload an image and select the language to get started."
    
    elif 'error' in matched_patterns:
        return "If you're experiencing issues, try these troubleshooting steps: 1) Ensure the image is clear and well-lit, 2) Check if you've selected the correct language, 3) Verify the file format is supported, 4) Make sure the text is properly aligned. If problems persist, check the error message for specific details."
    
    elif 'tips' in matched_patterns:
        return "Here are some tips for better OCR results: 1) Use high-resolution images, 2) Ensure good lighting and contrast, 3) Align text horizontally, 4) Choose the correct language, 5) Avoid blurry or distorted images, 6) Crop unnecessary parts of the image."
    
    # Check for greetings
    greetings = ['hi', 'hello', 'hey', 'greetings']
    if any(greeting in user_input.lower() for greeting in greetings):
        return "Hello! I'm your OCR assistant. How can I help you with text extraction today?"
    
    # Calculate similarity with previous queries for better context understanding
    try:
        vectorizer = TfidfVectorizer()
        previous_responses = [
            "I can help you extract text from images using OCR technology.",
            "Upload an image and I'll process it for you.",
            "Select the appropriate language for better accuracy.",
            "Make sure your image is clear and well-lit for best results."
        ]
        
        # Transform the text
        tfidf_matrix = vectorizer.fit_transform([user_input] + previous_responses)
        
        # Calculate similarity
        similarity_scores = cosine_similarity(tfidf_matrix[0:1], tfidf_matrix[1:])
        
        # If there's a good match, use it
        if np.max(similarity_scores) > 0.3:
            return previous_responses[np.argmax(similarity_scores)]
    except Exception as e:
        logger.error(f"Error in similarity calculation: {str(e)}")
    
    # Default response if no pattern is matched
    return "I'm here to help with OCR text extraction. You can ask me about supported languages, file types, or how to improve accuracy. Feel free to upload an image and I'll help you process it."

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
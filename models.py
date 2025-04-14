from flask_sqlalchemy import SQLAlchemy
from datetime import datetime

db = SQLAlchemy()

class ChatHistory(db.Model):
    __tablename__ = 'chat_history'
    
    id = db.Column(db.Integer, primary_key=True)
    user_message = db.Column(db.Text, nullable=False)
    bot_response = db.Column(db.Text, nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    language = db.Column(db.String(10), default='en')

    def __repr__(self):
        return f'<Chat {self.id}>'

class OCRResult(db.Model):
    __tablename__ = 'ocr_result'
    
    id = db.Column(db.Integer, primary_key=True)
    filename = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text, nullable=False)
    language = db.Column(db.String(10), nullable=False)
    timestamp = db.Column(db.DateTime, default=datetime.utcnow)
    translated_text = db.Column(db.Text, nullable=True)
    translation_language = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return f'<OCRResult {self.id}>' 
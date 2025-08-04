import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QMessageBox, QComboBox
)
from PyQt6.QtCore import Qt
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate
import mysql.connector
import os
from dotenv import load_dotenv
import requests
import json

# Load environment variables
load_dotenv()

class DatabaseManager:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                user=os.getenv('DB_USER', 'root'),
                password=os.getenv('DB_PASSWORD', ''),
                database=os.getenv('DB_NAME', 'fieldbuddy')
            )
            print("Database connection successful")
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL: {err}")
            QMessageBox.critical(None, "Database Error", 
                               f"Could not connect to database: {err}")
    
    def get_recommended_crop(self, username):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT recommendedCrop FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            cursor.close()
            return result.get("recommendedCrop", "") if result else ""
        except mysql.connector.Error as err:
            print(f"Error fetching recommended crop: {err}")
            return ""
    
    def close(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

# Create a custom prompt template for agriculture assistance
template = (
    "You are a helpful and knowledgeable agriculture assistant. Your goal is to provide useful information and advice to farmers. "
    "The user's details are:\n"
    "Username: {username}\n"
    "Location: {state}, {city}\n"
    "Contact: {email}, {phone}\n"
    "Previous Recommendations: {recommendedCrop}\n\n"
    "Based on this information, provide personalized advice about:\n"
    "1. Weather patterns and forecasts for their region\n"
    "2. Soil conditions and recommendations\n"
    "3. Suitable crops based on their location and previous recommendations\n"
    "4. Market prices and trends in their area\n"
    "5. Farming techniques specific to their region\n"
    "6. Pest control and disease prevention for their crops\n"
    "7. Irrigation and water management advice\n"
    "8. Fertilizer recommendations based on their soil type\n\n"
    "If you don't know the answer, say 'I don't know.'\n\n"
    "Chatbot: {question}\n\n"
    "User: {answer}\n\n"
    "Chatbot:"
)
CHAT_PROMPT = PromptTemplate(
    template=template, 
    input_variables=["question", "answer", "username", "state", "city", "email", "phone", "recommendedCrop"]
)

# Initialize local LLM
llm_local = Ollama(model="llama3.2")

def chat(question, answer="", user_data=None, use_online=False):
    try:
        # Use default values if user_data is not provided
        username = user_data.get("username", "") if user_data else ""
        state = user_data.get("state", "") if user_data else ""
        city = user_data.get("city", "") if user_data else ""
        email = user_data.get("email", "") if user_data else ""
        phone = user_data.get("phone", "") if user_data else ""
        recommendedCrop = user_data.get("recommendedCrop", "") if user_data else ""
        
        formatted_prompt = CHAT_PROMPT.format(
            question=question,
            answer=answer,
            username=username,
            state=state,
            city=city,
            email=email,
            phone=phone,
            recommendedCrop=recommendedCrop
        )
        
        # Choose the appropriate LLM based on the mode
        if use_online:
            if not os.getenv("GOOGLE_API_KEY"):
                return "Error: Google API key not found. Please set GOOGLE_API_KEY in your environment variables."
            
            # Make REST API call to Gemini
            url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={os.getenv('GOOGLE_API_KEY')}"
            headers = {'Content-Type': 'application/json'}
            data = {
                "contents": [{
                    "parts": [{"text": formatted_prompt}]
                }]
            }
            
            try:
                response = requests.post(url, headers=headers, json=data)
                response.raise_for_status()
                result = response.json()
                return result['candidates'][0]['content']['parts'][0]['text']
            except requests.exceptions.RequestException as e:
                return f"Error using Gemini API: {str(e)}"
            except (KeyError, IndexError) as e:
                return f"Error parsing Gemini response: {str(e)}"
        else:
            response = llm_local(formatted_prompt)
            return response.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# PyQt6 GUI Application
class ChatbotApp(QWidget):
    def __init__(self, user_data=None):
        super().__init__()
        self.user_data = user_data or {}
        self.db_manager = DatabaseManager()
        self.use_online = False  # Default to local mode
        
        # Get recommended crop from database
        username = self.user_data.get("username", "")
        recommended_crop = self.db_manager.get_recommended_crop(username)
        if recommended_crop:
            self.user_data["recommendedCrop"] = recommended_crop
        
        # Create greeting based on recommended crop
        if recommended_crop and recommended_crop != "ADVEN":
            self.current_question = f"Hello {username}! Based on your previous recommended crop ({recommended_crop}), how can I assist you?"
        else:
            self.current_question = f"Hello {username}! How can I assist you with farming today?"
            
        self.chat_history = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("FieldBuddy Chatbot")
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("background-color: #f4f1de;")

        # Main layout
        main_layout = QVBoxLayout()
        
        # Top bar with back button and mode switch
        top_bar = QHBoxLayout()
        
        # Back button
        self.back_button = QPushButton("← Back")
        self.back_button.setStyleSheet("""
            background-color: #bc4749; 
            color: white; 
            border-radius: 8px; 
            padding: 8px;
            font-size: 14px;
        """)
        self.back_button.clicked.connect(self.close)
        top_bar.addWidget(self.back_button)
        
        # Add stretch to push the mode switch to the right
        top_bar.addStretch()
        
        # Mode switch container
        switch_container = QWidget()
        switch_container.setStyleSheet("""
            QWidget {
                background-color: #f4f1de;
                border-radius: 15px;
                padding: 5px;
            }
        """)
        switch_layout = QHBoxLayout(switch_container)
        switch_layout.setContentsMargins(0, 0, 0, 0)
        
        # Dynamic mode label
        self.mode_label = QLabel("Switch to Online")
        self.mode_label.setStyleSheet("""
            QLabel {
                color: #386641;
                font-size: 14px;
                font-weight: bold;
                padding: 0 5px;
            }
        """)
        switch_layout.addWidget(self.mode_label)
        
        # Toggle switch
        self.mode_switch = QPushButton()
        self.mode_switch.setCheckable(True)
        self.mode_switch.setFixedSize(60, 30)
        self.mode_switch.setStyleSheet("""
            QPushButton {
                background-color: #6a994e;
                border: none;
                border-radius: 15px;
                padding: 2px;
            }
            QPushButton:checked {
                background-color: #386641;
            }
            QPushButton::indicator {
                width: 26px;
                height: 26px;
                border-radius: 13px;
                background-color: white;
                position: absolute;
                left: 2px;
                top: 2px;
                transition: left 0.2s;
            }
            QPushButton::indicator:checked {
                left: 32px;
            }
        """)
        self.mode_switch.clicked.connect(self.toggle_mode_with_label)
        switch_layout.addWidget(self.mode_switch)
        
        top_bar.addWidget(switch_container)
        main_layout.addLayout(top_bar)

        # Chat history display
        self.chat_display = QTextEdit()
        self.chat_display.setReadOnly(True)
        self.chat_display.setStyleSheet("""
            background-color: #ffffff; 
            border-radius: 10px;
            padding: 10px;
            font-size: 14px;
        """)
        main_layout.addWidget(self.chat_display)

        # User Input Area (Chatbox)
        input_layout = QHBoxLayout()

        self.user_input = QLineEdit()
        self.user_input.setPlaceholderText("Type your message...")
        self.user_input.setStyleSheet("""
            background-color: #f4f1de;  /* Light beige background */
            border: 2px solid #6a994e; /* Green border */
            border-radius: 8px;
            padding: 8px;
            font-size: 14px;
            color: #386641;            /* Dark green text color */
        """)
        self.user_input.returnPressed.connect(self.send_message)

        self.send_button = QPushButton("Send")
        self.send_button.setStyleSheet("""
            background-color: #6a994e; 
            color: white; 
            border-radius: 8px; 
            padding: 8px;
        """)
        self.send_button.clicked.connect(self.send_message)

        self.clear_button = QPushButton("Clear Chat")
        self.clear_button.setStyleSheet("""
            background-color: #bc4749; 
            color: white; 
            border-radius: 8px; 
            padding: 8px;
        """)
        self.clear_button.clicked.connect(self.clear_chat)

        input_layout.addWidget(self.user_input)
        input_layout.addWidget(self.send_button)
        input_layout.addWidget(self.clear_button)

        main_layout.addLayout(input_layout)
        self.setLayout(main_layout)

        self.update_chat_display(f"Chatbot: {self.current_question}", "left")

    def toggle_mode_with_label(self, checked):
        self.use_online = checked
        if checked:
            self.mode_label.setText("Switch to Offline")
            mode_text = "Online (Gemini)"
        else:
            self.mode_label.setText("Switch to Online")
            mode_text = "Local (Ollama)"
        self.update_chat_display(f"System: Switched to {mode_text} mode", "left")

    def send_message(self):
        user_answer = self.user_input.text().strip()
        if not user_answer:
            return

        self.update_chat_display(f"You: {user_answer}", "right")
        self.user_input.clear()

        # Get chatbot's response with user data
        next_question = chat(self.current_question, user_answer, self.user_data, self.use_online)
        self.current_question = next_question

        self.update_chat_display(f"Chatbot: {next_question}", "left")

    def update_chat_display(self, message, alignment="left"):
        color = "#6a994e" if alignment == "right" else "#386641"
        alignment_flag = Qt.AlignmentFlag.AlignRight if alignment == "right" else Qt.AlignmentFlag.AlignLeft

        formatted_message = f"<p style='color:{color}; text-align:{alignment};'><b>{message}</b></p>"
        self.chat_display.append(formatted_message)

    def clear_chat(self):
        self.chat_display.clear()
        # Reset to personalized greeting
        username = self.user_data.get("username", "")
        recommended_crop = self.db_manager.get_recommended_crop(username)
        
        if recommended_crop and recommended_crop != "ADVEN":
            self.current_question = f"Hello {username}! Based on your previous recommended crop ({recommended_crop}), how can I assist you?"
        else:
            self.current_question = f"Hello {username}! How can I assist you with farming today?"
            
        self.update_chat_display(f"Chatbot: {self.current_question}", "left")

    def closeEvent(self, event):
        self.db_manager.close()
        event.accept()

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatbotApp()
    window.showMaximized()
    sys.exit(app.exec())
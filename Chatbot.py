import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QLineEdit, QPushButton, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt
from langchain_ollama import OllamaLLM as Ollama
from langchain.prompts import PromptTemplate

# Create a custom prompt template for agriculture assistance
template = (
    "You are a helpful and knowledgeable agriculture assistant. Your goal is to provide useful information and advice to farmers. "
    "Answer questions about weather, soil, fertilizers, and farming techniques. If you don't know the answer, say 'I don't know.'\n\n"
    "Chatbot: {question}\n\n"
    "User: {answer}\n\n"
    "Chatbot:"
)
CHAT_PROMPT = PromptTemplate(template=template, input_variables=["question", "answer"])

# Load the locally installed Llama 3.2 via Ollama
llm = Ollama(model="llama3.2")

def chat(question, answer=""):
    try:
        formatted_prompt = CHAT_PROMPT.format(question=question, answer=answer)
        response = llm(formatted_prompt)
        return response.strip()
    except Exception as e:
        return f"Error: {str(e)}"

# PyQt6 GUI Application
class ChatbotApp(QWidget):
    def __init__(self):
        super().__init__()
        self.current_question = "How can I assist you with farming today?"
        self.chat_history = []
        self.initUI()

    def initUI(self):
        self.setWindowTitle("FieldBuddy Chatbot")
        self.setGeometry(100, 100, 800, 700)
        self.setStyleSheet("background-color: #f4f1de;")

        # Main layout
        main_layout = QVBoxLayout()
        
        # Top bar with back button
        top_bar = QHBoxLayout()
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
        top_bar.addStretch()  # Push the back button to the left
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

    def send_message(self):
        user_answer = self.user_input.text().strip()
        if not user_answer:
            return

        self.update_chat_display(f"You: {user_answer}", "right")
        self.user_input.clear()

        # Get chatbot's response
        next_question = chat(self.current_question, user_answer)
        self.current_question = next_question

        self.update_chat_display(f"Chatbot: {next_question}", "left")

    def update_chat_display(self, message, alignment="left"):
        color = "#6a994e" if alignment == "right" else "#386641"
        alignment_flag = Qt.AlignmentFlag.AlignRight if alignment == "right" else Qt.AlignmentFlag.AlignLeft

        formatted_message = f"<p style='color:{color}; text-align:{alignment};'><b>{message}</b></p>"
        self.chat_display.append(formatted_message)

    def clear_chat(self):
        self.chat_display.clear()
        self.current_question = "How can I assist you with farming today?"
        self.update_chat_display(f"Chatbot: {self.current_question}", "left")

# Run the application
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = ChatbotApp()
    window.showMaximized()
    sys.exit(app.exec())
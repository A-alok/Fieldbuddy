import sys
import mysql.connector
from PyQt6 import QtCore, QtGui
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QFrame, QCheckBox, QMessageBox, QStackedWidget)
from PyQt6.QtCore import Qt, QSettings
from PyQt6.QtGui import QFont, QIcon, QPixmap
from home_modified import HomeWindow
import subprocess

class DatabaseManager:
    def __init__(self):
        try:
            self.connection = mysql.connector.connect(
                host="localhost",
                user="root",
                password="Tiger@2010",
                database="fieldbuddy"
            )
            self.create_tables()
            print("Database connection successful")
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL: {err}")
            QMessageBox.critical(None, "Database Error", 
                               f"Could not connect to database: {err}")
    
    def create_tables(self):
        cursor = self.connection.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                remember_me BOOLEAN DEFAULT FALSE
            )
        ''')
        self.connection.commit()
        cursor.close()
    
    def register_user(self, username, password):
        try:
            cursor = self.connection.cursor()
            query = "INSERT INTO users (username, password) VALUES (%s, %s)"
            cursor.execute(query, (username, password))
            self.connection.commit()
            cursor.close()
            return True, "Registration successful"
        except mysql.connector.Error as err:
            if err.errno == 1062:
                return False, "Username already exists"
            return False, f"Error: {err}"
    
    def authenticate_user(self, username, password):
        try:
            cursor = self.connection.cursor()
            query = "SELECT * FROM users WHERE username = %s AND password = %s"
            cursor.execute(query, (username, password))
            result = cursor.fetchone()
            cursor.close()
            return (True, "Login successful") if result else (False, "Invalid username or password")
        except mysql.connector.Error as err:
            return False, f"Error: {err}"
    
    def update_remember_me(self, username, remember):
        try:
            cursor = self.connection.cursor()
            query = "UPDATE users SET remember_me = %s WHERE username = %s"
            cursor.execute(query, (remember, username))
            self.connection.commit()
            cursor.close()
        except mysql.connector.Error as err:
            print(f"Error updating remember_me: {err}")
    
    def close(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

class MountainAuthApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.settings = QSettings("FieldBuddy", "LoginApp")
        self.setStyleSheet("""
            QToolTip {
                background-color: #f8f9fa;
                color: #212529;
                border: 1px solid #dee2e6;
                padding: 5px;
                border-radius: 5px;
                font-size: 12px;
            }
            QLineEdit[error="true"] {
                border: 2px solid #dc3545;
                border-radius: 15px;
            }
        """)
        
        self.db_manager = DatabaseManager()
        self.setWindowTitle("Mountain Authentication")
        self.setMinimumSize(500, 700)
        self.setWindowIcon(QIcon("icon.png"))
        self.background_image = QPixmap("D:\\Project\\new\\bg.jpg")
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QVBoxLayout(self.central_widget)
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        
        self.stacked_widget = QStackedWidget()
        self.main_layout.addWidget(self.stacked_widget)
        
        self.create_login_page()
        self.create_signup_page()
        self.stacked_widget.setCurrentIndex(0)
        
        # Load remembered credentials if they exist
        self.load_remembered_credentials()
        
        self.show()
    
    def load_remembered_credentials(self):
        remember = self.settings.value("remember_me", False, type=bool)
        if remember:
            username = self.settings.value("username", "")
            password = self.settings.value("password", "")
            self.login_username_input.setText(username)
            self.login_password_input.setText(password)
            self.remember_checkbox.setChecked(True)
    
    def save_credentials(self, username, password, remember):
        self.settings.setValue("remember_me", remember)
        if remember:
            self.settings.setValue("username", username)
            self.settings.setValue("password", password)
        else:
            self.settings.remove("username")
            self.settings.remove("password")
    
    def paintEvent(self, event):
        painter = QtGui.QPainter(self)
        scaled_image = self.background_image.scaled(self.size(), 
                                                   Qt.AspectRatioMode.KeepAspectRatioByExpanding,
                                                   Qt.TransformationMode.SmoothTransformation)
        painter.drawPixmap(self.rect(), scaled_image)
    
    def validate_password(self, password):
        if len(password) < 8:
            return False, "Password must be at least 8 characters long"
        if not any(c.isupper() for c in password):
            return False, "Password must contain at least one uppercase letter"
        if not any(c.islower() for c in password):
            return False, "Password must contain at least one lowercase letter"
        if not any(c.isdigit() for c in password):
            return False, "Password must contain at least one digit"
        if all(c.isalnum() for c in password):
            return False, "Password must contain at least one special character"
        return True, "Password is valid"
    
    def set_input_error(self, input_field, has_error):
        input_field.setProperty("error", has_error)
        input_field.style().unpolish(input_field)
        input_field.style().polish(input_field)
    
    def create_login_page(self):
        login_page = QWidget()
        page_layout = QVBoxLayout(login_page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        
        outer_container = QWidget()
        outer_container.setObjectName("outerContainer")
        outer_container.setFixedWidth(350)
        outer_container.setStyleSheet("""
            #outerContainer {
                background-color: rgba(222,255,201,1);
                border-radius: 20px;
                padding: 10px;
                background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                stop: 0.57 #ECEAA7,
                stop: 1 #F5F5F5);
            }
        """)
        
        outer_layout = QVBoxLayout(outer_container)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        login_container = QWidget()
        login_container.setObjectName("loginContainer")
        login_container.setStyleSheet("""
            #loginContainer {
                background-color: rgba(10, 10, 10, 0);
                border-radius: 15px;
            }
        """)
        outer_layout.addWidget(login_container)
        
        login_layout = QVBoxLayout(login_container)
        login_layout.setContentsMargins(30, 40, 30, 40)
        login_layout.setSpacing(20)
        
        title_label = QLabel("Log In")
        title_label.setFont(QFont("Bebas Neue", 26, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #37880c;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(title_label)
        login_layout.addSpacing(30)
        
        username_label = QLabel("User Name")
        username_label.setStyleSheet("color: #37880c; font-size: 16px;")
        login_layout.addWidget(username_label)
        
        username_frame = QFrame()
        username_frame.setStyleSheet("""
            QFrame {
                border-bottom: 2px solid white;
                padding-bottom: 5px;
                margin-bottom: 20px;
            }
        """)
        username_layout = QVBoxLayout(username_frame)
        username_layout.setContentsMargins(0, 0, 0, 0)
        
        self.login_username_input = QLineEdit()
        self.login_username_input.setToolTip("Enter your registered username")
        self.login_username_input.setStyleSheet("""
            QLineEdit {
                border:2px solid #e9ecef;
                border-radius:15px;
                font-size: 16px;
                color: black;
                background: white;
                padding :5px;
            }
        """)
        # Connect textChanged signal to clear error state
        self.login_username_input.textChanged.connect(
            lambda: self.set_input_error(self.login_username_input, False))
        username_layout.addWidget(self.login_username_input)
        login_layout.addWidget(username_frame)
        
        password_label = QLabel("Password")
        password_label.setStyleSheet("color: #37880c; font-size: 16px;")
        login_layout.addWidget(password_label)
        
        password_frame = QFrame()
        password_frame.setStyleSheet("""
            QFrame {
                border-bottom: 2px solid white;
                padding-bottom: 5px;
                margin-bottom: 30px;
            }
        """)
        password_layout = QVBoxLayout(password_frame)
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        self.login_password_input = QLineEdit()
        self.login_password_input.setToolTip("Enter your account password")
        self.login_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.login_password_input.setStyleSheet("""
            QLineEdit {
                border:2px solid #e9ecef;
                border-radius:15px;
                font-size: 16px;
                color: black;
                background: white;
                padding :5px;
            }
        """)
        # Connect textChanged signal to clear error state
        self.login_password_input.textChanged.connect(
            lambda: self.set_input_error(self.login_password_input, False))
        password_layout.addWidget(self.login_password_input)
        login_layout.addWidget(password_frame)
        
        self.remember_checkbox = QCheckBox("Remember me")
        self.remember_checkbox.setToolTip("Keep me logged in on this device")
        self.remember_checkbox.setStyleSheet("""
            QCheckBox {
                color: white;
                font-size: 14px;
            }
            QCheckBox::indicator {
                width: 18px;
                height: 18px;
                background-color: rgba(255, 255, 255, 0.2);
                border-radius: 3px;
            }
            QCheckBox::indicator:checked {
                background-color: #4a8db7;
            }
        """)
        login_layout.addWidget(self.remember_checkbox)
        login_layout.addSpacing(10)
        
        login_button = QPushButton("L o g  I n")
        login_button.setToolTip("Click to login to your account")
        login_button.setFixedHeight(50)
        login_button.setCursor(Qt.CursorShape.PointingHandCursor)
        login_button.setStyleSheet("""
            QPushButton {
                background-color: #2a4d69;
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 18px;
                letter-spacing: 3px;
            }
            QPushButton:hover {
                background-color: #3a6189;
            }
            QPushButton:pressed {
                background-color: #1a3d59;
            }
        """)
        login_button.clicked.connect(self.login)
        login_layout.addWidget(login_button)
        
        signup_layout = QHBoxLayout()
        signup_text = QLabel("Don't have an account?")
        signup_text.setStyleSheet("color: white; font-size: 14px;")
        
        signup_link = QPushButton("Sign Up")
        signup_link.setToolTip("Create a new account")
        signup_link.setCursor(Qt.CursorShape.PointingHandCursor)
        signup_link.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #4a8db7;
                font-size: 14px;
                font-weight: bold;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #6aaddb;
            }
        """)
        signup_link.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(1))
        
        signup_layout.addStretch()
        signup_layout.addWidget(signup_text)
        signup_layout.addWidget(signup_link)
        signup_layout.addStretch()
        login_layout.addLayout(signup_layout)
        
        self.login_error_label = QLabel("")
        self.login_error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
        self.login_error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        login_layout.addWidget(self.login_error_label)
        
        page_layout.addStretch(1)
        page_layout.addWidget(outer_container, alignment=Qt.AlignmentFlag.AlignCenter)
        page_layout.addStretch(1)
        self.stacked_widget.addWidget(login_page)
    
    def create_signup_page(self):
        signup_page = QWidget()
        page_layout = QVBoxLayout(signup_page)
        page_layout.setContentsMargins(0, 0, 0, 0)
        
        outer_container = QWidget()
        outer_container.setObjectName("outerContainer")
        outer_container.setFixedWidth(350)
        outer_container.setStyleSheet("""
            #outerContainer {
                background-color: rgba(222,255,201,1);
                border-radius: 20px;
                padding: 10px;
                background: QLinearGradient(x1: 0, y1: 0, x2: 0, y2: 1, 
                stop: 0.57 #ECEAA7, 
                stop: 1 #F5F5F5); 
            }
        """)
        
        outer_layout = QVBoxLayout(outer_container)
        outer_layout.setContentsMargins(10, 10, 10, 10)
        
        signup_container = QWidget()
        signup_container.setObjectName("signupContainer")
        signup_container.setStyleSheet("""
            #signupContainer {
                background-color: rgba(10, 10, 10, 0);
                border-radius: 15px;
            }
        """)
        outer_layout.addWidget(signup_container)
        
        signup_layout = QVBoxLayout(signup_container)
        signup_layout.setContentsMargins(30, 40, 30, 40)
        signup_layout.setSpacing(20)
        
        title_label = QLabel("Sign Up")
        title_label.setFont(QFont("Bebas Neue", 26, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #37880c;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signup_layout.addWidget(title_label)
        signup_layout.addSpacing(30)
        
        username_label = QLabel("Choose Username")
        username_label.setStyleSheet("color: #37880c; font-size: 16px;")
        signup_layout.addWidget(username_label)
        
        username_frame = QFrame()
        username_frame.setStyleSheet("""
            QFrame {
                border-bottom: 2px solid white;
                padding-bottom: 5px;
                margin-bottom: 20px;
            }
        """)
        username_layout = QVBoxLayout(username_frame)
        username_layout.setContentsMargins(0, 0, 0, 0)
        
        self.signup_username_input = QLineEdit()
        self.signup_username_input.setToolTip("Unique 4-20 characters, letters and numbers only")
        self.signup_username_input.setStyleSheet("""
            QLineEdit {
                border:2px solid #e9ecef;
                border-radius:15px;
                font-size: 16px;
                color: black;
                background: white;
                padding :5px;
            }
        """)
        # Connect textChanged signal to clear error state
        self.signup_username_input.textChanged.connect(
            lambda: self.set_input_error(self.signup_username_input, False))
        username_layout.addWidget(self.signup_username_input)
        signup_layout.addWidget(username_frame)
        
        password_label = QLabel("Create Password")
        password_label.setStyleSheet("color: #37880c; font-size: 16px;")
        signup_layout.addWidget(password_label)
        
        password_frame = QFrame()
        password_frame.setStyleSheet("""
            QFrame {
                border-bottom: 2px solid white;
                padding-bottom: 5px;
                margin-bottom: 20px;
            }
        """)
        password_layout = QVBoxLayout(password_frame)
        password_layout.setContentsMargins(0, 0, 0, 0)
        
        self.signup_password_input = QLineEdit()
        self.signup_password_input.setToolTip(
            "Password requirements:\n"
            "- Minimum 8 characters\n"
            "- At least one uppercase letter (A-Z)\n"
            "- At least one lowercase letter (a-z)\n"
            "- At least one digit (0-9)\n"
            "- At least one special character (!@#$%^&*)"
        )
        self.signup_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.signup_password_input.setStyleSheet("""
            QLineEdit {
                border:2px solid #e9ecef;
                border-radius:15px;
                font-size: 16px;
                color: black;
                background: white;
                padding :5px;
            }
        """)
        # Connect textChanged signal to clear error state
        self.signup_password_input.textChanged.connect(
            lambda: self.set_input_error(self.signup_password_input, False))
        password_layout.addWidget(self.signup_password_input)
        signup_layout.addWidget(password_frame)
        
        confirm_label = QLabel("Confirm Password")
        confirm_label.setStyleSheet("color: #37880c; font-size: 16px;")
        signup_layout.addWidget(confirm_label)
        
        confirm_frame = QFrame()
        confirm_frame.setStyleSheet("""
            QFrame {
                border-bottom: 2px solid white;
                padding-bottom: 5px;
                margin-bottom: 30px;
            }
        """)
        confirm_layout = QVBoxLayout(confirm_frame)
        confirm_layout.setContentsMargins(0, 0, 0, 0)
        self.confirm_password_input = QLineEdit()
        self.confirm_password_input.setToolTip("Re-enter your password")
        self.confirm_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.confirm_password_input.setStyleSheet("""
            QLineEdit {
                border:2px solid #e9ecef;
                border-radius:15px;
                font-size: 16px;
                color: black;
                background: white;
                padding :5px;
            }
        """)
        # Connect textChanged signal to clear error state
        self.confirm_password_input.textChanged.connect(
            lambda: self.set_input_error(self.confirm_password_input, False))
        confirm_layout.addWidget(self.confirm_password_input)
        signup_layout.addWidget(confirm_frame)
        
        register_button = QPushButton("J o i n")
        register_button.setToolTip("Create your new account")
        register_button.setFixedHeight(50)
        register_button.setCursor(Qt.CursorShape.PointingHandCursor)
        register_button.setStyleSheet("""
            QPushButton {
                background-color: #2a4d69;
                border: none;
                border-radius: 10px;
                color: white;
                font-size: 18px;
                letter-spacing: 3px;
            }
            QPushButton:hover {
                background-color: #3a6189;
            }
            QPushButton:pressed {
                background-color: #1a3d59;
            }
        """)
        register_button.clicked.connect(self.register)
        signup_layout.addWidget(register_button)
        
        login_layout = QHBoxLayout()
        login_text = QLabel("Already have an account?")
        login_text.setStyleSheet("color: white; font-size: 14px;")
        
        login_link = QPushButton("Log In")
        login_link.setToolTip("Go to login page")
        login_link.setCursor(Qt.CursorShape.PointingHandCursor)
        login_link.setStyleSheet("""
            QPushButton {
                background: none;
                border: none;
                color: #4a8db7;
                font-size: 14px;
                font-weight: bold;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #6aaddb;
            }
        """)
        login_link.clicked.connect(lambda: self.stacked_widget.setCurrentIndex(0))
        
        login_layout.addStretch()
        login_layout.addWidget(login_text)
        login_layout.addWidget(login_link)
        login_layout.addStretch()
        signup_layout.addLayout(login_layout)
        
        self.signup_error_label = QLabel("")
        self.signup_error_label.setStyleSheet("color: #ff6b6b; font-size: 14px;")
        self.signup_error_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        signup_layout.addWidget(self.signup_error_label)
        
        page_layout.addStretch(1)
        page_layout.addWidget(outer_container, alignment=Qt.AlignmentFlag.AlignCenter)
        page_layout.addStretch(1)
        self.stacked_widget.addWidget(signup_page)
    
    def login(self):
        username = self.login_username_input.text().strip()
        password = self.login_password_input.text().strip()
        remember = self.remember_checkbox.isChecked()
        
        # Reset all error states and messages
        self.set_input_error(self.login_username_input, False)
        self.set_input_error(self.login_password_input, False)
        self.login_error_label.setText("")
        
        # Validate inputs
        if not username:
            self.set_input_error(self.login_username_input, True)
            self.login_error_label.setText("Please enter username")
            return
            
        if not password:
            self.set_input_error(self.login_password_input, True)
            self.login_error_label.setText("Please enter password")
            return
        
        # Attempt authentication
        success, message = self.db_manager.authenticate_user(username, password)
        
        if success:
            # Save credentials if "Remember me" is checked
            self.save_credentials(username, password, remember)
            
            # Update remember_me status in database
            self.db_manager.update_remember_me(username, remember)
            
            QMessageBox.information(self, "Success", "Login successful!")
            self.login_username_input.clear()
            self.login_password_input.clear()
            self.login_error_label.setText("")
            self.close()
            self.launch_home_dashboard(username)
        else:
            self.set_input_error(self.login_username_input, True)
            self.set_input_error(self.login_password_input, True)
            self.login_error_label.setText(message)
    
    def launch_home_dashboard(self, username):
        # Close the current window
        self.close()
         # Launch home.py with the username
        subprocess.Popen([sys.executable, "home_modified.py", username])
    
    def register(self):
        username = self.signup_username_input.text().strip()
        password = self.signup_password_input.text().strip()
        confirm_password = self.confirm_password_input.text().strip()
        
        # Reset all error states and messages
        self.set_input_error(self.signup_username_input, False)
        self.set_input_error(self.signup_password_input, False)
        self.set_input_error(self.confirm_password_input, False)
        self.signup_error_label.setText("")
        
        # Validate inputs
        if not username:
            self.set_input_error(self.signup_username_input, True)
            self.signup_error_label.setText("Please choose a username")
            return
            
        if not password:
            self.set_input_error(self.signup_password_input, True)
            self.signup_error_label.setText("Please create a password")
            return
            
        if not confirm_password:
            self.set_input_error(self.confirm_password_input, True)
            self.signup_error_label.setText("Please confirm your password")
            return
        
        if password != confirm_password:
            self.set_input_error(self.signup_password_input, True)
            self.set_input_error(self.confirm_password_input, True)
            self.signup_error_label.setText("Passwords do not match")
            return
        
        is_valid, message = self.validate_password(password)
        if not is_valid:
            self.set_input_error(self.signup_password_input, True)
            self.set_input_error(self.confirm_password_input, True)
            self.signup_error_label.setText(message)
            return
        
        # Attempt registration
        success, message = self.db_manager.register_user(username, password)
        
        if success:
            QMessageBox.information(self, "Success", "Registration successful! You can now log in.")
            self.signup_username_input.clear()
            self.signup_password_input.clear()
            self.confirm_password_input.clear()
            self.signup_error_label.setText("")
            self.stacked_widget.setCurrentIndex(0)
        else:
            self.set_input_error(self.signup_username_input, True)
            self.signup_error_label.setText(message)
    
    def closeEvent(self, event):
        self.db_manager.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setFont(QFont("Bebas Neue"))
    window = MountainAuthApp()
    window.showMaximized()
    sys.exit(app.exec())
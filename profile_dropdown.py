import sys
import os
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialog,
    QLineEdit, QPushButton, QFormLayout, QFrame, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QGuiApplication

class ProfileEditDialog(QDialog):
    def __init__(self, parent=None, user_data=None):
        super().__init__(parent)
        self.setWindowTitle("Edit Profile")
        self.setMinimumWidth(400)
        self.setStyleSheet("""
            QDialog {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #f8f9fa, stop:1 #e6f4ea);
            }
            QLabel {
                color: #343a40;
                font-size: 14px;
                font-weight: 500;
                padding: 5px 0;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
                color: #495057;
                background-color: white;
                min-width: 250px;
            }
            QLineEdit:focus {
                border: 2px solid #2b8a3e;
            }
            QPushButton {
                background-color: #2b8a3e;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 6px;
                font-size: 14px;
                font-weight: bold;
                min-width: 100px;
            }
            QPushButton:hover {
                background-color: #2f9e44;
            }
            QPushButton:pressed {
                background-color: #248232;
            }
            QPushButton#cancelButton {
                background-color: #6c757d;
            }
            QPushButton#cancelButton:hover {
                background-color: #5a6268;
            }
        """)
        
        if user_data is None:
            user_data = {
                "username": "",
                "email": "",
                "phone": "",
                "state": "",
                "city": ""
            }
        
        # Create form layout
        layout = QFormLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Add fields
        
        self.phone_input = QLineEdit(user_data["phone"])
        layout.addRow("Phone:", self.phone_input)
        
        self.email_input = QLineEdit(user_data["email"])
        layout.addRow("Email:", self.email_input)
        
        self.state_input = QLineEdit(user_data["state"])
        layout.addRow("State:", self.state_input)
        
        self.city_input = QLineEdit(user_data["city"])
        layout.addRow("City:", self.city_input)
        
        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(15)
        
        save_button = QPushButton("Save")
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addRow(button_layout)
        
        save_button.clicked.connect(self.accept)
    
    def get_user_data(self):
        return {
            "username": self.username_input.text(),
            "email": self.email_input.text(),
            "phone": self.phone_input.text(),
            "state": self.state_input.text(),
            "city": self.city_input.text()
        }

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
        # Create users table if it doesn't exist
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INT AUTO_INCREMENT PRIMARY KEY,
                username VARCHAR(50) UNIQUE NOT NULL,
                password VARCHAR(100) NOT NULL,
                remember_me BOOLEAN DEFAULT FALSE,
                email VARCHAR(100),
                phone VARCHAR(20),
                state VARCHAR(50),
                city VARCHAR(50)
            )
        ''')
        self.connection.commit()
        cursor.close()
    
    def update_user_profile(self, username, email, phone, state, city):
        try:
            cursor = self.connection.cursor()
            query = """
                UPDATE users 
                SET email = %s, phone = %s, state = %s, city = %s 
                WHERE username = %s
            """
            cursor.execute(query, (email, phone, state, city, username))
            self.connection.commit()
            cursor.close()
            return True, "Profile updated successfully"
        except mysql.connector.Error as err:
            return False, f"Error updating profile: {err}"
    
    def get_user_data(self, username):
        try:
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT username, email, phone, state, city FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                return result
            else:
                return {
                    "username": username,
                    "email": "",
                    "phone": "",
                    "state": "",
                    "city": ""
                }
        except mysql.connector.Error as err:
            print(f"Error fetching user data: {err}")
            return {
                "username": username,
                "email": "",
                "phone": "",
                "state": "",
                "city": ""
            }
    
    def close(self):
        if hasattr(self, 'connection') and self.connection.is_connected():
            self.connection.close()
            print("Database connection closed")

class ProfileMenu(QWidget):
    def __init__(self, username):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Position near the profile icon in home.py
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        
        # Position in top right corner, slightly offset from edge
        self.setGeometry(screen_width - 220, 100, 200, 150)
        
        self.username = username
        self.db_manager = DatabaseManager()
        self.load_user_data()
        self.initUI()
    
    def load_user_data(self):
        # Load user data from database
        self.user_data = self.db_manager.get_user_data(self.username)
        
        # Save to session file for other parts of the app
        with open("user_session.txt", "w") as f:
            for key, value in self.user_data.items():
                f.write(f"{key}={value}\n")
    
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create dropdown frame
        dropdown_frame = QFrame()
        dropdown_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
            }
            QPushButton {
                background-color: transparent;
                color: #343a40;
                border: none;
                text-align: left;
                padding: 10px 15px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #f1f3f5;
                color: #2b8a3e;
            }
        """)
        
        # Add shadow effect using QGraphicsDropShadowEffect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 60))
        dropdown_frame.setGraphicsEffect(shadow)
        
        dropdown_layout = QVBoxLayout(dropdown_frame)
        dropdown_layout.setContentsMargins(0, 0, 0, 0)
        dropdown_layout.setSpacing(0)
        
        # User info section
        user_info = QLabel(f"{self.user_data['username']}")
        user_info.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        user_info.setStyleSheet("""
            background-color: #2b8a3e;
            color: white;
            padding: 12px;
            border-top-left-radius: 8px;
            border-top-right-radius: 8px;
        """)
        user_info.setAlignment(Qt.AlignmentFlag.AlignCenter)
        dropdown_layout.addWidget(user_info)
        
        # Edit Profile button
        edit_profile_btn = QPushButton("Edit Profile")
        edit_profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_profile_btn.clicked.connect(self.editProfile)
        dropdown_layout.addWidget(edit_profile_btn)
        
        # Add separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e9ecef;")
        separator.setFixedHeight(1)
        dropdown_layout.addWidget(separator)
        
        # Logout button
        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        dropdown_layout.addWidget(logout_btn)
        
        main_layout.addWidget(dropdown_frame)
        self.setLayout(main_layout)
    
    def editProfile(self):
        dialog = ProfileEditDialog(None, self.user_data)
        if dialog.exec():
            # Update user data and save to database
            updated_data = dialog.get_user_data()
            success, message = self.db_manager.update_user_profile(
                updated_data["username"],
                updated_data["email"],
                updated_data["phone"],
                updated_data["state"],
                updated_data["city"]
            )
            
            if success:
                # Update session file
                with open("user_session.txt", "w") as f:
                    for key, value in updated_data.items():
                        f.write(f"{key}={value}\n")
                
                QMessageBox.information(None, "Profile Updated", "Your profile has been updated successfully!")
                
                # Close menu and restart home to reflect changes
                self.close()
                self.db_manager.close()
                os.execl(sys.executable, sys.executable, "home.py")
            else:
                QMessageBox.critical(None, "Error", message)
    
    def logout(self):
        # Remove session file
        if os.path.exists("user_session.txt"):
            os.remove("user_session.txt")
        
        # Close menu and database connection
        self.close()
        self.db_manager.close()
        
        # Launch login2.py
        import subprocess
        subprocess.Popen([sys.executable, "login2.py"])
        
        # Find and close home.py process
        for proc in QApplication.topLevelWidgets():
            if proc.windowTitle() == "FieldBuddy Dashboard":
                proc.close()

# For testing the profile menu directly
if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Create a test username - in real usage, this would come from login
    test_username = "USERNAME"
    if len(sys.argv) > 1:
        test_username = sys.argv[1]
    
    window = ProfileMenu(test_username)
    window.show()
    sys.exit(app.exec())
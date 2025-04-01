# profile_dropdown.py
import sys
import os
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialog,
    QLineEdit, QPushButton, QFormLayout, QFrame, QMessageBox, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QGuiApplication
# Remove the circular import
# from login2 import MountainAuthApp
# from home_modified import HomeWindow

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
            QLineEdit[readOnly="true"] {
                background-color: #f1f3f5;
                color: #868e96;
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
        
        # Initialize with empty data if none provided
        self.user_data = user_data or {
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
        
        # Username field (read-only)
        self.username_input = QLineEdit(self.user_data.get("username", ""))
        self.username_input.setReadOnly(True)
        self.username_input.setProperty("readOnly", "true")  # For styling
        layout.addRow("Username:", self.username_input)
        
        # Phone field
        self.phone_input = QLineEdit(self.user_data.get("phone", ""))
        layout.addRow("Phone:", self.phone_input)
        
        # Email field
        self.email_input = QLineEdit(self.user_data.get("email", ""))
        layout.addRow("Email:", self.email_input)
        
        # State field
        self.state_input = QLineEdit(self.user_data.get("state", ""))
        layout.addRow("State:", self.state_input)
        
        # City field
        self.city_input = QLineEdit(self.user_data.get("city", ""))
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
                # Ensure all fields exist even if NULL in database
                return {
                    "username": result.get("username", username),
                    "email": result.get("email", ""),
                    "phone": result.get("phone", ""),
                    "state": result.get("state", ""),
                    "city": result.get("city", "")
                }
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
    logoutRequested = pyqtSignal()
    restartRequested = pyqtSignal()
    
    def __init__(self, username, parent=None):
        super().__init__()
        self.setWindowFlags(Qt.WindowType.FramelessWindowHint | Qt.WindowType.Popup)
        self.setAttribute(Qt.WidgetAttribute.WA_TranslucentBackground)
        
        # Store parent window reference
        self.parent_window = parent
        
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
        self.user_data = self.db_manager.get_user_data(self.username)
        # Remove the file writing part
    
    def initUI(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
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
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setXOffset(0)
        shadow.setYOffset(5)
        shadow.setColor(QColor(0, 0, 0, 60))
        dropdown_frame.setGraphicsEffect(shadow)
        
        dropdown_layout = QVBoxLayout(dropdown_frame)
        dropdown_layout.setContentsMargins(0, 0, 0, 0)
        dropdown_layout.setSpacing(0)
        
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
        
        edit_profile_btn = QPushButton("Edit Profile")
        edit_profile_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        edit_profile_btn.clicked.connect(self.editProfile)
        dropdown_layout.addWidget(edit_profile_btn)
        
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setStyleSheet("background-color: #e9ecef;")
        separator.setFixedHeight(1)
        dropdown_layout.addWidget(separator)
        
        logout_btn = QPushButton("Logout")
        logout_btn.setCursor(Qt.CursorShape.PointingHandCursor)
        logout_btn.clicked.connect(self.logout)
        dropdown_layout.addWidget(logout_btn)
        
        main_layout.addWidget(dropdown_frame)
        self.setLayout(main_layout)
    
    def editProfile(self):
        dialog = ProfileEditDialog(None, self.user_data)
        if dialog.exec():
            updated_data = dialog.get_user_data()
            try:
                success, message = self.db_manager.update_user_profile(
                    updated_data["username"],
                    updated_data["email"],
                    updated_data["phone"],
                    updated_data["state"],
                    updated_data["city"]
                )
                
                if success:
                    # Update the internal user_data
                    self.user_data = updated_data
                    
                    QMessageBox.information(None, "Profile Updated", "Your profile has been updated successfully!")
                    
                    # Close just the dialog
                    self.close()
                    
                    # Comment out the restart request to avoid closing the application
                    # self.restartRequested.emit()
                else:
                    QMessageBox.critical(None, "Error", message)
            except Exception as e:
                QMessageBox.critical(None, "Error", f"An unexpected error occurred: {str(e)}")
    
    def logout(self):
        # Remove this section
        # if os.path.exists("user_session.txt"):
        #    os.remove("user_session.txt")

        # Close the parent window (home_modified.py) if it exists
        if self.parent_window:
            self.parent_window.close()
        
        # Import here to avoid circular import
        from login2 import MountainAuthApp
        
        # Open login window
        self.login = MountainAuthApp()
        self.login.showMaximized()
        self.close()
        
        # Close database connection
        self.db_manager.close()
        self.logoutRequested.emit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    test_username = "test_user" if len(sys.argv) < 2 else sys.argv[1]
    window = ProfileMenu(test_username)
    window.show()
    sys.exit(app.exec())


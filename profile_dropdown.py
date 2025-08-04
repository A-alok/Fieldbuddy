import sys
import os
import mysql.connector
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout, QDialog, QMessageBox,
    QLineEdit, QPushButton, QFormLayout, QFrame, QGraphicsDropShadowEffect, QComboBox
)
from PyQt6.QtCore import Qt, QPoint, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon, QPalette, QColor, QGuiApplication
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

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
                padding: 5px;
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
            QLineEdit:invalid {
                border: 2px solid #dc3545;
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
            QLabel.error {
                color: #dc3545;
                font-size: 12px;
                margin-top: 5px;
            }
            QComboBox {
                padding: 5px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
                color: #495057;
                background-color: white;
                min-width: 250px;
            }
            QComboBox:focus {
                border: 2px solid #2b8a3e;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(images/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        
        # Initialize database manager
        self.db_manager = DatabaseManager()
        
        # Initialize with empty data if none provided
        self.user_data = user_data or {
            "username": "",
            "email": "",
            "phone": "",
            "state": "",
            "city": ""
        }

        # If we have a username, try to fetch existing data from database
        if self.user_data.get("username"):
            db_data = self.db_manager.get_user_data(self.user_data["username"])
            if db_data:
                self.user_data = db_data
                print(f"Loaded existing data from database: {self.user_data}")

        # Create form layout
        layout = QFormLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(8)
        layout.setVerticalSpacing(8)
        layout.setHorizontalSpacing(8)
        
        # Username field (read-only)
        self.username_input = QLineEdit(self.user_data.get("username", ""))
        self.username_input.setReadOnly(True)
        self.username_input.setProperty("readOnly", "true")
        self.username_input.setToolTip("Your username cannot be changed")
        layout.addRow("Username:", self.username_input)
        
        # Add spacing after username
        spacer1 = QLabel("")
        spacer1.setFixedHeight(10)
        layout.addRow("", spacer1)
        
        # Phone field with validation
        self.phone_input = QLineEdit(self.user_data.get("phone", ""))
        self.phone_input.setMaxLength(10)
        self.phone_input.textChanged.connect(self.validate_phone)
        self.phone_input.setToolTip("Enter your 10-digit mobile number\nExample: 9876543210")
        self.phone_error = QLabel()
        self.phone_error.setObjectName("error")
        layout.addRow("Phone:", self.phone_input)
        layout.addRow("", self.phone_error)
        
        # Add spacing after phone
        spacer2 = QLabel("")
        spacer2.setFixedHeight(10)
        layout.addRow("", spacer2)
        
        # Email field with validation
        self.email_input = QLineEdit(self.user_data.get("email", ""))
        self.email_input.textChanged.connect(self.validate_email)
        self.email_input.setToolTip("Enter your email address\nMust end with @gmail.com\nExample: user@gmail.com")
        self.email_error = QLabel()
        self.email_error.setObjectName("error")
        layout.addRow("Email:", self.email_input)
        layout.addRow("", self.email_error)
        
        # Add spacing after email
        spacer3 = QLabel("")
        spacer3.setFixedHeight(10)
        layout.addRow("", spacer3)
        
        # State field with dropdown
        self.state_input = QComboBox()
        self.state_input.setStyleSheet("""
            QComboBox {
                padding: 4px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
                color: #495057;
                background-color: white;
                min-width: 250px;
            }
            QComboBox:focus {
                border: 2px solid #2b8a3e;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(images/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.state_input.setToolTip("Select your state from the dropdown\nCities will update automatically based on your selection")
        
        # Dictionary of states and their major cities
        self.state_cities = {
            "Andhra Pradesh": ["Visakhapatnam", "Vijayawada", "Guntur", "Nellore", "Kurnool", "Tirupati", 
                             "Rajahmundry", "Kakinada", "Kadapa", "Anantapur", "Eluru", "Ongole", "Nandyal",
                             "Machilipatnam", "Adoni", "Tenali", "Chittoor", "Hindupur", "Proddatur", "Bhimavaram"],
            
            "Arunachal Pradesh": ["Itanagar", "Naharlagun", "Pasighat", "Tawang", "Bomdila", "Ziro", "Along",
                                "Tezu", "Daporijo", "Anini", "Khonsa", "Aalo", "Miao", "Roing", "Changlang"],
            
            "Assam": ["Guwahati", "Silchar", "Dibrugarh", "Jorhat", "Nagaon", "Tinsukia", "Tezpur", "Sivasagar",
                     "Barpeta", "Dhubri", "Goalpara", "Bongaigaon", "Karimganj", "Hailakandi", "Lakhimpur",
                     "Mangaldoi", "Dhemaji", "North Lakhimpur", "Golaghat", "Haflong"],
            
            "Bihar": ["Patna", "Gaya", "Bhagalpur", "Muzaffarpur", "Darbhanga", "Arrah", "Begusarai", "Katihar",
                     "Munger", "Chapra", "Bettiah", "Hajipur", "Sasaram", "Dehri", "Siwan", "Motihari",
                     "Nawada", "Bagaha", "Buxar", "Kishanganj"],
            
            "Chhattisgarh": ["Raipur", "Bhilai", "Bilaspur", "Korba", "Durg", "Raigarh", "Rajnandgaon", "Ambikapur",
                           "Mahasamund", "Dhamtari", "Jagdalpur", "Janjgir", "Kanker", "Kawardha", "Mungeli",
                           "Baloda Bazar", "Bemetara", "Sakti", "Chirmiri", "Baikunthpur"],
            
            "Goa": ["Panaji", "Margao", "Vasco da Gama", "Mapusa", "Ponda", "Mormugao", "Bicholim", "Curchorem",
                   "Valpoi", "Sanguem", "Quepem", "Canacona", "Pernem", "Sanquelim", "Cuncolim"],
            
            "Gujarat": ["Ahmedabad", "Surat", "Vadodara", "Rajkot", "Bhavnagar", "Gandhinagar", "Jamnagar", "Junagadh",
                       "Anand", "Navsari", "Morbi", "Nadiad", "Surendranagar", "Bharuch", "Valsad", "Porbandar",
                       "Godhra", "Palanpur", "Veraval", "Bhuj"],
            
            "Haryana": ["Faridabad", "Gurgaon", "Panipat", "Ambala", "Yamunanagar", "Rohtak", "Hisar", "Karnal",
                      "Sonipat", "Panchkula", "Bhiwani", "Sirsa", "Bahadurgarh", "Jind", "Thanesar", "Kaithal",
                      "Rewari", "Palwal", "Hansi", "Narnaul"],
            
            "Himachal Pradesh": ["Shimla", "Mandi", "Solan", "Dharamshala", "Bilaspur", "Kullu", "Chamba", "Una",
                               "Hamirpur", "Nahan", "Palampur", "Kangra", "Mandi", "Sundarnagar", "Rampur",
                               "Paonta Sahib", "Nalagarh", "Jogindernagar", "Manali", "Dalhousie"],
            
            "Jharkhand": ["Ranchi", "Jamshedpur", "Dhanbad", "Bokaro", "Hazaribagh", "Deoghar", "Giridih", "Hazaribagh",
                         "Ramgarh", "Medininagar", "Chirkunda", "Bokaro Steel City", "Phusro", "Chatra", "Garhwa",
                         "Koderma", "Jhumri Tilaiya", "Mango", "Sahibganj", "Madhupur"],
            
            "Karnataka": ["Bangalore", "Mysore", "Hubli", "Mangalore", "Belgaum", "Gulbarga", "Davanagere", "Bellary",
                         "Bijapur", "Shimoga", "Tumkur", "Raichur", "Bidar", "Hospet", "Hassan", "Gadag", "Udupi",
                         "Robertsonpet", "Bhadravati", "Chitradurga"],
            
            "Kerala": ["Thiruvananthapuram", "Kochi", "Kozhikode", "Kollam", "Thrissur", "Kannur", "Alappuzha", "Kottayam",
                      "Palakkad", "Manjeri", "Thalassery", "Ponnani", "Vatakara", "Kanhangad", "Taliparamba", "Koyilandy",
                      "Neyyattinkara", "Kayamkulam", "Nedumangad", "Kattappana"],
            
            "Madhya Pradesh": ["Bhopal", "Indore", "Jabalpur", "Gwalior", "Ujjain", "Sagar", "Ratlam", "Satna",
                             "Murwara", "Singrauli", "Rewa", "Burhanpur", "Khandwa", "Chhindwara", "Morena", "Bhind",
                             "Guna", "Shivpuri", "Vidisha", "Chhatarpur"],
            
            "Maharashtra": ["Mumbai", "Pune", "Nagpur", "Thane", "Nashik", "Aurangabad", "Solapur", "Amravati",
                          "Kolhapur", "Nanded", "Sangli", "Malegaon", "Jalgaon", "Akola", "Latur", "Dhule",
                          "Ahmednagar", "Ichalkaranji", "Parbhani", "Bhusawal"],
            
            "Manipur": ["Imphal", "Thoubal", "Bishnupur", "Churachandpur", "Ukhrul", "Kakching", "Lilong", "Mayang Imphal",
                       "Yairipok", "Moirang", "Nambol", "Oinam", "Sekmai", "Wangjing", "Khongman", "Konthoujam",
                       "Lamlai", "Sagolband", "Kwakta", "Kumbi"],
            
            "Meghalaya": ["Shillong", "Tura", "Jowai", "Nongpoh", "Williamnagar", "Baghmara", "Nongstoin", "Mairang",
                         "Mawkyrwat", "Resubelpara", "Mawphlang", "Sohra", "Mawkyrwat", "Nongkrem", "Mawryngkneng",
                         "Mawshynrut", "Mawkyrwat", "Mawphlang", "Mawryngkneng", "Mawshynrut"],
            
            "Mizoram": ["Aizawl", "Lunglei", "Saiha", "Champhai", "Kolasib", "Serchhip", "Lawngtlai", "Mamit",
                       "Saitual", "Khawzawl", "Hnahthial", "Siaha", "Thenzawl", "Bilkhawthlir", "Darlawn",
                       "Tlabung", "Vairengte", "Zawlnuam", "Phullen", "Saitual"],
            
            "Nagaland": ["Kohima", "Dimapur", "Mokokchung", "Tuensang", "Wokha", "Zunheboto", "Phek", "Kiphire",
                        "Longleng", "Peren", "Mon", "Noklak", "Tseminyu", "Bhandari", "Tuli", "Meluri",
                        "Pfutsero", "Chozuba", "Jalukie", "Tizit"],
            
            "Odisha": ["Bhubaneswar", "Cuttack", "Rourkela", "Brahmapur", "Sambalpur", "Puri", "Balasore", "Bhadrak",
                      "Baripada", "Jharsuguda", "Jeypore", "Bargarh", "Paradip", "Rayagada", "Jagatsinghpur",
                      "Kendrapara", "Balangir", "Boudh", "Dhenkanal", "Kendujhar"],
            
            "Punjab": ["Ludhiana", "Amritsar", "Jalandhar", "Patiala", "Bathinda", "Mohali", "Pathankot", "Hoshiarpur",
                      "Moga", "Batala", "Muktsar", "Barnala", "Firozpur", "Kapurthala", "Phagwara", "Abohar",
                      "Malerkotla", "Khanna", "Gobindgarh", "Faridkot"],
            
            "Rajasthan": ["Jaipur", "Jodhpur", "Kota", "Bikaner", "Ajmer", "Udaipur", "Bhilwara", "Alwar", "Bharatpur",
                         "Sri Ganganagar", "Sikar", "Pali", "Tonk", "Hanumangarh", "Beawar", "Kishangarh", "Baran",
                         "Chittorgarh", "Banswara", "Dungarpur"],
            
            "Sikkim": ["Gangtok", "Namchi", "Mangan", "Gyalshing", "Ravangla", "Singtam", "Jorethang", "Rangpo",
                      "Melli", "Geyzing", "Pelling", "Rhenock", "Rongli", "Soreng", "Yuksom", "Lachen", "Lachung",
                      "Zuluk", "Nayabazar", "Temi"],
            
            "Tamil Nadu": ["Chennai", "Coimbatore", "Madurai", "Tiruchirappalli", "Salem", "Tirunelveli", "Tiruppur",
                         "Erode", "Vellore", "Thoothukudi", "Dindigul", "Thanjavur", "Hosur", "Nagercoil", "Kanchipuram",
                         "Karaikudi", "Neyveli", "Cuddalore", "Kumbakonam", "Tiruvannamalai"],
            
            "Telangana": ["Hyderabad", "Warangal", "Nizamabad", "Karimnagar", "Khammam", "Ramagundam", "Mahbubnagar",
                        "Nalgonda", "Adilabad", "Suryapet", "Miryalaguda", "Jagtial", "Siddipet", "Wanaparthy",
                        "Kagaznagar", "Gadwal", "Sircilla", "Koratla", "Mancherial", "Mandamarri"],
            
            "Tripura": ["Agartala", "Udaipur", "Dharmanagar", "Kailasahar", "Belonia", "Khowai", "Teliamura", "Ambassa",
                       "Kumarghat", "Sabroom", "Bishalgarh", "Sonamura", "Kamalpur", "Amarpur", "Melaghar", "Santirbazar",
                       "Jampuijala", "Dumburnagar", "Panisagar", "Karbook"],
            
            "Uttar Pradesh": ["Lucknow", "Kanpur", "Varanasi", "Agra", "Meerut", "Allahabad", "Ghaziabad", "Noida",
                            "Aligarh", "Bareilly", "Moradabad", "Saharanpur", "Gorakhpur", "Faizabad", "Jhansi",
                            "Muzaffarnagar", "Mathura", "Firozabad", "Shahjahanpur", "Rampur"],
            
            "Uttarakhand": ["Dehradun", "Haridwar", "Roorkee", "Haldwani", "Rudrapur", "Kashipur", "Rishikesh", "Ramnagar",
                          "Pithoragarh", "Srinagar", "Kotdwara", "Mussoorie", "Almora", "Nainital", "Haldwani",
                          "Rudrapur", "Kashipur", "Bazpur", "Manglaur", "Laksar"],
            
            "West Bengal": ["Kolkata", "Howrah", "Durgapur", "Asansol", "Siliguri", "Bardhaman", "Malda", "Habra",
                          "Kharagpur", "Shantipur", "Ranaghat", "Haldia", "Raiganj", "Krishnanagar", "Nabadwip",
                          "Medinipur", "Jalpaiguri", "Balurghat", "Basirhat", "Bankura"]
        }
        
        # Add all Indian states
        self.state_input.addItems(self.state_cities.keys())
        
        # City field with dropdown
        self.city_input = QComboBox()
        self.city_input.setStyleSheet("""
            QComboBox {
                padding: 4px;
                border: 1px solid #ced4da;
                border-radius: 6px;
                font-size: 14px;
                color: #495057;
                background-color: white;
                min-width: 250px;
            }
            QComboBox:focus {
                border: 2px solid #2b8a3e;
            }
            QComboBox::drop-down {
                border: none;
                width: 30px;
            }
            QComboBox::down-arrow {
                image: url(images/down-arrow.png);
                width: 12px;
                height: 12px;
            }
        """)
        self.city_input.setToolTip("Select your city from the dropdown\nAvailable cities are based on your selected state")
        
        # Connect state change to update cities
        self.state_input.currentTextChanged.connect(self.update_cities)
        
        # Set current state and city if available
        current_state = self.user_data.get("state", "")
        current_city = self.user_data.get("city", "")
        
        if current_state:
            index = self.state_input.findText(current_state)
            if index >= 0:
                self.state_input.setCurrentIndex(index)
                if current_city:
                    self.update_cities(current_state)
                    city_index = self.city_input.findText(current_city)
                    if city_index >= 0:
                        self.city_input.setCurrentIndex(city_index)
        
        layout.addRow("State:", self.state_input)
        
        # Add spacing after state
        spacer4 = QLabel("")
        spacer4.setFixedHeight(10)
        layout.addRow("", spacer4)
        
        layout.addRow("City:", self.city_input)
        
        # Add buttons
        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(0, 8, 0, 0)
        
        save_button = QPushButton("Save")
        save_button.setCursor(Qt.CursorShape.PointingHandCursor)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setObjectName("cancelButton")
        cancel_button.setCursor(Qt.CursorShape.PointingHandCursor)
        cancel_button.clicked.connect(self.reject)
        
        button_layout.addWidget(save_button)
        button_layout.addWidget(cancel_button)
        
        layout.addRow(button_layout)
        
        save_button.clicked.connect(self.save_profile)
    
    def validate_phone(self, text):
        """Validate phone number format"""
        if not text:
            self.phone_error.setText("")
            return False
        if not text.isdigit():
            self.phone_error.setText("Phone number must contain only digits")
            return False
        if len(text) != 10:
            self.phone_error.setText("Phone number must be 10 digits")
            return False
        self.phone_error.setText("")
        return True
    
    def validate_email(self, text):
        """Validate email format"""
        if not text:
            self.email_error.setText("")
            return False
        if not text.endswith("@gmail.com"):
            self.email_error.setText("Email must end with @gmail.com")
            return False
        self.email_error.setText("")
        return True
    
    def update_cities(self, state):
        """Update the city dropdown based on selected state"""
        self.city_input.clear()
        if state in self.state_cities:
            self.city_input.addItems(self.state_cities[state])
    
    def get_user_data(self):
        return {
            "username": self.username_input.text(),
            "email": self.email_input.text(),
            "phone": self.phone_input.text(),
            "state": self.state_input.currentText(),
            "city": self.city_input.currentText()
        }
    
    def save_profile(self):
        # Validate inputs
        if not self.validate_phone(self.phone_input.text()):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid 10-digit phone number")
            return
            
        if not self.validate_email(self.email_input.text()):
            QMessageBox.warning(self, "Validation Error", "Please enter a valid email ending with @gmail.com")
            return
        
        # Get the updated data from the form
        updated_data = self.get_user_data()
        print(f"Saving profile data: {updated_data}")
        
        # Update the profile in the database
        success, message = self.db_manager.update_user_profile(
            updated_data["username"],
            updated_data["email"],
            updated_data["phone"],
            updated_data["state"],
            updated_data["city"]
        )
        
        if success:
            QMessageBox.information(self, "Success", "Profile updated successfully!")
            self.accept()
        else:
            QMessageBox.critical(self, "Error", message)

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
            
    
    def update_recommendation(self, username, crop_name):
        """Update the recommended crop for a user"""
        try:
            cursor = self.connection.cursor()
            update_query = """
                UPDATE users 
                SET recommendedCrop = %s 
                WHERE username = %s
            """
            cursor.execute(update_query, (crop_name, username))
            self.connection.commit()
            return cursor.rowcount > 0
        except mysql.connector.Error as e:
            print(f"Error updating recommendation: {e}")
            return False
    
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
                city VARCHAR(50),
                recommendedCrop VARCHAR(100)
            )
        ''')
        self.connection.commit()
        cursor.close()
    
    def update_user_profile(self, username, email, phone, state, city):
        try:
            print(f"Attempting to update profile for user: {username}")
            print(f"New data - Email: {email}, Phone: {phone}, State: {state}, City: {city}")
            
            # First check if user exists
            cursor = self.connection.cursor()
            check_query = "SELECT username FROM users WHERE username = %s"
            cursor.execute(check_query, (username,))
            if not cursor.fetchone():
                cursor.close()
                return False, f"User '{username}' does not exist in the database. Please register first."
            
            # If user exists, proceed with update
            update_query = """
                UPDATE users 
                SET email = %s, phone = %s, state = %s, city = %s 
                WHERE username = %s
            """
            cursor.execute(update_query, (email, phone, state, city, username))
            self.connection.commit()
            
            # Check if any rows were affected
            if cursor.rowcount > 0:
                print(f"Successfully updated profile for user: {username}")
                cursor.close()
                return True, "Profile updated successfully"
            else:
                print(f"No changes were made for user: {username}")
                cursor.close()
                return True, "No changes were made to the profile"
                
        except mysql.connector.Error as err:
            print(f"Database error while updating profile: {err}")
            return False, f"Error updating profile: {err}"
        except Exception as e:
            print(f"Unexpected error while updating profile: {e}")
            return False, f"An unexpected error occurred: {e}"
    
    def get_user_data(self, username):
        try:
            print(f"Fetching data for user: {username}")
            cursor = self.connection.cursor(dictionary=True)
            query = "SELECT username, email, phone, state, city, recommendedCrop FROM users WHERE username = %s"
            cursor.execute(query, (username,))
            result = cursor.fetchone()
            cursor.close()
            
            if result:
                print(f"Found user data: {result}")
                return result
            else:
                print(f"No data found for user: {username}")
                return None
                
        except mysql.connector.Error as err:
            print(f"Database error while fetching user data: {err}")
            return None
        except Exception as e:
            print(f"Unexpected error while fetching user data: {e}")
            return None
    
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
        self.user_data = {}
        self.load_user_data()
        self.initUI()
    
    def load_user_data(self):
        print("Loading data for user:", self.username)  # Debug print
        if not self.username:
            return
            
        try:
            db_data = self.db_manager.get_user_data(self.username)
            print("Data from DB:", db_data)  # Debug print
            
            if db_data:
                self.user_data = db_data
            else:
                # Initialize with default values if no data found
                self.user_data = {
                    "username": self.username,
                    "email": "",
                    "phone": "",
                    "state": "",
                    "city": "",
                    "recommendedCrop": ""
                }
        except Exception as e:
            print(f"Error loading user data: {str(e)}")
            self.user_data = {
                "username": self.username,
                "email": "",
                "phone": "",
                "state": "",
                "city": "",
                "recommendedCrop": ""
            }
    
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
        
        user_info = QLabel(f"{self.user_data.get('username', 'Unknown User')}")
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
                    self.close()
                else:
                    QMessageBox.critical(None, "Error", message)
            except Exception as e:
                QMessageBox.critical(None, "Error", f"An unexpected error occurred: {str(e)}")
    
    def logout(self):
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
    window.showMaximized()
    sys.exit(app.exec())
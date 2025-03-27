import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSpacerItem, QSizePolicy, QFrame, QPushButton, QGraphicsDropShadowEffect, QMainWindow
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon, QBrush, QPalette, QResizeEvent, QGuiApplication
import subprocess

class HomeWindow(QMainWindow):
    def __init__(self, username=None):
        super().__init__()
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.setWindowTitle("FieldBuddy Dashboard")
        self.setupWindowSize()
        
        # Store username
        self.username = username
        
        # Load user data
        self.load_user_data()
        
        self.initUI()

    def load_user_data(self):
        self.user_data = {
            "username": self.username if self.username else "USERNAME",
            "email": "",
            "phone": "",
            "state": "",
            "city": ""
        }
        
        # Check if session file exists and load user data
        if os.path.exists("user_session.txt"):
            with open("user_session.txt", "r") as f:
                for line in f:
                    if "=" in line:
                        key, value = line.strip().split("=", 1)
                        if key in self.user_data:
                            self.user_data[key] = value

    def setupWindowSize(self):
        screen = QGuiApplication.primaryScreen()
        screen_geometry = screen.geometry()
        screen_width = screen_geometry.width()
        screen_height = screen_geometry.height()

        window_width = int(screen_width * 0.8)
        window_height = int(screen_height * 0.8)

        x = (screen_width - window_width) // 2
        y = (screen_height - window_height) // 2

        self.setGeometry(x, y, window_width, window_height)

    def initUI(self):
        self.central_widget.setAutoFillBackground(True)
        self.background = QPixmap(r"D:\Project\new\bg.jpg")
        if self.background.isNull():
            print("Error: Background image not found!")
        self.updateBackground()

        self.resize_components()

    def resize_components(self):
        window_width = self.width()
        window_height = self.height()

        width_scale = window_width / 1000
        height_scale = window_height / 600

        logo_size = int(120 * min(width_scale, height_scale))
        user_circle_size = int(60 * min(width_scale, height_scale))
        card_width = int(220 * width_scale)
        card_height = int(130 * height_scale)
        recommendation_card_width = int(400 * width_scale)
        chatbot_circle_size = int(80 * min(width_scale, height_scale))
        font_size = int(24 * min(width_scale, height_scale))

        self.logo_circle = self.createCircleLabel(logo_size, "rgba(255, 255, 255, 0.7)", "#228B22", r"D:\Project\new\leaf.png")
        self.fieldbuddy_label = self.createLabel("FieldBuddy", font_size, "#228B22", bold=True)
        self.user_circle = self.createClickableCircle(user_circle_size, "rgba(255, 255, 255, 0.7)", "#228B22", r"D:\Project\new\profile-png-icon-2.jpg", self.onProfileClicked)
        
        # Display the username from the user data
        self.user_name_label = self.createClickableLabel(self.user_data["username"].upper(), int(10 * min(width_scale, height_scale)), "#228B22", self.onProfileClicked, bold=True)
        
        self.chatbot_circle = self.createClickableCircle(chatbot_circle_size, "rgba(255, 255, 255, 0.7)", "#228B22", r"D:\Project\new\Ai.png", self.onChatbotClicked)

        weather_card = self.createCard("WEATHER", r"D:\Project\new\weather.png", self.onWeatherClicked, card_width, card_height)
        market_price_card = self.createCard("MARKET PRICE", r"D:\Project\new\growth.png", self.onMarketPriceClicked, card_width, card_height)
        crop_details_card = self.createCard("CROP DETAILS", r"D:\Project\new\instructions.png", self.onCropDetailsClicked, card_width, card_height)
        recommendation_card = self.createRecommendationCard("RECOMMENDATION", r"D:\Project\new\main farmer.png", self.onRecommendationClicked, recommendation_card_width, card_height)

        self.setupTopBar()
        self.setupCenterContent(weather_card, market_price_card, crop_details_card, recommendation_card)
        self.setupChatbot()
        self.setupMainLayout()

    def updateBackground(self):
        palette = self.central_widget.palette()
        palette.setBrush(self.central_widget.backgroundRole(), QBrush(self.background.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio)))
        self.central_widget.setPalette(palette)

    def resizeEvent(self, event):
        self.updateBackground()
        self.resize_components()
        super().resizeEvent(event)

    def setupTopBar(self):
        top_left_layout = QHBoxLayout()
        top_left_layout.setSpacing(20)
        top_left_layout.addWidget(self.logo_circle, alignment=Qt.AlignmentFlag.AlignLeft)
        top_left_layout.addWidget(self.fieldbuddy_label, alignment=Qt.AlignmentFlag.AlignLeft)

        user_layout = QVBoxLayout()
        user_layout.setSpacing(0)
        user_layout.setContentsMargins(0, 0, 0, 0)
        user_layout.addWidget(self.user_circle, alignment=Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop)
        user_layout.addWidget(self.user_name_label, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.top_layout = QHBoxLayout()
        self.top_layout.setSpacing(20)
        self.top_layout.addLayout(top_left_layout)
        self.top_layout.addStretch()
        self.top_layout.addLayout(user_layout)

    def setupCenterContent(self, weather_card, market_price_card, crop_details_card, recommendation_card):
        recommendation_layout = QHBoxLayout()
        recommendation_layout.addStretch()
        recommendation_layout.addWidget(recommendation_card)
        recommendation_layout.addStretch()

        bottom_cards_layout = QHBoxLayout()
        bottom_cards_layout.setSpacing(20)
        bottom_cards_layout.addWidget(weather_card)
        bottom_cards_layout.addWidget(market_price_card)
        bottom_cards_layout.addWidget(crop_details_card)

        self.center_layout = QVBoxLayout()
        self.center_layout.setSpacing(30)
        self.center_layout.addLayout(recommendation_layout)
        self.center_layout.addLayout(bottom_cards_layout)

    def setupChatbot(self):
        self.chatbot_layout = QHBoxLayout()
        self.chatbot_layout.addStretch()
        self.chatbot_layout.addWidget(self.chatbot_circle)

    def setupMainLayout(self):
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        main_layout.addLayout(self.top_layout)
        main_layout.addLayout(self.center_layout)
        main_layout.addSpacerItem(QSpacerItem(20, 40, QSizePolicy.Policy.Minimum, QSizePolicy.Policy.Expanding))
        main_layout.addLayout(self.chatbot_layout)

        self.central_widget.setLayout(main_layout)

    def createCircleLabel(self, size, bg_color, border_color, image_path):
        label = QLabel()
        label.setFixedSize(size, size)
        label.setStyleSheet(f"""
            background-color: {bg_color};
            border: 2px solid {border_color};
            border-radius: {size // 2}px;
            padding: 5px;
        """)
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Error: Unable to load image from {image_path}")
        else:
            label.setPixmap(pixmap.scaled(size - 10, size - 10, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def createLabel(self, text, font_size, color, bold=False):
        label = QLabel(text)
        label.setFont(QFont("Bebas Neue Semi Rounded", font_size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        label.setStyleSheet(f"color: {color}; padding: 5px;")
        return label

    def createClickableLabel(self, text, font_size, color, callback, bold=False):
        button = QPushButton(text)
        button.setFont(QFont("Bebas Neue Semi Rounded", font_size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        button.setStyleSheet(f"""
            color: {color};
            background: rgba(255, 255, 255, 0.7);
            border: none;
            padding: 5px;
            margin: 0;
        """)
        button.clicked.connect(callback)
        return button

    def createClickableCircle(self, size, bg_color, border_color, image_path, callback):
        button = QPushButton()
        button.setFixedSize(size, size)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: {size // 2}px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: rgba(211, 232, 195, 0.7);
            }}
        """)
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Error: Unable to load image from {image_path}")
        else:
            button.setIcon(QIcon(pixmap))
            button.setIconSize(QSize(size - 10, size - 10))
        button.clicked.connect(callback)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(Qt.GlobalColor.gray)
        shadow.setOffset(3, 3)
        button.setGraphicsEffect(shadow)

        return button

    def createCard(self, text, icon_path, callback, width=220, height=130):
        button = QPushButton()
        button.setFixedSize(width, height)
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.7);
                border: 2px solid #228B22;
                border-radius: 15px;
                padding: 10px;
            }
            QPushButton:hover {
                background-color: rgba(211, 232, 195, 0.7);
            }
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(Qt.GlobalColor.gray)
        shadow.setOffset(3, 3)
        button.setGraphicsEffect(shadow)

        icon_label = QLabel(button)
        pixmap = QPixmap(icon_path)
        if pixmap.isNull():
            print(f"Error: Unable to load image from {icon_path}")
        else:
            icon_label.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        text_label = QLabel(text, button)
        text_label.setFont(QFont("Bebas Neue Semi Rounded", 12, QFont.Weight.Bold))
        text_label.setStyleSheet("color: #228B22; padding: 5px; background-color: transparent;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QVBoxLayout(button)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        button.clicked.connect(callback)
        return button

    def createRecommendationCard(self, text, image_path, callback, width=400, height=130):
        button = QPushButton()
        button.setFixedSize(width, height)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.7);
                border: 2px solid #228B22;
                border-radius: 15px;
                padding: 10px;
            }}
            QPushButton:hover {{
                background-color: rgba(211, 232, 195, 0.7);
            }}
        """)

        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(Qt.GlobalColor.gray)
        shadow.setOffset(3, 3)
        button.setGraphicsEffect(shadow)

        image_label = QLabel(button)
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Error: Unable to load image from {image_path}")
        else:
            image_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        image_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        text_label = QLabel(text, button)
        text_label.setFont(QFont("Bebas Neue Semi Rounded", 12, QFont.Weight.Bold))
        text_label.setStyleSheet("color: #228B22; padding: 5px; background-color: transparent;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        layout = QHBoxLayout(button)
        layout.addWidget(image_label)
        layout.addWidget(text_label)

        button.clicked.connect(callback)
        return button

    def onProfileClicked(self):
        # Launch profile menu dropdown with the current username
        subprocess.Popen([sys.executable, "profile_dropdown.py", self.user_data["username"]])

    def onRecommendationClicked(self):
        print("Recommendation clicked!")

    def onWeatherClicked(self):
        print("Weather clicked!")

    def onMarketPriceClicked(self):
        print("Market Price clicked!")

    def onCropDetailsClicked(self):
        print("Crop Details clicked!")

    def onChatbotClicked(self):
        print("Chatbot clicked!")

# For compatibility with login2.py
class FieldBuddyDashboard(HomeWindow):
    def __init__(self, username=None):
        super().__init__(username)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Get username from command line if provided
    username = None
    if len(sys.argv) > 1:
        username = sys.argv[1]
        
    window = HomeWindow(username)
    window.show()
    sys.exit(app.exec())
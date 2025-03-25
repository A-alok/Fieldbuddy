import sys
from PyQt6.QtWidgets import (
    QApplication, QWidget, QLabel, QVBoxLayout, QHBoxLayout,
    QSpacerItem, QSizePolicy, QFrame, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QPixmap, QIcon, QBrush, QPalette

class FieldBuddyDashboard(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("FieldBuddy Dashboard")
        self.setGeometry(100, 100, 1000, 600)
        self.initUI()

    def initUI(self):
        # Set background image for the entire dashboard
        self.setAutoFillBackground(True)
        self.background = QPixmap(r"D:\Project\new\bg.jpg")  # Use raw string for path
        if self.background.isNull():
            print("Error: Background image not found!")
        self.updateBackground()

        self.setupTopBar()
        self.setupCenterContent()
        self.setupChatbot()
        self.setupMainLayout()

    def updateBackground(self):
        """Update the background image to fit the current window size."""
        palette = self.palette()
        palette.setBrush(self.backgroundRole(), QBrush(self.background.scaled(self.size(), Qt.AspectRatioMode.IgnoreAspectRatio)))
        self.setPalette(palette)

    def resizeEvent(self, event):
        """Override resizeEvent to update the background image when the window is resized."""
        self.updateBackground()
        super().resizeEvent(event)

    def setupTopBar(self):
        # Logo and FieldBuddy text
        self.logo_circle = self.createCircleLabel(120, "rgba(255, 255, 255, 0.7)", "#228B22", r"D:\Project\new\leaf.png")  # Semi-transparent background
        self.fieldbuddy_label = self.createLabel("FieldBuddy", 24, "#228B22", bold=True)

        # User circle and username (clickable)
        self.user_circle = self.createClickableCircle(60, "rgba(255, 255, 255, 0.7)", "#228B22", r"D:\Project\new\profile-png-icon-2.jpg", self.onProfileClicked)  # Semi-transparent background
        self.user_name_label = self.createClickableLabel("USERNAME", 10, "#228B22", self.onProfileClicked, bold=True)

        # Layouts
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

    def setupCenterContent(self):
        # Recommendation card (clickable)
        recommendation_card = self.createRecommendationCard("RECOMMENDATION", r"D:\Project\new\main farmer.png", self.onRecommendationClicked)

        # Other cards (clickable)
        weather_card = self.createCard("WEATHER", r"D:\Project\new\weather.png", self.onWeatherClicked)  # Add weather icon
        market_price_card = self.createCard("MARKET PRICE", r"D:\Project\new\growth.png", self.onMarketPriceClicked)  # Add market icon
        crop_details_card = self.createCard("CROP DETAILS", r"D:\Project\new\instructions.png", self.onCropDetailsClicked)  # Add crop icon

        # Layout for the recommendation card (centered)
        recommendation_layout = QHBoxLayout()
        recommendation_layout.addStretch()
        recommendation_layout.addWidget(recommendation_card)
        recommendation_layout.addStretch()

        # Layout for the bottom cards (Market Price, Crop Details, Weather)
        bottom_cards_layout = QHBoxLayout()
        bottom_cards_layout.setSpacing(20)
        bottom_cards_layout.addWidget(weather_card)
        bottom_cards_layout.addWidget(market_price_card)
        bottom_cards_layout.addWidget(crop_details_card)

        # Main center layout
        self.center_layout = QVBoxLayout()
        self.center_layout.setSpacing(30)
        self.center_layout.addLayout(recommendation_layout)  # Add recommendation card
        self.center_layout.addLayout(bottom_cards_layout)  # Add bottom cards

    def setupChatbot(self):
        # Chatbot circle (clickable)
        self.chatbot_circle = self.createClickableCircle(80, "rgba(255, 255, 255, 0.7)", "#228B22", r"D:\Project\new\Ai.png", self.onChatbotClicked)  # Semi-transparent background

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

        self.setLayout(main_layout)

    def createCircleLabel(self, size, bg_color, border_color, image_path):
        label = QLabel()
        label.setFixedSize(size, size)
        label.setStyleSheet(f"""
            background-color: {bg_color};
            border: 2px solid {border_color};
            border-radius: {size // 2}px;
            padding: 5px;  /* Add padding */
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
        label.setFont(QFont("Arial", font_size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        label.setStyleSheet(f"color: {color}; padding: 5px; background-color: rgba(255, 255, 255, 0.7);")  # Semi-transparent background
        return label

    def createClickableLabel(self, text, font_size, color, callback, bold=False):
        button = QPushButton(text)
        button.setFont(QFont("Arial", font_size, QFont.Weight.Bold if bold else QFont.Weight.Normal))
        button.setStyleSheet(f"""
            color: {color};
            background: rgba(255, 255, 255, 0.7);  /* Semi-transparent background */
            border: none;
            padding: 5px;  /* Add padding */
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
                padding: 5px;  /* Add padding */
            }}
            QPushButton:hover {{
                background-color: rgba(211, 232, 195, 0.7); /* Lighter green on hover */
            }}
        """)
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Error: Unable to load image from {image_path}")
        else:
            button.setIcon(QIcon(pixmap))
            button.setIconSize(QSize(size - 10, size - 10))  # Use QSize directly
        button.clicked.connect(callback)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(Qt.GlobalColor.gray)
        shadow.setOffset(3, 3)
        button.setGraphicsEffect(shadow)

        return button

    def createCard(self, text, icon_path, callback):
        button = QPushButton()
        button.setFixedSize(220, 130)
        button.setStyleSheet("""
            QPushButton {
                background-color: rgba(255, 255, 255, 0.7);  /* Semi-transparent background */
                border: 2px solid #228B22;
                border-radius: 15px;
                padding: 10px;  /* Add padding */
            }
            QPushButton:hover {
                background-color: rgba(211, 232, 195, 0.7); /* Lighter green on hover */
            }
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(Qt.GlobalColor.gray)
        shadow.setOffset(3, 3)
        button.setGraphicsEffect(shadow)

        # Add icon above the text
        icon_label = QLabel(button)
        pixmap = QPixmap(icon_path)
        if pixmap.isNull():
            print(f"Error: Unable to load image from {icon_path}")
        else:
            icon_label.setPixmap(pixmap.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Add text
        text_label = QLabel(text, button)
        text_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        text_label.setStyleSheet("color: #228B22; padding: 5px; background-color: transparent;")  # Transparent background
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout for icon and text
        layout = QVBoxLayout(button)
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label, alignment=Qt.AlignmentFlag.AlignCenter)

        button.clicked.connect(callback)
        return button

    def createRecommendationCard(self, text, image_path, callback):
        button = QPushButton()
        button.setFixedSize(400, 130)
        button.setStyleSheet(f"""
            QPushButton {{
                background-color: rgba(255, 255, 255, 0.7);  /* Semi-transparent background */
                border: 2px solid #228B22;
                border-radius: 15px;
                padding: 10px;  /* Add padding */
            }}
            QPushButton:hover {{
                background-color: rgba(211, 232, 195, 0.7); /* Lighter green on hover */
            }}
        """)

        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(Qt.GlobalColor.gray)
        shadow.setOffset(3, 3)
        button.setGraphicsEffect(shadow)

        # Add image on the left
        image_label = QLabel(button)
        pixmap = QPixmap(image_path)
        if pixmap.isNull():
            print(f"Error: Unable to load image from {image_path}")
        else:
            image_label.setPixmap(pixmap.scaled(100, 100, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation))
        image_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)

        # Add text on the right
        text_label = QLabel(text, button)
        text_label.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        text_label.setStyleSheet("color: #228B22; padding: 5px; background-color: transparent;")  # Transparent background
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)

        # Layout for image and text
        layout = QHBoxLayout(button)
        layout.addWidget(image_label)
        layout.addWidget(text_label)

        button.clicked.connect(callback)
        return button

    # Click event handlers
    def onProfileClicked(self):
        print("Profile clicked!")

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

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = FieldBuddyDashboard()
    window.show()
    sys.exit(app.exec())
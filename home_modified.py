import sys
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QMessageBox,
    QHBoxLayout, QLabel, QPushButton, QGraphicsDropShadowEffect
)
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QBrush
from PyQt6.QtCore import Qt, QSize, QRect
from PyQt6.QtGui import QGuiApplication

class HomeWindow(QMainWindow):
    def __init__(self, username=None):
        super().__init__()
        self.username = username
        self.user_data = self.initialize_user_data()
        self.setup_ui()

    def initialize_user_data(self):
        """Initialize user data with default values"""
        return {
            "username": self.username if self.username else "GUEST",
            "email": "",
            "phone": "",
            "state": "",
            "city": "",
            "recommendedCrop": ""
        }

    def load_user_data(self):
        """Load user data from database"""
        if not self.username:
            return
            
        try:
            from profile_dropdown import DatabaseManager
            db_manager = DatabaseManager()
            db_data = db_manager.get_user_data(self.username)
            
            if db_data:
                # Update only existing fields to preserve defaults
                for key, value in db_data.items():
                    if key in self.user_data:
                        self.user_data[key] = value
                print(f"Loaded user data: {self.user_data}")  # Debug print
            db_manager.close()
        except Exception as e:
            print(f"Error loading user data: {str(e)}")
            QMessageBox.warning(self, "Database Error", 
                              "Could not load user data. Using default values.")

    def setup_ui(self):
        """Setup the main user interface"""
        self.setWindowTitle("FieldBuddy Dashboard")
        self.setWindowIcon(QIcon("images/FieldBuddyLOGO.png"))
        
        # Set initial window size (90% of screen)
        screen = QGuiApplication.primaryScreen().availableGeometry()
        self.setGeometry(
            int(screen.width() * 0.05), 
            int(screen.height() * 0.05),
            int(screen.width() * 0.9),
            int(screen.height() * 0.9)
        )
        
        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.setup_background()
        self.create_ui_components()
        self.setup_layouts()

    def setup_background(self):
        """Set the background image"""
        self.central_widget.setAutoFillBackground(True)
        palette = self.central_widget.palette()
        
        bg = QPixmap(r"E:\Project\new\bg.jpg")
        if not bg.isNull():
            palette.setBrush(
                QPalette.ColorRole.Window,
                QBrush(bg.scaled(
                    self.size(),
                    Qt.AspectRatioMode.IgnoreAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            )
            self.central_widget.setPalette(palette)

    def create_ui_components(self):
        """Create all UI components with proper scaling"""
        window_width = self.width()
        window_height = self.height()
        scale_factor = min(window_width/1000, window_height/600)

        # Logo and title
        self.logo = self.create_circle_label(
            int(120 * scale_factor),
            "rgba(255,255,255,0.7)",
            "#228B22",
            "images/FieldBuddyLOGO.png"
        )
        
        self.title_label = self.create_label(
            "FieldBuddy",
            int(24 * scale_factor),
            "#228B22",
            bold=True
        )

        # User profile section
        self.profile_btn = self.create_circle_button(
            int(60 * scale_factor),
            "rgba(255,255,255,0.7)",
            "#228B22",
            r"E:\Project\new\profile-png-icon-2.jpg",
            self.on_profile_clicked
        )
        
        self.username_label = self.create_clickable_label(
            self.user_data["username"].upper(),
            int(14 * scale_factor),
            "#228B22",
            self.on_profile_clicked
        )

        # Feature cards
        card_width = int(220 * (window_width/1000))
        card_height = int(130 * (window_height/600))
        
        self.weather_card = self.create_card(
            "WEATHER",
            r"E:\Project\new\weather.png",
            self.on_weather_clicked,
            card_width,
            card_height
        )
        
        self.market_card = self.create_card(
            "MARKET PRICE",
            r"E:\Project\new\growth.png",
            self.on_market_clicked,
            card_width,
            card_height
        )
        
        self.crop_card = self.create_card(
            "CROP DETAILS",
            r"E:\Project\new\instructions.png",
            self.on_crop_clicked,
            card_width,
            card_height
        )

        # Recommendation card
        rec_width = int(400 * (window_width/1000))
        rec_text = "GET RECOMMENDATION"
        if self.user_data.get("recommendedCrop") and self.user_data["recommendedCrop"] != "ADVEN":
            rec_text += f"\nLast: {self.user_data['recommendedCrop']}"
            
        self.recommendation_card = self.create_recommendation_card(
            rec_text,
            r"E:\Project\new\main farmer.png",
            self.on_recommendation_clicked,
            rec_width,
            card_height
        )

        # Chatbot button
        self.chatbot_btn = self.create_circle_button(
            int(80 * scale_factor),
            "rgba(255,255,255,0.7)",
            "#228B22",
            r"E:\Project\new\Ai.png",
            self.on_chatbot_clicked
        )

    def setup_layouts(self):
        """Setup all layout managers"""
        main_layout = QVBoxLayout(self.central_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Top bar layout
        top_layout = QHBoxLayout()
        top_layout.addWidget(self.logo)
        top_layout.addWidget(self.title_label)
        top_layout.addStretch()
        
        user_layout = QVBoxLayout()
        user_layout.addWidget(self.profile_btn, 0, Qt.AlignmentFlag.AlignHCenter)
        user_layout.addWidget(self.username_label, 0, Qt.AlignmentFlag.AlignHCenter)
        top_layout.addLayout(user_layout)
        
        main_layout.addLayout(top_layout)

        # Center content layout
        center_layout = QVBoxLayout()
        
        # Recommendation card centered
        rec_layout = QHBoxLayout()
        rec_layout.addStretch()
        rec_layout.addWidget(self.recommendation_card)
        rec_layout.addStretch()
        center_layout.addLayout(rec_layout)

        # Other cards in row
        cards_layout = QHBoxLayout()
        cards_layout.addWidget(self.weather_card)
        cards_layout.addWidget(self.market_card)
        cards_layout.addWidget(self.crop_card)
        center_layout.addLayout(cards_layout)
        
        main_layout.addLayout(center_layout)
        main_layout.addStretch()

        # Chatbot button at bottom right
        chatbot_layout = QHBoxLayout()
        chatbot_layout.addStretch()
        chatbot_layout.addWidget(self.chatbot_btn)
        main_layout.addLayout(chatbot_layout)

    # UI Component Creation Methods
    def create_circle_label(self, size, bg_color, border_color, image_path):
        """Create a circular label with image"""
        label = QLabel()
        label.setFixedSize(size, size)
        label.setStyleSheet(f"""
            background-color: {bg_color};
            border: 2px solid {border_color};
            border-radius: {size//2}px;
            padding: 5px;
        """)
        
        # Try to load the image
        try:
            print(f"Attempting to load image from: {image_path}")  # Debug print
            pixmap = QPixmap(image_path)
            if not pixmap.isNull():
                print("Image loaded successfully")  # Debug print
                label.setPixmap(pixmap.scaled(
                    size-10, size-10,
                    Qt.AspectRatioMode.KeepAspectRatio,
                    Qt.TransformationMode.SmoothTransformation
                ))
            else:
                print("Failed to load image - pixmap is null")  # Debug print
                # If image loading fails, show text instead
                label.setText("FB")
                label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                label.setFont(QFont("Arial", int(size/3), QFont.Weight.Bold))
        except Exception as e:
            print(f"Error loading image: {str(e)}")  # Debug print
            # Show text as fallback
            label.setText("FB")
            label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            label.setFont(QFont("Arial", int(size/3), QFont.Weight.Bold))
        
        return label

    def create_label(self, text, font_size, color, bold=False):
        """Create a styled text label"""
        label = QLabel(text)
        label.setFont(QFont("Bebas Neue Semi Rounded", font_size, 
                          QFont.Weight.Bold if bold else QFont.Weight.Normal))
        label.setStyleSheet(f"color: {color}; padding: 5px;")
        return label

    def create_clickable_label(self, text, font_size, color, callback, bold=False):
        """Create a clickable text label"""
        btn = QPushButton(text)
        btn.setFont(QFont("Bebas Neue Semi Rounded", font_size, 
                         QFont.Weight.Bold if bold else QFont.Weight.Normal))
        btn.setStyleSheet(f"""
            color: {color};
            background: transparent;
            border: none;
            padding: 0;
            text-decoration: underline;
        """)
        btn.clicked.connect(callback)
        return btn

    def create_circle_button(self, size, bg_color, border_color, image_path, callback):
        """Create a circular button with image"""
        btn = QPushButton()
        btn.setFixedSize(size, size)
        btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {bg_color};
                border: 2px solid {border_color};
                border-radius: {size//2}px;
                padding: 5px;
            }}
            QPushButton:hover {{
                background-color: rgba(211, 232, 195, 0.7);
            }}
        """)
        
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            btn.setIcon(QIcon(pixmap))
            btn.setIconSize(QSize(size-10, size-10))
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(Qt.GlobalColor.gray)
        shadow.setOffset(3, 3)
        btn.setGraphicsEffect(shadow)
        
        btn.clicked.connect(callback)
        return btn

    def create_card(self, title, icon_path, callback, width=220, height=130):
        """Create a feature card with icon and title"""
        btn = QPushButton()
        btn.setFixedSize(width, height)
        btn.setStyleSheet("""
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
        btn.setGraphicsEffect(shadow)

        # Card content layout
        layout = QVBoxLayout(btn)
        
        # Icon
        icon = QLabel()
        pixmap = QPixmap(icon_path)
        if not pixmap.isNull():
            icon.setPixmap(pixmap.scaled(
                50, 50,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon)

        # Title
        title_label = QLabel(title)
        title_label.setFont(QFont("Bebas Neue Semi Rounded", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #228B22;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label)

        btn.clicked.connect(callback)
        return btn

    def create_recommendation_card(self, text, image_path, callback, width=400, height=130):
        """Create the recommendation card with image and text"""
        btn = QPushButton()
        btn.setFixedSize(width, height)
        btn.setStyleSheet("""
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
        btn.setGraphicsEffect(shadow)

        # Card content layout
        layout = QHBoxLayout(btn)
        
        # Image
        image = QLabel()
        pixmap = QPixmap(image_path)
        if not pixmap.isNull():
            image.setPixmap(pixmap.scaled(
                100, 100,
                Qt.AspectRatioMode.KeepAspectRatio,
                Qt.TransformationMode.SmoothTransformation
            ))
        image.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        layout.addWidget(image)

        # Text
        text_label = QLabel(text)
        text_label.setFont(QFont("Bebas Neue Semi Rounded", 12, QFont.Weight.Bold))
        text_label.setStyleSheet("color: #228B22;")
        text_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(text_label)

        btn.clicked.connect(callback)
        return btn

    # Event Handlers
    def on_profile_clicked(self):
        """Handle profile button click"""
        from profile_dropdown import ProfileMenu
        self.profile_menu = ProfileMenu(self.username, self)
        self.profile_menu.show()

    def on_recommendation_clicked(self):
        """Handle recommendation card click"""
        from Recommend import CropRecommendationApp
        self.recommendation_window = CropRecommendationApp(self.username)
        self.recommendation_window.destroyed.connect(self.refresh_ui)
        self.recommendation_window.showMaximized()

    def on_weather_clicked(self):
        """Handle weather card click"""
        from weather import MainWindow
        self.weather_window = MainWindow()
        self.weather_window.showMaximized()

    def on_market_clicked(self):
        """Handle market price card click"""
        from marketPrice import MarketPriceWindow
        self.market_window = MarketPriceWindow()
        self.market_window.showMaximized()

    def on_crop_clicked(self):
        """Handle crop details card click with proper data validation"""
        # Refresh data from database first
        self.load_user_data()
        
        # Get and clean the recommended crop value
        recommended_crop = str(self.user_data.get("recommendedCrop", "")).strip()
        
        # Debug prints (remove after testing)
        print(f"User: {self.username}, Recommended crop: '{recommended_crop}'")
        
        # Check if we have a valid recommendation
        if recommended_crop and recommended_crop.upper() != "ADVEN":
            try:
                from detail import CropRecommendationResult
                
                # Verify recommended_crop exists and has a value
                if 'recommended_crop' not in locals() and 'recommended_crop' not in globals():
                    raise ValueError("recommended_crop is not defined")
                
                print(f"Attempting to open crop details for: {recommended_crop}")
                
                self.crop_window = CropRecommendationResult(
                    crop_name=recommended_crop
                )
                self.crop_window.showMaximized()
                
            except ImportError as ie:
                print(f"Import failed: {ie}")
                QMessageBox.warning(self, "Error", "Could not find crop details module.")
                
            except NameError as ne:
                print(f"Variable not found: {ne}")
                QMessageBox.warning(self, "Error", "Crop recommendation data is missing.")
                
            except Exception as e:
                print(f"Unexpected error: {e}")
                QMessageBox.warning(self, "Error", "Could not open crop details window.")
        else:
            QMessageBox.information(
                self, 
                "No Recommendation",
                "You don't have any crop recommendations yet.\n"
                "Please get a recommendation first."
            )
            # Optional: Open recommendation window automatically
            # self.on_recommendation_clicked()

    def on_chatbot_clicked(self):
        """Handle chatbot button click"""
        from Chatbot import ChatbotApp
        self.chatbot = ChatbotApp(self.user_data)
        self.chatbot.showMaximized()

    def refresh_ui(self):
        """Refresh the UI after returning from recommendation"""
        self.load_user_data()
        self.create_ui_components()
        self.setup_layouts()

    def resizeEvent(self, event):
        """Handle window resize events"""
        self.setup_background()
        self.create_ui_components()
        self.setup_layouts()
        super().resizeEvent(event)

class FieldBuddyDashboard(HomeWindow):
    """Compatibility class for login system"""
    def __init__(self, username=None):
        super().__init__(username)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    
    # Get username from command line if provided
    username = sys.argv[1] if len(sys.argv) > 1 else None
    
    window = HomeWindow(username)
    window.showMaximized()
    sys.exit(app.exec())
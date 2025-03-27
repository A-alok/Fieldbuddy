import sys
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QLabel, QPushButton,
    QComboBox, QHBoxLayout, QVBoxLayout, QScrollArea, QFrame, 
    QMessageBox, QGridLayout, QLineEdit, QSizePolicy
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QFont, QLinearGradient, QColor, QPainter, QPixmap, QPalette
import requests
from datetime import datetime, timedelta
import pytz
import math
import numpy as np
import re

# List of major Indian cities with coordinates
INDIAN_CITIES = [
    ('Mumbai', 19.0760, 72.8777),
    ('Delhi', 28.7041, 77.1025),
    ('Bangalore', 12.9716, 77.5946),
    ('Kolkata', 22.5726, 88.3639),
    ('Chennai', 13.0827, 80.2707),
    ('Hyderabad', 17.3850, 78.4867),
    ('Pune', 18.5204, 73.8567)
]

class WeatherContentWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.parent_window = parent
        self.unit = '°C'
        self.weather_data = None
        self.forecast_data = None
        self.api_key = "8bd9b52bf43178e87f744a1d2dd2745f"
        self.current_city = INDIAN_CITIES[0]
        self.current_text_color = QColor(Qt.GlobalColor.black)
        self.init_ui()
        self.update_weather()

    def init_ui(self):
        self.setStyleSheet("""
            QWidget {
                background: rgba(255, 255, 255, 0.1);
                color: black;
                border-radius: 15px;
            }
            QPushButton {
                background: rgba(0, 100, 0, 0.6);
                border-radius: 10px;
                padding: 8px;
                color: white;
                font-size: 14px;
            }
            QComboBox {
                background: white;
                border-radius: 5px;
                padding: 8px;
                color: black;
                font-size: 14px;
            }
            QComboBox QAbstractItemView {
                background: white;
                border-radius: 5px;
                color: black;
            }
            QLineEdit {
                background: rgba(255, 255, 255, 0.8);
                border-radius: 5px;
                padding: 8px;
                color: black;
                font-size: 14px;
            }
            QScrollArea {
                border: none;
                background: transparent;
            }
            QFrame {
                background: rgba(255, 255, 255, 0.2);
                border-radius: 10px;
                padding: 10px;
            }
        """)

        # Font configurations with dynamic sizing
        self.base_width = 1200
        self.title_font = QFont('Arial', 16, QFont.Weight.Bold)
        self.temp_font = QFont('Arial', 56, QFont.Weight.Bold)
        self.section_font = QFont('Arial', 12, QFont.Weight.Bold)
        self.detail_font = QFont('Arial', 12)

        # Main scroll area for responsiveness
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        # Main container widget
        container = QWidget()
        scroll_area.setWidget(container)
        
        # Main layout for the container
        main_layout = QVBoxLayout(container)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header Section with Back Button
        header = QHBoxLayout()
        
        # Back Button
        self.back_btn = QPushButton("← Back")
        self.back_btn.setFont(QFont("Segoe UI", 10))
        self.back_btn.setFixedSize(80, 30)
        self.back_btn.setStyleSheet("""
            QPushButton {
                background-color: #2b8a3e;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
            }
            QPushButton:hover {
                background-color: #2f9e44;
            }
            QPushButton:pressed {
                background-color: #248232;
            }
        """)
        self.back_btn.setToolTip("Go back to previous screen")
        self.back_btn.clicked.connect(self.go_back)
        header.addWidget(self.back_btn)

        # City selection widgets
        self.city_combo = QComboBox()
        self.city_combo.addItems([city[0] for city in INDIAN_CITIES])
        self.city_combo.setFont(self.detail_font)
        self.city_combo.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        self.city_input = QLineEdit()
        self.city_input.setPlaceholderText("Enter any city name")
        self.city_input.setFont(self.detail_font)
        self.city_input.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        
        city_selection_layout = QHBoxLayout()
        city_selection_layout.addWidget(QLabel("City:"), stretch=0)
        city_selection_layout.addWidget(self.city_combo, stretch=2)
        city_selection_layout.addWidget(QLabel("OR"), stretch=0)
        city_selection_layout.addWidget(self.city_input, stretch=2)
        city_selection_layout.setSpacing(10)

        # Unit selection
        self.unit_combo = QComboBox()
        self.unit_combo.addItems(["°C", "°F"])
        self.unit_combo.setFont(self.detail_font)
        self.unit_combo.setFixedWidth(100)

        # Refresh button
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.setFont(self.detail_font)
        self.refresh_btn.setFixedWidth(150)

        # Add remaining header elements
        header.addLayout(city_selection_layout)
        header.addWidget(QLabel("Unit:"), stretch=0)
        header.addWidget(self.unit_combo, stretch=0)
        header.addWidget(self.refresh_btn, stretch=0)
        header.addStretch(1)
        header.setSpacing(15)

        main_layout.addLayout(header)

        # Current weather display
        current_weather_layout = QGridLayout()
        current_weather_layout.setVerticalSpacing(15)
        current_weather_layout.setHorizontalSpacing(30)
        
        # Temperature display
        self.temp_label = QLabel("--")
        self.temp_label.setFont(self.temp_font)
        self.temp_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.temp_label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        
        # Weather parameters with emojis
        self.feels_like_label = QLabel("🌡️ Feels like: --")
        self.high_low_label = QLabel("⬆️/⬇️ High/Low: --/--")
        self.humidity_label = QLabel("💧 Humidity: --%")
        self.wind_label = QLabel("🌬️ Wind: -- m/s")
        self.pressure_label = QLabel("⏲️ Pressure: -- hPa")
        self.visibility_label = QLabel("👁️ Visibility: -- km")
        self.dew_point_label = QLabel("💦 Dew Point: --")
        self.precipitation_label = QLabel("🌧️ Precipitation: -- mm")
        self.clouds_label = QLabel("☁️ Cloud Cover: --%")

        # Set fonts for parameters
        for label in [self.feels_like_label, self.high_low_label, 
                     self.humidity_label, self.wind_label,
                     self.pressure_label, self.visibility_label,
                     self.dew_point_label, self.precipitation_label,
                     self.clouds_label]:
            label.setFont(self.detail_font)
            label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)

        # Grid layout for current weather
        current_weather_layout.addWidget(self.temp_label, 0, 0, 2, 2)
        current_weather_layout.addWidget(self.feels_like_label, 2, 0)
        current_weather_layout.addWidget(self.high_low_label, 2, 1)
        current_weather_layout.addWidget(self.create_section_label("Atmospheric Conditions 🌡️", self.section_font), 3, 0, 1, 2)
        current_weather_layout.addWidget(self.humidity_label, 4, 0)
        current_weather_layout.addWidget(self.dew_point_label, 4, 1)
        current_weather_layout.addWidget(self.pressure_label, 5, 0)
        current_weather_layout.addWidget(self.precipitation_label, 5, 1)
        current_weather_layout.addWidget(self.create_section_label("Wind & Visibility 💨", self.section_font), 6, 0, 1, 2)
        current_weather_layout.addWidget(self.wind_label, 7, 0)
        current_weather_layout.addWidget(self.visibility_label, 7, 1)
        current_weather_layout.addWidget(self.clouds_label, 8, 0)

        main_layout.addLayout(current_weather_layout)

        # Forecast sections
        self.create_forecast_sections(main_layout)

        # Set the scroll area as the main layout
        layout = QVBoxLayout(self)
        layout.addWidget(scroll_area)
        layout.setContentsMargins(0, 0, 0, 0)

        # Connect signals
        self.unit_combo.currentTextChanged.connect(self.change_unit)
        self.refresh_btn.clicked.connect(self.update_weather)
        self.city_combo.currentIndexChanged.connect(self.combo_city_changed)
        self.city_input.editingFinished.connect(self.input_city_changed)

    def create_forecast_sections(self, main_layout):
        """Create the forecast sections with responsive layouts"""
        # Daily forecast section
        daily_section = self.create_section_label("5-Day Forecast 📅", self.section_font)
        main_layout.addWidget(daily_section)
        
        # Scroll area for daily forecast
        daily_scroll = QScrollArea()
        daily_scroll.setWidgetResizable(True)
        daily_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        daily_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        daily_scroll.setFixedHeight(180)
        
        daily_container = QWidget()
        self.daily_layout = QHBoxLayout(daily_container)
        self.daily_layout.setContentsMargins(5, 5, 5, 5)
        self.daily_layout.setSpacing(15)
        
        # Create 7-day forecast containers
        self.daily_frames = []
        for _ in range(7):
            day_frame = QFrame()
            day_frame.setMinimumWidth(150)
            day_frame.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
            
            day_layout = QVBoxLayout(day_frame)
            day_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.daily_frames.append(day_frame)
            self.daily_layout.addWidget(day_frame)
        
        daily_scroll.setWidget(daily_container)
        main_layout.addWidget(daily_scroll)
        main_layout.addSpacing(20)

        # Hourly forecast section
        hourly_section = self.create_section_label("Hourly Forecast ⏳", self.section_font)
        main_layout.addWidget(hourly_section)
        
        # Scroll area for hourly forecast
        hourly_scroll = QScrollArea()
        hourly_scroll.setWidgetResizable(True)
        hourly_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        hourly_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        hourly_scroll.setFixedHeight(150)
        
        hourly_container = QWidget()
        self.hourly_layout = QHBoxLayout(hourly_container)
        self.hourly_layout.setContentsMargins(5, 5, 5, 5)
        self.hourly_layout.setSpacing(15)
        
        # Create 8-hour forecast containers
        self.hourly_frames = []
        for _ in range(8):
            hour_frame = QFrame()
            hour_frame.setMinimumWidth(120)
            hour_frame.setSizePolicy(QSizePolicy.Policy.MinimumExpanding, QSizePolicy.Policy.Expanding)
            
            hour_layout = QVBoxLayout(hour_frame)
            hour_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.hourly_frames.append(hour_frame)
            self.hourly_layout.addWidget(hour_frame)
        
        hourly_scroll.setWidget(hourly_container)
        main_layout.addWidget(hourly_scroll)
        main_layout.addSpacing(20)

        # Graphs section
        graph_section = self.create_section_label("Weather Trends 📈", self.section_font)
        main_layout.addWidget(graph_section)
        
        # Graph container with dynamic sizing
        graph_container = QWidget()
        graph_container.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        graph_layout = QVBoxLayout(graph_container)
        
        self.figure = plt.figure(figsize=(10, 6))
        self.canvas = FigureCanvas(self.figure)
        self.canvas.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        graph_layout.addWidget(self.canvas)
        
        main_layout.addWidget(graph_container)
        main_layout.addStretch(1)

    def create_section_label(self, text, font):
        label = QLabel(text)
        label.setFont(font)
        label.setStyleSheet("color: #004d00; font-weight: bold;")
        label.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        return label

    def resizeEvent(self, event):
        """Handle dynamic resizing of elements"""
        super().resizeEvent(event)
        
        # Adjust font sizes based on window size
        width = self.width()
        
        # Calculate scaling factors with limits
        scale_factor = min(1.5, max(0.8, width / self.base_width))
        
        # Update fonts
        self.title_font.setPointSize(int(16 * scale_factor))
        self.temp_font.setPointSize(int(56 * scale_factor))
        self.section_font.setPointSize(int(12 * scale_factor))
        self.detail_font.setPointSize(int(12 * min(1.2, scale_factor)))
        
        # Update specific elements
        self.temp_label.setFont(self.temp_font)
        
        # Update forecast frame sizes
        day_frame_width = int(150 * scale_factor)
        hour_frame_width = int(120 * scale_factor)
        
        for frame in self.daily_frames:
            frame.setMinimumWidth(day_frame_width)
        
        for frame in self.hourly_frames:
            frame.setMinimumWidth(hour_frame_width)

    def go_back(self):
        """Handle back button click with navigation logic"""
        reply = QMessageBox.question(
            self, 'Confirm',
            'Return to previous screen? Unsaved changes will be lost.',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            if self.parent_window:
                self.parent_window.close()
            else:
                QApplication.instance().quit()

    def get_weather_emoji(self, condition):
        emoji_map = {
            'Clear': '☀️',
            'Clouds': '☁️',
            'Rain': '🌧️',
            'Thunderstorm': '⛈️',
            'Snow': '❄️',
            'Mist': '🌫️',
            'Smoke': '💨',
            'Haze': '🌫️',
            'Dust': '💨',
            'Fog': '🌁'
        }
        return emoji_map.get(condition, '🌤️')

    def combo_city_changed(self, index):
        if index >= 0:
            self.city_input.clear()
            self.current_city = INDIAN_CITIES[index]
            self.update_weather()

    def input_city_changed(self):
        city = self.city_input.text().strip()
        if city:
            self.city_combo.setCurrentIndex(-1)
            self.current_city = city
            self.update_weather()

    def paintEvent(self, event):
        painter = QPainter(self)
        
        if self.weather_data:
            condition = self.weather_data['weather'][0]['main']
            image_path = self.get_weather_image(condition)
            if image_path:
                pixmap = QPixmap(image_path)
                if not pixmap.isNull():
                    self.background_pixmap = pixmap.scaled(
                        self.size(), 
                        Qt.AspectRatioMode.IgnoreAspectRatio,
                        Qt.TransformationMode.SmoothTransformation
                    )
                    painter.drawPixmap(self.rect(), self.background_pixmap)
                    
                    # Get dominant color and determine text color
                    dominant_color = self.get_dominant_color(pixmap)
                    text_color = self.get_text_color(dominant_color)
                    
                    # Calculate luminance for overlay decision
                    r = dominant_color.red() / 255
                    g = dominant_color.green() / 255
                    b = dominant_color.blue() / 255
                    luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
                    
                    # Apply semi-transparent overlay for mid-tone backgrounds
                    if 0.3 < luminance < 0.7:
                        overlay_color = QColor(0, 0, 0, 60) if text_color == QColor(Qt.GlobalColor.white) else QColor(255, 255, 255, 60)
                        painter.fillRect(self.rect(), overlay_color)
                    
                    self.set_text_color(text_color)
                    return
        
        # Fallback gradient
        self.background_pixmap = None
        gradient = QLinearGradient(0, 0, self.width(), self.height())
        gradient.setColorAt(0, QColor(200, 255, 200))
        gradient.setColorAt(1, QColor(150, 200, 150))
        painter.fillRect(self.rect(), gradient)
        self.set_text_color(QColor(Qt.GlobalColor.black))

    def get_weather_image(self, condition):
        weather_images = {
            'Clear': "D:\\Project\\new\zip file weather part\clear sky.jpg",
            'Fog': "D:\\Project\\new\zip file weather part\foggy image.jpg",
            'Dust': "D:\\Project\\new\zip file weather part\dusty image.jpg",
            'Haze': "D:\\Project\\new\zip file weather part\haze images.jpg",
            'Smoke': "D:\\Project\\new\zip file weather part\smoky image.jpg",
            'Mist': "D:\\Project\\new\zip file weather part\misty images.jpg",
            'Snow': "D:\\Project\\new\zip file weather part\snow image.jpg",
            'Thunderstorm': "D:\\Project\\new\\zip file weather part\thunderstrom image.jpg",
            'Rain': "D:\\Project\\new\\zip file weather part\rainy sky images.jpg",
            'Clouds': "D:\\Project\\new\\zip file weather part\cloudy sky.jpg"
        }
        return weather_images.get(condition, None)

    def get_text_color(self, background_color):
        r = background_color.red() / 255
        g = background_color.green() / 255
        b = background_color.blue() / 255
        
        r = r / 12.92 if r <= 0.03928 else ((r + 0.055) / 1.055) ** 2.4
        g = g / 12.92 if g <= 0.03928 else ((g + 0.055) / 1.055) ** 2.4
        b = b / 12.92 if b <= 0.03928 else ((b + 0.055) / 1.055) ** 2.4
        
        luminance = 0.2126 * r + 0.7152 * g + 0.0722 * b
        
        if luminance < 0.5:
            return QColor(Qt.GlobalColor.white)
        else:
            return QColor(Qt.GlobalColor.black)

    def get_dominant_color(self, pixmap):
        return pixmap.toImage().pixelColor(pixmap.width() // 2, pixmap.height() // 2)

    def set_text_color(self, color):
        self.current_text_color = color
        color_name = color.name()
        
        palette = self.palette()
        palette.setColor(QPalette.ColorRole.WindowText, color)
        palette.setColor(QPalette.ColorRole.Text, color)
        palette.setColor(QPalette.ColorRole.ButtonText, color)
        self.setPalette(palette)
        
        text_style = f"color: {color_name};"
        bold_style = f"color: {color_name}; font-weight: bold;"
        
        self.temp_label.setStyleSheet(bold_style)
        
        for label in [
            self.feels_like_label, self.high_low_label, 
            self.humidity_label, self.wind_label,
            self.pressure_label, self.visibility_label,
            self.dew_point_label, self.precipitation_label,
            self.clouds_label
        ]:
            label.setStyleSheet(text_style)
        
        for child in self.findChildren(QLabel):
            if any(section in child.text() for section in [
                "Atmospheric Conditions", "Wind & Visibility", 
                "5-Day Forecast", "Hourly Forecast", "Weather Trends"
            ]):
                child.setStyleSheet(bold_style)
            else:
                current_style = child.styleSheet()
                if "color:" not in current_style:
                    child.setStyleSheet(f"{current_style}; {text_style}")
                else:
                    child.setStyleSheet(re.sub(r"color:\s*[^;]+;", f"color: {color_name};", current_style))
        
        for button in self.findChildren(QPushButton):
            if button != self.back_btn:
                button.setStyleSheet(f"""
                    background: rgba(0, 100, 0, 0.6);
                    border-radius: 10px;
                    padding: 8px;
                    font-size: 14px;
                    color: {color_name};
                """)
        
        for frame in self.findChildren(QFrame):
            if "border-radius: 10px;" in frame.styleSheet():
                frame.setStyleSheet(f"""
                    background: rgba(255, 255, 255, 0.2);
                    border-radius: 10px;
                    padding: 10px;
                """)
                for label in frame.findChildren(QLabel):
                    label.setStyleSheet(text_style)
        
        def update_child_colors(parent):
            for child in parent.children():
                if isinstance(child, QLabel):
                    child.setStyleSheet(text_style)
                elif isinstance(child, QFrame):
                    update_child_colors(child)
        
        if hasattr(self, 'hourly_widget'):
            update_child_colors(self.hourly_widget)
        if hasattr(self, 'daily_widget'):
            update_child_colors(self.daily_widget)

    def change_unit(self, unit):
        self.unit = unit
        self.update_display()
        self.update_hourly_forecast(pytz.timezone('Asia/Kolkata'))
        self.update_daily_forecast(pytz.timezone('Asia/Kolkata'))
        self.update_graphs()

    def update_weather(self):
        try:
            if isinstance(self.current_city, tuple):
                city_name, lat, lon = self.current_city
                timezone = pytz.timezone('Asia/Kolkata')
            else:
                city = self.current_city
                geo_url = f"http://api.openweathermap.org/geo/1.0/direct?q={city},IN&limit=1&appid={self.api_key}"
                geo_response = requests.get(geo_url)
                
                if geo_response.status_code != 200 or not geo_response.json():
                    QMessageBox.critical(self, "Error", "City not found")
                    return
                geo_data = geo_response.json()[0]
                lat = geo_data['lat']
                lon = geo_data['lon']
                timezone = pytz.timezone('Asia/Kolkata')

            weather_url = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&units=metric&appid={self.api_key}"
            forecast_url = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&units=metric&appid={self.api_key}"

            weather_response = requests.get(weather_url)
            forecast_response = requests.get(forecast_url)

            if weather_response.status_code == 200:
                self.weather_data = weather_response.json()
                self.update_display()
                self.update()
            else:
                QMessageBox.critical(self, "Error", weather_response.json().get('message', 'Unknown error'))

            if forecast_response.status_code == 200:
                self.forecast_data = forecast_response.json()
                self.update_hourly_forecast(timezone)
                self.update_daily_forecast(timezone)
                self.update_graphs()
            else:
                QMessageBox.critical(self, "Error", forecast_response.json().get('message', 'Unknown error'))

        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def convert_temp(self, temp):
        return temp * 9/5 + 32 if self.unit == '°F' else temp

    def calculate_dew_point(self, temp, humidity):
        a = 17.625
        b = 243.04
        alpha = math.log(humidity/100) + (a * temp)/(b + temp)
        return (b * alpha) / (a - alpha)

    def update_display(self):
        if self.weather_data:
            try:
                main = self.weather_data['main']
                weather = self.weather_data['weather'][0]
                wind = self.weather_data['wind']
                clouds = self.weather_data['clouds']
                rain = self.weather_data.get('rain', {})
                visibility = self.weather_data.get('visibility', 0)

                temp = self.convert_temp(main['temp'])
                feels_like = self.convert_temp(main['feels_like'])
                temp_max = self.convert_temp(main['temp_max'])
                temp_min = self.convert_temp(main['temp_min'])
                dew_point = self.convert_temp(self.calculate_dew_point(main['temp'], main['humidity']))
                condition_emoji = self.get_weather_emoji(weather['main'])

                self.temp_label.setText(f"{temp:.1f}{self.unit} {condition_emoji}")
                self.feels_like_label.setText(f"🌡️ Feels like: {feels_like:.1f}{self.unit}")
                self.high_low_label.setText(f"⬆️/⬇️ {temp_max:.1f}{self.unit}/{temp_min:.1f}{self.unit}")
                self.humidity_label.setText(f"💧 Humidity: {main['humidity']}%")
                self.wind_label.setText(f"🌬️ Wind: {wind['speed']} m/s, {wind.get('deg', '--')}°")
                self.pressure_label.setText(f"⏲️ Pressure: {main['pressure']} hPa")
                self.visibility_label.setText(f"👁️ Visibility: {visibility/1000:.1f} km" if visibility else "👁️ Visibility: --")
                self.dew_point_label.setText(f"💦 Dew Point: {dew_point:.1f}{self.unit}")
                self.precipitation_label.setText(f"🌧️ Precipitation: {rain.get('1h', 0)} mm")
                self.clouds_label.setText(f"☁️ Cloud Cover: {clouds['all']}%")

            except KeyError as e:
                QMessageBox.critical(self, "Data Error", f"Missing data field: {e}")

    def update_hourly_forecast(self, timezone):
        if not self.forecast_data:
            return
            
        for frame in self.hourly_frames:
            while frame.layout().count() > 0:
                child = frame.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        hourly_items = self.forecast_data['list'][:8]
        
        for i in range(8):
            if i < len(hourly_items):
                item = hourly_items[i]
                dt = datetime.fromtimestamp(item['dt'], tz=timezone)
                temp = self.convert_temp(item['main']['temp'])
                precip = item.get('rain', {}).get('3h', 0)
                condition_emoji = self.get_weather_emoji(item['weather'][0]['main'])
                
                time_label = QLabel(dt.strftime("%I:%M %p"))
                temp_label = QLabel(f"{temp:.1f}{self.unit} {condition_emoji}")
                precip_label = QLabel(f"🌧️ {precip}mm")
                
                for label in [time_label, temp_label, precip_label]:
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setStyleSheet(f"color: {self.current_text_color.name()};")
                
                self.hourly_frames[i].layout().addWidget(time_label)
                self.hourly_frames[i].layout().addWidget(temp_label)
                self.hourly_frames[i].layout().addWidget(precip_label)

    def update_daily_forecast(self, timezone):
        if not self.forecast_data:
            return
            
        for frame in self.daily_frames:
            while frame.layout().count() > 0:
                child = frame.layout().takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
        
        daily_data = {}
        for item in self.forecast_data['list']:
            date = datetime.fromtimestamp(item['dt'], tz=timezone).date()
            if date not in daily_data:
                daily_data[date] = []
            daily_data[date].append(item)
        
        days = sorted(daily_data.keys())[:7]
        
        for i in range(7):
            if i < len(days):
                date = days[i]
                day_data = daily_data[date]
                
                conditions = [entry['weather'][0]['main'] for entry in day_data]
                condition = max(set(conditions), key=conditions.count)
                
                temps = [self.convert_temp(entry['main']['temp']) for entry in day_data]
                max_temp = max(temps)
                min_temp = min(temps)
                
                day_label = QLabel(date.strftime("%a %d %b"))
                temp_label = QLabel(f"⬆️{max_temp:.1f}{self.unit}\n⬇️{min_temp:.1f}{self.unit}")
                condition_label = QLabel(self.get_weather_emoji(condition))
                
                for label in [day_label, temp_label, condition_label]:
                    label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    label.setStyleSheet(f"color: {self.current_text_color.name()};")
                
                self.daily_frames[i].layout().addWidget(day_label)
                self.daily_frames[i].layout().addWidget(condition_label)
                self.daily_frames[i].layout().addWidget(temp_label)

    # ... [previous imports and code remain the same until the update_graphs method] ...

    def update_graphs(self):
        self.figure.clear()
        
        if self.forecast_data:
            try:
                if not self.forecast_data['list']:
                    return
                
                # Create grid spec with adjusted height ratios
                gs = self.figure.add_gridspec(2, 1, height_ratios=[2, 1], hspace=0.5)
                
                # Temperature plot - make it taller
                ax1 = self.figure.add_subplot(gs[0])
                times = [datetime.fromtimestamp(entry['dt']) for entry in self.forecast_data['list'][:24]]
                temps = [self.convert_temp(entry['main']['temp']) for entry in self.forecast_data['list'][:24]]
                
                ax1.plot(times, temps, 'r-', marker='o', markersize=6)
                ax1.set_title('Temperature Trend 🌡️', fontsize=14)
                ax1.set_ylabel(f'Temperature ({self.unit})', fontsize=12)
                ax1.tick_params(axis='both', which='major', labelsize=10)
                ax1.grid(True, alpha=0.3)
                
                # Format x-axis to prevent label overlapping
                from matplotlib.dates import DateFormatter, HourLocator
                date_format = DateFormatter('%H:%M\n%d-%b')
                ax1.xaxis.set_major_formatter(date_format)
                ax1.xaxis.set_major_locator(HourLocator(interval=3))  # Show every 3 hours
                
                # Precipitation plot
                ax2 = self.figure.add_subplot(gs[1])
                
                precip = []
                for entry in self.forecast_data['list'][:24]:
                    if 'rain' in entry:
                        if '3h' in entry['rain']:
                            precip.append(entry['rain']['3h'])
                        else:
                            precip.append(entry['rain'].get('1h', 0))
                    else:
                        precip.append(0)
                
                # Set consistent y-axis limits
                max_precip = max(precip) if precip else 1
                ax2.set_ylim(0, max(5, max_precip * 1.2))  # Add 20% padding
                
                # Use narrower bars with space between them
                bar_width = 0.05  # Reduced from 0.08
                bar_spacing = 0.02
                positions = np.arange(len(times))
                
                bars = ax2.bar(positions, precip, width=bar_width, color='blue', alpha=0.7)
                
                # Add value labels only if they fit
                for i, bar in enumerate(bars):
                    if precip[i] > 0 and max_precip < 10:  # Only label if not too crowded
                        ax2.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.05,
                                f'{precip[i]:.1f}', ha='center', va='bottom', fontsize=8)
                
                ax2.set_title('Precipitation 🌧️', fontsize=14)
                ax2.set_ylabel('Rain (mm)', fontsize=12)
                
                # Set x-axis ticks to match temperature plot
                ax2.set_xticks(positions)
                ax2.set_xticklabels([t.strftime('%H:%M') for t in times], rotation=45, ha='right')
                ax2.tick_params(axis='both', which='major', labelsize=10)
                ax2.grid(True, alpha=0.3)
                
                # Adjust layout to prevent clipping
                self.figure.tight_layout(pad=2.0, h_pad=2.0)
                self.canvas.draw()

            except Exception as e:
                print("Graph error:", e)
                QMessageBox.warning(self, "Graph Warning", f"Could not update graphs: {e}")

# ... [rest of the code remains the same] ...
class WeatherWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("India Weather Dashboard")
        self.setGeometry(100, 100, 1200, 900)
        self.setCentralWidget(WeatherContentWidget(self))
        self.setStyleSheet("background-color: #f0f0f0;")
        
    def showMaximized(self):
        super().showMaximized()
        self.centralWidget().resizeEvent(None)

def run_weather_app():
    app = QApplication(sys.argv)
    window = WeatherWindow()
    window.showMaximized()
    sys.exit(app.exec())

if __name__ == '__main__':
    run_weather_app()
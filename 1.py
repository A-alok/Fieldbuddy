import sys
import csv
import json
import os
import requests
import chardet
import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import LabelEncoder
from pathlib import Path
from file_processor import FileProcessor

from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QLabel, QLineEdit,
    QPushButton, QMessageBox, QGridLayout, QGroupBox, QHBoxLayout,
    QFileDialog
)

from PyQt6.QtGui import QFont, QIcon
from PyQt6.QtCore import QSize, Qt
import ee

# Authenticate your Google account
ee.Authenticate()
# Initialize Google Earth Engine
ee.Initialize(project='ee-galok2812')

# OpenWeather API Key
OPENWEATHER_API_KEY = "127c824b89d5120bc1cc6a65e8337bd3"  # Replace with your valid API key

class CropRecommendationApp(QWidget):
    def __init__(self):
        super().__init__()
        self.init_ui()
        self.setStyleSheet("""
            QWidget {
                background-color: qlineargradient(spread:pad, x1:0, y1:0, x2:1, y2:1, stop:0 #f8f9fa, stop:1 #e6f4ea);
            }
            QGroupBox {
                border: 2px solid #e9ecef;
                border-radius: 8px;
                margin-top: 15px;
                padding-top: 20px;
                background-color: white;   
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #2b8a3e;
                font-weight: bold;
            }
            QLabel {
                color: #343a40;
                font-size: 14px;
            }
            QLineEdit {
                padding: 10px;
                border: 1px solid #ced4da;
                border-radius: 4px;
                font-size: 14px;
                color: rgb(41, 33, 33);
            }
            QLineEdit:focus {
                border: 2px solid #2b8a3e;
            }
            QPushButton {
                background-color: #2b8a3e;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
                min-width: 200px;
            }
            QPushButton:hover {
                background-color: #2f9e44;
            }
            QPushButton:pressed {
                background-color: #248232;
            }
        """)
        self.model = self.load_and_train_model()

    def load_and_train_model(self):
        # Load the dataset
        df = pd.read_csv('Crop_recommendation.csv')
        
        # Encode the labels
        label_encoder = LabelEncoder()
        df['label'] = label_encoder.fit_transform(df['label'])
        
        # Features and target
        X = df[['N', 'P', 'K', 'temperature', 'humidity', 'ph', 'rainfall']]
        y = df['label']
        
        # Split the data
        X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
        
        # Train the model
        model = RandomForestClassifier(n_estimators=100, random_state=42)
        model.fit(X_train, y_train)
        
        return model, label_encoder

    def init_ui(self):
        self.setWindowTitle("FieldBuddy: SmartCrop Advisor for Sustainable Farming")
        self.setWindowIcon(QIcon("leaf.png"))
        self.setGeometry(100, 100, 800, 700)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)

        # Header Section
        header = QHBoxLayout()
        icon_label = QLabel()
        icon_label.setPixmap(QIcon("leaf.png").pixmap(40, 40))
        header.addWidget(icon_label)
        
        title = QLabel("FieldBuddy!!!")
        title.setFont(QFont("Segoe UI", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #2b8a3e;")
        header.addWidget(title)
        header.addStretch()
        main_layout.addLayout(header)

        # Location Input
        location_box = QHBoxLayout()
        location_label = QLabel("🌍 Location:")
        location_label.setFont(QFont("Segoe UI", 12))
        self.location_input = QLineEdit()
        self.location_input.setPlaceholderText("Enter city or region...")
        self.location_input.setToolTip("Enter the name of your city or region to fetch weather data.")
        self.location_input.setStyleSheet("padding: 12px; font-size: 14px;")
        location_box.addWidget(location_label)
        location_box.addWidget(self.location_input)
        main_layout.addLayout(location_box)

        # Soil Parameters Group
        soil_group = QGroupBox("🌱 Soil Parameters")
        soil_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        grid_layout = QGridLayout()
        grid_layout.setVerticalSpacing(15)
        grid_layout.setHorizontalSpacing(20)
        
        # Existing soil parameter inputs
        self.nitrogen_input = self.create_input_field("Nitrogen (mg/kg):", grid_layout, 0)
        self.potassium_input = self.create_input_field("Potassium (mg/kg):", grid_layout, 1)
        self.phosphorus_input = self.create_input_field("Phosphorus (mg/kg):", grid_layout, 2)
        self.ph_input = self.create_input_field("Soil pH (0-14):", grid_layout, 3)

        # Add file upload box
        file_upload_box = QGroupBox("📁 Soil Report Upload")
        file_upload_box.setStyleSheet("QGroupBox { border: 2px dashed #ced4da; }")
        file_layout = QVBoxLayout()
        file_upload_box.setLayout(file_layout)
        
        self.upload_btn = QPushButton("Choose File")
        self.upload_btn.clicked.connect(self.upload_file)
        self.upload_btn.setFixedSize(120, 120)
        self.upload_btn.setStyleSheet("""
            QPushButton {
                background-color: #e9ecef;
                border: 2px dashed #ced4da;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #dee2e6;
            }
        """)
        
        self.file_label = QLabel("No file selected")
        self.file_label.setWordWrap(True)
        self.file_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        file_layout.addWidget(self.upload_btn, 0, Qt.AlignmentFlag.AlignHCenter)
        file_layout.addWidget(self.file_label)
        
        # Add to grid layout (spanning 4 rows)
        grid_layout.addWidget(file_upload_box, 0, 2, 4, 1)  # Row 0-3, Column 2

        soil_group.setLayout(grid_layout)
        main_layout.addWidget(soil_group)

        # Combined Climate and Weather Group
        climate_weather_group = QGroupBox("🌦️ Climate & Weather Parameters")
        climate_weather_group.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        climate_weather_layout = QGridLayout()
        climate_weather_layout.setVerticalSpacing(15)
        climate_weather_layout.setHorizontalSpacing(20)

        # Add the auto-load button
        self.add_auto_load_button(climate_weather_layout)

        # Climate and Weather Inputs
        self.temp_input = self.create_input_field("🌡️ Temperature (°C):", climate_weather_layout, 1)
        self.humidity_input = self.create_input_field("💧 Humidity (%):", climate_weather_layout, 2)
        self.annual_rain_input = self.create_input_field("Annual Rainfall (mm):", climate_weather_layout, 3)

        climate_weather_group.setLayout(climate_weather_layout)
        main_layout.addWidget(climate_weather_group)

        # Recommendation Button
        button_container = QHBoxLayout()
        self.submit_btn = QPushButton("📋 Get Crop Recommendation")
        self.submit_btn.setIconSize(QSize(24, 24))
        self.submit_btn.clicked.connect(self.get_recommendation)
        button_container.addStretch()
        button_container.addWidget(self.submit_btn)
        button_container.addStretch()
        main_layout.addLayout(button_container)

        self.setLayout(main_layout)

    def add_auto_load_button(self, layout):
        # Button to auto-load climate data
        auto_load_btn = QPushButton("🌍 Auto-Load Climate Data")
        auto_load_btn.setIconSize(QSize(24, 24))
        auto_load_btn.setToolTip("Click to automatically fetch climate data for the entered location.")
        auto_load_btn.clicked.connect(self.auto_load_climate_data)
        layout.addWidget(auto_load_btn, 0, 0, 1, 2)  # Span across two columns

    def auto_load_climate_data(self):
        location = self.location_input.text().strip()
        if not location:
            QMessageBox.critical(self, "Error", "Please enter a location first.")
            return

        try:
            # Fetch weather data
            temp, humidity = self.fetch_weather_data()
            if None in (temp, humidity):
                raise Exception("Failed to fetch weather data.")

            # Fetch annual rainfall
            annual_rain = self.fetch_annual_rainfall(location)
            if annual_rain is None:
                raise Exception("Failed to fetch annual rainfall data.")

            # Update the input fields
            self.temp_input.setText(f"{temp:.1f}")
            self.humidity_input.setText(f"{humidity}")
            self.annual_rain_input.setText(f"{annual_rain:.2f}")

            QMessageBox.information(self, "Success", "Climate data loaded successfully!")
        except Exception as e:
            QMessageBox.warning(self, "Internet Required", 
                                f"Failed to auto-load data: {str(e)}\n\nPlease enter values manually.")

    def upload_file(self):
        file_dialog = QFileDialog()
        file_path, _ = file_dialog.getOpenFileName(
            self,
            "Select Soil Report",
            "",
            "All Files (*);;CSV Files (*.csv);;Excel Files (*.xlsx *.xls);;PDF Files (*.pdf);;Text Files (*.txt)"
        )
        
        if file_path:
            self.file_label.setText(f"Selected:\n{file_path.split('/')[-1]}")
            self.file_label.setStyleSheet("color: #2b8a3e; font-size: 12px;")
            self.process_soil_report(file_path)
        else:
            self.file_label.setText("No file selected")
            self.file_label.setStyleSheet("color: #868e96;")

    def process_soil_report(self, file_path):
        try:
            processor = FileProcessor()
            data = processor.process_file(file_path)
            self.update_inputs(data)
            QMessageBox.information(self, "Success", "Soil report data loaded successfully!")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to process soil report: {str(e)}")

    def update_inputs(self, data):
        # Normalize keys by removing spaces and making lowercase
        normalized_data = {k.lower().replace(' ', ''): v for k, v in data.items()}
        
        input_mapping = {
            'nitrogen': self.nitrogen_input,
            'Nitrogen': self.nitrogen_input,  # Alternative spelling
            'n': self.nitrogen_input,       # Short form
            'N': self.nitrogen_input,   
            'phosphorus': self.phosphorus_input,
            'phosphorous': self.phosphorus_input,  # Alternative spelling
            'p': self.phosphorus_input,    # Short form
            'P': self.phosphorus_input,  
            'potassium': self.potassium_input,
            'Potassium': self.potassium_input,
            'k': self.potassium_input,     # Short form
            'K': self.potassium_input, 
            'ph': self.ph_input,
            'phvalue': self.ph_input,      # Alternative format
            'ph_value': self.ph_input      # Alternative format
        }
        
        found_any = False
        for key, input_field in input_mapping.items():
            if key in normalized_data:
                try:
                    value = str(normalized_data[key]).strip()
                    # Remove any units or extra text
                    value = ''.join(c for c in value if c.isdigit() or c in '.-')
                    input_field.setText(value)
                    found_any = True
                except (ValueError, AttributeError):
                    continue
        
        if not found_any:
            raise ValueError("No valid soil parameters found in the file")

    def create_input_field(self, label_text, layout, row):
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 11))
        input_field = QLineEdit()
        input_field.setPlaceholderText("Enter value...")
        input_field.setToolTip(f"Enter the {label_text.lower()} value.")
        input_field.setStyleSheet("padding: 10px; font-size: 13px;")
        layout.addWidget(label, row, 0)
        layout.addWidget(input_field, row, 1)
        return input_field

    def validate_inputs(self):
        try:
            n = float(self.nitrogen_input.text())
            k = float(self.potassium_input.text())
            p = float(self.phosphorus_input.text())
            ph = float(self.ph_input.text())
            temp = float(self.temp_input.text())
            humidity = float(self.humidity_input.text())
            annual_rain = float(self.annual_rain_input.text())
        except ValueError:
            QMessageBox.critical(self, "Error", "Please enter valid numbers for all parameters.")
            return None

        if not (0 <= ph <= 14):
            QMessageBox.critical(self, "Error", "Soil pH must be between 0 and 14.")
            return None

        if n < 0 or k < 0 or p < 0 or temp < 0 or humidity < 0 or annual_rain < 0:
            QMessageBox.critical(self, "Error", "Values cannot be negative.")
            return None

        return (n, k, p, ph, temp, humidity, annual_rain)

    def fetch_weather_data(self):
        location = self.location_input.text().strip()
        if not location:
            QMessageBox.critical(self, "Error", "Please enter a location.")
            return (None, None)

        try:
            weather_url = "https://api.openweathermap.org/data/2.5/weather"
            params = {
                'q': location,
                'appid': OPENWEATHER_API_KEY,
                'units': 'metric'
            }
            response = requests.get(weather_url, params=params)
            response.raise_for_status()
            data = response.json()

            temp = data['main']['temp']
            humidity = data['main']['humidity']

            return (temp, humidity)
        except requests.exceptions.HTTPError as e:
            if response.status_code == 404:
                QMessageBox.critical(self, "Error", "Location not found.")
            else:
                QMessageBox.critical(self, "Error", f"Failed to fetch weather: {str(e)}")
            return (None, None)
        except requests.exceptions.RequestException as e:
            QMessageBox.critical(self, "Error", f"Network error: {str(e)}")
            return (None, None)
        except KeyError:
            QMessageBox.critical(self, "Error", "Unexpected weather data format.")
            return (None, None)

    def fetch_annual_rainfall(self, location):
        try:
            # Convert location to coordinates using OpenWeather API
            geocode_url = "https://api.openweathermap.org/geo/1.0/direct"
            params = {
                'q': location,
                'limit': 1,
                'appid': OPENWEATHER_API_KEY
            }
            response = requests.get(geocode_url, params=params)
            response.raise_for_status()
            data = response.json()

            if not data:
                QMessageBox.critical(self, "Error", "Location not found.")
                return None

            lat, lon = data[0]['lat'], data[0]['lon']

            # Fetch annual rainfall using Google Earth Engine
            chirps = ee.ImageCollection('UCSB-CHG/CHIRPS/DAILY')
            roi = ee.Geometry.Point(lon, lat)
            chirps_filtered = chirps.filterDate('2022-01-01', '2022-12-31').filterBounds(roi)
            total_rainfall = chirps_filtered.sum().reduceRegion(
                reducer=ee.Reducer.mean(),
                geometry=roi,
                scale=5000
            ).get('precipitation').getInfo()

            if total_rainfall is None:
                QMessageBox.critical(self, "Error", "Failed to fetch rainfall data.")
                return None

            return total_rainfall
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to fetch rainfall data: {str(e)}")
            return None

    def get_recommendation(self):
        input_data = self.validate_inputs()
        if not input_data:
            return
            
        n, k, p, ph, temp, humidity, annual_rain = input_data

        # Prepare input data for prediction
        input_data = np.array([[n, p, k, temp, humidity, ph, annual_rain]])
        
        # Predict the crop
        model, label_encoder = self.model
        prediction = model.predict(input_data)
        predicted_crop = label_encoder.inverse_transform(prediction)[0]

        # Display the recommendation
        recommendation = f"🌱 Recommended crop: {predicted_crop}\n\n"
        recommendation += "⚠️ Consider soil testing and amendment for optimal results."

        msg = QMessageBox()
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setWindowTitle("Crop Recommendation")
        msg.setText(recommendation)
        msg.setFont(QFont("Segoe UI", 12))
        msg.setStyleSheet("""
            QMessageBox {
                background-color: white;
            }
            QLabel {
                color: #2b8a3e;
                font-size: 14px;
            }
            QPushButton {
                background-color: #2b8a3e;
                color: white;
                min-width: 100px;
            }
        """)
        msg.exec()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CropRecommendationApp()
    window.showMaximized()
    sys.exit(app.exec())
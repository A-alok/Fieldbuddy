import sys
import os
from PyQt6.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QTabWidget, QGroupBox, QScrollArea, QFrame,
    QFileDialog, QMessageBox
)
from PyQt6.QtGui import QFont, QPixmap, QIcon
from PyQt6.QtCore import Qt, QSize

# Global reference for file paths
file = __file__

class CropRecommendationResult(QWidget):
    def __init__(self, parent=None, crop_name=None, crop_data=None):
        super().__init__(parent)
        self.parent = parent
        self.crop_name = crop_name or "rice"  # Default crop if none provided
        self.crop_data = crop_data or self.get_default_crop_data()
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface"""
        # Set white background for main window
        self.setStyleSheet("background-color: white;")
        
        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)
        
        # Back button
        back_button = QPushButton("← Back to Form")
        back_button.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                color: #2b8a3e;
                border: none;
                font-weight: bold;
                text-align: left;
                padding: 8px 0;
            }
            QPushButton:hover {
                color: #2f9e44;
                text-decoration: underline;
            }
        """)
        back_button.clicked.connect(self.go_back)
        main_layout.addWidget(back_button)
        
        # Content layout (2 columns)
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left column - Crop info
        left_column = QVBoxLayout()
        
        # Recommendation header
        recommendation_box = QGroupBox()
        recommendation_box.setStyleSheet("""
            QGroupBox {
                background-color: #e6f4ea;
                border-radius: 8px;
                border: none;
                padding: 15px;
            }
        """)
        
        recommendation_layout = QVBoxLayout()
        
        header_label = QLabel("🌱 Recommended Crop")
        header_label.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        header_label.setStyleSheet("color: #2b8a3e;")
        
        crop_name_label = QLabel(self.crop_name.title())
        crop_name_label.setFont(QFont("Segoe UI", 18, QFont.Weight.Bold))
        crop_name_label.setStyleSheet("color: #2b8a3e;")
        
        description_label = QLabel(self.crop_data["description"])
        description_label.setWordWrap(True)
        description_label.setStyleSheet("color: #495057;")
        
        recommendation_layout.addWidget(header_label)
        recommendation_layout.addWidget(crop_name_label)
        recommendation_layout.addWidget(description_label)
        recommendation_box.setLayout(recommendation_layout)
        
        left_column.addWidget(recommendation_box)
        
        # Crop requirements
        requirements_box = QGroupBox("Crop Requirements")
        requirements_box.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        requirements_box.setStyleSheet("""
            QGroupBox {
                background-color: white;
                border: 1px solid #e9ecef;
                border-radius: 8px;
                margin-top: 15px;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                left: 10px;
                padding: 0 5px;
                color: #343a40;
            }
        """)
        
        requirements_layout = QVBoxLayout()
        requirements_layout.setSpacing(15)
        
        # Temperature
        temp_layout = QHBoxLayout()
        temp_icon = QLabel("🌡")
        temp_icon.setFont(QFont("Segoe UI", 12))
        
        temp_info = QVBoxLayout()
        temp_title = QLabel("Temperature")
        temp_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        temp_value = QLabel(self.crop_data["optimal_temperature"])
        temp_value.setStyleSheet("color: #495057;")
        
        temp_info.addWidget(temp_title)
        temp_info.addWidget(temp_value)
        
        temp_layout.addWidget(temp_icon)
        temp_layout.addLayout(temp_info)
        temp_layout.addStretch()
        
        # Water requirements
        water_layout = QHBoxLayout()
        water_icon = QLabel("💧")
        water_icon.setFont(QFont("Segoe UI", 12))
        
        water_info = QVBoxLayout()
        water_title = QLabel("Water Requirements")
        water_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        water_value = QLabel(self.crop_data["water_requirements"])
        water_value.setStyleSheet("color: #495057;")
        
        water_info.addWidget(water_title)
        water_info.addWidget(water_value)
        
        water_layout.addWidget(water_icon)
        water_layout.addLayout(water_info)
        water_layout.addStretch()
        
        # Growing season
        season_layout = QHBoxLayout()
        season_icon = QLabel("🌱")
        season_icon.setFont(QFont("Segoe UI", 12))
        
        season_info = QVBoxLayout()
        season_title = QLabel("Growing Season")
        season_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        season_value = QLabel(self.crop_data["growing_season"])
        season_value.setStyleSheet("color: #495057;")
        
        season_info.addWidget(season_title)
        season_info.addWidget(season_value)
        
        season_layout.addWidget(season_icon)
        season_layout.addLayout(season_info)
        season_layout.addStretch()
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        separator.setStyleSheet("background-color: #e9ecef;")
        
        # Soil preference
        soil_title = QLabel("Soil Preference")
        soil_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        soil_value = QLabel(self.crop_data["soil_preference"])
        soil_value.setWordWrap(True)
        soil_value.setStyleSheet("color: #495057;")
        
        # Nutritional value
        nutrition_title = QLabel("Nutritional Value")
        nutrition_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        nutrition_value = QLabel(self.crop_data["nutritional_value"])
        nutrition_value.setWordWrap(True)
        nutrition_value.setStyleSheet("color: #495057;")
        
        # Add all to requirements layout
        requirements_layout.addLayout(temp_layout)
        requirements_layout.addLayout(water_layout)
        requirements_layout.addLayout(season_layout)
        requirements_layout.addWidget(separator)
        requirements_layout.addWidget(soil_title)
        requirements_layout.addWidget(soil_value)
        requirements_layout.addSpacing(10)
        requirements_layout.addWidget(nutrition_title)
        requirements_layout.addWidget(nutrition_value)
        
        requirements_box.setLayout(requirements_layout)
        left_column.addWidget(requirements_box)
        left_column.addStretch()
        
        # Right column - Tabs with image and growing tips
        right_column = QVBoxLayout()
        
        # Create tab widget
        tabs = QTabWidget()
        tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e9ecef;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background-color: #f8f9fa;
                border: 1px solid #e9ecef;
                border-bottom: none;
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 8px 16px;
                margin-right: 2px;
                color: black; /* Changed text color to black */
            }
            QTabBar::tab:selected {
                background-color: white;
                border-bottom: 1px solid white;
            }
        """)
        
        # Image tab
        image_widget = QWidget()
        image_layout = QVBoxLayout()
        
        # Load image from local storage
        image_path = self.get_crop_image_path()
        image_label = QLabel()
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if os.path.exists(image_path):
            pixmap = QPixmap(image_path)
            pixmap = pixmap.scaled(400, 300, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            image_label.setPixmap(pixmap)
        else:
            image_label.setText("Image not available")
            image_label.setStyleSheet("""
                background-color: #f8f9fa;
                padding: 100px;
                border-radius: 8px;
                color: #adb5bd;
                font-size: 16px;
            """)
        
        image_layout.addWidget(image_label)
        image_widget.setLayout(image_layout)
        
        # Growing tips tab
        tips_widget = QScrollArea()
        tips_widget.setWidgetResizable(True)
        tips_content = QWidget()
        tips_layout = QVBoxLayout()
        tips_layout.setContentsMargins(10, 10, 10, 10)
        tips_layout.setSpacing(15)
        
        tips_title = QLabel(f"Growing Details for {self.crop_name.title()}")
        tips_title.setFont(QFont("Segoe UI", 12, QFont.Weight.Bold))
        tips_layout.addWidget(tips_title)

        # Climate
        climate_box = QGroupBox()
        climate_box.setStyleSheet("""
            QGroupBox {
                background-color: #e7f5ff;
                border-radius: 8px;
                border: none;
                padding: 15px;
            }
        """)
        climate_layout = QVBoxLayout()
        climate_title = QLabel("Climate")
        climate_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        climate_title.setStyleSheet("color: #1971c2;")
        climate_tips = QLabel(f"""
        • Optimal temperature: {self.crop_data["optimal_temperature"]}
        • Humidity requirements: Moderate to high
        • Frost sensitivity: Not frost tolerant
        """)
        climate_tips.setWordWrap(True)
        climate_layout.addWidget(climate_title)
        climate_layout.addWidget(climate_tips)
        climate_box.setLayout(climate_layout)
        tips_layout.addWidget(climate_box)

        # Soil Type
        soil_box = QGroupBox()
        soil_box.setStyleSheet("""
            QGroupBox {
                background-color: #e6f4ea;
                border-radius: 8px;
                border: none;
                padding: 15px;
            }
        """)
        soil_layout = QVBoxLayout()
        soil_title = QLabel("Soil Type")
        soil_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        soil_title.setStyleSheet("color: #2b8a3e;")
        soil_tips = QLabel(f"""
        • Preferred soil: {self.crop_data["soil_preference"]}
        • Drainage requirements: Moderate
        • Organic matter content: >2%
        """)
        soil_tips.setWordWrap(True)
        soil_layout.addWidget(soil_title)
        soil_layout.addWidget(soil_tips)
        soil_box.setLayout(soil_layout)
        tips_layout.addWidget(soil_box)

        # Growing Season
        season_box = QGroupBox()
        season_box.setStyleSheet("""
            QGroupBox {
                background-color: #fff9db;
                border-radius: 8px;
                border: none;
                padding: 15px;
            }
        """)
        season_layout = QVBoxLayout()
        season_title = QLabel("Growing Season")
        season_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        season_title.setStyleSheet("color: #e67700;")
        season_tips = QLabel(f"""
        • Best planting time: {self.crop_data["growing_season"]}
        • Duration: 3-6 months
        • Crop rotation: Annual
        """)
        season_tips.setWordWrap(True)
        season_layout.addWidget(season_title)
        season_layout.addWidget(season_tips)
        season_box.setLayout(season_layout)
        tips_layout.addWidget(season_box)

        # Yield Per Acre
        yield_box = QGroupBox()
        yield_box.setStyleSheet("""
            QGroupBox {
                background-color: #e6e6ff;
                border-radius: 8px;
                border: none;
                padding: 15px;
            }
        """)
        yield_layout = QVBoxLayout()
        yield_title = QLabel("Yield Per Acre")
        yield_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        yield_title.setStyleSheet("color: #4a47a3;")
        yield_tips = QLabel("""
        • Average yield: 2-3 tons
        • Harvest index: 0.4-0.5
        • Yield factors: Proper irrigation and fertilization
        """)
        yield_tips.setWordWrap(True)
        yield_layout.addWidget(yield_title)
        yield_layout.addWidget(yield_tips)
        yield_box.setLayout(yield_layout)
        tips_layout.addWidget(yield_box)

        # Market Price
        price_box = QGroupBox()
        price_box.setStyleSheet("""
            QGroupBox {
                background-color: #fde2ff;
                border-radius: 8px;
                border: none;
                padding: 15px;
            }
        """)
        price_layout = QVBoxLayout()
        price_title = QLabel("Market Price")
        price_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        price_title.setStyleSheet("color: #8e44ad;")
        price_tips = QLabel("""
        • Current price: $300-$500/ton
        • Price trends: Seasonal variations
        • Market demand: High
        """)
        price_tips.setWordWrap(True)
        price_layout.addWidget(price_title)
        price_layout.addWidget(price_tips)
        price_box.setLayout(price_layout)
        tips_layout.addWidget(price_box)

        # Maturity Day
        maturity_box = QGroupBox()
        maturity_box.setStyleSheet("""
            QGroupBox {
                background-color: #ffe8cc;
                border-radius: 8px;
                border: none;
                padding: 15px;
            }
        """)
        maturity_layout = QVBoxLayout()
        maturity_title = QLabel("Maturity Day")
        maturity_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        maturity_title.setStyleSheet("color: #d35400;")
        maturity_tips = QLabel("""
        • Days to maturity: 100-120 days
        • Growth stages: Vegetative, reproductive, ripening
        • Harvest window: 7-10 days
        """)
        maturity_tips.setWordWrap(True)
        maturity_layout.addWidget(maturity_title)
        maturity_layout.addWidget(maturity_tips)
        maturity_box.setLayout(maturity_layout)
        tips_layout.addWidget(maturity_box)

        # Water Requirement
        water_box = QGroupBox()
        water_box.setStyleSheet("""
            QGroupBox {
                background-color: #d0f0fd;
                border-radius: 8px;
                border: none;
                padding: 15px;
            }
        """)
        water_layout = QVBoxLayout()
        water_title = QLabel("Water Requirement")
        water_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        water_title.setStyleSheet("color: #1a73e8;")
        water_tips = QLabel(f"""
        • {self.crop_data["water_requirements"]}
        • Irrigation frequency: Weekly
        • Water depth: 5-10 cm
        """)
        water_tips.setWordWrap(True)
        water_layout.addWidget(water_title)
        water_layout.addWidget(water_tips)
        water_box.setLayout(water_layout)
        tips_layout.addWidget(water_box)

        # Nutrient Recommendation
        nutrient_box = QGroupBox()
        nutrient_box.setStyleSheet("""
            QGroupBox {
                background-color: #d4f7d4;
                border-radius: 8px;
                border: none;
                padding: 15px;
            }
        """)
        nutrient_layout = QVBoxLayout()
        nutrient_title = QLabel("Nutrient Recommendation")
        nutrient_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        nutrient_title.setStyleSheet("color: #2e7d32;")
        nutrient_tips = QLabel("""
        • NPK ratio: 4:2:1
        • Micronutrients: Zinc, Iron
        • Application timing: During tillering
        """)
        nutrient_tips.setWordWrap(True)
        nutrient_layout.addWidget(nutrient_title)
        nutrient_layout.addWidget(nutrient_tips)
        nutrient_box.setLayout(nutrient_layout)
        tips_layout.addWidget(nutrient_box)

        # Pest & Disease Information
        pest_box = QGroupBox()
        pest_box.setStyleSheet("""
            QGroupBox {
                background-color: #ffe5e5;
                border-radius: 8px;
                border: none;
                padding: 15px;
            }
        """)
        pest_layout = QVBoxLayout()
        pest_title = QLabel("Pest & Disease Information")
        pest_title.setFont(QFont("Segoe UI", 10, QFont.Weight.Bold))
        pest_title.setStyleSheet("color: #c62828;")
        pest_tips = QLabel("""
        • Common pests: Stem borers, leaf folders
        • Diseases: Blast, bacterial blight
        • Prevention: Crop rotation, resistant varieties
        """)
        pest_tips.setWordWrap(True)
        pest_layout.addWidget(pest_title)
        pest_layout.addWidget(pest_tips)
        pest_box.setLayout(pest_layout)
        tips_layout.addWidget(pest_box)
        
        tips_content.setLayout(tips_layout)
        tips_widget.setWidget(tips_content)
        
        # Add tabs
        tabs.addTab(image_widget, "Crop Image")
        tabs.addTab(tips_widget, "Crop Details")
        
        right_column.addWidget(tabs)
        
        # Add columns to content layout
        content_layout.addLayout(left_column, 1)
        content_layout.addLayout(right_column, 1)
        
        main_layout.addLayout(content_layout)
        
        # Add save button
        button_layout = QHBoxLayout()
        
        save_button = QPushButton("Save Recommendation")
        save_button.setIcon(QIcon.fromTheme("document-save"))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #2b8a3e;
                color: white;
                border: none;
                padding: 12px 25px;
                border-radius: 6px;
                font-size: 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2f9e44;
            }
        """)
        save_button.clicked.connect(self.save_recommendation)
        
        button_layout.addStretch()
        button_layout.addWidget(save_button)
        button_layout.addStretch()
        
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def get_default_crop_data(self):
        """Return default crop data if none is provided"""
        return {
            "description": "Rice is a staple food crop for more than half of the world's population. It's grown in flooded fields known as rice paddies.",
            "growing_season": "Summer to early autumn",
            "water_requirements": "High (flooded conditions)",
            "soil_preference": "Clay soils that hold water well, pH 5.5-6.5",
            "optimal_temperature": "20-35°C during growing season",
            "nutritional_value": "Good source of carbohydrates, contains some protein, vitamins and minerals"
        }
    
    def get_crop_image_path(self):
        """Get the path to the crop image in local storage"""
        base_paths = [
            os.path.join(os.path.dirname(os.path.abspath(file)), "images", "crops"),
            os.path.join(os.path.dirname(os.path.abspath(file)), "assets", "crops"),
            os.path.join(os.path.expanduser("~"), "FieldBuddy", "crops")
        ]
        
        for base_path in base_paths:
            for ext in ['.jpg', '.jpeg', '.png']:
                img_path = os.path.join(base_path, f"{self.crop_name.lower()}{ext}")
                if os.path.exists(img_path):
                    return img_path
        
        return os.path.join(os.path.dirname(os.path.abspath(file)), "images", "placeholder.png")
    
    def go_back(self):
        """Return to the main form"""
        if self.parent:
            self.parent.show_main_form()
        self.hide()
    
    def save_recommendation(self):
        """Save the recommendation as a PDF or text file"""
        file_path, _ = QFileDialog.getSaveFileName(
            self,
            "Save Recommendation",
            f"{self.crop_name}_recommendation.pdf",
            "PDF Files (*.pdf);;Text Files (*.txt)"
        )
        
        if file_path:
            try:
                if file_path.endswith('.pdf'):
                    self.save_as_pdf(file_path)
                else:
                    self.save_as_text(file_path)
                
                QMessageBox.information(
                    self,
                    "Success",
                    f"Recommendation saved to {os.path.basename(file_path)}"
                )
            except Exception as e:
                QMessageBox.critical(
                    self,
                    "Error",
                    f"Failed to save recommendation: {str(e)}"
                )
    
    def save_as_pdf(self, file_path):
        """Save recommendation as PDF"""
        try:
            from reportlab.lib.pagesizes import letter
            from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image
            from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
            from reportlab.lib import colors
            
            doc = SimpleDocTemplate(file_path, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom styles
            title_style = ParagraphStyle(
                'TitleStyle',
                parent=styles['Heading1'],
                textColor=colors.green,
                spaceAfter=12
            )
            
            heading_style = ParagraphStyle(
                'HeadingStyle',
                parent=styles['Heading2'],
                textColor=colors.darkgreen,
                spaceAfter=6
            )
            
            # Build content
            content = []
            content.append(Paragraph(f"Crop Recommendation: {self.crop_name.title()}", title_style))
            content.append(Spacer(1, 12))
            
            # Add all sections
            sections = [
                ("Description", self.crop_data["description"]),
                ("Growing Conditions", [
                    f"• Growing Season: {self.crop_data['growing_season']}",
                    f"• Water Requirements: {self.crop_data['water_requirements']}",
                    f"• Optimal Temperature: {self.crop_data['optimal_temperature']}",
                    f"• Soil Preference: {self.crop_data['soil_preference']}"
                ]),
                ("Nutritional Value", self.crop_data["nutritional_value"]),
                ("Crop Details", [
                    ("Climate", [
                        f"• Optimal temperature: {self.crop_data['optimal_temperature']}",
                        "• Humidity requirements: Moderate to high",
                        "• Frost sensitivity: Not frost tolerant"
                    ]),
                    ("Soil Type", [
                        f"• Preferred soil: {self.crop_data['soil_preference']}",
                        "• Drainage requirements: Moderate",
                        "• Organic matter content: >2%"
                    ]),
                    ("Growing Season", [
                        f"• Best planting time: {self.crop_data['growing_season']}",
                        "• Duration: 3-6 months",
                        "• Crop rotation: Annual"
                    ]),
                    ("Yield Per Acre", [
                        "• Average yield: 2-3 tons",
                        "• Harvest index: 0.4-0.5",
                        "• Yield factors: Proper irrigation and fertilization"
                    ]),
                    ("Market Price", [
                        "• Current price: $300-$500/ton",
                        "• Price trends: Seasonal variations",
                        "• Market demand: High"
                    ]),
                    ("Maturity Day", [
                        "• Days to maturity: 100-120 days",
                        "• Growth stages: Vegetative, reproductive, ripening",
                        "• Harvest window: 7-10 days"
                    ]),
                    ("Water Requirement", [
                        f"• {self.crop_data['water_requirements']}",
                        "• Irrigation frequency: Weekly",
                        "• Water depth: 5-10 cm"
                    ]),
                    ("Nutrient Recommendation", [
                        "• NPK ratio: 4:2:1",
                        "• Micronutrients: Zinc, Iron",
                        "• Application timing: During tillering"
                    ]),
                    ("Pest & Disease Information", [
                        "• Common pests: Stem borers, leaf folders",
                        "• Diseases: Blast, bacterial blight",
                        "• Prevention: Crop rotation, resistant varieties"
                    ])
                ])
            ]
            
            for section in sections:
                content.append(Paragraph(section[0] + ":", heading_style))
                if isinstance(section[1], list):
                    for item in section[1]:
                        if isinstance(item, tuple):  # Sub-sections
                            content.append(Paragraph(item[0], styles['Heading3']))
                            for subitem in item[1]:
                                content.append(Paragraph(f"• {subitem}", styles['Normal']))
                        else:
                            content.append(Paragraph(item, styles['Normal']))
                else:
                    content.append(Paragraph(section[1], styles['Normal']))
                content.append(Spacer(1, 12))
            
            # Add image if available
            img_path = self.get_crop_image_path()
            if os.path.exists(img_path) and not img_path.endswith("placeholder.png"):
                content.append(Spacer(1, 12))
                img = Image(img_path, width=300, height=200)
                content.append(img)
            
            doc.build(content)
            
        except ImportError:
            self.save_as_text(file_path.replace('.pdf', '.txt'))
            raise ImportError("ReportLab not installed. Saved as text instead.")
    
    def save_as_text(self, file_path):
        """Save recommendation as text file"""
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(f"CROP RECOMMENDATION: {self.crop_name.upper()}\n")
            f.write("="*50 + "\n\n")
            
            sections = [
                ("DESCRIPTION", self.crop_data["description"]),
                ("GROWING CONDITIONS", [
                    f"Growing Season: {self.crop_data['growing_season']}",
                    f"Water Requirements: {self.crop_data['water_requirements']}",
                    f"Optimal Temperature: {self.crop_data['optimal_temperature']}",
                    f"Soil Preference: {self.crop_data['soil_preference']}"
                ]),
                ("NUTRITIONAL VALUE", self.crop_data["nutritional_value"]),
                ("CROP DETAILS", [
                    ("CLIMATE", [
                        f"Optimal temperature: {self.crop_data['optimal_temperature']}",
                        "Humidity requirements: Moderate to high",
                        "Frost sensitivity: Not frost tolerant"
                    ]),
                    ("SOIL TYPE", [
                        f"Preferred soil: {self.crop_data['soil_preference']}",
                        "Drainage requirements: Moderate",
                        "Organic matter content: >2%"
                    ]),
                    ("GROWING SEASON", [
                        f"Best planting time: {self.crop_data['growing_season']}",
                        "Duration: 3-6 months",
                        "Crop rotation: Annual"
                    ]),
                    ("YIELD PER ACRE", [
                        "Average yield: 2-3 tons",
                        "Harvest index: 0.4-0.5",
                        "Yield factors: Proper irrigation and fertilization"
                    ]),
                    ("MARKET PRICE", [
                        "Current price: $300-$500/ton",
                        "Price trends: Seasonal variations",
                        "Market demand: High"
                    ]),
                    ("MATURITY DAY", [
                        "Days to maturity: 100-120 days",
                        "Growth stages: Vegetative, reproductive, ripening",
                        "Harvest window: 7-10 days"
                    ]),
                    ("WATER REQUIREMENT", [
                        self.crop_data["water_requirements"],
                        "Irrigation frequency: Weekly",
                        "Water depth: 5-10 cm"
                    ]),
                    ("NUTRIENT RECOMMENDATION", [
                        "NPK ratio: 4:2:1",
                        "Micronutrients: Zinc, Iron",
                        "Application timing: During tillering"
                    ]),
                    ("PEST & DISEASE INFORMATION", [
                        "Common pests: Stem borers, leaf folders",
                        "Diseases: Blast, bacterial blight",
                        "Prevention: Crop rotation, resistant varieties"
                    ])
                ])
            ]
            
            for section in sections:
                f.write(f"{section[0]}:\n")
                if isinstance(section[1], list):
                    for item in section[1]:
                        if isinstance(item, tuple):  # Sub-sections
                            f.write(f"\n{item[0]}:\n")
                            for subitem in item[1]:
                                f.write(f"  • {subitem}\n")
                        else:
                            f.write(f"• {item}\n")
                else:
                    f.write(f"{section[1]}\n")
                f.write("\n")

# Sample crop database
CROP_DATABASE = {
    "rice": {
        "description": "Rice is a staple food crop for more than half of the world's population. It's grown in flooded fields known as rice paddies.",
        "growing_season": "Summer to early autumn",
        "water_requirements": "High (flooded conditions)",
        "soil_preference": "Clay soils that hold water well, pH 5.5-6.5",
        "optimal_temperature": "20-35°C during growing season",
        "nutritional_value": "Good source of carbohydrates, contains some protein, vitamins and minerals"
    },
    "wheat": {
        "description": "Wheat is one of the world's most important cereal crops, used to make bread, pasta, and many other food products.",
        "growing_season": "Winter wheat (planted in fall) or spring wheat",
        "water_requirements": "Moderate",
        "soil_preference": "Well-drained loamy soils, pH 6.0-7.0",
        "optimal_temperature": "15-24°C during growing season",
        "nutritional_value": "Rich in carbohydrates, contains protein, fiber, B vitamins and minerals"
    }
}

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = CropRecommendationResult(crop_name="rice", crop_data=CROP_DATABASE["rice"])
    window.setWindowTitle("Crop Recommendation System")
    window.resize(1000, 700)
    window.show()
    sys.exit(app.exec())
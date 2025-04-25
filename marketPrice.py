import sys
import requests  # For API calls
from PyQt6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QLabel, QPushButton, QComboBox, QTableWidget, QTableWidgetItem,
    QHeaderView, QFrame, QGraphicsDropShadowEffect,QMessageBox, QLineEdit
)
from PyQt6.QtGui import QColor, QFont
from PyQt6.QtCore import Qt
from dotenv import load_dotenv
import os

# Load environment variables
load_dotenv()

class MarketPriceWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FieldBuddy - Market Prices")
        self.setGeometry(100, 100, 1400, 900)

        # ----------------------------------------------------------------
        #  Updated for data.gov.in:
        #  1) API key
        #  2) Endpoint = resource for daily prices
        # ----------------------------------------------------------------
        self.api_key = os.getenv('DATA_GOV_API_KEY')
        if not self.api_key:
            raise ValueError("DATA_GOV_API_KEY not found in environment variables")
        # Official data.gov.in resource URL for "Current Daily Price..." dataset
        self.api_endpoint = (
            "https://api.data.gov.in/resource/9ef84268-d588-465a-a308-a864a43d0070"
        )

        # List of Indian states (customize if needed)
        self.indian_states = self.load_indian_states()

        # Keep track of the user-selected price unit (default: "Quintal")
        self.selected_unit = "Quintal"

        self.init_ui()

    def load_indian_states(self):
        """
        Returns a list of all Indian states.
        (Add union territories if needed.)
        """
        states = [
            "Andhra Pradesh", "Arunachal Pradesh", "Assam", "Bihar", "Chhattisgarh",
            "Goa", "Gujarat", "Haryana", "Himachal Pradesh", "Jharkhand",
            "Karnataka", "Kerala", "Madhya Pradesh", "Maharashtra", "Manipur",
            "Meghalaya", "Mizoram", "Nagaland", "Odisha", "Punjab",
            "Rajasthan", "Sikkim", "Tamil Nadu", "Telangana", "Tripura",
            "Uttar Pradesh", "Uttarakhand", "West Bengal"
        ]
        return states

    def init_ui(self):
        self.setStyleSheet("QMainWindow { background-color: white; }")

        main_widget = QWidget()
        main_widget.setObjectName("mainContainer")
        self.setCentralWidget(main_widget)
        
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(5, 5)
        main_widget.setGraphicsEffect(shadow)

        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)  # Minimal external margins
        main_layout.setSpacing(15)  # Minimal spacing between widgets

        # ------------------- Header -------------------
        header_layout = QHBoxLayout()
        
        # Add back button
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
        header_layout.addWidget(self.back_btn)
        header_layout.addStretch()

        header_label = QLabel("🌾 Crop Market Price 📊")
        header_label.setStyleSheet("""
            QLabel {
                font-size: 32px;
                font-weight: bold;
                color: white;
                background-color: #2c5e2e;
                border-radius: 15px;
                padding: 20px;
            }
        """)
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_layout.addWidget(header_label)
        header_layout.addStretch()
        
        main_layout.addLayout(header_layout)

        # ------------------- Crop & Unit Selection -------------------
        selection_layout = QHBoxLayout()
        # 1) Crop
        crop_label = QLabel("Select Crop:")
        crop_label.setStyleSheet("font-size: 18px; color: #333; font-weight: bold;")
        
        self.crop_dropdown = QComboBox()
        crops = {
            "Wheat": "🌾",
            "Rice": "🍚",
            "Cotton": "🧵",
            "Soybean": "🟫",
            "Maize": "🌽"
        }
        for crop, emoji in crops.items():
            self.crop_dropdown.addItem(f"{crop} {emoji}", crop)
        self.crop_dropdown.setStyleSheet(self.get_combo_style())

        # 2) Price Unit
        unit_label = QLabel("Price Unit:")
        unit_label.setStyleSheet("font-size: 18px; color: #333; font-weight: bold;")

        self.unit_dropdown = QComboBox()
        self.unit_dropdown.setStyleSheet(self.get_combo_style())
        # Add unit options
        self.unit_dropdown.addItem("Quintal")
        self.unit_dropdown.addItem("Kilogram")
        self.unit_dropdown.addItem("Tonne")

        # Add to layout
        selection_layout.addWidget(crop_label)
        selection_layout.addWidget(self.crop_dropdown)
        selection_layout.addSpacing(50)
        selection_layout.addWidget(unit_label)
        selection_layout.addWidget(self.unit_dropdown)
        selection_layout.addStretch()
        main_layout.addLayout(selection_layout)

        # ------------------- Location Selection -------------------
        location_layout = QVBoxLayout()
        location_layout.setSpacing(15)

        # State Selection
        state_layout = QHBoxLayout()
        state_label = QLabel("State:")
        state_label.setStyleSheet("font-size: 16px; color: #333;")

        self.state_dropdown = QComboBox()
        self.state_dropdown.setStyleSheet(self.get_combo_style())
        # Add a placeholder item for "no state selected"
        self.state_dropdown.addItem("Select State", None)
        # Now add all actual states
        for st in self.indian_states:
            self.state_dropdown.addItem(st, st)

        state_layout.addWidget(state_label)
        state_layout.addWidget(self.state_dropdown)
        state_layout.addStretch()

        # District Input
        district_layout = QHBoxLayout()
        district_label = QLabel("District:")
        district_label.setStyleSheet("font-size: 16px; color: #333;")
        self.district_input = QLineEdit()
        self.district_input.setPlaceholderText("Enter district name")
        self.district_input.setStyleSheet(self.get_input_style())
        district_layout.addWidget(district_label)
        district_layout.addWidget(self.district_input)

        # Market Input
        market_layout = QHBoxLayout()
        market_label = QLabel("Market:")
        market_label.setStyleSheet("font-size: 16px; color: #333;")
        self.market_input = QLineEdit()
        self.market_input.setPlaceholderText("Enter market/mandi name")
        self.market_input.setStyleSheet(self.get_input_style())
        market_layout.addWidget(market_label)
        market_layout.addWidget(self.market_input)

        location_layout.addLayout(state_layout)
        
        main_layout.addLayout(location_layout)

        # ------------------- Summary Cards -------------------
        self.create_summary_cards(main_layout)

        # ------------------- Price Table -------------------
        self.create_price_table(main_layout)

        # ------------------- Refresh Button -------------------
        refresh_btn = QPushButton("🔄 Refresh Prices")
        refresh_btn.setStyleSheet(self.get_button_style())
        refresh_btn.clicked.connect(self.refresh_prices)
        main_layout.addWidget(refresh_btn, alignment=Qt.AlignmentFlag.AlignRight)

        # ------------------- Initialize Data -------------------
        self.populate_table()

        # ------------------- Connect Signals -------------------
        self.crop_dropdown.currentIndexChanged.connect(self.populate_table)
        self.state_dropdown.currentIndexChanged.connect(self.populate_table)
        self.district_input.textChanged.connect(self.populate_table)
        self.market_input.textChanged.connect(self.populate_table)
        self.unit_dropdown.currentIndexChanged.connect(self.update_unit_selection)

    def go_back(self):
        """Handle back button click"""
        reply = QMessageBox.question(
            self, 'Confirm Exit',
            'Are you sure you want to go back?',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            # Close the current window
            self.close()

    # ----------------------------------------------------------------
    #                           UI HELPERS
    # ----------------------------------------------------------------
    def get_combo_style(self):
        return """
            QComboBox {
                font-size: 16px;
                color: #333;
                padding: 12px;
                border: 2px solid #2c5e2e;
                border-radius: 8px;
                background: white;
                min-width: 200px;
            }
            QComboBox::drop-down {
                border-left: 2px solid #2c5e2e;
                width: 40px;
            }
        """

    def get_input_style(self):
        return """
            QLineEdit {
                font-size: 16px;
                color: #333;
                padding: 12px;
                border: 2px solid #2c5e2e;
                border-radius: 8px;
                background: white;
                min-width: 300px;
            }
        """

    def get_button_style(self):
        return """
            QPushButton {
                background-color: #2c5e2e;
                color: white;
                font-size: 16px;
                font-weight: bold;
                padding: 14px 30px;
                border-radius: 8px;
                border: none;
            }
            QPushButton:hover {
                background-color: #1e4020;
            }
        """

    def create_summary_cards(self, layout):
        summary_layout = QHBoxLayout()
        self.avg_card = self.create_summary_card("📊", "Average Price", "#e8f5e9")
        self.high_card = self.create_summary_card("🚀", "Highest Price", "#fff3e0")
        self.low_card = self.create_summary_card("📉", "Lowest Price", "#ffebee")
        summary_layout.addWidget(self.avg_card)
        summary_layout.addWidget(self.high_card)
        summary_layout.addWidget(self.low_card)
        layout.addLayout(summary_layout)

    def create_summary_card(self, icon, title, color):
        card = QFrame()
        card.setStyleSheet(f"""
            background-color: {color};
            border-radius: 12px;
            padding: 20px;
        """)
        layout = QVBoxLayout(card)
        layout.setSpacing(12)
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet("font-size: 28px;")
        
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; color: #444; font-weight: bold;")
        
        value_label = QLabel("₹0")
        value_label.setStyleSheet("font-size: 20px; color: #1e4020; font-weight: bold;")
        
        layout.addWidget(icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(value_label, alignment=Qt.AlignmentFlag.AlignCenter)
        
        return card

    def create_price_table(self, layout):
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        # We'll update the 4th column header dynamically (kg/q/t)
        self.table.setHorizontalHeaderLabels(["State", "District", "Market", "Price (₹/q)", "Trend"])
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.table.setStyleSheet("""
            QTableWidget {
                background: white;
                border: 2px solid #2c5e2e;
                border-radius: 12px;
                gridline-color: #ddd;
            }
            QHeaderView::section {
                background-color: #2c5e2e;
                color: white;
                padding: 16px;
                font-size: 16px;
                font-weight: bold;
                border: none;
            }
            QTableWidget::item {
                color: #333;
                padding: 12px;
                font-size: 15px;
                border-bottom: 1px solid #eee;
            }
        """)
        layout.addWidget(self.table)

    # ----------------------------------------------------------------
    #                      PRICE UNIT SELECTION
    # ----------------------------------------------------------------
    def update_unit_selection(self):
        """Update selected_unit and refresh table/summary accordingly."""
        self.selected_unit = self.unit_dropdown.currentText()
        # Also update the table header label to reflect the selected unit
        unit_label = {
            "Quintal": "Price (₹/q)",
            "Kilogram": "Price (₹/kg)",
            "Tonne": "Price (₹/t)"
        }.get(self.selected_unit, "Price")

        self.table.setHorizontalHeaderItem(3, QTableWidgetItem(unit_label))
        self.populate_table()

    def convert_price(self, base_price, unit):
        """
        Convert price from ₹/quintal (base) to:
         - Kilogram (kg): 1 quintal = 100 kg => price / 100
         - Quintal (q): no change
         - Tonne (t): 1 tonne = 10 quintals => price * 10
        """
        if unit == "Kilogram":
            return base_price / 100.0
        elif unit == "Tonne":
            return base_price * 10.0
        # Default: Quintal
        return base_price

    # ----------------------------------------------------------------
    #                    TABLE POPULATION & LOGIC
    # ----------------------------------------------------------------
    def populate_table(self):
        # Get user selections
        crop = self.crop_dropdown.currentData()
        selected_state = self.state_dropdown.currentData()  # None if "Select State"
        district = self.district_input.text().strip()
        market = self.market_input.text().strip()

        # Fetch filtered data (from data.gov.in or fallback)
        prices = self.get_filtered_data(crop, selected_state, district, market)

        # Update the table
        self.table.setRowCount(0)
        price_values = []

        for row, data in enumerate(prices):
            self.table.insertRow(row)
            
            # Convert the base price (assumed ₹/quintal) to user-selected unit
            base_price_str = data["price"].replace("₹", "").replace(",", "")
            try:
                base_price_val = float(base_price_str)  # Price in ₹ per quintal
            except ValueError:
                base_price_val = 0.0

            converted_price = self.convert_price(base_price_val, self.selected_unit)
            display_price = f"₹{converted_price:,.2f}"

            items = [
                QTableWidgetItem(data["state"]),
                QTableWidgetItem(data["district"]),
                QTableWidgetItem(data["market"]),
                QTableWidgetItem(display_price),
                QTableWidgetItem(data["trend"])
            ]

            for col, item in enumerate(items):
                # Make table cells read-only
                item.setFlags(item.flags() ^ Qt.ItemFlag.ItemIsEditable)
                
                # Trend coloring
                if col == 4:  # Trend column
                    color = "#1e4020" if "📈" in data["trend"] else "#d32f2f" if "📉" in data["trend"] else "#666666"
                    item.setForeground(QColor(color))

                self.table.setItem(row, col, item)

            price_values.append(converted_price)

        # Update summary cards
        if price_values:
            avg = sum(price_values) / len(price_values)
            self.avg_card.layout().itemAt(2).widget().setText(f"₹{avg:,.2f}")
            self.high_card.layout().itemAt(2).widget().setText(f"₹{max(price_values):,.2f}")
            self.low_card.layout().itemAt(2).widget().setText(f"₹{min(price_values):,.2f}")
        else:
            # If no data, reset summary
            self.avg_card.layout().itemAt(2).widget().setText("₹0")
            self.high_card.layout().itemAt(2).widget().setText("₹0")
            self.low_card.layout().itemAt(2).widget().setText("₹0")

        # Toggle columns (existing logic)
        self.toggle_columns(selected_state, district, market)

    def toggle_columns(self, state, district, market):
        """
        Dynamically show/hide columns based on user selection:
         1) Only State or No State => Show only State column
         2) State + District => Show State & District columns
         3) State + District + Market OR Only Market => Show all 3 columns
        """
        # (Columns: 0=State, 1=District, 2=Market, 3=Price, 4=Trend)
        self.table.setColumnHidden(1, True)  # District
        self.table.setColumnHidden(2, True)  # Market

        # Case 1: If user has not selected a state (None) or only selected a state
        if (not state and not district and not market) or (state and not district and not market):
            # Show only State column
            self.table.setColumnHidden(0, False)
        # Case 2: State + District (but no Market)
        elif state and district and not market:
            # Show State & District columns
            self.table.setColumnHidden(0, False)  # State
            self.table.setColumnHidden(1, False)  # District
        # Case 3: If user selects Market or (State+District+Market)
        else:
            # Show State, District, and Market columns
            self.table.setColumnHidden(0, False)
            self.table.setColumnHidden(1, False)
            self.table.setColumnHidden(2, False)

    # ----------------------------------------------------------------
    #                       DATA FETCHING
    # ----------------------------------------------------------------
    def get_filtered_data(self, crop, state, district, market):
        """
        Attempt to fetch data from data.gov.in using self.api_endpoint and self.api_key.
        If the request fails or no data is returned, fallback to sample_data.

        Because the data.gov.in resource might not be active or might require specific
        filters, this code may return an error or empty data. If so, we show sample_data.
        
        The JSON is expected to have fields:
          "state", "district", "market", "price", "trend"
        If your real data has different keys, adjust accordingly.
        """
        try:
            # We'll map "crop" to the "commodity" filter, as data.gov.in uses "filters[commodity]" for these.
            # Also "filters[state]" for states, etc., if supported by this dataset.
            # Some data.gov.in endpoints require you to specify filters in a certain way.
            params = {
                "api-key": self.api_key,
                "format": "json",
                "offset": 0,
                "limit": 10
            }

            # If the dataset supports filtering by commodity/state/district/market:
            if crop:
                params["filters[commodity]"] = crop
            if state:
                params["filters[state]"] = state
            # data.gov.in might not have direct "district" or "market" filters, but let's attempt:
            if district:
                params["filters[district]"] = district
            if market:
                params["filters[market]"] = market

            response = requests.get(self.api_endpoint, params=params, timeout=10)
            if response.status_code == 200:
                # Data.gov.in responses typically have a structure like:
                # {
                #   "records": [
                #       {
                #           "state": "Punjab",
                #           "district": "Amritsar",
                #           "commodity": "Wheat",
                #           "market": "Amritsar Main Mandi",
                #           "min_price": "2100",
                #           "max_price": "2150",
                #           "modal_price": "2150"
                #           ...
                #       },
                #       ...
                #   ]
                # }
                # We'll parse "records" and map them to our expected fields.
                raw_data = response.json()
                if "records" in raw_data and isinstance(raw_data["records"], list):
                    final_data = []
                    for rec in raw_data["records"]:
                        # We'll use "modal_price" as "price" (in ₹/quintal),
                        # and create a dummy "trend" or just "➖" if not available.
                        # Adjust as needed based on real fields.
                        state_val = rec.get("state", "N/A")
                        district_val = rec.get("district", "N/A")
                        market_val = rec.get("market", "N/A")
                        # Commodity can be rec.get("commodity")
                        modal_price = rec.get("modal_price", "0")
                        # We assume no direct "trend" field from data.gov.in,
                        # so let's set a placeholder or calculate if needed.
                        # For now, let's just do "➖ 0.0%" or something similar.
                        trend_val = "➖ 0.0%"

                        # Construct the item in the format we need
                        final_data.append({
                            "state": state_val,
                            "district": district_val,
                            "market": market_val,
                            "price": f"₹{modal_price}",
                            "trend": trend_val
                        })
                    
                    if final_data:
                        return final_data

            else:
                print(f"Request failed. Status code: {response.status_code}")
                print("Response:", response.text)

        except Exception as e:
            print(f"API fetch failed: {e}")

        # ------------------- Fallback to sample data -------------------
        sample_data = [
            {
                "crop": "Wheat",
                "state": "Punjab",
                "district": "Amritsar",
                "market": "Amritsar Main Mandi",
                "price": "₹2,150",
                "trend": "📈 2.5%"
            },
            {
                "crop": "Wheat",
                "state": "Uttar Pradesh",
                "district": "Agra",
                "market": "Agra Wholesale Market",
                "price": "₹2,080",
                "trend": "➖ 0.0%"
            },
            {
                "crop": "Rice",
                "state": "Andhra Pradesh",
                "district": "Guntur",
                "market": "Guntur Market Yard",
                "price": "₹3,400",
                "trend": "📈 1.8%"
            },
            {
                "crop": "Rice",
                "state": "Telangana",
                "district": "Hyderabad",
                "market": "Hyderabad Mandi",
                "price": "₹3,250",
                "trend": "📉 -1.2%"
            }
        ]

        # Filter the fallback data with the same logic
        filtered = []
        for item in sample_data:
            # If user picked a crop, match "item['crop']"
            if crop and item.get("crop") != crop:
                continue
            if state and item["state"] != state:
                continue
            if district and district.lower() not in item["district"].lower():
                continue
            if market and market.lower() not in item["market"].lower():
                continue
            filtered.append(item)
        return filtered

    def refresh_prices(self):
        self.populate_table()


# ---------------------- MAIN EXECUTION ----------------------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarketPriceWindow()
    window.showMaximized()
    sys.exit(app.exec())
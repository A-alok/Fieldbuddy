# FieldBuddy - Smart Agriculture Assistant

FieldBuddy is a comprehensive agricultural assistance application that helps farmers with crop recommendations, weather forecasting, market prices, and more.

## Features

- 🌱 Smart Crop Recommendation System
- 🌦️ Weather Forecasting and Analysis
- 💰 Market Price Tracking
- 📊 Crop Details and Information
- 🤖 AI-Powered Chatbot Assistant
- 👤 User Profile Management

## Prerequisites

- Python 3.8 or higher
- MySQL Server
- Tesseract OCR (for PDF processing)
- Poppler (for PDF to image conversion)

## Installation

1. Clone the repository:
```bash
git clone https://github.com/yourusername/fieldbuddy.git
cd fieldbuddy
```

2. Create and activate a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Set up environment variables:
```bash
cp .env.example .env
```
Edit the `.env` file with your configuration values.

5. Set up the database:
```sql
CREATE DATABASE fieldbuddy;
```

6. Run the application:
```bash
python main.py
```

## Project Structure

```
fieldbuddy/
├── config.py           # Configuration management
├── db_manager.py       # Database operations
├── utils.py           # Utility functions
├── Recommend.py       # Crop recommendation system
├── weather.py         # Weather forecasting
├── marketPrice.py     # Market price tracking
├── detail.py          # Crop details
├── Chatbot.py         # AI chatbot
├── login2.py          # Authentication
├── home_modified.py   # Main dashboard
├── profile_dropdown.py # User profile
├── file_processor.py  # File processing utilities
├── data/              # Data files
├── images/            # Image assets
└── logs/              # Application logs
```

## Security Features

- Password hashing using bcrypt
- SQL injection prevention
- Input validation and sanitization
- API key management
- Rate limiting
- Session management

## Performance Optimizations

- Database connection pooling
- Result caching
- Efficient file handling
- Resource cleanup
- Background processing

## Contributing

1. Fork the repository
2. Create a feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support, please open an issue in the GitHub repository or contact the development team.

## Acknowledgments

- OpenWeather API
- data.gov.in API
- Google Earth Engine
- Various open-source libraries 
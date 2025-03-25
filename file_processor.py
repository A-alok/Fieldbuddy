import pdfplumber
import re
from pdf2image import convert_from_path
import pytesseract
import pandas as pd
import json
import csv
from io import StringIO
import chardet

class FileProcessor:
    def process_file(self, file_path):
        """
        Process the uploaded file and extract soil parameters.
        Supports PDF, CSV, Excel, JSON, and text files.
        """
        if file_path.endswith('.pdf'):
            return self.process_pdf(file_path)
        elif file_path.endswith(('.csv', '.xls', '.xlsx')):
            return self.process_tabular(file_path)
        elif file_path.endswith('.json'):
            return self.process_json(file_path)
        elif file_path.endswith('.txt'):
            return self.process_text(file_path)
        else:
            raise ValueError("Unsupported file format")

    def process_pdf(self, pdf_path):
        """
        Extract text from a PDF file and extract N, P, K, and pH values.
        """
        text = self.extract_text_from_pdf(pdf_path)
        return self.extract_npk_ph(text)

    def extract_text_from_pdf(self, pdf_path):
        """
        Extract text from a PDF file using pdfplumber.
        If no text is found, use OCR (pytesseract) for scanned PDFs.
        """
        extracted_text = ""

        # Extract text using pdfplumber
        with pdfplumber.open(pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    extracted_text += text + "\n"

        # If no text is found, use OCR for scanned PDFs
        if not extracted_text.strip():
            images = convert_from_path(pdf_path)
            for img in images:
                extracted_text += pytesseract.image_to_string(img) + "\n"

        return extracted_text

    def extract_npk_ph(self, text):
        """
        Extract N, P, K, and pH values from text using regex patterns.
        """
        # Define regex patterns to handle different report formats
        nitrogen_patterns = [
            r"Nitrate\s*NO3-N\s*ppm\s*(\d+)",  # Pattern 1
            r"Nitrogen\s*[:=]?\s*([\d.]+)",  # Pattern 2
            r"N\s*\(?ppm\)?\s*[:=]?\s*([\d.]+)",  # Pattern 3
        ]

        phosphorus_patterns = [
            r"Olsen Phosphorus\s*ppm P\s*(\d+)",  # Pattern 1
            r"Phosphorus\s*[:=]?\s*([\d.]+)",  # Pattern 2
            r"P\s*\(?ppm\)?\s*[:=]?\s*([\d.]+)",  # Pattern 3
        ]

        potassium_patterns = [
            r"Potassium\s*ppm K\s*(\d+)",  # Pattern 1
            r"K\s*\(?ppm\)?\s*[:=]?\s*([\d.]+)",  # Pattern 2
            r"K2O\s*[:=]?\s*([\d.]+)",  # Pattern 3
        ]

        ph_patterns = [
            r"pH\s*[:=]?\s*([\d.]+)",  # Pattern 1
            r"Soil pH\s*([\d.]+)",  # Pattern 2
        ]

        # Function to search multiple regex patterns
        def search_patterns(patterns, text):
            for pattern in patterns:
                match = re.search(pattern, text, re.IGNORECASE)
                if match:
                    return match.group(1)
            return "Not found"

        # Extract values
        nitrogen = search_patterns(nitrogen_patterns, text)
        phosphorus = search_patterns(phosphorus_patterns, text)
        potassium = search_patterns(potassium_patterns, text)
        ph_value = search_patterns(ph_patterns, text)

        return {
            "nitrogen": nitrogen,
            "phosphorus": phosphorus,
            "potassium": potassium,
            "ph": ph_value,
        }

    def process_tabular(self, file_path):
        """
        Process CSV or Excel files to extract soil parameters.
        """
        if file_path.endswith('.csv'):
            # Detect file encoding
            with open(file_path, 'rb') as f:
                result = chardet.detect(f.read())
                encoding = result['encoding']
            df = pd.read_csv(file_path, encoding=encoding)
        else:
            df = pd.read_excel(file_path)

        # Normalize column names
        df.columns = df.columns.str.lower().str.replace(' ', '')
        data = df.iloc[0].to_dict()

        # Map column names to expected keys
        normalized_data = {}
        for key, value in data.items():
            if 'nitrogen' in key or 'n' == key:
                normalized_data['nitrogen'] = value
            elif 'phosphorus' in key or 'p' == key:
                normalized_data['phosphorus'] = value
            elif 'potassium' in key or 'k' == key:
                normalized_data['potassium'] = value
            elif 'ph' in key:
                normalized_data['ph'] = value

        return normalized_data

    def process_json(self, file_path):
        """
        Process JSON files to extract soil parameters.
        """
        with open(file_path, 'r') as f:
            data = json.load(f)

        if isinstance(data, list):
            data = data[0]
        elif not isinstance(data, dict):
            raise ValueError("Invalid JSON format")

        # Normalize keys
        normalized_data = {k.lower().replace(' ', ''): v for k, v in data.items()}
        return normalized_data

    def process_text(self, file_path):
        """
        Process text files to extract soil parameters.
        """
        with open(file_path, 'rb') as f:
            result = chardet.detect(f.read())
            encoding = result['encoding']
        with open(file_path, 'r', encoding=encoding) as f:
            text = f.read()

        data = {}
        for line in text.splitlines():
            if ':' in line:
                key, value = line.strip().split(':', 1)
                data[key.strip().lower()] = value.strip()
            elif '=' in line:
                key, value = line.strip().split('=', 1)
                data[key.strip().lower()] = value.strip()
            elif '-' in line:
                key, value = line.strip().split('-', 1)
                data[key.strip().lower()] = value.strip()

        return data
"""
PDF processing utilities for extracting health data
"""

import io
import re
from typing import Dict, Any, Optional, List
import fitz  # PyMuPDF
import pdfplumber
from PIL import Image
import pytesseract

class PDFProcessor:
    """PDF processing for health report extraction"""
    
    def __init__(self):
        self.health_keywords = {
            'age': [
                r'age[:\s]*(\d+)', 
                r'(\d+)\s*years?\s*old',
                r'age[:\s]*(\d+)\s*years?',
                r'(\d+)\s*yr',
                r'age[:\s]*(\d+)\s*yr'
            ],
            'cholesterol': [
                r'cholesterol[:\s]*(\d+)', 
                r'total\s*cholesterol[:\s]*(\d+)',
                r'chol[:\s]*(\d+)',
                r'tc[:\s]*(\d+)',
                r'cholesterol\s*level[:\s]*(\d+)',
                r'(\d+)\s*mg/dl\s*cholesterol',
                r'cholesterol[:\s]*(\d+)\s*mg/dl'
            ],
            'blood_pressure': [
                r'blood\s*pressure[:\s]*(\d+)', 
                r'bp[:\s]*(\d+)', 
                r'(\d+)/(\d+)\s*mmhg',
                r'(\d+)\s*/\s*(\d+)',
                r'systolic[:\s]*(\d+)',
                r'diastolic[:\s]*(\d+)',
                r'pressure[:\s]*(\d+)'
            ],
            'heart_rate': [
                r'heart\s*rate[:\s]*(\d+)', 
                r'pulse[:\s]*(\d+)', 
                r'hr[:\s]*(\d+)',
                r'pulse\s*rate[:\s]*(\d+)',
                r'heart\s*beat[:\s]*(\d+)',
                r'(\d+)\s*bpm',
                r'rate[:\s]*(\d+)\s*bpm'
            ],
            'blood_sugar': [
                r'blood\s*sugar[:\s]*(\d+)', 
                r'glucose[:\s]*(\d+)', 
                r'fbs[:\s]*(\d+)',
                r'fasting\s*glucose[:\s]*(\d+)',
                r'glucose\s*level[:\s]*(\d+)',
                r'(\d+)\s*mg/dl\s*glucose',
                r'sugar[:\s]*(\d+)\s*mg/dl'
            ],
            'gender': [
                r'gender[:\s]*(male|female)', 
                r'sex[:\s]*(male|female)',
                r'patient[:\s]*(male|female)',
                r'(male|female)\s*patient'
            ],
            'smoking': [
                r'smoking[:\s]*(yes|no|never|former|current)', 
                r'smoker[:\s]*(yes|no)',
                r'tobacco[:\s]*(yes|no|never|former|current)',
                r'cigarette[:\s]*(yes|no|never|former|current)',
                r'smoke[:\s]*(yes|no|never|former|current)'
            ],
            'diabetes': [
                r'diabetes[:\s]*(yes|no)', 
                r'diabetic[:\s]*(yes|no)',
                r'dm[:\s]*(yes|no)',
                r'diabetes\s*mellitus[:\s]*(yes|no)',
                r'type\s*2\s*diabetes[:\s]*(yes|no)'
            ],
            'obesity': [
                r'obesity[:\s]*(yes|no)', 
                r'obese[:\s]*(yes|no)', 
                r'bmi[:\s]*(\d+\.?\d*)',
                r'body\s*mass\s*index[:\s]*(\d+\.?\d*)',
                r'weight[:\s]*(\d+)\s*kg',
                r'overweight[:\s]*(yes|no)'
            ],
            'family_history': [
                r'family\s*history[:\s]*(yes|no)', 
                r'hereditary[:\s]*(yes|no)',
                r'family\s*history\s*of\s*heart\s*disease[:\s]*(yes|no)',
                r'fh[:\s]*(yes|no)',
                r'genetic[:\s]*(yes|no)'
            ],
            'exercise': [
                r'exercise[:\s]*(\d+)', 
                r'physical\s*activity[:\s]*(\d+)',
                r'workout[:\s]*(\d+)',
                r'fitness[:\s]*(\d+)',
                r'activity[:\s]*(\d+)',
                r'(\d+)\s*hours?\s*per\s*week',
                r'(\d+)\s*hours?\s*exercise'
            ],
            'stress': [
                r'stress[:\s]*(\d+)', 
                r'stress\s*level[:\s]*(\d+)',
                r'anxiety[:\s]*(\d+)',
                r'mental\s*stress[:\s]*(\d+)',
                r'psychological[:\s]*(\d+)'
            ],
            'chest_pain': [
                r'chest\s*pain[:\s]*(yes|no)', 
                r'angina[:\s]*(yes|no)',
                r'chest\s*discomfort[:\s]*(yes|no)',
                r'cardiac\s*pain[:\s]*(yes|no)',
                r'chest\s*tightness[:\s]*(yes|no)'
            ],
            'alcohol': [
                r'alcohol[:\s]*(none|moderate|heavy)', 
                r'drinking[:\s]*(none|moderate|heavy)',
                r'alcohol\s*consumption[:\s]*(none|moderate|heavy)',
                r'drinks[:\s]*(none|moderate|heavy)',
                r'ethanol[:\s]*(none|moderate|heavy)'
            ]
        }
        
        # Common OCR misreadings for numbers
        self.ocr_corrections = {
            '0': ['O', 'o', 'Q', 'D'],
            '1': ['I', 'l', '|', '!'],
            '2': ['Z', 'z'],
            '3': ['B', 'E'],
            '4': ['A', 'h'],
            '5': ['S', 's'],
            '6': ['G', 'b'],
            '7': ['T', 't'],
            '8': ['B', 'g'],
            '9': ['g', 'q', 'p']
        }
        
        # Medical value ranges for validation
        self.medical_ranges = {
            'age': (18, 120),
            'cholesterol': (100, 600),
            'blood_pressure': (60, 250),
            'heart_rate': (40, 200),
            'blood_sugar': (70, 300),
            'exercise': (0, 24),
            'stress': (1, 10)
        }
    
    def _correct_ocr_number(self, text: str) -> str:
        """Correct common OCR misreadings in numbers"""
        corrected = text
        for digit, alternatives in self.ocr_corrections.items():
            for alt in alternatives:
                corrected = corrected.replace(alt, digit)
        return corrected
    
    def _extract_number_with_correction(self, text: str, field_name: str) -> Optional[int]:
        """Extract and correct numbers from text"""
        # First try direct extraction
        numbers = re.findall(r'\d+', text)
        if numbers:
            for num_str in numbers:
                corrected_num = self._correct_ocr_number(num_str)
                try:
                    num = int(corrected_num)
                    # Validate against medical ranges
                    if field_name in self.medical_ranges:
                        min_val, max_val = self.medical_ranges[field_name]
                        if min_val <= num <= max_val:
                            return num
                    else:
                        return num
                except ValueError:
                    continue
        
        # Try to find numbers with units
        unit_patterns = {
            'cholesterol': r'(\d+)\s*mg/dl',
            'blood_pressure': r'(\d+)\s*mmhg',
            'heart_rate': r'(\d+)\s*bpm',
            'blood_sugar': r'(\d+)\s*mg/dl'
        }
        
        if field_name in unit_patterns:
            matches = re.findall(unit_patterns[field_name], text, re.IGNORECASE)
            if matches:
                try:
                    num = int(self._correct_ocr_number(matches[0]))
                    if field_name in self.medical_ranges:
                        min_val, max_val = self.medical_ranges[field_name]
                        if min_val <= num <= max_val:
                            return num
                except ValueError:
                    pass
        
        return None
    
    def _extract_blood_pressure(self, text: str) -> Optional[int]:
        """Extract blood pressure (systolic) from text"""
        # Try different BP formats
        patterns = [
            r'(\d+)/(\d+)',  # 120/80
            r'(\d+)\s*/\s*(\d+)',  # 120 / 80
            r'(\d+)\s*-\s*(\d+)',  # 120-80
            r'systolic[:\s]*(\d+)',  # systolic: 120
            r'bp[:\s]*(\d+)',  # bp: 120
        ]
        
        for pattern in patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                try:
                    if isinstance(matches[0], tuple):
                        systolic = int(self._correct_ocr_number(matches[0][0]))
                    else:
                        systolic = int(self._correct_ocr_number(matches[0]))
                    
                    # Validate systolic pressure
                    if 60 <= systolic <= 250:
                        return systolic
                except ValueError:
                    continue
        
        return None
    
    def extract_from_pdf(self, pdf_content: bytes) -> Dict[str, Any]:
        """
        Extract health data from PDF content
        
        Args:
            pdf_content: PDF file content as bytes
            
        Returns:
            Dictionary with extracted health data
        """
        try:
            # Try pdfplumber first
            extracted_data = self._extract_with_pdfplumber(pdf_content)
            if extracted_data:
                return extracted_data
            
            # Fallback to PyMuPDF
            extracted_data = self._extract_with_pymupdf(pdf_content)
            if extracted_data:
                return extracted_data
            
            return {}
            
        except Exception as e:
            print(f"Error extracting from PDF: {e}")
            return {}
    
    def _extract_with_pdfplumber(self, pdf_content: bytes) -> Optional[Dict[str, Any]]:
        """Extract text using pdfplumber"""
        try:
            with pdfplumber.open(io.BytesIO(pdf_content)) as pdf:
                text = ""
                for page in pdf.pages:
                    text += page.extract_text() or ""
                
                return self._parse_text(text)
                
        except Exception as e:
            print(f"Error with pdfplumber: {e}")
            return None
    
    def _extract_with_pymupdf(self, pdf_content: bytes) -> Optional[Dict[str, Any]]:
        """Extract text using PyMuPDF"""
        try:
            doc = fitz.open(stream=pdf_content, filetype="pdf")
            text = ""
            for page in doc:
                text += page.get_text()
            doc.close()
            
            return self._parse_text(text)
            
        except Exception as e:
            print(f"Error with PyMuPDF: {e}")
            return None
    
    def _parse_text(self, text: str) -> Dict[str, Any]:
        """
        Parse extracted text to find health metrics with intelligent OCR correction
        
        Args:
            text: Extracted text from PDF
            
        Returns:
            Dictionary with parsed health data
        """
        data = {}
        text_lower = text.lower()
        
        # Extract each metric using enhanced patterns
        for metric, patterns in self.health_keywords.items():
            for pattern in patterns:
                match = re.search(pattern, text_lower, re.IGNORECASE)
                if match:
                    if metric in ['age', 'cholesterol', 'heart_rate', 'blood_sugar', 'exercise', 'stress']:
                        # Use intelligent number extraction
                        value = self._extract_number_with_correction(match.group(0), metric)
                        if value:
                            data[metric] = value
                    elif metric == 'blood_pressure':
                        # Special handling for blood pressure
                        value = self._extract_blood_pressure(match.group(0))
                        if value:
                            data[metric] = value
                    elif metric == 'gender':
                        gender = match.group(1).lower()
                        data[metric] = 'Male' if gender == 'male' else 'Female'
                    elif metric in ['smoking', 'diabetes', 'family_history', 'chest_pain']:
                        value = match.group(1).lower()
                        if value in ['yes', 'current']:
                            data[metric] = 'Yes'
                        elif value in ['no', 'never']:
                            data[metric] = 'No'
                        elif value == 'former':
                            data[metric] = 'Former'
                    elif metric == 'alcohol':
                        value = match.group(1).lower()
                        if value == 'none':
                            data[metric] = 'nan'  # Map to training data value
                        elif value == 'moderate':
                            data[metric] = 'Moderate'
                        elif value == 'heavy':
                            data[metric] = 'Heavy'
                    elif metric == 'obesity':
                        # Handle BMI values
                        if 'bmi' in match.group(0).lower():
                            bmi_value = self._extract_number_with_correction(match.group(0), 'bmi')
                            if bmi_value:
                                data[metric] = 'Yes' if bmi_value >= 30 else 'No'
                        else:
                            value = match.group(1).lower()
                            data[metric] = 'Yes' if value in ['yes', 'obese'] else 'No'
                    break
        
        # Try alternative extraction methods for missing critical values
        if 'cholesterol' not in data:
            # Look for cholesterol in different formats
            cholesterol_patterns = [
                r'chol[:\s]*(\d+)',
                r'tc[:\s]*(\d+)',
                r'(\d+)\s*mg/dl',
                r'cholesterol[:\s]*(\d+)'
            ]
            for pattern in cholesterol_patterns:
                matches = re.findall(pattern, text_lower)
                if matches:
                    value = self._extract_number_with_correction(matches[0], 'cholesterol')
                    if value:
                        data['cholesterol'] = value
                        break
        
        if 'blood_pressure' not in data:
            # Look for BP in different formats
            bp_value = self._extract_blood_pressure(text)
            if bp_value:
                data['blood_pressure'] = bp_value
        
        # Set intelligent defaults for missing fields based on context
        defaults = {
            'age': 45,  # More realistic default
            'gender': 'Male',
            'cholesterol': 200,
            'blood_pressure': 120,
            'heart_rate': 72,
            'smoking': 'Never',
            'alcohol': 'nan',
            'exercise': 3,
            'family_history': 'No',
            'diabetes': 'No',
            'obesity': 'No',
            'stress': 5,
            'blood_sugar': 100,
            'chest_pain': 'No'
        }
        
        for key, default_value in defaults.items():
            if key not in data:
                data[key] = default_value
        
        return data
    
    def extract_from_image(self, image_content: bytes) -> Dict[str, Any]:
        """
        Extract health data from image using OCR
        
        Args:
            image_content: Image file content as bytes
            
        Returns:
            Dictionary with extracted health data
        """
        try:
            # Open image
            image = Image.open(io.BytesIO(image_content))
            
            # Extract text using OCR
            text = pytesseract.image_to_string(image)
            
            # Parse extracted text
            return self._parse_text(text)
            
        except Exception as e:
            print(f"Error extracting from image: {e}")
            return {}
    
    def map_to_schema(self, extracted_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Map extracted data to HeartDiseaseInput schema
        
        Args:
            extracted_data: Raw extracted data
            
        Returns:
            Mapped data for schema validation
        """
        mapped_data = {}
        
        # Age - ensure it's within valid range
        age = extracted_data.get('age', 50)
        if age < 18:
            age = 30  # Default to reasonable age if extracted value is too low
        elif age > 120:
            age = 80  # Default to reasonable age if extracted value is too high
        mapped_data['age'] = age
        
        # Gender
        gender = extracted_data.get('gender', 'male')
        if 'female' in gender.lower():
            mapped_data['gender'] = 'Female'
        else:
            mapped_data['gender'] = 'Male'
        
        # Cholesterol - ensure it's within valid range
        cholesterol = extracted_data.get('cholesterol', 200)
        if cholesterol < 100:
            cholesterol = 180  # Default to reasonable cholesterol if extracted value is too low
        elif cholesterol > 600:
            cholesterol = 250  # Default to reasonable cholesterol if extracted value is too high
        mapped_data['cholesterol'] = cholesterol
        
        # Blood pressure - ensure it's within valid range
        blood_pressure = extracted_data.get('blood_pressure', 120)
        if blood_pressure < 60:
            blood_pressure = 110  # Default to reasonable blood pressure if extracted value is too low
        elif blood_pressure > 250:
            blood_pressure = 140  # Default to reasonable blood pressure if extracted value is too high
        mapped_data['blood_pressure'] = blood_pressure
        
        # Heart rate - ensure it's within valid range
        heart_rate = extracted_data.get('heart_rate', 72)
        if heart_rate < 40:
            heart_rate = 70  # Default to reasonable heart rate if extracted value is too low
        elif heart_rate > 200:
            heart_rate = 80  # Default to reasonable heart rate if extracted value is too high
        mapped_data['heart_rate'] = heart_rate
        
        # Smoking
        smoking = extracted_data.get('smoking', 'never')
        if 'current' in smoking.lower():
            mapped_data['smoking'] = 'Current'
        elif 'former' in smoking.lower():
            mapped_data['smoking'] = 'Former'
        else:
            mapped_data['smoking'] = 'Never'
        
        # Alcohol
        alcohol = extracted_data.get('alcohol', 'none')
        if 'heavy' in alcohol.lower():
            mapped_data['alcohol_intake'] = 'Heavy'
        elif 'moderate' in alcohol.lower():
            mapped_data['alcohol_intake'] = 'Moderate'
        else:
            mapped_data['alcohol_intake'] = 'nan'  # Map to training data value
        
        # Exercise hours - ensure it's within valid range
        exercise_hours = extracted_data.get('exercise', 3)
        if exercise_hours < 0:
            exercise_hours = 2  # Default to reasonable exercise hours if extracted value is negative
        elif exercise_hours > 24:
            exercise_hours = 5  # Default to reasonable exercise hours if extracted value is too high
        mapped_data['exercise_hours'] = exercise_hours
        
        # Family history
        family_history = extracted_data.get('family_history', 'no')
        mapped_data['family_history'] = 'yes' in family_history.lower()
        
        # Diabetes
        diabetes = extracted_data.get('diabetes', 'no')
        mapped_data['diabetes'] = 'yes' in diabetes.lower()
        
        # Obesity
        obesity = extracted_data.get('obesity', 'no')
        mapped_data['obesity'] = 'yes' in obesity.lower()
        
        # Stress level - ensure it's within valid range
        stress_level = extracted_data.get('stress', 5)
        if stress_level < 1:
            stress_level = 3  # Default to reasonable stress level if extracted value is too low
        elif stress_level > 10:
            stress_level = 7  # Default to reasonable stress level if extracted value is too high
        mapped_data['stress_level'] = stress_level
        
        # Blood sugar - ensure it's within valid range
        blood_sugar = extracted_data.get('blood_sugar', 100)
        if blood_sugar < 70:
            blood_sugar = 95  # Default to reasonable blood sugar if extracted value is too low
        elif blood_sugar > 300:
            blood_sugar = 120  # Default to reasonable blood sugar if extracted value is too high
        mapped_data['blood_sugar'] = blood_sugar
        
        # Exercise induced angina
        chest_pain = extracted_data.get('chest_pain', 'no')
        mapped_data['exercise_induced_angina'] = 'yes' in chest_pain.lower()
        
        # Chest pain type (default)
        mapped_data['chest_pain_type'] = 'Asymptomatic'
        
        return mapped_data

# Global processor instance
pdf_processor = PDFProcessor()

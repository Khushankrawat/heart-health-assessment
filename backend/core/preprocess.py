"""
Data preprocessing utilities
"""

import pandas as pd
import numpy as np
from typing import Dict, Any, List
from sklearn.preprocessing import LabelEncoder
from .schema import HeartDiseaseInput

class DataPreprocessor:
    """Data preprocessing utilities for heart disease prediction"""
    
    def __init__(self):
        self.label_encoders = {}
        self.feature_meta = None
    
    def load_feature_meta(self, meta_path: str):
        """Load feature metadata"""
        import json
        with open(meta_path, 'r') as f:
            self.feature_meta = json.load(f)
        
        # Recreate label encoders
        if 'label_encoders' in self.feature_meta:
            for col, classes in self.feature_meta['label_encoders'].items():
                le = LabelEncoder()
                le.classes_ = np.array(classes)
                self.label_encoders[col] = le
    
    def preprocess_input(self, input_data: HeartDiseaseInput) -> Dict[str, Any]:
        """
        Preprocess input data for prediction
        
        Args:
            input_data: Pydantic model with input features
            
        Returns:
            Dictionary with preprocessed features
        """
        # Convert to dictionary with enum values
        data_dict = input_data.model_dump()
        
        # Map snake_case to original dataset column names
        column_mapping = {
            'age': 'Age',
            'gender': 'Gender',
            'cholesterol': 'Cholesterol',
            'blood_pressure': 'Blood Pressure',
            'heart_rate': 'Heart Rate',
            'smoking': 'Smoking',
            'alcohol_intake': 'Alcohol Intake',
            'exercise_hours': 'Exercise Hours',
            'family_history': 'Family History',
            'diabetes': 'Diabetes',
            'obesity': 'Obesity',
            'stress_level': 'Stress Level',
            'blood_sugar': 'Blood Sugar',
            'exercise_induced_angina': 'Exercise Induced Angina',
            'chest_pain_type': 'Chest Pain Type'
        }
        
        # Convert to original column names
        mapped_data = {}
        for snake_case_key, original_key in column_mapping.items():
            if snake_case_key in data_dict:
                mapped_data[original_key] = data_dict[snake_case_key]
        
        # Apply label encoding for categorical features
        if self.feature_meta and 'categorical_features' in self.feature_meta:
            for col in self.feature_meta['categorical_features']:
                if col in mapped_data and col in self.label_encoders:
                    try:
                        # Convert boolean to string for encoding
                        value = mapped_data[col]
                        if isinstance(value, bool):
                            value = "Yes" if value else "No"
                        
                        # Convert enum to string if needed
                        if hasattr(value, 'value'):
                            value = value.value
                        elif hasattr(value, '__class__') and 'Enum' in str(value.__class__):
                            # Try to get the enum value
                            try:
                                value = value.value
                            except:
                                value = str(value).split('.')[-1]  # Get the enum name
                        
                        # Encode categorical value
                        encoded_value = self.label_encoders[col].transform([str(value)])[0]
                        mapped_data[col] = encoded_value
                    except ValueError:
                        # Handle unknown categories
                        print(f"Unknown category '{mapped_data[col]}' for feature '{col}'")
                        mapped_data[col] = 0  # Default to first category
        
        return mapped_data
    
    def validate_input_range(self, input_data: HeartDiseaseInput) -> List[str]:
        """
        Validate input data ranges
        
        Args:
            input_data: Input data to validate
            
        Returns:
            List of validation errors
        """
        errors = []
        
        # Age validation
        if input_data.age < 18 or input_data.age > 120:
            errors.append("Age must be between 18 and 120 years")
        
        # Cholesterol validation
        if input_data.cholesterol < 100 or input_data.cholesterol > 600:
            errors.append("Cholesterol must be between 100 and 600 mg/dL")
        
        # Blood pressure validation
        if input_data.blood_pressure < 60 or input_data.blood_pressure > 250:
            errors.append("Blood pressure must be between 60 and 250 mmHg")
        
        # Heart rate validation
        if input_data.heart_rate < 40 or input_data.heart_rate > 200:
            errors.append("Heart rate must be between 40 and 200 bpm")
        
        # Stress level validation
        if input_data.stress_level < 1 or input_data.stress_level > 10:
            errors.append("Stress level must be between 1 and 10")
        
        # Blood sugar validation
        if input_data.blood_sugar < 70 or input_data.blood_sugar > 300:
            errors.append("Blood sugar must be between 70 and 300 mg/dL")
        
        # Exercise hours validation
        if input_data.exercise_hours < 0 or input_data.exercise_hours > 24:
            errors.append("Exercise hours must be between 0 and 24 per week")
        
        return errors

# Global preprocessor instance
preprocessor_instance = DataPreprocessor()

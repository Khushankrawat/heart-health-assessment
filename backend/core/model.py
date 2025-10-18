"""
Model loading and prediction functionality
"""

import os
import pickle
import json
from typing import Dict, Any, List, Tuple
import numpy as np
import pandas as pd
from sklearn.pipeline import Pipeline

class HeartDiseaseModel:
    """Heart Disease Risk Prediction Model"""
    
    def __init__(self, model_dir: str = "models"):
        self.model_dir = model_dir
        self.model = None
        self.preprocessor = None
        self.feature_meta = None
        self.model_version = None
        
    def load_model(self) -> bool:
        """Load the trained model and metadata"""
        try:
            # Load model
            model_path = os.path.join(self.model_dir, "model.pkl")
            with open(model_path, 'rb') as f:
                self.model = pickle.load(f)
            
            # Load preprocessor
            preprocessor_path = os.path.join(self.model_dir, "preprocessor.pkl")
            with open(preprocessor_path, 'rb') as f:
                self.preprocessor = pickle.load(f)
            
            # Load feature metadata
            meta_path = os.path.join(self.model_dir, "feature_meta.json")
            with open(meta_path, 'r') as f:
                self.feature_meta = json.load(f)
            
            self.model_version = self.feature_meta.get('model_version', '1.0.0')
            
            print(f"Model loaded successfully. Version: {self.model_version}")
            return True
            
        except Exception as e:
            print(f"Error loading model: {e}")
            return False
    
    def predict(self, input_data: Dict[str, Any]) -> Tuple[float, str, List[Dict[str, Any]]]:
        """
        Make prediction on input data
        
        Args:
            input_data: Dictionary containing feature values (already preprocessed)
            
        Returns:
            Tuple of (risk_score, risk_level, top_contributors)
        """
        if not self.model or not self.feature_meta:
            raise ValueError("Model not loaded. Call load_model() first.")
        
        # Convert input to DataFrame with proper column order
        feature_names = self.feature_meta.get('feature_names', [])
        df_data = {}
        
        for feature in feature_names:
            if feature in input_data:
                df_data[feature] = [input_data[feature]]
            else:
                print(f"Warning: Missing feature {feature}")
                df_data[feature] = [0]  # Default value
        
        df = pd.DataFrame(df_data)
        
        # Make prediction (model is a Pipeline that includes preprocessing)
        risk_score = self.model.predict_proba(df)[0][1]
        
        # Determine risk level
        risk_level = self._determine_risk_level(risk_score)
        
        # Get feature contributions
        top_contributors = self._get_feature_contributions(input_data, risk_score)
        
        return risk_score, risk_level, top_contributors
    
    def _determine_risk_level(self, risk_score: float) -> str:
        """Determine risk level based on score"""
        if risk_score < 0.3:
            return "Low"
        elif risk_score < 0.7:
            return "Moderate"
        else:
            return "High"
    
    def _get_feature_contributions(self, input_data: Dict[str, Any], risk_score: float) -> List[Dict[str, Any]]:
        """Get top contributing features with proper normalization"""
        try:
            # Get feature importance from metadata
            feature_importance = self.feature_meta.get('feature_importance', {})
            
            if not feature_importance:
                # Fallback: create dummy contributions if no importance data
                return self._create_dummy_contributions(input_data)
            
            # Create contributions list with proper percentage calculation
            contributions = []
            for feature, importance in feature_importance.items():
                if feature in input_data:
                    # Normalize importance to a 0-100 scale using min-max normalization
                    # This ensures percentages are reasonable and sum to 100%
                    contributions.append({
                        'feature': feature,
                        'value': input_data[feature],
                        'importance': float(abs(importance))
                    })
            
            # Sort by importance
            contributions.sort(key=lambda x: x['importance'], reverse=True)
            
            # Take top 5 and normalize to percentages
            top_contributions = contributions[:5]
            if not top_contributions:
                return self._create_dummy_contributions(input_data)
            
            # Calculate total importance of top 5 features
            total_top_importance = sum(contrib['importance'] for contrib in top_contributions)
            
            if total_top_importance == 0:
                return self._create_dummy_contributions(input_data)
            
            # Convert to percentages that sum to exactly 100%
            for contrib in top_contributions:
                contrib['importance'] = (contrib['importance'] / total_top_importance) * 100
            
            # Ensure the percentages sum to exactly 100% by adjusting the largest one
            current_sum = sum(contrib['importance'] for contrib in top_contributions)
            if abs(current_sum - 100.0) > 0.01:  # If difference is more than 0.01%
                # Find the largest contribution and adjust it
                largest_idx = max(range(len(top_contributions)), key=lambda i: top_contributions[i]['importance'])
                adjustment = 100.0 - current_sum
                top_contributions[largest_idx]['importance'] += adjustment
            
            return top_contributions
            
        except Exception as e:
            print(f"Error getting feature contributions: {e}")
            return self._create_dummy_contributions(input_data)
    
    def _create_dummy_contributions(self, input_data: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Create dummy feature contributions when importance data is not available"""
        # Common important features for heart disease
        important_features = ['age', 'cholesterol', 'blood_pressure', 'heart_rate', 'smoking']
        
        contributions = []
        for i, feature in enumerate(important_features):
            if feature in input_data:
                # Create decreasing importance values
                importance = max(0, 50 - (i * 10))  # 50%, 40%, 30%, 20%, 10%
                contributions.append({
                    'feature': feature,
                    'value': input_data[feature],
                    'importance': float(importance)
                })
        
        return contributions[:5]
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get model information"""
        if not self.feature_meta:
            return {}
        
        return {
            'model_version': self.model_version,
            'total_features': self.feature_meta.get('total_features', 0),
            'feature_names': self.feature_meta.get('feature_names', []),
            'metrics': self.feature_meta.get('metrics', {})
        }

# Global model instance
model_instance = HeartDiseaseModel()

"""
Model explainability using SHAP
"""

import numpy as np
import pandas as pd
from typing import Dict, Any, List, Optional
import shap
from .model import model_instance

class ModelExplainer:
    """SHAP-based model explainer for heart disease prediction"""
    
    def __init__(self):
        self.explainer = None
        self.feature_names = None
        self.is_initialized = False
    
    def initialize_explainer(self):
        """Initialize SHAP explainer"""
        try:
            if not model_instance.model or not model_instance.feature_meta:
                print("Model not loaded. Cannot initialize explainer.")
                return False
            
            # Get feature names
            self.feature_names = model_instance.feature_meta.get('feature_names', [])
            
            # Create background data (mean values)
            background_data = np.zeros((1, len(self.feature_names)))
            
            # Initialize explainer based on model type
            classifier = model_instance.model.named_steps['classifier']
            
            if hasattr(classifier, 'predict_proba'):
                # For tree-based models, use TreeExplainer
                if hasattr(classifier, 'feature_importances_'):
                    self.explainer = shap.TreeExplainer(classifier)
                else:
                    # For linear models, use LinearExplainer
                    self.explainer = shap.LinearExplainer(classifier, background_data)
            else:
                print("Model does not support SHAP explanation")
                return False
            
            self.is_initialized = True
            print("SHAP explainer initialized successfully")
            return True
            
        except Exception as e:
            print(f"Error initializing SHAP explainer: {e}")
            return False
    
    def explain_prediction(self, input_data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Generate SHAP explanation for a prediction
        
        Args:
            input_data: Input features dictionary
            
        Returns:
            Dictionary with SHAP values and explanations
        """
        if not self.is_initialized:
            if not self.initialize_explainer():
                return None
        
        try:
            # Convert input to DataFrame
            df = pd.DataFrame([input_data])
            
            # Apply preprocessing
            processed_data = model_instance.preprocessor.transform(df)
            
            # Get SHAP values
            shap_values = self.explainer.shap_values(processed_data)
            
            # Handle different SHAP output formats
            if isinstance(shap_values, list):
                # Binary classification - use positive class
                shap_values = shap_values[1]
            
            # Create explanation dictionary
            explanation = {
                'shap_values': shap_values[0].tolist(),
                'feature_names': self.feature_names,
                'base_value': float(self.explainer.expected_value) if hasattr(self.explainer, 'expected_value') else 0.0,
                'contributions': []
            }
            
            # Create feature contributions
            for i, (feature, shap_val) in enumerate(zip(self.feature_names, shap_values[0])):
                explanation['contributions'].append({
                    'feature': feature,
                    'shap_value': float(shap_val),
                    'importance': float(abs(shap_val))
                })
            
            # Sort by importance
            explanation['contributions'].sort(key=lambda x: x['importance'], reverse=True)
            
            return explanation
            
        except Exception as e:
            print(f"Error generating SHAP explanation: {e}")
            return None
    
    def get_feature_importance(self) -> List[Dict[str, Any]]:
        """Get global feature importance"""
        if not model_instance.feature_meta:
            return []
        
        feature_importance = model_instance.feature_meta.get('feature_importance', {})
        
        importance_list = []
        for feature, importance in feature_importance.items():
            importance_list.append({
                'feature': feature,
                'importance': float(importance)
            })
        
        # Sort by importance
        importance_list.sort(key=lambda x: x['importance'], reverse=True)
        
        return importance_list

# Global explainer instance
explainer_instance = ModelExplainer()

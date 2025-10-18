"""
Prediction API endpoints
"""

from fastapi import APIRouter, HTTPException, Depends
from typing import Dict, Any
from core.schema import HeartDiseaseInput, HeartDiseasePrediction, FeatureContribution, ErrorResponse
from core.model import model_instance, HeartDiseaseModel
from core.preprocess import preprocessor_instance, DataPreprocessor
from core.explain import explainer_instance

router = APIRouter(prefix="/api", tags=["prediction"])

def get_model():
    """Dependency to get model instance"""
    if not model_instance.model:
        raise HTTPException(status_code=500, detail="Model not loaded")
    return model_instance

def get_preprocessor():
    """Dependency to get preprocessor instance"""
    return preprocessor_instance

@router.post("/predict", response_model=HeartDiseasePrediction)
async def predict_heart_disease(
    input_data: HeartDiseaseInput,
    model: HeartDiseaseModel = Depends(get_model),
    preprocessor: DataPreprocessor = Depends(get_preprocessor)
):
    """
    Predict heart disease risk from input features
    
    Args:
        input_data: Heart disease input features
        model: Loaded model instance
        preprocessor: Data preprocessor instance
        
    Returns:
        Heart disease prediction with risk score and explanations
    """
    try:
        # Validate input
        validation_errors = preprocessor.validate_input_range(input_data)
        if validation_errors:
            raise HTTPException(status_code=400, detail=f"Validation errors: {', '.join(validation_errors)}")
        
        # Preprocess input
        processed_data = preprocessor.preprocess_input(input_data)
        
        # Make prediction
        risk_score, risk_level, top_contributors = model.predict(processed_data)
        
        # Generate educational notes
        notes = generate_educational_notes(risk_level, risk_score, top_contributors)
        
        # Create feature contributions
        feature_contributions = [
            FeatureContribution(
                feature=contrib['feature'],
                value=contrib['value'],
                importance=contrib['importance']
            )
            for contrib in top_contributors
        ]
        
        return HeartDiseasePrediction(
            risk_score=risk_score,
            risk_level=risk_level,
            top_contributors=feature_contributions,
            model_version=model.model_version,
            notes=notes
        )
        
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Prediction failed: {str(e)}")

def generate_educational_notes(risk_level: str, risk_score: float, top_contributors: list) -> list:
    """Generate educational notes based on prediction"""
    notes = []
    
    # Risk level specific notes
    if risk_level == "High":
        notes.append("⚠️ High risk detected. Please consult a healthcare professional immediately.")
        notes.append("Consider lifestyle changes: quit smoking, increase exercise, manage stress.")
    elif risk_level == "Moderate":
        notes.append("⚠️ Moderate risk detected. Regular health checkups are recommended.")
        notes.append("Focus on preventive measures: maintain healthy diet, regular exercise.")
    else:
        notes.append("✅ Low risk detected. Continue maintaining a healthy lifestyle.")
        notes.append("Regular exercise and balanced diet help maintain heart health.")
    
    # Feature-specific recommendations
    for contrib in top_contributors[:3]:  # Top 3 contributors
        feature = contrib['feature'].lower()
        if 'age' in feature:
            notes.append("Age is a significant factor. Regular health screenings become more important with age.")
        elif 'smoking' in feature:
            notes.append("Smoking significantly increases heart disease risk. Consider smoking cessation programs.")
        elif 'exercise' in feature:
            notes.append("Regular physical activity helps reduce heart disease risk.")
        elif 'stress' in feature:
            notes.append("High stress levels can impact heart health. Consider stress management techniques.")
        elif 'cholesterol' in feature:
            notes.append("High cholesterol increases heart disease risk. Consider dietary changes and medication.")
        elif 'blood_pressure' in feature:
            notes.append("High blood pressure is a major risk factor. Monitor regularly and consider treatment.")
    
    # General disclaimer
    notes.append("This tool is for educational use only and not for medical diagnosis.")
    
    return notes

@router.get("/model-info")
async def get_model_info(model: HeartDiseaseModel = Depends(get_model)):
    """Get model information and metadata"""
    try:
        model_info = model.get_model_info()
        return model_info
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Failed to get model info: {str(e)}")

@router.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "service": "heart-disease-predictor"}

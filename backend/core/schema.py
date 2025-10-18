"""
Pydantic schemas for Heart Disease Risk Predictor API
"""

from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from enum import Enum

class GenderEnum(str, Enum):
    MALE = "Male"
    FEMALE = "Female"

class SmokingEnum(str, Enum):
    NEVER = "Never"
    FORMER = "Former"
    CURRENT = "Current"

class AlcoholEnum(str, Enum):
    NONE = "nan"  # Map to the actual value in training data
    MODERATE = "Moderate"
    HEAVY = "Heavy"

class ChestPainEnum(str, Enum):
    TYPICAL_ANGINA = "Typical Angina"
    ATYPICAL_ANGINA = "Atypical Angina"
    NON_ANGINAL_PAIN = "Non-anginal Pain"
    ASYMPTOMATIC = "Asymptomatic"

class RiskLevelEnum(str, Enum):
    LOW = "Low"
    MODERATE = "Moderate"
    HIGH = "High"

class HeartDiseaseInput(BaseModel):
    """Input schema for heart disease prediction"""
    age: int = Field(..., ge=18, le=120, description="Age in years")
    gender: GenderEnum = Field(..., description="Gender")
    cholesterol: int = Field(..., ge=100, le=600, description="Cholesterol level (mg/dL)")
    blood_pressure: int = Field(..., ge=60, le=250, description="Blood pressure (mmHg)")
    heart_rate: int = Field(..., ge=40, le=200, description="Resting heart rate (bpm)")
    smoking: SmokingEnum = Field(..., description="Smoking status")
    alcohol_intake: AlcoholEnum = Field(..., description="Alcohol consumption level")
    exercise_hours: int = Field(..., ge=0, le=24, description="Exercise hours per week")
    family_history: bool = Field(..., description="Family history of heart disease")
    diabetes: bool = Field(..., description="Diabetes status")
    obesity: bool = Field(..., description="Obesity status")
    stress_level: int = Field(..., ge=1, le=10, description="Stress level (1-10 scale)")
    blood_sugar: int = Field(..., ge=70, le=300, description="Blood sugar level (mg/dL)")
    exercise_induced_angina: bool = Field(..., description="Exercise induced angina")
    chest_pain_type: ChestPainEnum = Field(..., description="Type of chest pain")

    @validator('age')
    def validate_age(cls, v):
        if v < 18 or v > 120:
            raise ValueError('Age must be between 18 and 120')
        return v

    @validator('cholesterol')
    def validate_cholesterol(cls, v):
        if v < 100 or v > 600:
            raise ValueError('Cholesterol must be between 100 and 600 mg/dL')
        return v

    @validator('blood_pressure')
    def validate_blood_pressure(cls, v):
        if v < 60 or v > 250:
            raise ValueError('Blood pressure must be between 60 and 250 mmHg')
        return v

    @validator('heart_rate')
    def validate_heart_rate(cls, v):
        if v < 40 or v > 200:
            raise ValueError('Heart rate must be between 40 and 200 bpm')
        return v

    @validator('stress_level')
    def validate_stress_level(cls, v):
        if v < 1 or v > 10:
            raise ValueError('Stress level must be between 1 and 10')
        return v

    @validator('blood_sugar')
    def validate_blood_sugar(cls, v):
        if v < 70 or v > 300:
            raise ValueError('Blood sugar must be between 70 and 300 mg/dL')
        return v

class FeatureContribution(BaseModel):
    """Feature contribution for explainability"""
    feature: str = Field(..., description="Feature name")
    value: float = Field(..., description="Contribution value")
    importance: float = Field(..., description="Feature importance")

class HeartDiseasePrediction(BaseModel):
    """Output schema for heart disease prediction"""
    risk_score: float = Field(..., ge=0, le=1, description="Risk probability (0-1)")
    risk_level: RiskLevelEnum = Field(..., description="Risk level category")
    top_contributors: List[FeatureContribution] = Field(..., description="Top contributing features")
    model_version: str = Field(..., description="Model version used")
    notes: List[str] = Field(default_factory=list, description="Educational recommendations")

class UploadResponse(BaseModel):
    """Response schema for file upload"""
    success: bool = Field(..., description="Upload success status")
    message: str = Field(..., description="Response message")
    extracted_data: Optional[HeartDiseaseInput] = Field(None, description="Extracted health data")
    confidence: Optional[float] = Field(None, ge=0, le=1, description="Extraction confidence")

class ErrorResponse(BaseModel):
    """Error response schema"""
    error: str = Field(..., description="Error message")
    detail: Optional[str] = Field(None, description="Detailed error information")

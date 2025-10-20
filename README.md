# Heart Health Assessment

A professional AI-powered web application for cardiovascular risk evaluation using advanced machine learning. Features a modern medical-themed interface with automated health report processing and comprehensive risk analysis.

## Features

- **AI-Powered Prediction**: Uses trained XGBoost/Logistic Regression models for accurate cardiovascular risk assessment
- **Medical Report Upload**: Supports PDF, JPG, and PNG health reports with intelligent data extraction
- **Health Assessment Form**: Comprehensive questionnaire for manual health data entry
- **Explainable AI**: Shows top contributing factors with properly normalized percentages (sum to 100%)
- **Risk Categorization**: Low/Moderate/High risk levels with professional medical recommendations
- **Professional UI**: Medical-themed design inspired by healthcare booking platforms
- **Responsive Design**: Modern interface built with React, TailwindCSS, and shadcn/ui

## Architecture

### Backend (FastAPI)
- **Model Training**: XGBoost classifier with fallback to Logistic Regression
- **API Endpoints**: `/api/predict` and `/api/upload`
- **File Processing**: PDF parsing and OCR for image extraction
- **Data Validation**: Comprehensive input validation and error handling
- **CORS Support**: Configured for frontend integration

### Frontend (React + Vite)
- **Medical Report Upload**: Professional drag-and-drop interface with medical-themed design
- **Health Assessment Form**: Comprehensive questionnaire with medical terminology
- **Cardiovascular Risk Display**: Professional risk visualization with normalized percentages
- **Medical UI Theme**: Healthcare-inspired design with stethoscope icons and medical colors
- **Responsive Design**: Mobile-first approach with professional medical styling

### Machine Learning
- **Model**: XGBoost Classifier (ROC-AUC: 0.95+)
- **Features**: 15 health indicators (age, cholesterol, blood pressure, etc.)
- **Preprocessing**: StandardScaler for numeric features, LabelEncoder for categorical
- **Explainability**: Normalized feature importance percentages (sum to 100%)
- **Risk Assessment**: Professional cardiovascular risk categorization

## Model Performance

- **Accuracy**: 87.3%
- **Precision**: 87.3%
- **Recall**: 87.3%
- **F1-Score**: 87.3%
- **ROC-AUC**: 95.2%

## Tech Stack

### Backend
- **FastAPI**: Modern Python web framework
- **scikit-learn**: Machine learning library
- **XGBoost**: Gradient boosting framework
- **PyMuPDF**: PDF processing
- **pytesseract**: OCR for image processing
- **SHAP**: Model explainability

### Frontend
- **React 18**: UI framework
- **TypeScript**: Type safety
- **Vite**: Build tool
- **TailwindCSS**: Styling
- **shadcn/ui**: Component library
- **Lucide React**: Icons
- **Axios**: HTTP client

## Quick Start

### Prerequisites
- Python 3.8+
- Node.js 16+
- pip and npm

### Local Development

1. **Clone the repository**
   ```bash
   git clone <repository-url>
   cd heart_disease_prediction
   ```

2. **Install Python dependencies**
   ```bash
   pip install -r backend/requirements.txt
   ```

3. **Train the model**
   ```bash
   python scripts/train.py
   ```

4. **Install frontend dependencies**
   ```bash
   cd frontend
   npm install
   ```

5. **Start the backend**
   ```bash
   cd backend
   python app.py
   ```

6. **Start the frontend** (in a new terminal)
   ```bash
   cd frontend
   npm run dev
   ```

7. **Access the application**
   - Frontend: http://localhost:5173 (or next available port)
   - Backend API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Project Structure

```
heart_health_assessment/
├── scripts/
│   └── train.py                 # Model training script
├── backend/
│   ├── app.py                   # FastAPI application
│   ├── requirements.txt         # Python dependencies
│   ├── routers/
│   │   ├── predict.py          # Prediction endpoints
│   │   └── upload.py            # File upload endpoints
│   ├── core/
│   │   ├── model.py            # Model loading and prediction
│   │   ├── preprocess.py       # Data preprocessing
│   │   ├── explain.py          # SHAP explainability
│   │   ├── schema.py           # Pydantic schemas
│   │   ├── pdf.py              # PDF processing
│   │   └── ocr.py              # OCR processing
│   └── models/                 # Trained model artifacts
│       ├── model.pkl
│       ├── preprocessor.pkl
│       └── feature_meta.json
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── UploadCard.tsx   # Medical report upload
│   │   │   ├── ManualForm.tsx   # Health assessment form
│   │   │   ├── ResultCard.tsx   # Risk assessment display
│   │   │   └── ui/              # shadcn/ui components
│   │   ├── lib/
│   │   │   ├── api.ts          # API client
│   │   │   └── utils.ts        # Utility functions
│   │   ├── App.tsx             # Main application
│   │   ├── index.css           # Medical-themed styling
│   │   └── main.tsx            # Entry point
│   ├── package.json
│   └── vite.config.ts
├── heart_disease_dataset.csv   # Training dataset
├── .gitignore                  # Git ignore rules
└── README.md                   # This file
```

## API Documentation

### Endpoints

#### `POST /api/predict`
Predict heart disease risk from input features.

**Request Body:**
```json
{
  "age": 50,
  "gender": "Male",
  "cholesterol": 200,
  "blood_pressure": 120,
  "heart_rate": 72,
  "smoking": "Never",
  "alcohol_intake": "None",
  "exercise_hours": 3,
  "family_history": false,
  "diabetes": false,
  "obesity": false,
  "stress_level": 5,
  "blood_sugar": 100,
  "exercise_induced_angina": false,
  "chest_pain_type": "Asymptomatic"
}
```

**Response:**
```json
{
  "risk_score": 0.25,
  "risk_level": "Low",
  "top_contributors": [
    {
      "feature": "Age",
      "value": 50,
      "importance": 50.8
    },
    {
      "feature": "Gender", 
      "value": 1,
      "importance": 33.9
    }
  ],
  "model_version": "1.0.0",
  "notes": ["Professional medical recommendations..."]
}
```

#### `POST /api/upload`
Upload medical report (PDF/image) for automated data extraction.

**Request:** Multipart form data with file

**Response:**
```json
{
  "success": true,
  "message": "Medical data extracted successfully",
  "extracted_data": { /* HeartDiseaseInput */ },
  "confidence": 0.8
}
```

## Configuration

### Environment Variables

The application uses default configurations. For custom setup, you can set:

```bash
# API Configuration
VITE_API_URL=http://localhost:8000/api
API_HOST=0.0.0.0
API_PORT=8000

# Model Configuration
MODEL_PATH=backend/models
MODEL_VERSION=1.0.0

# File Upload
MAX_FILE_SIZE=10485760
ALLOWED_FILE_TYPES=application/pdf,image/jpeg,image/jpg,image/png
```

### Model Training

To retrain the model with new data:

1. **Prepare dataset**
   - Place CSV file in project root
   - Ensure target column is named "Heart Disease"

2. **Run training**
   ```bash
   python scripts/train.py
   ```

3. **Model artifacts** will be saved to `backend/models/`

## Testing

### Manual Testing
1. Upload sample medical reports (PDF/images)
2. Test health assessment form validation
3. Verify cardiovascular risk prediction accuracy
4. Check feature importance percentages sum to 100%
5. Test error handling and edge cases

## Performance

- **Model Inference**: < 100ms
- **File Upload**: < 2s for 10MB files
- **OCR Processing**: < 5s for images
- **PDF Processing**: < 3s for documents

## Security & Privacy

- **No Data Storage**: Uploaded files are processed and discarded
- **Input Validation**: Comprehensive validation on all inputs
- **CORS Protection**: Environment-based configuration for specific origins
- **Error Handling**: Secure error messages without sensitive data
- **Rate Limiting**: Per-IP rate limiting to prevent abuse
- **File Security**: Magic byte validation and content scanning
- **Input Sanitization**: All user inputs sanitized before processing
- **Security Logging**: Comprehensive logging of security events
- **Production Ready**: Environment-based security configuration

See [SECURITY.md](SECURITY.md) for detailed security configuration guide.

## Medical Disclaimer

**This tool is for educational purposes only and should not replace professional medical advice.**

- Always consult qualified healthcare professionals for medical concerns
- Results should not replace medical diagnosis or treatment
- Use at your own risk
- No medical liability assumed

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## Acknowledgments

- Heart disease dataset for model training
- FastAPI and React communities
- shadcn/ui for component library
- Medical UI design inspiration

## Support

For issues and questions:
- Create an issue on GitHub
- Check the documentation
- Review the API docs at `/docs`

---

**Built with love for better cardiovascular health awareness**

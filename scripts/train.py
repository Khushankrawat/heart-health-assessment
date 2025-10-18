#!/usr/bin/env python3
"""
Heart Disease Risk Predictor - Model Training Script

This script trains an XGBoost classifier on the heart disease dataset,
evaluates performance metrics, and saves the trained model artifacts.
"""

import os
import json
import pickle
import warnings
from pathlib import Path
from typing import Dict, Any, Tuple

import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split, StratifiedKFold
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.metrics import (
    accuracy_score, precision_score, recall_score, f1_score,
    roc_auc_score, confusion_matrix, classification_report
)
from sklearn.linear_model import LogisticRegression
import xgboost as xgb

warnings.filterwarnings('ignore')

# Configuration
RANDOM_STATE = 42
TEST_SIZE = 0.15
VAL_SIZE = 0.15
MODEL_VERSION = "1.0.0"

def load_and_prepare_data(file_path: str) -> Tuple[pd.DataFrame, str]:
    """Load dataset and detect target column."""
    print(f"Loading dataset from {file_path}...")
    df = pd.read_csv(file_path)
    
    # Detect target column
    target_candidates = ['Heart Disease', 'heart_disease', 'target', 'output', 'label']
    target_col = None
    
    for col in target_candidates:
        if col in df.columns:
            target_col = col
            break
    
    if target_col is None:
        raise ValueError("Could not find target column. Expected one of: " + str(target_candidates))
    
    print(f"Target column detected: {target_col}")
    print(f"Dataset shape: {df.shape}")
    print(f"Target distribution:\n{df[target_col].value_counts()}")
    
    return df, target_col

def preprocess_features(df: pd.DataFrame, target_col: str) -> Tuple[pd.DataFrame, Dict[str, Any]]:
    """Preprocess features and create metadata."""
    print("Preprocessing features...")
    
    # Separate features and target
    X = df.drop(columns=[target_col])
    y = df[target_col]
    
    # Identify numeric and categorical columns
    numeric_cols = X.select_dtypes(include=[np.number]).columns.tolist()
    categorical_cols = X.select_dtypes(include=['object']).columns.tolist()
    
    print(f"Numeric columns: {numeric_cols}")
    print(f"Categorical columns: {categorical_cols}")
    
    # Handle categorical variables
    label_encoders = {}
    for col in categorical_cols:
        le = LabelEncoder()
        X[col] = le.fit_transform(X[col].astype(str))
        label_encoders[col] = le
    
    # Create feature metadata
    feature_meta = {
        'numeric_features': numeric_cols,
        'categorical_features': categorical_cols,
        'label_encoders': {col: le.classes_.tolist() for col, le in label_encoders.items()},
        'target_column': target_col,
        'model_version': MODEL_VERSION,
        'total_features': len(X.columns),
        'feature_names': X.columns.tolist()
    }
    
    return X, y, feature_meta

def create_preprocessing_pipeline(feature_meta: Dict[str, Any]) -> Pipeline:
    """Create preprocessing pipeline."""
    print("Creating preprocessing pipeline...")
    
    numeric_features = feature_meta['numeric_features']
    categorical_features = feature_meta['categorical_features']
    
    # Preprocessing steps
    numeric_transformer = StandardScaler()
    
    # For categorical features, we'll use the already encoded values
    categorical_transformer = 'passthrough'
    
    # Create column transformer
    preprocessor = ColumnTransformer(
        transformers=[
            ('num', numeric_transformer, numeric_features),
            ('cat', categorical_transformer, categorical_features)
        ]
    )
    
    return preprocessor

def train_model(X_train: pd.DataFrame, y_train: pd.Series, 
                X_val: pd.DataFrame, y_val: pd.Series,
                preprocessor: Pipeline) -> Tuple[Any, Dict[str, float]]:
    """Train XGBoost model with fallback to Logistic Regression."""
    print("Training model...")
    
    # Try XGBoost first
    try:
        print("Attempting to train XGBoost model...")
        model = xgb.XGBClassifier(
            random_state=RANDOM_STATE,
            eval_metric='logloss',
            early_stopping_rounds=10,
            n_estimators=100
        )
        
        # Create full pipeline
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])
        
        # Train with early stopping
        pipeline.fit(
            X_train, y_train,
            classifier__eval_set=[(X_val, y_val)],
            classifier__verbose=False
        )
        
        print("XGBoost model trained successfully!")
        
    except Exception as e:
        print(f"XGBoost failed: {e}")
        print("Falling back to Logistic Regression...")
        
        model = LogisticRegression(random_state=RANDOM_STATE, max_iter=1000)
        pipeline = Pipeline([
            ('preprocessor', preprocessor),
            ('classifier', model)
        ])
        
        pipeline.fit(X_train, y_train)
        print("Logistic Regression model trained successfully!")
    
    # Evaluate on validation set
    y_val_pred = pipeline.predict(X_val)
    y_val_proba = pipeline.predict_proba(X_val)[:, 1]
    
    val_metrics = {
        'accuracy': accuracy_score(y_val, y_val_pred),
        'precision': precision_score(y_val, y_val_pred, average='weighted'),
        'recall': recall_score(y_val, y_val_pred, average='weighted'),
        'f1': f1_score(y_val, y_val_pred, average='weighted'),
        'roc_auc': roc_auc_score(y_val, y_val_proba)
    }
    
    return pipeline, val_metrics

def evaluate_model(pipeline: Pipeline, X_test: pd.DataFrame, y_test: pd.Series) -> Dict[str, Any]:
    """Evaluate model on test set."""
    print("Evaluating model on test set...")
    
    y_pred = pipeline.predict(X_test)
    y_proba = pipeline.predict_proba(X_test)[:, 1]
    
    metrics = {
        'accuracy': accuracy_score(y_test, y_pred),
        'precision': precision_score(y_test, y_pred, average='weighted'),
        'recall': recall_score(y_test, y_pred, average='weighted'),
        'f1': f1_score(y_test, y_pred, average='weighted'),
        'roc_auc': roc_auc_score(y_test, y_proba)
    }
    
    # Confusion matrix
    cm = confusion_matrix(y_test, y_pred)
    metrics['confusion_matrix'] = cm.tolist()
    
    # Classification report
    report = classification_report(y_test, y_pred, output_dict=True)
    metrics['classification_report'] = report
    
    return metrics

def get_feature_importance(pipeline: Pipeline, feature_names: list) -> Dict[str, float]:
    """Extract feature importance if available."""
    try:
        # Try to get feature importance from the classifier
        classifier = pipeline.named_steps['classifier']
        
        if hasattr(classifier, 'feature_importances_'):
            importances = classifier.feature_importances_
        elif hasattr(classifier, 'coef_'):
            # For logistic regression, use absolute coefficients
            importances = np.abs(classifier.coef_[0])
        else:
            return {}
        
        # Create feature importance dictionary
        feature_importance = dict(zip(feature_names, importances))
        
        # Sort by importance
        sorted_importance = dict(sorted(feature_importance.items(), 
                                      key=lambda x: x[1], reverse=True))
        
        return sorted_importance
        
    except Exception as e:
        print(f"Could not extract feature importance: {e}")
        return {}

def save_model_artifacts(pipeline: Pipeline, feature_meta: Dict[str, Any], 
                        metrics: Dict[str, Any], feature_importance: Dict[str, float],
                        output_dir: str):
    """Save model artifacts to disk."""
    print(f"Saving model artifacts to {output_dir}...")
    
    # Create output directory
    os.makedirs(output_dir, exist_ok=True)
    
    # Save model
    model_path = os.path.join(output_dir, 'model.pkl')
    with open(model_path, 'wb') as f:
        pickle.dump(pipeline, f)
    print(f"Model saved to {model_path}")
    
    # Save preprocessor separately
    preprocessor_path = os.path.join(output_dir, 'preprocessor.pkl')
    with open(preprocessor_path, 'wb') as f:
        pickle.dump(pipeline.named_steps['preprocessor'], f)
    print(f"Preprocessor saved to {preprocessor_path}")
    
    # Save feature metadata
    feature_meta['metrics'] = metrics
    feature_meta['feature_importance'] = feature_importance
    
    meta_path = os.path.join(output_dir, 'feature_meta.json')
    with open(meta_path, 'w') as f:
        json.dump(feature_meta, f, indent=2)
    print(f"Feature metadata saved to {meta_path}")

def print_results_summary(metrics: Dict[str, Any], feature_importance: Dict[str, float]):
    """Print training results summary."""
    print("\n" + "="*60)
    print("TRAINING RESULTS SUMMARY")
    print("="*60)
    
    print(f"\nModel Performance Metrics:")
    print(f"  Accuracy:  {metrics['accuracy']:.4f}")
    print(f"  Precision: {metrics['precision']:.4f}")
    print(f"  Recall:   {metrics['recall']:.4f}")
    print(f"  F1-Score: {metrics['f1']:.4f}")
    print(f"  ROC-AUC:  {metrics['roc_auc']:.4f}")
    
    print(f"\nConfusion Matrix:")
    cm = np.array(metrics['confusion_matrix'])
    print(f"  [[{cm[0,0]:3d}, {cm[0,1]:3d}]")
    print(f"   [{cm[1,0]:3d}, {cm[1,1]:3d}]]")
    
    if feature_importance:
        print(f"\nTop 10 Most Important Features:")
        for i, (feature, importance) in enumerate(list(feature_importance.items())[:10]):
            print(f"  {i+1:2d}. {feature:<20} {importance:.4f}")
    
    print("\n" + "="*60)

def main():
    """Main training function."""
    print("Heart Disease Risk Predictor - Model Training")
    print("="*50)
    
    # Paths
    dataset_path = "heart_disease_dataset.csv"
    output_dir = "backend/models"
    
    # Check if dataset exists
    if not os.path.exists(dataset_path):
        raise FileNotFoundError(f"Dataset not found at {dataset_path}")
    
    try:
        # Load and prepare data
        df, target_col = load_and_prepare_data(dataset_path)
        
        # Preprocess features
        X, y, feature_meta = preprocess_features(df, target_col)
        
        # Split data
        print("Splitting data into train/validation/test sets...")
        X_temp, X_test, y_temp, y_test = train_test_split(
            X, y, test_size=TEST_SIZE, random_state=RANDOM_STATE, stratify=y
        )
        
        X_train, X_val, y_train, y_val = train_test_split(
            X_temp, y_temp, test_size=VAL_SIZE/(1-TEST_SIZE), 
            random_state=RANDOM_STATE, stratify=y_temp
        )
        
        print(f"Train set: {X_train.shape[0]} samples")
        print(f"Validation set: {X_val.shape[0]} samples")
        print(f"Test set: {X_test.shape[0]} samples")
        
        # Create preprocessing pipeline
        preprocessor = create_preprocessing_pipeline(feature_meta)
        
        # Train model
        pipeline, val_metrics = train_model(X_train, y_train, X_val, y_val, preprocessor)
        
        # Evaluate on test set
        test_metrics = evaluate_model(pipeline, X_test, y_test)
        
        # Get feature importance
        feature_importance = get_feature_importance(pipeline, feature_meta['feature_names'])
        
        # Save artifacts
        save_model_artifacts(pipeline, feature_meta, test_metrics, feature_importance, output_dir)
        
        # Print results
        print_results_summary(test_metrics, feature_importance)
        
        print(f"\nTraining completed successfully!")
        print(f"Model artifacts saved to: {output_dir}")
        
    except Exception as e:
        print(f"Training failed with error: {e}")
        raise

if __name__ == "__main__":
    main()

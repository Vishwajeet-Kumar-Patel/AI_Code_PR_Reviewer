"""
ML Training Service for Code Review Model

This service handles:
- Data collection from historical reviews
- Feature extraction from code
- Model training and fine-tuning
- Model evaluation and versioning
- A/B testing framework
"""

import asyncio
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Tuple

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, precision_recall_fscore_support, confusion_matrix
from sklearn.model_selection import train_test_split
import joblib
import openai

from app.core.config import settings
from app.db.database import get_db
from sqlalchemy.orm import Session
from sqlalchemy import select

logger = logging.getLogger(__name__)


class MLTrainingService:
    """Service for training and managing ML models for code review"""
    
    def __init__(self):
        self.model_dir = Path("models/trained")
        self.model_dir.mkdir(parents=True, exist_ok=True)
        self.current_model_version = "v1.0.0"
        
    async def collect_training_data(
        self, 
        db: Session,
        days_back: int = 90,
        min_samples: int = 1000
    ) -> pd.DataFrame:
        """
        Collect historical code review data for training
        
        Args:
            db: Database session
            days_back: Number of days to look back
            min_samples: Minimum number of samples required
            
        Returns:
            DataFrame with training features and labels
        """
        logger.info(f"Collecting training data from last {days_back} days...")
        
        cutoff_date = datetime.utcnow() - timedelta(days=days_back)
        
        # Query historical reviews from database
        # This is a simplified version - extend based on your actual schema
        query = """
        SELECT 
            r.id,
            r.pr_number,
            r.repository,
            r.code_quality_score,
            r.security_score,
            r.complexity_score,
            r.lines_added,
            r.lines_deleted,
            r.files_changed,
            r.issues_found,
            r.critical_issues,
            r.security_vulnerabilities,
            r.created_at,
            r.ai_confidence_score,
            r.review_time_seconds
        FROM code_reviews r
        WHERE r.created_at >= :cutoff_date
        AND r.ai_confidence_score IS NOT NULL
        ORDER BY r.created_at DESC
        """
        
        # Execute query and convert to DataFrame
        result = db.execute(query, {"cutoff_date": cutoff_date})
        data = result.fetchall()
        
        if len(data) < min_samples:
            logger.warning(f"Insufficient training data: {len(data)} < {min_samples}")
            return None
            
        df = pd.DataFrame(data, columns=[
            'id', 'pr_number', 'repository', 'code_quality_score',
            'security_score', 'complexity_score', 'lines_added',
            'lines_deleted', 'files_changed', 'issues_found',
            'critical_issues', 'security_vulnerabilities', 'created_at',
            'ai_confidence_score', 'review_time_seconds'
        ])
        
        logger.info(f"Collected {len(df)} training samples")
        return df
    
    def extract_features(self, df: pd.DataFrame) -> Tuple[np.ndarray, np.ndarray]:
        """
        Extract features from raw data for ML training
        
        Args:
            df: Raw data DataFrame
            
        Returns:
            Tuple of (features, labels)
        """
        # Feature engineering
        df['change_ratio'] = df['lines_added'] / (df['lines_deleted'] + 1)
        df['issue_density'] = df['issues_found'] / (df['files_changed'] + 1)
        df['critical_ratio'] = df['critical_issues'] / (df['issues_found'] + 1)
        df['security_risk'] = df['security_vulnerabilities'] * df['security_score']
        
        # Select features for training
        feature_columns = [
            'lines_added',
            'lines_deleted',
            'files_changed',
            'issues_found',
            'critical_issues',
            'security_vulnerabilities',
            'change_ratio',
            'issue_density',
            'critical_ratio',
            'security_risk'
        ]
        
        X = df[feature_columns].fillna(0).values
        
        # Create labels: Binary classification for "needs review" vs "auto-approve"
        # Logic: If code_quality_score < 70 OR security_score < 80 OR critical_issues > 0
        y = ((df['code_quality_score'] < 70) | 
             (df['security_score'] < 80) | 
             (df['critical_issues'] > 0)).astype(int).values
        
        logger.info(f"Extracted features: {X.shape}, Labels: {y.shape}")
        logger.info(f"Class distribution: {np.bincount(y)}")
        
        return X, y
    
    async def train_model(
        self,
        X: np.ndarray,
        y: np.ndarray,
        model_type: str = "gradient_boosting"
    ) -> Dict:
        """
        Train ML model on extracted features
        
        Args:
            X: Feature matrix
            y: Labels
            model_type: Type of model to train
            
        Returns:
            Training results and metrics
        """
        logger.info(f"Training {model_type} model...")
        
        # Split data
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # Select model
        if model_type == "random_forest":
            model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                n_jobs=-1
            )
        elif model_type == "gradient_boosting":
            model = GradientBoostingClassifier(
                n_estimators=100,
                max_depth=5,
                learning_rate=0.1,
                random_state=42
            )
        else:
            raise ValueError(f"Unknown model type: {model_type}")
        
        # Train model
        model.fit(X_train, y_train)
        
        # Evaluate
        y_pred = model.predict(X_test)
        accuracy = accuracy_score(y_test, y_pred)
        precision, recall, f1, _ = precision_recall_fscore_support(
            y_test, y_pred, average='binary'
        )
        
        results = {
            'model_type': model_type,
            'version': self.current_model_version,
            'accuracy': float(accuracy),
            'precision': float(precision),
            'recall': float(recall),
            'f1_score': float(f1),
            'training_samples': len(X_train),
            'test_samples': len(X_test),
            'trained_at': datetime.utcnow().isoformat(),
            'confusion_matrix': confusion_matrix(y_test, y_pred).tolist()
        }
        
        # Save model
        model_path = self.model_dir / f"{model_type}_{self.current_model_version}.pkl"
        joblib.dump(model, model_path)
        
        # Save metadata
        metadata_path = self.model_dir / f"{model_type}_{self.current_model_version}_metadata.json"
        with open(metadata_path, 'w') as f:
            json.dump(results, f, indent=2)
        
        logger.info(f"Model trained successfully: Accuracy={accuracy:.3f}, F1={f1:.3f}")
        logger.info(f"Model saved to: {model_path}")
        
        return results
    
    async def fine_tune_llm(
        self,
        training_examples: List[Dict],
        base_model: str = "gpt-3.5-turbo"
    ) -> Dict:
        """
        Fine-tune LLM on custom code review data
        
        Args:
            training_examples: List of training examples in OpenAI format
            base_model: Base model to fine-tune
            
        Returns:
            Fine-tuning job details
        """
        logger.info(f"Starting fine-tuning job for {base_model}...")
        
        # Prepare training file
        training_file_path = self.model_dir / "fine_tune_training.jsonl"
        with open(training_file_path, 'w') as f:
            for example in training_examples:
                f.write(json.dumps(example) + '\n')
        
        try:
            # Upload training file
            with open(training_file_path, 'rb') as f:
                response = openai.File.create(
                    file=f,
                    purpose='fine-tune'
                )
            file_id = response['id']
            
            # Create fine-tuning job
            fine_tune_response = openai.FineTune.create(
                training_file=file_id,
                model=base_model,
                n_epochs=3,
                batch_size=8,
                learning_rate_multiplier=0.1
            )
            
            results = {
                'fine_tune_id': fine_tune_response['id'],
                'status': fine_tune_response['status'],
                'model': base_model,
                'created_at': datetime.utcnow().isoformat(),
                'training_examples': len(training_examples)
            }
            
            logger.info(f"Fine-tuning job created: {fine_tune_response['id']}")
            return results
            
        except Exception as e:
            logger.error(f"Fine-tuning failed: {e}")
            raise
    
    def load_model(self, model_type: str, version: Optional[str] = None) -> object:
        """Load trained model from disk"""
        if version is None:
            version = self.current_model_version
            
        model_path = self.model_dir / f"{model_type}_{version}.pkl"
        if not model_path.exists():
            raise FileNotFoundError(f"Model not found: {model_path}")
            
        model = joblib.load(model_path)
        logger.info(f"Loaded model: {model_path}")
        return model
    
    async def predict(
        self,
        features: Dict,
        model_type: str = "gradient_boosting"
    ) -> Dict:
        """
        Make prediction using trained model
        
        Args:
            features: Feature dictionary
            model_type: Type of model to use
            
        Returns:
            Prediction results
        """
        try:
            model = self.load_model(model_type)
            
            # Prepare features
            feature_array = np.array([[
                features.get('lines_added', 0),
                features.get('lines_deleted', 0),
                features.get('files_changed', 0),
                features.get('issues_found', 0),
                features.get('critical_issues', 0),
                features.get('security_vulnerabilities', 0),
                features.get('change_ratio', 0),
                features.get('issue_density', 0),
                features.get('critical_ratio', 0),
                features.get('security_risk', 0)
            ]])
            
            # Make prediction
            prediction = model.predict(feature_array)[0]
            probability = model.predict_proba(feature_array)[0]
            
            return {
                'needs_manual_review': bool(prediction),
                'confidence': float(max(probability)),
                'probabilities': {
                    'auto_approve': float(probability[0]),
                    'needs_review': float(probability[1])
                },
                'model_used': model_type,
                'model_version': self.current_model_version
            }
            
        except Exception as e:
            logger.error(f"Prediction failed: {e}")
            return {
                'needs_manual_review': True,
                'confidence': 0.5,
                'error': str(e)
            }
    
    async def compare_models_ab_test(
        self,
        test_data: pd.DataFrame,
        model_a: str = "gradient_boosting",
        model_b: str = "random_forest"
    ) -> Dict:
        """
        A/B test comparison between two models
        
        Args:
            test_data: Test dataset
            model_a: First model type
            model_b: Second model type
            
        Returns:
            Comparison results
        """
        logger.info(f"Running A/B test: {model_a} vs {model_b}")
        
        X, y = self.extract_features(test_data)
        
        results = {}
        for model_type in [model_a, model_b]:
            try:
                model = self.load_model(model_type)
                y_pred = model.predict(X)
                
                accuracy = accuracy_score(y, y_pred)
                precision, recall, f1, _ = precision_recall_fscore_support(
                    y, y_pred, average='binary'
                )
                
                results[model_type] = {
                    'accuracy': float(accuracy),
                    'precision': float(precision),
                    'recall': float(recall),
                    'f1_score': float(f1)
                }
            except Exception as e:
                logger.error(f"Failed to test {model_type}: {e}")
                results[model_type] = {'error': str(e)}
        
        # Determine winner
        if model_a in results and model_b in results:
            winner = model_a if results[model_a]['f1_score'] > results[model_b]['f1_score'] else model_b
            results['winner'] = winner
            results['improvement'] = abs(
                results[model_a]['f1_score'] - results[model_b]['f1_score']
            ) / results[model_b]['f1_score'] * 100
        
        logger.info(f"A/B test complete. Winner: {results.get('winner', 'N/A')}")
        return results


# Singleton instance
ml_training_service = MLTrainingService()

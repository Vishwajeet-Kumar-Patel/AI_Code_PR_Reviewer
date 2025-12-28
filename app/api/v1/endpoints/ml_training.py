"""
ML Training API Endpoints

Endpoints for ML model training, evaluation, and management
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks
from sqlalchemy.orm import Session
from typing import Dict, Optional

from app.core.deps import get_current_user, get_db
from app.models.auth import User
from app.services.ml_training_service import ml_training_service

router = APIRouter()


@router.post("/train", response_model=Dict)
async def train_model(
    background_tasks: BackgroundTasks,
    model_type: str = "gradient_boosting",
    days_back: int = 90,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start ML model training
    
    - **model_type**: Type of model (gradient_boosting, random_forest)
    - **days_back**: Days of historical data to use
    """
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Collect training data
        df = await ml_training_service.collect_training_data(db, days_back=days_back)
        
        if df is None or len(df) < 100:
            raise HTTPException(
                status_code=400,
                detail=f"Insufficient training data. Need at least 100 samples, got {len(df) if df is not None else 0}"
            )
        
        # Extract features
        X, y = ml_training_service.extract_features(df)
        
        # Train model in background
        background_tasks.add_task(
            ml_training_service.train_model,
            X, y, model_type
        )
        
        return {
            "status": "training_started",
            "model_type": model_type,
            "training_samples": len(X),
            "message": "Model training started in background"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.get("/models", response_model=Dict)
async def list_models(
    current_user: User = Depends(get_current_user)
):
    """List all trained models"""
    import json
    from pathlib import Path
    
    model_dir = Path("models/trained")
    if not model_dir.exists():
        return {"models": []}
    
    models = []
    for metadata_file in model_dir.glob("*_metadata.json"):
        with open(metadata_file) as f:
            metadata = json.load(f)
            models.append(metadata)
    
    return {"models": models, "total": len(models)}


@router.post("/predict", response_model=Dict)
async def predict_review_need(
    features: Dict,
    model_type: str = "gradient_boosting",
    current_user: User = Depends(get_current_user)
):
    """
    Predict if code needs manual review
    
    - **features**: Code metrics (lines_added, files_changed, etc.)
    - **model_type**: Model to use for prediction
    """
    try:
        result = await ml_training_service.predict(features, model_type)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/ab-test", response_model=Dict)
async def run_ab_test(
    model_a: str = "gradient_boosting",
    model_b: str = "random_forest",
    days_back: int = 30,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Run A/B test between two models
    
    - **model_a**: First model to compare
    - **model_b**: Second model to compare
    - **days_back**: Days of test data to use
    """
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Get test data
        df = await ml_training_service.collect_training_data(db, days_back=days_back)
        
        if df is None or len(df) < 50:
            raise HTTPException(
                status_code=400,
                detail="Insufficient test data"
            )
        
        # Run comparison
        results = await ml_training_service.compare_models_ab_test(df, model_a, model_b)
        return results
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@router.post("/fine-tune-llm", response_model=Dict)
async def fine_tune_llm(
    background_tasks: BackgroundTasks,
    base_model: str = "gpt-3.5-turbo",
    training_examples_count: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Start LLM fine-tuning job
    
    - **base_model**: Base model to fine-tune
    - **training_examples_count**: Number of examples to use
    """
    if current_user.role not in ["admin", "super_admin"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    try:
        # Prepare training examples from historical reviews
        query = """
        SELECT r.code_snippet, r.review_comment, r.severity
        FROM code_reviews r
        WHERE r.ai_confidence_score >= 0.9
        ORDER BY r.created_at DESC
        LIMIT :limit
        """
        
        result = db.execute(query, {"limit": training_examples_count})
        examples = result.fetchall()
        
        # Format for OpenAI fine-tuning
        training_examples = [
            {
                "messages": [
                    {"role": "system", "content": "You are a code review expert."},
                    {"role": "user", "content": f"Review this code:\n{ex.code_snippet}"},
                    {"role": "assistant", "content": ex.review_comment}
                ]
            }
            for ex in examples
        ]
        
        # Start fine-tuning in background
        background_tasks.add_task(
            ml_training_service.fine_tune_llm,
            training_examples,
            base_model
        )
        
        return {
            "status": "fine_tuning_started",
            "base_model": base_model,
            "training_examples": len(training_examples),
            "message": "Fine-tuning job started. Check status later."
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

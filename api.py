# api.py
import os
import json
import joblib
import numpy as np
import pandas as pd
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Dict
from datetime import datetime
from sklearn.ensemble import GradientBoostingRegressor
from sklearn.pipeline import Pipeline
from sklearn.base import BaseEstimator, TransformerMixin

app = FastAPI(title="Instagram Optimization API")

# Configuration
MODELS_DIR = "user_models"
os.makedirs(MODELS_DIR, exist_ok=True)

# Pydantic Models
class PostData(BaseModel):
    user_id: str
    caption: str
    media_type: str  # 'image' or 'video'
    hour: int
    day_of_week: int
    hashtag_count: int
    niche: str

class TrainingPost(BaseModel):
    timestamp: str
    likes: int
    comments: int
    new_followers: int
    media_type: str
    hashtags: str
    caption: str
    hour: int = None
    day_of_week: int = None

class TrainingData(BaseModel):
    user_id: str
    posts: List[TrainingPost]

class PredictionResponse(BaseModel):
    likes: int
    comments: int
    new_followers: int
    model_version: str

# Custom Preprocessor
class DataPreprocessor(TransformerMixin, BaseEstimator):
    def fit(self, X, y=None):
        return self
        
    def transform(self, X):
        X = X.copy()
        X['media_type'] = X['media_type'].map({'image': 0, 'video': 1})
        
        # Convert niche to categorical code
        if 'niche' in X.columns:
            X['niche'] = X['niche'].astype('category').cat.codes
        
        return X

# Helper Functions
def get_user_model_path(user_id: str) -> str:
    return os.path.join(MODELS_DIR, f"{user_id}.joblib")

def get_user_data_path(user_id: str) -> str:
    return os.path.join(MODELS_DIR, f"{user_id}_data.json")

def initialize_user_model(user_id: str):
    model = Pipeline([
        ('preprocessor', DataPreprocessor()),
        ('regressor', GradientBoostingRegressor(
            n_estimators=50,
            random_state=hash(user_id) % 1000  # Unique but deterministic seed
        ))
    ])
    
    model_path = get_user_model_path(user_id)
    joblib.dump(model, model_path)
    
    # Initialize empty training data
    data_path = get_user_data_path(user_id)
    with open(data_path, 'w') as f:
        json.dump({"posts": []}, f)
    
    return model

def load_user_model(user_id: str):
    model_path = get_user_model_path(user_id)
    if os.path.exists(model_path):
        return joblib.load(model_path)
    return initialize_user_model(user_id)

def load_user_data(user_id: str) -> dict:
    data_path = get_user_data_path(user_id)
    if os.path.exists(data_path):
        with open(data_path, 'r') as f:
            return json.load(f)
    return {"posts": []}

def save_user_data(user_id: str, data: dict):
    with open(get_user_data_path(user_id), 'w') as f:
        json.dump(data, f)

def prepare_training_data(raw_data: List[TrainingPost]) -> pd.DataFrame:
    df = pd.DataFrame([post.dict() for post in raw_data])
    
    # Convert timestamp
    df['timestamp'] = pd.to_datetime(df['timestamp'])
    
    # Extract features
    df['hour'] = df['timestamp'].dt.hour
    df['
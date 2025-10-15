"""
Enhanced model service for Insider Threat Detection.

This service provides a unified interface for model management,
inference, and monitoring with support for multiple model types
and advanced features like model versioning and A/B testing.
"""

import asyncio
import time
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, Tuple
from dataclasses import dataclass
from enum import Enum
import joblib
import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler, LabelEncoder
from scipy.sparse import csr_matrix
import tensorflow as tf

from ..core.config import get_settings
from ..core.logging import get_logger, get_performance_logger
from ..api.exceptions import ModelLoadError, ModelInferenceError
from ..utils.feature_engineering import FeatureEngineer
from ..utils.preprocessing import DataPreprocessor


logger = get_logger(__name__)
performance_logger = get_performance_logger()


class ModelType(str, Enum):
    """Supported model types."""
    XGBOOST = "xgboost"
    LSTM = "lstm"
    HYBRID = "hybrid"


@dataclass
class ModelMetadata:
    """Model metadata container."""
    name: str
    version: str
    model_type: ModelType
    created_at: str
    accuracy: Optional[float] = None
    precision: Optional[float] = None
    recall: Optional[float] = None
    f1_score: Optional[float] = None
    features: Optional[List[str]] = None
    description: Optional[str] = None


@dataclass
class InferenceResult:
    """Inference result container."""
    prediction: int
    probability: float
    confidence: float
    model_name: str
    model_version: str
    inference_time: float
    features_used: List[str]
    metadata: Dict[str, Any]


class ModelService:
    """Enhanced model service for managing and running ML models."""
    
    def __init__(self):
        self.settings = get_settings()
        self.models: Dict[str, Any] = {}
        self.metadata: Dict[str, ModelMetadata] = {}
        self.feature_engineer = FeatureEngineer()
        self.preprocessor = DataPreprocessor()
        self._initialized = False
    
    async def initialize(self) -> None:
        """Initialize the model service."""
        if self._initialized:
            return
        
        logger.info("Initializing model service")
        
        try:
            # Load models
            await self._load_models()
            
            # Validate models
            await self._validate_models()
            
            self._initialized = True
            logger.info("Model service initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize model service: {str(e)}", exc_info=True)
            raise ModelLoadError(f"Model service initialization failed: {str(e)}")
    
    async def _load_models(self) -> None:
        """Load all available models."""
        model_dir = Path(self.settings.model.model_dir)
        
        if not model_dir.exists():
            raise ModelLoadError(f"Model directory does not exist: {model_dir}")
        
        # Load XGBoost model
        xgb_model_path = model_dir / "xgb_model_v4.pkl"
        if xgb_model_path.exists():
            await self._load_xgboost_model(xgb_model_path)
        
        # Load LSTM model
        lstm_model_path = model_dir / "lstm_model.h5"
        if lstm_model_path.exists():
            await self._load_lstm_model(lstm_model_path)
        
        # Load hybrid model components
        await self._load_hybrid_components(model_dir)
    
    async def _load_xgboost_model(self, model_path: Path) -> None:
        """Load XGBoost model and related artifacts."""
        try:
            # Load model
            model = joblib.load(model_path)
            self.models["xgboost"] = model
            
            # Load scaler
            scaler_path = model_path.parent / "xgb_scaler_v4.pkl"
            if scaler_path.exists():
                self.models["xgb_scaler"] = joblib.load(scaler_path)
            
            # Load label encoder
            le_path = model_path.parent / "xgb_le_v4.pkl"
            if le_path.exists():
                self.models["xgb_le"] = joblib.load(le_path)
            
            # Load vectorizer
            vect_path = model_path.parent / "action_vect_v4.pkl"
            if vect_path.exists():
                self.models["xgb_vect"] = joblib.load(vect_path)
            
            # Load user stats
            stats_path = model_path.parent / "user_stats_v4.pkl"
            if stats_path.exists():
                self.models["xgb_user_stats"] = joblib.load(stats_path)
            
            # Create metadata
            self.metadata["xgboost"] = ModelMetadata(
                name="XGBoost",
                version="v4",
                model_type=ModelType.XGBOOST,
                created_at=time.ctime(model_path.stat().st_mtime),
                features=self._get_xgb_features()
            )
            
            logger.info("XGBoost model loaded successfully")
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load XGBoost model: {str(e)}")
    
    async def _load_lstm_model(self, model_path: Path) -> None:
        """Load LSTM model and related artifacts."""
        try:
            # Load model
            model = tf.keras.models.load_model(model_path)
            self.models["lstm"] = model
            
            # Load action vocabulary
            vocab_path = model_path.parent / "action_vocab.pkl"
            if vocab_path.exists():
                self.models["lstm_vocab"] = joblib.load(vocab_path)
            
            # Load metadata
            metadata_path = model_path.parent / "lstm_metadata.pkl"
            if metadata_path.exists():
                self.models["lstm_metadata"] = joblib.load(metadata_path)
            
            # Create metadata
            self.metadata["lstm"] = ModelMetadata(
                name="LSTM",
                version="v2",
                model_type=ModelType.LSTM,
                created_at=time.ctime(model_path.stat().st_mtime),
                features=self._get_lstm_features()
            )
            
            logger.info("LSTM model loaded successfully")
            
        except Exception as e:
            raise ModelLoadError(f"Failed to load LSTM model: {str(e)}")
    
    async def _load_hybrid_components(self, model_dir: Path) -> None:
        """Load hybrid model components."""
        try:
            # Load hybrid threshold
            threshold_path = model_dir / "hybrid_threshold.json"
            if threshold_path.exists():
                import json
                with open(threshold_path, 'r') as f:
                    self.models["hybrid_threshold"] = json.load(f)
            
            # Create hybrid metadata
            self.metadata["hybrid"] = ModelMetadata(
                name="Hybrid Ensemble",
                version="v2",
                model_type=ModelType.HYBRID,
                created_at=time.ctime(),
                description="Combined XGBoost and LSTM ensemble model"
            )
            
            logger.info("Hybrid model components loaded successfully")
            
        except Exception as e:
            logger.warning(f"Failed to load hybrid components: {str(e)}")
    
    async def _validate_models(self) -> None:
        """Validate loaded models."""
        required_models = ["xgboost", "lstm"]
        missing_models = [model for model in required_models if model not in self.models]
        
        if missing_models:
            raise ModelLoadError(f"Missing required models: {missing_models}")
        
        logger.info("Model validation completed successfully")
    
    def _get_xgb_features(self) -> List[str]:
        """Get XGBoost model features."""
        if "xgboost" in self.models:
            try:
                return self.models["xgboost"].feature_names_in_.tolist()
            except AttributeError:
                return []
        return []
    
    def _get_lstm_features(self) -> List[str]:
        """Get LSTM model features."""
        return ["action_sequence", "sequence_length"]
    
    async def predict(
        self,
        session_data: Dict[str, Any],
        model_type: Optional[ModelType] = None
    ) -> InferenceResult:
        """Run inference on session data."""
        if not self._initialized:
            raise ModelInferenceError("Model service not initialized")
        
        start_time = time.time()
        
        try:
            # Preprocess data
            processed_data = await self.preprocessor.preprocess_session(session_data)
            
            # Extract features
            features = await self.feature_engineer.extract_features(processed_data)
            
            # Run inference
            if model_type == ModelType.XGBOOST:
                result = await self._predict_xgboost(features)
            elif model_type == ModelType.LSTM:
                result = await self._predict_lstm(features)
            else:
                result = await self._predict_hybrid(features)
            
            # Calculate inference time
            inference_time = time.time() - start_time
            
            # Log performance
            performance_logger.log_inference_time(
                model_name=result.model_name,
                inference_time=inference_time,
                input_size=len(features),
                request_id=session_data.get("request_id")
            )
            
            # Update result with timing
            result.inference_time = inference_time
            
            return result
            
        except Exception as e:
            logger.error(f"Inference failed: {str(e)}", exc_info=True)
            raise ModelInferenceError(f"Inference failed: {str(e)}")
    
    async def _predict_xgboost(self, features: Dict[str, Any]) -> InferenceResult:
        """Run XGBoost prediction."""
        try:
            # Prepare features
            X = self._prepare_xgb_features(features)
            
            # Run prediction
            model = self.models["xgboost"]
            probability = model.predict_proba(X)[0][1]
            prediction = int(probability > self.settings.model.threshold)
            
            return InferenceResult(
                prediction=prediction,
                probability=probability,
                confidence=abs(probability - 0.5) * 2,
                model_name="XGBoost",
                model_version=self.metadata["xgboost"].version,
                inference_time=0,  # Will be set by caller
                features_used=self._get_xgb_features(),
                metadata={"model_type": "xgboost"}
            )
            
        except Exception as e:
            raise ModelInferenceError(f"XGBoost prediction failed: {str(e)}")
    
    async def _predict_lstm(self, features: Dict[str, Any]) -> InferenceResult:
        """Run LSTM prediction."""
        try:
            # Prepare sequence
            sequence = self._prepare_lstm_sequence(features)
            
            # Run prediction
            model = self.models["lstm"]
            probability = model.predict(sequence, verbose=0)[0][0]
            prediction = int(probability > self.settings.model.threshold)
            
            return InferenceResult(
                prediction=prediction,
                probability=probability,
                confidence=abs(probability - 0.5) * 2,
                model_name="LSTM",
                model_version=self.metadata["lstm"].version,
                inference_time=0,  # Will be set by caller
                features_used=self._get_lstm_features(),
                metadata={"model_type": "lstm"}
            )
            
        except Exception as e:
            raise ModelInferenceError(f"LSTM prediction failed: {str(e)}")
    
    async def _predict_hybrid(self, features: Dict[str, Any]) -> InferenceResult:
        """Run hybrid ensemble prediction."""
        try:
            # Get individual predictions
            xgb_result = await self._predict_xgboost(features)
            lstm_result = await self._predict_lstm(features)
            
            # Combine predictions
            xgb_weight = self.settings.model.xgb_weight
            lstm_weight = self.settings.model.lstm_weight
            
            hybrid_probability = (
                xgb_result.probability * xgb_weight +
                lstm_result.probability * lstm_weight
            )
            
            prediction = int(hybrid_probability > self.settings.model.threshold)
            
            return InferenceResult(
                prediction=prediction,
                probability=hybrid_probability,
                confidence=abs(hybrid_probability - 0.5) * 2,
                model_name="Hybrid Ensemble",
                model_version=self.metadata["hybrid"].version,
                inference_time=0,  # Will be set by caller
                features_used=self._get_xgb_features() + self._get_lstm_features(),
                metadata={
                    "model_type": "hybrid",
                    "xgb_probability": xgb_result.probability,
                    "lstm_probability": lstm_result.probability,
                    "xgb_weight": xgb_weight,
                    "lstm_weight": lstm_weight
                }
            )
            
        except Exception as e:
            raise ModelInferenceError(f"Hybrid prediction failed: {str(e)}")
    
    def _prepare_xgb_features(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepare features for XGBoost model."""
        # Implementation depends on your feature engineering
        # This is a placeholder
        return np.array([[0.0] * 10])  # Adjust based on your model
    
    def _prepare_lstm_sequence(self, features: Dict[str, Any]) -> np.ndarray:
        """Prepare sequence for LSTM model."""
        # Implementation depends on your sequence preparation
        # This is a placeholder
        return np.array([[[0.0] * 50]])  # Adjust based on your model
    
    async def get_model_info(self) -> Dict[str, ModelMetadata]:
        """Get information about loaded models."""
        return self.metadata.copy()
    
    async def get_model_health(self) -> Dict[str, Any]:
        """Get model health status."""
        return {
            "initialized": self._initialized,
            "models_loaded": list(self.models.keys()),
            "metadata_available": list(self.metadata.keys()),
            "cache_enabled": self.settings.model.cache_enabled,
            "cache_ttl": self.settings.model.cache_ttl,
        }
    
    async def cleanup(self) -> None:
        """Cleanup model service resources."""
        logger.info("Cleaning up model service")
        self.models.clear()
        self.metadata.clear()
        self._initialized = False

import json
import logging
import subprocess
import sys
from pathlib import Path

from app.services.embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class ClassificationService:
    def __init__(self) -> None:
        self.ml_dir = Path(__file__).parent.parent.parent.parent.parent / "services" / "ml"
        self.model_dir = self.ml_dir / "model"
        self.model_path = self.model_dir / "classifier.keras"
        self.labels_path = self.model_dir / "labels.json"

        self.model = None
        self.labels = None
        self.embedding_service = EmbeddingService()

    def _ensure_model_trained(self) -> None:
        if not self.model_path.exists() or not self.labels_path.exists():
            logger.info(
                "TensorFlow classification model not found. Triggering training pipeline..."
            )
            train_script = self.ml_dir / "train.py"
            if train_script.exists():
                try:
                    # Run train.py in same Python env
                    result = subprocess.run(
                        [sys.executable, str(train_script)],
                        check=True,
                        capture_output=True,
                        text=True,
                    )
                    logger.info("Model trained successfully.")
                    logger.debug(result.stdout)
                except subprocess.CalledProcessError as e:
                    logger.error(f"Failed to auto-train model: {e.stderr}")
                    raise RuntimeError(f"Failed to auto-train classifier: {e.stderr}") from e
            else:
                logger.error(f"Training script not found at {train_script}")
                raise FileNotFoundError(f"Training script not found at {train_script}")

    def _load_model(self) -> None:
        if self.model is not None and self.labels is not None:
            return

        self._ensure_model_trained()

        try:
            # Lazy import to speed up startup times
            import tensorflow as tf

            logger.info(f"Loading Keras classifier from {self.model_path}")
            self.model = tf.keras.models.load_model(str(self.model_path))

            with open(self.labels_path) as f:
                self.labels = json.load(f)
        except Exception as e:
            logger.error(f"Error loading classification model: {e}")
            raise RuntimeError(f"Could not load TensorFlow classifier: {e}") from e

    def classify_text(self, title: str, content: str) -> dict:
        try:
            self._load_model()

            text_to_embed = f"{title}\n{content}"
            embedding = self.embedding_service.embed_text(text_to_embed)

            # Convert embedding to numpy array with shape (1, 384)
            import numpy as np

            x = np.array([embedding], dtype=np.float32)

            # Predict
            predictions = self.model.predict(x, verbose=0)
            pred_idx = int(np.argmax(predictions[0]))
            confidence = float(predictions[0][pred_idx])

            category = self.labels[pred_idx]

            return {"category": category, "confidence": confidence}
        except Exception as e:
            logger.error(f"Failed to classify text: {e}")
            return {"category": "Uncategorized", "confidence": 0.0}

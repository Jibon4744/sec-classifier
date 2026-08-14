import os
import json
import logging
import numpy as np
from PIL import Image
from huggingface_hub import hf_hub_download
from app.core.config import settings

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Try to import tensorflow or fallback to tflite_runtime
try:
    import tensorflow as tf
    Interpreter = tf.lite.Interpreter
except ImportError:
    try:
        from tflite_runtime.interpreter import Interpreter
    except ImportError:
        raise ImportError("Neither tensorflow nor tflite-runtime is installed. Please install one of them.")

class ClassifierService:
    def __init__(self):
        self.repo_id = settings.HF_REPO_ID
        self.class_names = [
            'Alternaria leaf spot', 'Downy Mildew', 'Early Bloom', 'Full Bloom', 
            'Healthy', 'Mature Bud', 'Powdery Mildew', 'Wilted', 'Wilted leaf', 'Young Bud'
        ]
        self.weights = {
            'mobilenet': 0.25316455811242594,
            'resnet50': 0.25546604500710124,
            'efficientnetv2s': 0.24856156614674546,
            'vgg16': 0.24280783073372736
        }
        
        # Subsets of classes for the two modes
        self.disease_classes = ['Alternaria leaf spot', 'Downy Mildew', 'Powdery Mildew', 'Wilted leaf', 'Healthy']
        self.stage_classes = ['Young Bud', 'Mature Bud', 'Early Bloom', 'Full Bloom', 'Wilted']
        
        # Load local JSON lookup tables
        self.diseases_data = self._load_json_data("diseases.json")
        self.stages_data = self._load_json_data("stages.json")
        
        # Cache paths for models
        self.model_files = {
            'mobilenet': 'MobileNet_float16.tflite',
            'resnet50': 'resnet50_float16.tflite',
            'efficientnetv2s': 'EfficientNetV2S_float16.tflite',
            'vgg16': 'vgg16_float16.tflite'
        }
        self.interpreters = {}
        
    def _load_json_data(self, filename: str) -> dict:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        filepath = os.path.join(base_dir, "data", filename)
        try:
            with open(filepath, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading metadata file {filename} at {filepath}: {e}")
            return {}

    def preload_models(self):
        """Downloads models from Hugging Face Hub and instantiates TFLite Interpreters."""
        for key, filename in self.model_files.items():
            if key not in self.interpreters:
                logger.info(f"Loading model {key} ({filename})...")
                try:
                    # hf_hub_download handles local caching automatically
                    model_path = hf_hub_download(repo_id=self.repo_id, filename=filename)
                    interpreter = Interpreter(model_path=model_path)
                    interpreter.allocate_tensors()
                    self.interpreters[key] = interpreter
                    logger.info(f"Successfully loaded and allocated {key}")
                except Exception as e:
                    logger.error(f"Failed to load model {key} from Hugging Face: {e}")
                    raise RuntimeError(f"Could not load model {key}: {e}")

    def _preprocess_image(self, image: Image.Image, target_size=(224, 224)) -> np.ndarray:
        """Resizes, scales, and prepares image for TFLite inference."""
        # Convert to RGB if not already
        if image.mode != "RGB":
            image = image.convert("RGB")
        # Resize to expected shape
        image = image.resize(target_size)
        # Convert to array and scale [0, 1]
        img_array = np.array(image, dtype=np.float32) / 255.0
        # Expand dims to batch size [1, 224, 224, 3]
        img_array = np.expand_dims(img_array, axis=0)
        return img_array

    def _softmax(self, x: np.ndarray) -> np.ndarray:
        """Computes softmax probabilities for raw logits."""
        # Subtract max for numerical stability
        e_x = np.exp(x - np.max(x, axis=-1, keepdims=True))
        return e_x / np.sum(e_x, axis=-1, keepdims=True)

    def _run_ensemble_inference(self, img_array: np.ndarray) -> np.ndarray:
        """Executes inference on all 4 models and weights their softmax outputs."""
        self.preload_models() # Ensure models are loaded
        
        # Accumulate weighted probabilities
        weighted_probs = np.zeros(len(self.class_names))
        
        for key, interpreter in self.interpreters.items():
            input_details = interpreter.get_input_details()[0]
            output_details = interpreter.get_output_details()[0]
            
            # Set input tensor
            interpreter.set_tensor(input_details['index'], img_array)
            # Run inference
            interpreter.invoke()
            # Get raw output
            output_data = interpreter.get_tensor(output_details['index'])
            
            # Apply softmax to guarantee probabilities
            probs = self._softmax(output_data)[0]
            
            # Weighted aggregation
            weight = self.weights[key]
            weighted_probs += weight * probs
            
        return weighted_probs

    def predict_disease(self, image: Image.Image) -> tuple[str, float, dict]:
        """Classifies disease by performing subset softmax over disease classes."""
        img_array = self._preprocess_image(image)
        weighted_probs = self._run_ensemble_inference(img_array)
        
        # Extract indices and values for disease classes
        disease_indices = [self.class_names.index(c) for c in self.disease_classes]
        disease_scores = weighted_probs[disease_indices]
        
        # Re-normalize subset scores to sum to 1.0
        sum_scores = np.sum(disease_scores)
        if sum_scores > 0:
            disease_scores = disease_scores / sum_scores
            
        best_idx = np.argmax(disease_scores)
        predicted_class = self.disease_classes[best_idx]
        confidence = float(disease_scores[best_idx])
        
        # Get static lookup info
        info = self.diseases_data.get(predicted_class, {
            "cause": "Unknown",
            "treatment": "No information available.",
            "severity": "Unknown"
        })
        
        return predicted_class, confidence, info

    def predict_growth_stage(self, image: Image.Image) -> tuple[str, float, dict]:
        """Classifies growth stage by performing subset softmax over stage classes."""
        img_array = self._preprocess_image(image)
        weighted_probs = self._run_ensemble_inference(img_array)
        
        # Extract indices and values for stage classes
        stage_indices = [self.class_names.index(c) for c in self.stage_classes]
        stage_scores = weighted_probs[stage_indices]
        
        # Re-normalize subset scores to sum to 1.0
        sum_scores = np.sum(stage_scores)
        if sum_scores > 0:
            stage_scores = stage_scores / sum_scores
            
        best_idx = np.argmax(stage_scores)
        predicted_class = self.stage_classes[best_idx]
        confidence = float(stage_scores[best_idx])
        
        # Get static lookup info
        info = self.stages_data.get(predicted_class, {
            "description": "No description available.",
            "typical_days_to_harvest": "Unknown"
        })
        
        return predicted_class, confidence, info

# Singleton instance for general reuse
classifier_service = ClassifierService()

"""
Model module for sentiment analysis using TensorFlow.
"""

import tensorflow as tf
from tensorflow.keras import layers, models
import numpy as np
from typing import Tuple, Dict, Any, List
import logging
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns
import matplotlib.pyplot as plt

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class SentimentModel:
    """Class for sentiment analysis model using TensorFlow."""
    
    def __init__(self, input_dim: int, num_classes: int = 2):
        """
        Initialize the sentiment model.
        
        Args:
            input_dim: Input dimension (vocabulary size)
            num_classes: Number of output classes
        """
        self.input_dim = input_dim
        self.num_classes = num_classes
        self.model = self._create_model()
    
    def _create_model(self) -> tf.keras.Model:
        """
        Create a neural network model for sentiment analysis.
        
        Returns:
            Compiled TensorFlow model
        """
        model = models.Sequential([
            # Input layer
            layers.Dense(512, activation='relu', input_dim=self.input_dim),
            layers.Dropout(0.3),
            
            # Hidden layers
            layers.Dense(256, activation='relu'),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu'),
            layers.Dropout(0.3),
            
            # Output layer
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        # Compile model
        model.compile(
            optimizer='adam',
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, 
              X_train: np.ndarray,
              y_train: np.ndarray,
              X_val: np.ndarray,
              y_val: np.ndarray,
              epochs: int = 10,
              batch_size: int = 32) -> tf.keras.callbacks.History:
        """
        Train the sentiment analysis model.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Training history
        """
        # Early stopping to prevent overfitting
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=3,
            restore_best_weights=True
        )
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=[early_stopping],
            verbose=1
        )
        
        return history
    
    def evaluate(self, X_test: np.ndarray, y_test: np.ndarray) -> Dict[str, Any]:
        """
        Evaluate the model on test data.
        
        Args:
            X_test: Test features
            y_test: Test labels
            
        Returns:
            Dictionary containing evaluation metrics
        """
        # Get predictions
        y_pred = self.model.predict(X_test)
        y_pred_classes = np.argmax(y_pred, axis=1)
        
        # Calculate metrics
        report = classification_report(y_test, y_pred_classes, output_dict=True)
        
        # Create confusion matrix
        cm = confusion_matrix(y_test, y_pred_classes)
        
        return {
            'classification_report': report,
            'confusion_matrix': cm
        }
    
    def predict(self, text_vector: np.ndarray) -> np.ndarray:
        """
        Predict sentiment of input text.
        
        Args:
            text_vector: Vectorized text input
            
        Returns:
            Model prediction
        """
        return self.model.predict(text_vector)
    
    def save(self, filepath: str) -> None:
        """
        Save the model to disk.
        
        Args:
            filepath: Path to save the model
        """
        self.model.save(filepath)
        logger.info(f"Model saved to {filepath}")
    
    @classmethod
    def load(cls, filepath: str) -> 'SentimentModel':
        """
        Load a model from disk.
        
        Args:
            filepath: Path to the saved model
            
        Returns:
            Loaded SentimentModel instance
        """
        loaded_model = tf.keras.models.load_model(filepath)
        instance = cls(input_dim=loaded_model.input_shape[1])
        instance.model = loaded_model
        logger.info(f"Model loaded from {filepath}")
        return instance


# Keep the functional API for compatibility with existing code
def create_model(input_dim: int, num_classes: int = 2) -> tf.keras.Model:
    """
    Create a neural network model for sentiment analysis.
    
    Args:
        input_dim: Input dimension (vocabulary size)
        num_classes: Number of output classes
        
    Returns:
        Compiled TensorFlow model
    """
    model = models.Sequential([
        # Input layer
        layers.Dense(512, activation='relu', input_dim=input_dim),
        layers.Dropout(0.3),
        
        # Hidden layers
        layers.Dense(256, activation='relu'),
        layers.Dropout(0.3),
        
        layers.Dense(128, activation='relu'),
        layers.Dropout(0.3),
        
        # Output layer
        layers.Dense(num_classes, activation='softmax')
    ])
    
    # Compile model
    model.compile(
        optimizer='adam',
        loss='sparse_categorical_crossentropy',
        metrics=['accuracy']
    )
    
    return model

def train_model(model: tf.keras.Model,
                X_train: np.ndarray,
                y_train: np.ndarray,
                X_val: np.ndarray,
                y_val: np.ndarray,
                epochs: int = 10,
                batch_size: int = 32) -> tf.keras.callbacks.History:
    """
    Train the sentiment analysis model.
    
    Args:
        model: TensorFlow model to train
        X_train: Training features
        y_train: Training labels
        X_val: Validation features
        y_val: Validation labels
        epochs: Number of training epochs
        batch_size: Batch size for training
        
    Returns:
        Training history
    """
    # Early stopping to prevent overfitting
    early_stopping = tf.keras.callbacks.EarlyStopping(
        monitor='val_loss',
        patience=3,
        restore_best_weights=True
    )
    
    # Train model
    history = model.fit(
        X_train, y_train,
        epochs=epochs,
        batch_size=batch_size,
        validation_data=(X_val, y_val),
        callbacks=[early_stopping],
        verbose=1
    )
    
    return history

def evaluate_model(model: tf.keras.Model,
                  X_test: np.ndarray,
                  y_test: np.ndarray) -> Dict[str, Any]:
    """
    Evaluate the model on test data.
    
    Args:
        model: Trained TensorFlow model
        X_test: Test features
        y_test: Test labels
        
    Returns:
        Dictionary containing evaluation metrics
    """
    # Get predictions
    y_pred = model.predict(X_test)
    y_pred_classes = np.argmax(y_pred, axis=1)
    
    # Calculate metrics
    report = classification_report(y_test, y_pred_classes, output_dict=True)
    
    # Create confusion matrix
    cm = confusion_matrix(y_test, y_pred_classes)
    
    return {
        'classification_report': report,
        'confusion_matrix': cm
    }

def plot_training_history(history: tf.keras.callbacks.History) -> None:
    """
    Plot training and validation metrics from model training history.
    
    Args:
        history: History object returned by model.fit()
    """
    # Create figure with 2 subplots
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15, 5))
    
    # Plot training & validation accuracy
    ax1.plot(history.history['accuracy'])
    if 'val_accuracy' in history.history:
        ax1.plot(history.history['val_accuracy'])
        ax1.legend(['Train', 'Validation'], loc='upper left')
    else:
        ax1.legend(['Train'], loc='upper left')
    ax1.set_title('Model Accuracy')
    ax1.set_ylabel('Accuracy')
    ax1.set_xlabel('Epoch')
    
    # Plot training & validation loss
    ax2.plot(history.history['loss'])
    if 'val_loss' in history.history:
        ax2.plot(history.history['val_loss'])
        ax2.legend(['Train', 'Validation'], loc='upper left')
    else:
        ax2.legend(['Train'], loc='upper left')
    ax2.set_title('Model Loss')
    ax2.set_ylabel('Loss')
    ax2.set_xlabel('Epoch')
    
    plt.tight_layout()
    # plt.show()  # Comment out to prevent displaying/saving
    plt.close(fig)  # Close the figure to free memory
    
    logger.info("Training history plot created (display disabled)")


def plot_confusion_matrix(cm: np.ndarray, classes: List[str] = None) -> None:
    """
    Plot confusion matrix.
    
    Args:
        cm: Confusion matrix array
        classes: List of class names
    """
    if classes is None:
        classes = ['Negative', 'Positive']
    
    fig = plt.figure(figsize=(8, 6))
    sns.heatmap(cm, annot=True, fmt="d", cmap=plt.cm.Blues, 
                xticklabels=classes, yticklabels=classes)
    plt.ylabel('True Label')
    plt.xlabel('Predicted Label')
    plt.title('Confusion Matrix')
    plt.tight_layout()
    # plt.show()  # Comment out to prevent displaying/saving
    plt.close(fig)  # Close the figure to free memory
    
    logger.info("Confusion matrix plot created (display disabled)")

class EnhancedSentimentModel(SentimentModel):
    """Enhanced sentiment model with more sophisticated architecture and regularization."""
    
    def _create_model(self) -> tf.keras.Model:
        """
        Create an enhanced neural network model for sentiment analysis.
        
        Returns:
            Compiled TensorFlow model
        """
        # L2 regularization to prevent overfitting
        regularizer = tf.keras.regularizers.l2(0.001)
        
        model = models.Sequential([
            # Input layer
            layers.Dense(512, activation='relu', input_dim=self.input_dim,
                        kernel_regularizer=regularizer),
            layers.BatchNormalization(),
            layers.Dropout(0.4),
            
            # Hidden layers with residual connections
            layers.Dense(256, activation='relu', kernel_regularizer=regularizer),
            layers.BatchNormalization(),
            layers.Dropout(0.3),
            
            layers.Dense(128, activation='relu', kernel_regularizer=regularizer),
            layers.BatchNormalization(),
            layers.Dropout(0.2),
            
            # Output layer
            layers.Dense(self.num_classes, activation='softmax')
        ])
        
        # Compile model with a more sophisticated optimizer
        optimizer = tf.keras.optimizers.Adam(
            learning_rate=0.001,
            beta_1=0.9,
            beta_2=0.999,
            epsilon=1e-07,
            amsgrad=True
        )
        
        model.compile(
            optimizer=optimizer,
            loss='sparse_categorical_crossentropy',
            metrics=['accuracy']
        )
        
        return model
    
    def train(self, 
              X_train: np.ndarray,
              y_train: np.ndarray,
              X_val: np.ndarray,
              y_val: np.ndarray,
              epochs: int = 15,
              batch_size: int = 32) -> tf.keras.callbacks.History:
        """
        Train the enhanced sentiment analysis model with learning rate scheduling.
        
        Args:
            X_train: Training features
            y_train: Training labels
            X_val: Validation features
            y_val: Validation labels
            epochs: Number of training epochs
            batch_size: Batch size for training
            
        Returns:
            Training history
        """
        # Learning rate scheduler
        lr_scheduler = tf.keras.callbacks.ReduceLROnPlateau(
            monitor='val_loss',
            factor=0.5,
            patience=2,
            min_lr=1e-6,
            verbose=1
        )
        
        # Early stopping to prevent overfitting
        early_stopping = tf.keras.callbacks.EarlyStopping(
            monitor='val_loss',
            patience=5,
            restore_best_weights=True,
            verbose=1
        )
        
        # Train model
        history = self.model.fit(
            X_train, y_train,
            epochs=epochs,
            batch_size=batch_size,
            validation_data=(X_val, y_val),
            callbacks=[early_stopping, lr_scheduler],
            verbose=1
        )
        
        return history 
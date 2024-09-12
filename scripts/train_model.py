import tensorflow as tf
from tensorflow.keras.models import Sequential, load_model
from tensorflow.keras.layers import Dense, Dropout
import numpy as np
import os
import gc  # Garbage collector

# Function to check if a model exists and load it, otherwise create a new one
def load_or_create_model(input_shape, num_classes, model_path="data/chess_ai_model.h5"):
    if os.path.exists(model_path):
        print("Loading existing model...")
        model = load_model(model_path)
    else:
        print("No existing model found, creating a new model...")
        model = Sequential([
            Dense(1024, input_dim=input_shape, activation='relu'),
            Dropout(0.3),
            Dense(512, activation='relu'),
            Dropout(0.3),
            Dense(num_classes, activation='softmax')  # Output layer with softmax
        ])
        model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])
    return model

# Function to load and combine old and new data
def load_and_combine_data(data_dir="data", new_data_dir=None):
    # Load existing data
    X_old = np.load(f"{data_dir}/X.npy")
    y_old = np.load(f"{data_dir}/y.npy")
    
    print(f"Shape of old X: {X_old.shape}")
    print(f"Shape of old y: {y_old.shape}")
    
    # If new data exists, concatenate with the old data
    if new_data_dir:
        X_new = np.load(f"{new_data_dir}/new_X.npy")
        y_new = np.load(f"{new_data_dir}/new_y.npy")
        
        print(f"Shape of new X: {X_new.shape}")
        print(f"Shape of new y: {y_new.shape}")
        
        # Concatenate old and new data
        X_combined = np.concatenate((X_old, X_new), axis=0)
        y_combined = np.concatenate((y_old, y_new), axis=0)
        
        print(f"Shape of combined X: {X_combined.shape}")
        print(f"Shape of combined y: {y_combined.shape}")
        
        # Free memory
        del X_new, y_new
    else:
        X_combined, y_combined = X_old, y_old
    
    return X_combined, y_combined

# Main training process
def main():
    data_dir = "data"  # Directory for old data
    new_data_dir = None  # Update this if new data is added, e.g., "new_data"

    # Load and combine old and new data
    X, y = load_and_combine_data(data_dir, new_data_dir)
    
    # Get the input shape and number of output classes
    input_shape = X.shape[1]
    num_classes = y.shape[1]
    
    # Load the existing model or create a new one
    model = load_or_create_model(input_shape, num_classes)
    
    # Train the model on the combined dataset
    history = model.fit(X, y, epochs=10, batch_size=512, validation_split=0.1)
    
    # Free memory after training
    del X, y
    gc.collect()

    # Save the updated model
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    model.save(f"{data_dir}/chess_ai_model.h5")
    print(f"Model saved as 'chess_ai_model.h5' in the '{data_dir}' folder.")

if __name__ == "__main__":
    main()

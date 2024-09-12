import tensorflow as tf
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Dense, Dropout
import numpy as np
import os
import gc  # Garbage collector

# Load the preprocessed data
X = np.load("data/X.npy")
y = np.load("data/y.npy")

# Check the shape of X and y
print(f"Shape of X: {X.shape}")
print(f"Shape of y: {y.shape}")  # Should be (num_samples, num_classes)

# Get the number of output classes (should match the second dimension of y)
num_classes = y.shape[1]

# Define a simple feedforward neural network for move prediction
model = Sequential([
    Dense(1024, input_dim=X.shape[1], activation='relu'),
    Dropout(0.3),
    Dense(512, activation='relu'),
    Dropout(0.3),
    Dense(num_classes, activation='softmax')  # Use num_classes from y.shape[1]
])

# Compile the model
model.compile(optimizer='adam', loss='categorical_crossentropy', metrics=['accuracy'])

# Reduce batch size to avoid memory issues
history = model.fit(X, y, epochs=10, batch_size=512, validation_split=0.1)

# Free up memory after training
del X, y
gc.collect()

# Create the 'data' directory if it doesn't exist
if not os.path.exists("data"):
    os.makedirs("data")

# Save the trained model
model.save("data/chess_ai_model.h5")
print("Model saved as 'chess_ai_model.h5' in the 'data/' folder.")


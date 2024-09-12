# **Chess AI Engine with Neural Networks**

This project is a **Chess AI Engine** built using **Pygame** for the graphical interface and **TensorFlow** for the neural network model. The engine allows a human player to compete against an AI that predicts the best moves based on a pre-trained model. The AI is trained using historical chess games stored in **PGN (Portable Game Notation)** format.

## **Project Structure**


## **How the Chess AI Works**

1. **Data Collection and Preprocessing**:
   - Historical chess games are stored in **PGN** format. These games are parsed and preprocessed into a format that the neural network model can understand.
   - Each chess board state is converted into a 3D tensor (12x8x8), and each corresponding move is encoded as an integer index.
   - The processed data is stored in `X.npy` (board states) and `y.npy` (moves).

2. **Neural Network Training**:
   - The neural network is trained to predict the best move given a particular board state.
   - The model uses **TensorFlow** and is trained using the data in `X.npy` and `y.npy`. After training, the model is saved as `chess_ai_model.h5`.

3. **Game Execution**:
   - The chess game is played using **Pygame**, with the human player playing as white, and the AI (black) using the trained neural network model to predict its moves.
   - The AI predicts its move by analyzing the current board state and choosing the best move according to the model's output.

## **Getting Started**

### **Prerequisites**

Ensure you have the following installed:
- **Python 3.8+**
- **Pip** (Python package installer)
- **Git** (optional, if cloning from GitHub)

### **Installation**

1. **Clone the repository** (or download it):


   git clone https://github.com/YOUR-USERNAME/chess_engine.git
   
   cd chess_engine

3. **Create a virtual enironment**

   python3 -m venv myenv
   
   source myenv/bin/activate
   
   On Windows: myenv\Scripts\activate

5. **Install the dependencies**
   pip install -r requirements.txt

The trained model will be saved as chess_ai_model.h5, which will be used by the chess game to predict moves.

### **File Descriptions**


**chess_game.py**: Main script that runs the chess game using Pygame and the trained AI.

**data_preprocessing.py**: Preprocesses PGN chess games into a format suitable for training the neural network.

**train_model.py**: Trains the neural network using the processed chess data and saves the model as chess_ai_model.h5.

**chess_ai_model.h5**: The trained neural network model used by the AI to predict moves during the game.

**move_dict.json and reverse_move_dict.json**: Dictionaries for converting chess moves to numerical indices and vice versa.

**assets/**: Folder containing images of chess pieces used in the Pygame interface.

**X.npy and y.npy**: Preprocessed input and output data for training the neural network model.


### **To install all dependencies**

pip install -r requirements.txt

### **How to Add More Data**
Add additional PGN files of chess games to your project.

Run the data_preprocessing.py script to process the new data.

Retrain the model using train_model.py to include the new data in the AI's learning process.

### **Contributing**

If you'd like to contribute to this project:

Fork the repository.

Create a new branch.

Submit a pull request.
   




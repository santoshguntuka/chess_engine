import chess.pgn
import numpy as np
import json
import os
import gc  # Garbage collector

# Function to parse a batch of games from a PGN file
def parse_pgn_batch(pgn_file, start_game, batch_size):
    games = []
    with open(pgn_file) as pgn:
        for i in range(start_game):
            chess.pgn.read_game(pgn)  # Skip games until we reach the batch start point

        for _ in range(batch_size):
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            board = game.board()
            for move in game.mainline_moves():
                games.append((board.copy(), move))
                board.push(move)
    return games

# Function to convert the board state into a tensor (12x8x8)
def board_to_tensor(board):
    tensor = np.zeros((12, 8, 8), dtype=np.float32)
    piece_map = {chess.PAWN: 0, chess.KNIGHT: 1, chess.BISHOP: 2, chess.ROOK: 3, chess.QUEEN: 4, chess.KING: 5}
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            piece_type = piece_map[piece.piece_type]
            color = 0 if piece.color == chess.WHITE else 1
            tensor[color * 6 + piece_type][7 - chess.square_rank(square)][chess.square_file(square)] = 1
    return tensor.flatten()

# Helper function to one-hot encode y values
def one_hot_encode(y, num_classes):
    return np.eye(num_classes)[y]

# Create move dictionaries (move to label and label to move)
def create_move_dict(training_data, move_dict=None):
    all_moves = set(move.uci() for _, move in training_data)
    if move_dict is None:
        move_list = sorted(list(all_moves))
        move_dict = {move: idx for idx, move in enumerate(move_list)}
        reverse_move_dict = {idx: move for move, idx in move_dict.items()}
    else:
        current_index = max(move_dict.values()) + 1
        for move in all_moves:
            if move not in move_dict:
                move_dict[move] = current_index
                current_index += 1
        reverse_move_dict = {idx: move for move, idx in move_dict.items()}
    return move_dict, reverse_move_dict

# Save the move_dict and reverse_move_dict to JSON
def save_dicts(move_dict, reverse_move_dict, data_dir="data"):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    with open(f"{data_dir}/move_dict.json", "w") as f:
        json.dump(move_dict, f)
    with open(f"{data_dir}/reverse_move_dict.json", "w") as f:
        json.dump(reverse_move_dict, f)

# Function to pad arrays to the same size
def pad_arrays(y_existing, y_new):
    num_classes_existing = y_existing.shape[1]
    num_classes_new = y_new.shape[1]

    # If existing data has fewer classes, pad it
    if num_classes_existing < num_classes_new:
        pad_width = num_classes_new - num_classes_existing
        y_existing = np.pad(y_existing, ((0, 0), (0, pad_width)), 'constant')
    
    # If new data has fewer classes, pad it
    elif num_classes_new < num_classes_existing:
        pad_width = num_classes_existing - num_classes_new
        y_new = np.pad(y_new, ((0, 0), (0, pad_width)), 'constant')

    return y_existing, y_new

# Prepare the dataset (appending new data)
# Prepare the dataset (appending new data)
def create_dataset(training_data, move_dict, data_dir="data"):
    # Ensure the 'data' directory exists
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    X, y = [], []
    num_classes = len(move_dict)  # Get total number of unique moves for one-hot encoding

    for board, move in training_data:
        X.append(board_to_tensor(board))
        y.append(move_dict[move.uci()])

    X = np.array(X)
    y = np.array(y)

    # One-hot encode the new y data
    y = one_hot_encode(y, num_classes)

    # Load existing data if it exists
    if os.path.exists(f"{data_dir}/X.npy"):
        print("Loading existing data...")
        X_existing = np.load(f"{data_dir}/X.npy")
        y_existing = np.load(f"{data_dir}/y.npy")

        # Check if dimensions of the new data and old data are the same
        if X_existing.shape[1] != X.shape[1]:
            raise ValueError(f"Dimension mismatch between existing X and new X: {X_existing.shape[1]} vs {X.shape[1]}")

        # Pad y_existing and y to the same number of classes before concatenating
        y_existing, y = pad_arrays(y_existing, y)

        # Concatenate the old and new data
        X = np.concatenate((X_existing, X), axis=0)
        y = np.concatenate((y_existing, y), axis=0)

    # Save the updated dataset
    np.save(f"{data_dir}/X.npy", X)
    np.save(f"{data_dir}/y.npy", y)


# Main process to parse PGN, create dictionaries, and generate dataset in batches
if __name__ == "__main__":
    # Path to your existing PGN file and your Google Drive PGN file
    pgn_files = [
        "/content/chess_engine/scripts/lichess_data.pgn",  # Example existing data
        "/content/drive/MyDrive/Chess_png/lichess_db_standard_rated_2016-08.pgn"  # Your file from Google Drive
    ]

    batch_size = 1000  # Number of games to process per batch
    total_games = 5000  # Total games to process per PGN file

    # Load existing move_dict if it exists
    move_dict_path = "data/move_dict.json"
    if os.path.exists(move_dict_path):
        with open(move_dict_path, 'r') as f:
            move_dict = json.load(f)
    else:
        move_dict = None

    for pgn_file in pgn_files:
        print(f"Processing file: {pgn_file}")

        for start_game in range(0, total_games, batch_size):
            print(f"Processing games {start_game} to {start_game + batch_size}...")
            training_data_batch = parse_pgn_batch(pgn_file, start_game, batch_size)

            # Create or update move dictionaries with the batch data
            move_dict, reverse_move_dict = create_move_dict(training_data_batch, move_dict)

            # Create and save the dataset for this batch
            create_dataset(training_data_batch, move_dict)

            # Free up memory after processing the batch
            del training_data_batch
            gc.collect()

    # Save the updated move dictionaries
    save_dicts(move_dict, reverse_move_dict)
    
    print("Data preprocessing complete. Files saved in the 'data/' folder.")

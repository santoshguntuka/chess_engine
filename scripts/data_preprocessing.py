import chess.pgn
import numpy as np
import os
import json
from tensorflow.keras.utils import to_categorical

# Function to parse PGN file and return a list of board states and moves
def parse_pgn(pgn_file, max_games=10000):
    games = []
    with open(pgn_file) as pgn:
        for _ in range(max_games):
            game = chess.pgn.read_game(pgn)
            if game is None:
                break
            board = game.board()
            for move in game.mainline_moves():
                games.append((board.copy(), move))
                board.push(move)
    return games

# Convert the board state into a tensor (12x8x8)
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

# Create move dictionaries (move to label and label to move)
def create_move_dict(training_data):
    all_moves = set(move.uci() for _, move in training_data)
    move_list = sorted(list(all_moves))
    move_dict = {move: idx for idx, move in enumerate(move_list)}
    reverse_move_dict = {idx: move for move, idx in move_dict.items()}
    return move_dict, reverse_move_dict

# Save move_dict and reverse_move_dict to JSON
def save_dicts(move_dict, reverse_move_dict, data_dir="data"):
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    with open(f"{data_dir}/move_dict.json", "w") as f:
        json.dump(move_dict, f)
    with open(f"{data_dir}/reverse_move_dict.json", "w") as f:
        json.dump(reverse_move_dict, f)

# Prepare the dataset
def create_dataset(training_data, move_dict, data_dir="data"):
    X, y = [], []
    for board, move in training_data:
        X.append(board_to_tensor(board))
        y.append(move_dict[move.uci()])

    X = np.array(X)
    y = np.array(y)

    # One-hot encode the labels (y)
    y = to_categorical(y, num_classes=len(move_dict))

    # Save the dataset
    np.save(f"{data_dir}/X.npy", X)
    np.save(f"{data_dir}/y.npy", y)

# Main process to parse PGN, create dictionaries, and generate dataset
if __name__ == "__main__":
    pgn_file = "lichess_data.pgn"  # Path to your PGN file
    training_data = parse_pgn(pgn_file, max_games=5000)  # Parse up to 5000 games

    # Create and save move dictionaries
    move_dict, reverse_move_dict = create_move_dict(training_data)
    save_dicts(move_dict, reverse_move_dict)

    # Create and save the dataset
    create_dataset(training_data, move_dict)

    print("Data preprocessing complete. Files saved in the 'data/' folder.")

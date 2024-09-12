import pygame
import sys
import chess
import tensorflow as tf
import numpy as np
import json

# Initialize Pygame
pygame.init()

# Define constants
WIDTH, HEIGHT = 640, 640  # Chessboard is 8x8, so each square is 80x80
SQUARE_SIZE = WIDTH // 8
FPS = 60  # Frames per second

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
LIGHT_SQUARE = (240, 217, 181)
DARK_SQUARE = (181, 136, 99)

# Set up the display window
window = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Chess Game")

# Load images for the pieces
PIECES = {
    chess.PAWN: {"w": pygame.image.load("assets/white_pawn.png"), "b": pygame.image.load("assets/black_pawn.png")},
    chess.ROOK: {"w": pygame.image.load("assets/white_rook.png"), "b": pygame.image.load("assets/black_rook.png")},
    chess.KNIGHT: {"w": pygame.image.load("assets/white_knight.png"), "b": pygame.image.load("assets/black_knight.png")},
    chess.BISHOP: {"w": pygame.image.load("assets/white_bishop.png"), "b": pygame.image.load("assets/black_bishop.png")},
    chess.QUEEN: {"w": pygame.image.load("assets/white_queen.png"), "b": pygame.image.load("assets/black_queen.png")},
    chess.KING: {"w": pygame.image.load("assets/white_king.png"), "b": pygame.image.load("assets/black_king.png")}
}

# Resize pieces to fit on the board
for piece in PIECES:
    for color in PIECES[piece]:
        PIECES[piece][color] = pygame.transform.scale(PIECES[piece][color], (SQUARE_SIZE, SQUARE_SIZE))

# Chess board using python-chess
board = chess.Board()

# Load the AI model and move dictionaries
model = tf.keras.models.load_model('data/chess_ai_model.h5')  # Load the trained model
with open('data/move_dict.json', 'r') as f:
    move_dict = json.load(f)
with open('data/reverse_move_dict.json', 'r') as f:
    reverse_move_dict = json.load(f)

# Function to predict the AI's move using the neural network
def predict_ai_move(board):
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
    
    board_tensor = board_to_tensor(board)
    board_tensor = np.expand_dims(board_tensor, axis=0)  # Add batch dimension
    predictions = model.predict(board_tensor)[0]  # Get predictions

    # Get the best predicted move
    predicted_move_idx = np.argmax(predictions)
    predicted_move_uci = reverse_move_dict[str(predicted_move_idx)]
    ai_move = chess.Move.from_uci(predicted_move_uci)

    # Ensure the predicted move is legal
    if ai_move in board.legal_moves:
        return ai_move
    else:
        return np.random.choice(list(board.legal_moves))  # Fallback in case of an illegal move

# Function to draw the chessboard
def draw_chessboard(window):
    font = pygame.font.SysFont("Arial", 24)

    for row in range(8):
        for col in range(8):
            color = LIGHT_SQUARE if (row + col) % 2 == 0 else DARK_SQUARE
            pygame.draw.rect(window, color, (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE))

            # Add column labels (a-h) at the bottom
            if row == 7:
                label = font.render(chr(97 + col), True, BLACK if color == LIGHT_SQUARE else WHITE)
                window.blit(label, (col * SQUARE_SIZE + SQUARE_SIZE - 20, HEIGHT - 30))

            # Add row labels (1-8) on the left
            if col == 0:
                label = font.render(str(8 - row), True, BLACK if color == LIGHT_SQUARE else WHITE)
                window.blit(label, (10, row * SQUARE_SIZE + 10))

# Function to draw pieces on the board
def draw_pieces(window, board):
    for square in chess.SQUARES:
        piece = board.piece_at(square)
        if piece:
            row = 7 - (square // 8)  # Pygame's Y axis is reversed
            col = square % 8
            color = "w" if piece.color == chess.WHITE else "b"
            window.blit(PIECES[piece.piece_type][color], (col * SQUARE_SIZE, row * SQUARE_SIZE))

# Convert mouse position to board position (row, col)
def get_square_under_mouse(pos):
    x, y = pos
    row = y // SQUARE_SIZE
    col = x // SQUARE_SIZE
    return chess.square(col, 7 - row)

# Main loop
def main():
    global board
    clock = pygame.time.Clock()
    selected_square = None

    # Main game loop
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.MOUSEBUTTONDOWN:
                pos = pygame.mouse.get_pos()
                square = get_square_under_mouse(pos)

                if selected_square is None:
                    piece = board.piece_at(square)
                    if piece and piece.color == board.turn:  # Human player's turn
                        selected_square = square
                        print(f"Selected {piece} on {chess.square_name(selected_square)}")
                else:
                    move = chess.Move(from_square=selected_square, to_square=square)

                    # Check if the move is legal, then push it to the board
                    if board.is_legal(move):
                        board.push(move)
                        selected_square = None

                        # Check for end conditions (checkmate, stalemate)
                        if board.is_checkmate():
                            print("Checkmate!")
                            pygame.quit()
                            sys.exit()
                        elif board.is_stalemate():
                            print("Stalemate!")
                            pygame.quit()
                            sys.exit()
                        elif board.is_check():
                            print("Check!")
                    else:
                        selected_square = None

        # AI's turn
        if not board.turn:  # AI plays as black
            ai_move = predict_ai_move(board)
            board.push(ai_move)

            # Check for end conditions (checkmate, stalemate)
            if board.is_checkmate():
                print("Checkmate! AI wins!")
                pygame.quit()
                sys.exit()
            elif board.is_stalemate():
                print("Stalemate!")
                pygame.quit()
                sys.exit()
            elif board.is_check():
                print("Check!")

        # Fill the window with the chessboard
        draw_chessboard(window)

        # Draw the pieces on the board
        draw_pieces(window, board)

        # Update the display
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()

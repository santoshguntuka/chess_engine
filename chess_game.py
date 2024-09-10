import pygame
import sys
import chess

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

# Function to handle pawn promotion
def handle_pawn_promotion():
    """
    Allows the player to choose what piece the pawn should be promoted to.
    """
    promotion_menu = True
    promotion_choice = None

    while promotion_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle keyboard input for promotion
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_q:
                    promotion_choice = chess.QUEEN
                elif event.key == pygame.K_r:
                    promotion_choice = chess.ROOK
                elif event.key == pygame.K_b:
                    promotion_choice = chess.BISHOP
                elif event.key == pygame.K_n:
                    promotion_choice = chess.KNIGHT

                if promotion_choice:
                    promotion_menu = False

        # Draw promotion options
        window.fill(WHITE)
        font = pygame.font.SysFont("Arial", 30)
        text = font.render("Promote pawn to (Q)ueen, (R)ook, (B)ishop, (K)night:", True, BLACK)
        window.blit(text, (20, HEIGHT // 2 - 40))

        pygame.display.flip()

    return promotion_choice

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
                    if piece and piece.color == board.turn:
                        selected_square = square
                        print(f"Selected {piece} on {chess.square_name(selected_square)}")
                else:
                    move = chess.Move(from_square=selected_square, to_square=square)

                    # Handle pawn promotion
                    if board.is_legal(move):
                        if board.piece_at(selected_square).piece_type == chess.PAWN:
                            # Check if pawn is promoting (white to rank 1 or black to rank 8)
                            if (board.turn == chess.WHITE and chess.square_rank(square) == 0) or \
                               (board.turn == chess.BLACK and chess.square_rank(square) == 7):
                                # Prompt player for pawn promotion
                                promotion_choice = handle_pawn_promotion()
                                move = chess.Move(from_square=selected_square, to_square=square, promotion=promotion_choice)

                        board.push(move)
                        selected_square = None

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

        # Fill the window with the chessboard
        draw_chessboard(window)

        # Draw the pieces on the board
        draw_pieces(window, board)

        # Update the display
        pygame.display.update()
        clock.tick(FPS)


if __name__ == "__main__":
    main()


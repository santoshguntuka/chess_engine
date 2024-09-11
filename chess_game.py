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

# Function to handle pawn promotion with a pop-up
def handle_pawn_promotion(window):
    """
    Allows the player to choose what piece the pawn should be promoted to using a small pop-up.
    """
    promotion_menu = True
    promotion_choice = None
    popup_width, popup_height = 200, 100  # Pop-up size
    popup_x = (WIDTH - popup_width) // 2  # Center the pop-up
    popup_y = (HEIGHT - popup_height) // 2
    
    font = pygame.font.SysFont("Arial", 24)
    
    while promotion_menu:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            # Handle mouse clicks for promotion
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()

                # Check if the user clicked on the piece options
                if popup_x + 10 <= mouse_x <= popup_x + 50 and popup_y + 40 <= mouse_y <= popup_y + 80:
                    promotion_choice = chess.QUEEN
                elif popup_x + 60 <= mouse_x <= popup_x + 100 and popup_y + 40 <= mouse_y <= popup_y + 80:
                    promotion_choice = chess.ROOK
                elif popup_x + 110 <= mouse_x <= popup_x + 150 and popup_y + 40 <= mouse_y <= popup_y + 80:
                    promotion_choice = chess.BISHOP
                elif popup_x + 160 <= mouse_x <= popup_x + 200 and popup_y + 40 <= mouse_y <= popup_y + 80:
                    promotion_choice = chess.KNIGHT

                if promotion_choice:
                    promotion_menu = False

        # Draw the pop-up box
        pygame.draw.rect(window, WHITE, (popup_x, popup_y, popup_width, popup_height))
        pygame.draw.rect(window, BLACK, (popup_x, popup_y, popup_width, popup_height), 2)  # Border

        # Draw text for promotion options
        text = font.render("Choose Promotion", True, BLACK)
        window.blit(text, (popup_x + 20, popup_y + 10))

        # Draw the promotion options
        pygame.draw.rect(window, LIGHT_SQUARE, (popup_x + 10, popup_y + 40, 40, 40))
        window.blit(PIECES[chess.QUEEN]['w'], (popup_x + 10, popup_y + 40))

        pygame.draw.rect(window, LIGHT_SQUARE, (popup_x + 60, popup_y + 40, 40, 40))
        window.blit(PIECES[chess.ROOK]['w'], (popup_x + 60, popup_y + 40))

        pygame.draw.rect(window, LIGHT_SQUARE, (popup_x + 110, popup_y + 40, 40, 40))
        window.blit(PIECES[chess.BISHOP]['w'], (popup_x + 110, popup_y + 40))

        pygame.draw.rect(window, LIGHT_SQUARE, (popup_x + 160, popup_y + 40, 40, 40))
        window.blit(PIECES[chess.KNIGHT]['w'], (popup_x + 160, popup_y + 40))

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

                    # Check if the selected piece is a pawn and is eligible for promotion
                    if board.piece_at(selected_square).piece_type == chess.PAWN:
                        # If the pawn is about to promote (white pawn to 8th rank, black pawn to 1st rank)
                        if (board.turn == chess.WHITE and chess.square_rank(square) == 7) or \
                           (board.turn == chess.BLACK and chess.square_rank(square) == 0):
                            # Trigger promotion
                            promotion_choice = handle_pawn_promotion(window)
                            if promotion_choice:
                                # Update the move with the chosen promotion piece
                                move = chess.Move(from_square=selected_square, to_square=square, promotion=promotion_choice)

                    # If the move is legal, push it to the board
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

        # Fill the window with the chessboard
        draw_chessboard(window)

        # Draw the pieces on the board
        draw_pieces(window, board)

        # Update the display
        pygame.display.update()
        clock.tick(FPS)

if __name__ == "__main__":
    main()

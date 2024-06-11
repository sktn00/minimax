"""
Cat and Mouse game

This is a game where a cat tries to catch a mouse on an 8x8 grid.
The mouse tries to reach a randomly placed escape square on the edge of the board.
The cat and mouse take turns moving, and the game ends when either the cat catches
the mouse, the mouse reaches the escape square, or the mouse survives for 20 moves.
"""

import random

import pygame

# Constants
BOARD_SIZE = 8
SQUARE_SIZE = 100
SCREEN_SIZE = BOARD_SIZE * SQUARE_SIZE

# Initialize Pygame
pygame.init()

# Set up the display
screen = pygame.display.set_mode((SCREEN_SIZE, SCREEN_SIZE))
pygame.display.set_caption("Cat and Mouse")

# Load images
cat_image = pygame.image.load("cat.png").convert_alpha()
mouse_image = pygame.image.load("mouse.png").convert_alpha()
cat_image = pygame.transform.scale(cat_image, (SQUARE_SIZE, SQUARE_SIZE))
mouse_image = pygame.transform.scale(mouse_image, (SQUARE_SIZE, SQUARE_SIZE))


def draw_board(escape_pos):
    """
    Draw the game board.

    Args:
        escape_pos (tuple): The position of the escape square.
    """
    for row in range(BOARD_SIZE):
        for col in range(BOARD_SIZE):
            color = (255, 178, 102) if (row + col) % 2 == 0 else (153, 76, 0)
            pygame.draw.rect(
                screen,
                color,
                (col * SQUARE_SIZE, row * SQUARE_SIZE, SQUARE_SIZE, SQUARE_SIZE),
            )

    # Draw escape square
    pygame.draw.rect(
        screen,
        (0, 255, 0),
        (
            escape_pos[1] * SQUARE_SIZE,
            escape_pos[0] * SQUARE_SIZE,
            SQUARE_SIZE,
            SQUARE_SIZE,
        ),
    )


def draw_cat_and_mouse(cat_pos, mouse_pos):
    """
    Draw the cat and mouse on the board.

    Args:
        cat_pos (tuple): The position of the cat.
        mouse_pos (tuple): The position of the mouse.
    """
    screen.blit(cat_image, (cat_pos[1] * SQUARE_SIZE, cat_pos[0] * SQUARE_SIZE))
    screen.blit(mouse_image, (mouse_pos[1] * SQUARE_SIZE, mouse_pos[0] * SQUARE_SIZE))


def calculate_manhattan_distance(pos1, pos2):
    """
    Calculate the Manhattan distance between two points.

    Args:
        pos1 (tuple): The first position.
        pos2 (tuple): The second position.

    Returns:
        int: The Manhattan distance between the two positions.
    """
    return abs(pos1[0] - pos2[0]) + abs(pos1[1] - pos2[1])


def random_edge_pos(mouse_pos, min_distance):
    """
    Generate a random edge position at least min_distance away from the mouse.

    Args:
        mouse_pos (tuple): The position of the mouse.
        min_distance (int): The minimum distance from the mouse.

    Returns:
        tuple: A random edge position that meets the distance requirement.
    """
    possible_positions = []
    for i in range(BOARD_SIZE):
        positions = [(0, i), (i, BOARD_SIZE - 1), (BOARD_SIZE - 1, i), (i, 0)]
        for pos in positions:
            if calculate_manhattan_distance(pos, mouse_pos) >= min_distance:
                possible_positions.append(pos)

    if not possible_positions:
        # If no position is far enough, choose the farthest one
        max_distance = -1
        farthest_pos = None
        for i in range(BOARD_SIZE):
            positions = [(0, i), (i, BOARD_SIZE - 1), (BOARD_SIZE - 1, i), (i, 0)]
            for pos in positions:
                dist = calculate_manhattan_distance(pos, mouse_pos)
                if dist > max_distance:
                    max_distance = dist
                    farthest_pos = pos
        return farthest_pos

    return random.choice(possible_positions)


def move_cat(cat_pos, mouse_pos, escape_pos, depth, alpha, beta, maximizing_player):
    """
    Determine the best move for the cat using the minimax algorithm with Alpha-Beta pruning.

    Args:
        cat_pos (tuple): The current position of the cat.
        mouse_pos (tuple): The current position of the mouse.
        escape_pos (tuple): The position of the escape square.
        depth (int): The remaining depth in the game tree.
        alpha (float): The current alpha value for pruning.
        beta (float): The current beta value for pruning.
        maximizing_player (bool): True if the current player is maximizing, False otherwise.

    Returns:
        tuple: The best move for the cat, and the evaluation score of that move.
    """
    # Check for immediate capture opportunity
    capture_moves = [
        (cat_pos[0] + dx, cat_pos[1] + dy)
        for dx, dy in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        if (cat_pos[0] + dx, cat_pos[1] + dy) == mouse_pos
        and 0 <= cat_pos[0] + dx < BOARD_SIZE
        and 0 <= cat_pos[1] + dy < BOARD_SIZE
    ]
    if capture_moves:
        return capture_moves[0], 1000  # Large bonus for capturing the mouse

    if depth == 0 or cat_caught_mouse(cat_pos, mouse_pos):
        # Use Manhattan distance
        distance_to_mouse = -calculate_manhattan_distance(cat_pos, mouse_pos) * 15
        distance_to_escape = -calculate_manhattan_distance(cat_pos, escape_pos) * 8

        # Combine all components
        return None, distance_to_mouse + distance_to_escape

    # Now including diagonal moves: up, down, left, right, and all four diagonals
    possible_moves = [
        (cat_pos[0] + dx, cat_pos[1] + dy)
        for dx, dy in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        if 0 <= cat_pos[0] + dx < BOARD_SIZE and 0 <= cat_pos[1] + dy < BOARD_SIZE
    ]

    if maximizing_player:
        max_eval = float("-inf")
        best_moves = []
        for move in possible_moves:
            _, eval_score = move_cat(
                move, mouse_pos, escape_pos, depth - 1, alpha, beta, False
            )
            if eval_score > max_eval:
                max_eval = eval_score
                best_moves = [move]
            elif eval_score == max_eval:
                # Add randomness in tie-breaking
                best_moves.append(move)
            alpha = max(alpha, eval_score)
            if beta <= alpha:
                break
        # Randomly choose among the best moves
        return random.choice(best_moves), max_eval
    else:
        min_eval = float("inf")  # Initialize with positive infinity
        best_moves = []
        for move in possible_moves:
            _, eval_score = move_cat(
                move, mouse_pos, escape_pos, depth - 1, alpha, beta, True
            )
            if eval_score < min_eval:
                min_eval = eval_score
                best_moves = [move]
            elif eval_score == min_eval:
                # Add randomness in tie-breaking
                best_moves.append(move)
            beta = min(beta, eval_score)
            if beta <= alpha:
                break
        # Randomly choose among the best moves
        return random.choice(best_moves), min_eval


def move_mouse(mouse_pos, cat_pos, escape_pos):
    """
    Determine the best move for the mouse.

    Args:
        mouse_pos (tuple): The current position of the mouse.
        cat_pos (tuple): The current position of the cat.
        escape_pos (tuple): The position of the escape square.

    Returns:
        tuple: The best move for the mouse.
    """
    # Calculate all possible moves
    possible_moves = [
        (mouse_pos[0] + dx, mouse_pos[1] + dy)
        for dx, dy in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        if 0 <= mouse_pos[0] + dx < BOARD_SIZE and 0 <= mouse_pos[1] + dy < BOARD_SIZE
    ]

    # Immediate actions
    if escape_pos in possible_moves:
        return escape_pos  # Escape if possible

    if cat_pos in possible_moves:
        possible_moves.remove(cat_pos)  # Never move onto the cat's current square

    # Predict the cat's possible next moves
    cat_next_moves = [
        (cat_pos[0] + dx, cat_pos[1] + dy)
        for dx, dy in [
            (-1, 0),
            (1, 0),
            (0, -1),
            (0, 1),
            (-1, -1),
            (-1, 1),
            (1, -1),
            (1, 1),
        ]
        if 0 <= cat_pos[0] + dx < BOARD_SIZE and 0 <= cat_pos[1] + dy < BOARD_SIZE
    ]

    # Filter out moves that would allow the cat to capture immediately
    safe_moves = [move for move in possible_moves if move not in cat_next_moves]

    # If there are safe moves, only consider those; otherwise, consider all moves
    evaluation_moves = safe_moves if safe_moves else possible_moves

    best_moves = []
    best_score = float("-inf")

    for move in evaluation_moves:
        # Calculate distance to cat (want to maximize this)
        cat_distance = calculate_manhattan_distance(move, cat_pos)

        # If all moves are unsafe, prioritize the one that keeps us farthest from the cat
        if not safe_moves:
            best_moves = [
                max(
                    possible_moves,
                    key=lambda m: calculate_manhattan_distance(m, cat_pos),
                )
            ]
            break

        # Calculate progress towards escape square (want to maximize this)
        current_distance = calculate_manhattan_distance(mouse_pos, escape_pos)
        new_distance = calculate_manhattan_distance(move, escape_pos)
        escape_progress = current_distance - new_distance

        # Apply other factors: corner penalty, escape weight
        corner_penalty = (
            -3
            if move
            in [
                (0, 0),
                (0, BOARD_SIZE - 1),
                (BOARD_SIZE - 1, 0),
                (BOARD_SIZE - 1, BOARD_SIZE - 1),
            ]
            else 0
        )
        escape_weight = 2  # Prioritize escape more
        safe_bonus = 5 if move in safe_moves else 0  # Extra bonus for safe moves

        score = (
            cat_distance
            + (escape_weight * escape_progress)
            + corner_penalty
            + safe_bonus
        )

        # Update best moves
        if score > best_score:
            best_score = score
            best_moves = [move]
        elif score == best_score:
            # Add randomness in tie-breaking
            best_moves.append(move)

    # Randomly choose among the best moves
    return random.choice(best_moves) if best_moves else mouse_pos


def cat_caught_mouse(cat_pos, mouse_pos):
    """
    Check if the cat caught the mouse.

    Args:
        cat_pos (tuple): The position of the cat.
        mouse_pos (tuple): The position of the mouse.

    Returns:
        bool: True if the cat caught the mouse, False otherwise.
    """
    return cat_pos == mouse_pos


def mouse_escaped(mouse_pos, escape_pos):
    """
    Check if the mouse reached the escape square.

    Args:
        mouse_pos (tuple): The position of the mouse.
        escape_pos (tuple): The position of the escape square.

    Returns:
        bool: True if the mouse reached the escape square, False otherwise.
    """
    return mouse_pos == escape_pos


def display_board(escape_pos):
    """
    Display the board after each move.

    Args:
        escape_pos (tuple): The position of the escape square.
    """
    screen.fill((0, 0, 0))
    draw_board(escape_pos)
    draw_cat_and_mouse(cat_pos, mouse_pos)
    pygame.display.flip()


def main():
    """
    Main function to run the game.
    """
    global cat_pos, mouse_pos

    # Ensure a minimum distance between cat and mouse at the start
    while True:
        cat_pos = (random.randint(0, BOARD_SIZE - 1), random.randint(0, BOARD_SIZE - 1))
        mouse_pos = (
            random.randint(0, BOARD_SIZE - 1),
            random.randint(0, BOARD_SIZE - 1),
        )
        if calculate_manhattan_distance(cat_pos, mouse_pos) >= 4:
            break

    # Increase the minimum distance for the escape square
    min_distance = 5
    escape_pos = random_edge_pos(mouse_pos, min_distance)

    # Main game loop
    move_count = 0
    turns = 0
    running = True
    while running:
        # Move cat on even turns
        if turns % 2 == 0:
            best_move, _ = move_cat(
                cat_pos,
                mouse_pos,
                escape_pos,
                depth=3,
                alpha=float("-inf"),
                beta=float("inf"),
                maximizing_player=True,
            )
            cat_pos = best_move if best_move else cat_pos
            display_board(escape_pos)
            pygame.time.delay(300)

            # Check game conditions
            if cat_caught_mouse(cat_pos, mouse_pos):
                print("Cat caught the mouse! Game over.")
                running = False

        # Move mouse on odd turns
        else:
            mouse_pos = move_mouse(mouse_pos, cat_pos, escape_pos)
            display_board(escape_pos)
            pygame.time.delay(300)

            # Check game conditions after mouse moves
            if cat_caught_mouse(cat_pos, mouse_pos):
                print("Cat caught the mouse! Game over.")
                running = False
            elif mouse_escaped(mouse_pos, escape_pos):
                print("Mouse reached the escape square! Mouse wins!")
                running = False

            # Check if mouse won by survival
            move_count += 1
            if move_count >= 20:
                print("Mouse survived for 20 moves! Mouse wins!")
                running = False

        # Event handling
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False

        turns += 1

    # Keep the window open for a moment after the game ends
    pygame.time.delay(500)
    pygame.quit()


if __name__ == "__main__":
    main()

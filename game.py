import pygame
import sys
import numpy as np
import random
import time

pygame.init()

WIDTH, HEIGHT = 700, 800
GRID_SIZE = 5
CELL_SIZE = 100
BOARD_SIZE = GRID_SIZE * CELL_SIZE
LINE_WIDTH = 2
FPS = 60
MARGIN = 20

BG_COLOR = (30, 30, 30)
LINE_COLOR = (80, 80, 80)
PLAYER_COLOR = (0, 204, 204)
AI_COLOR = (204, 0, 102)
TEXT_COLOR = (255, 255, 255)
SCORE_BOX_COLOR = (50, 50, 50)
HIGHLIGHT_COLOR = (255, 255, 0)
BUTTON_COLOR = (100, 100, 100)
BUTTON_HOVER_COLOR = (130, 130, 130)
BUTTON_TEXT_COLOR = (255, 255, 255)

BOARD_OFFSET_X = (WIDTH - BOARD_SIZE) // 2
BOARD_OFFSET_Y = 20

screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Cyber Grid: Strategic Network Game")
font = pygame.font.SysFont('Arial', 24)
small_font = pygame.font.SysFont('Arial', 18)
title_font = pygame.font.SysFont('Arial', 30, bold=True)
clock = pygame.time.Clock()

board = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
game_over = False
player_score = 0
ai_score = 0
turn = 1
difficulty = 2
last_move = None
game_start_time = time.time()

games_played = 0
player_wins = 0
ai_wins = 0
draws = 0

class Button:
    def __init__(self, x, y, width, height, text, font, action=None, selected=False):
        self.rect = pygame.Rect(x, y, width, height)
        self.text = text
        self.font = font
        self.action = action
        self.selected = selected

    def draw(self, surface):
        if self.selected:
            pygame.draw.rect(surface, BUTTON_HOVER_COLOR, self.rect)
            border_width = 2
        else:
            mouse_pos = pygame.mouse.get_pos()
            if self.rect.collidepoint(mouse_pos):
                pygame.draw.rect(surface, BUTTON_HOVER_COLOR, self.rect)
                border_width = 1
            else:
                pygame.draw.rect(surface, BUTTON_COLOR, self.rect)
                border_width = 1
                
        pygame.draw.rect(surface, TEXT_COLOR, self.rect, border_width)
        
        text_surface = self.font.render(self.text, True, BUTTON_TEXT_COLOR)
        text_rect = text_surface.get_rect(center=self.rect.center)
        surface.blit(text_surface, text_rect)

    def check_click(self, position):
        if self.rect.collidepoint(position):
            if self.action:
                self.action()
            return True
        return False

def draw_grid():
    pygame.draw.rect(screen, BG_COLOR, (BOARD_OFFSET_X, BOARD_OFFSET_Y, BOARD_SIZE, BOARD_SIZE))
    
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, LINE_COLOR, 
                         (BOARD_OFFSET_X, BOARD_OFFSET_Y + i * CELL_SIZE), 
                         (BOARD_OFFSET_X + BOARD_SIZE, BOARD_OFFSET_Y + i * CELL_SIZE), 
                         LINE_WIDTH)
    
    for i in range(GRID_SIZE + 1):
        pygame.draw.line(screen, LINE_COLOR, 
                         (BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y), 
                         (BOARD_OFFSET_X + i * CELL_SIZE, BOARD_OFFSET_Y + BOARD_SIZE), 
                         LINE_WIDTH)

def draw_nodes():
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            center_x = BOARD_OFFSET_X + col * CELL_SIZE + CELL_SIZE // 2
            center_y = BOARD_OFFSET_Y + row * CELL_SIZE + CELL_SIZE // 2
            
            if last_move is not None and row == last_move[0] and col == last_move[1]:
                pygame.draw.rect(
                    screen, 
                    HIGHLIGHT_COLOR, 
                    (BOARD_OFFSET_X + col * CELL_SIZE + 5, 
                     BOARD_OFFSET_Y + row * CELL_SIZE + 5, 
                     CELL_SIZE - 10, CELL_SIZE - 10),
                    width=3
                )
            
            if board[row][col] == 1:
                for r in range(3, 0, -1):
                    pygame.draw.circle(
                        screen, 
                        PLAYER_COLOR, 
                        (center_x, center_y), 
                        CELL_SIZE // 3 + r,
                        width=1
                    )
                
                pygame.draw.circle(screen, PLAYER_COLOR, (center_x, center_y), CELL_SIZE // 3)
                pygame.draw.circle(screen, BG_COLOR, (center_x, center_y), CELL_SIZE // 5)
            
            elif board[row][col] == 2:
                offset = CELL_SIZE // 3
                pygame.draw.line(
                    screen, AI_COLOR,
                    (center_x - offset, center_y - offset), 
                    (center_x + offset, center_y + offset),
                    width=5
                )
                pygame.draw.line(
                    screen, AI_COLOR,
                    (center_x + offset, center_y - offset), 
                    (center_x - offset, center_y + offset),
                    width=5
                )

def draw_scoreboard():
    pygame.draw.rect(screen, SCORE_BOX_COLOR, (0, BOARD_OFFSET_Y + BOARD_SIZE + MARGIN, WIDTH, HEIGHT - (BOARD_OFFSET_Y + BOARD_SIZE + MARGIN)))
    
    score_y = BOARD_OFFSET_Y + BOARD_SIZE + MARGIN * 2
    
    pygame.draw.circle(screen, PLAYER_COLOR, (40, score_y + 15), 15)
    pygame.draw.circle(screen, BG_COLOR, (40, score_y + 15), 8)
    player_text = font.render(f"Player: {player_score}", True, PLAYER_COLOR)
    screen.blit(player_text, (65, score_y))
    
    x_offset = 15
    pygame.draw.line(screen, AI_COLOR, (WIDTH - 50 - x_offset, score_y + 5), (WIDTH - 30 - x_offset, score_y + 25), width=4)
    pygame.draw.line(screen, AI_COLOR, (WIDTH - 30 - x_offset, score_y + 5), (WIDTH - 50 - x_offset, score_y + 25), width=4)
    ai_text = font.render(f"AI: {ai_score}", True, AI_COLOR)
    screen.blit(ai_text, (WIDTH - 120, score_y))

    if not game_over:
        turn_text = font.render(f"Turn: {'Player' if turn == 1 else 'AI'}", True, TEXT_COLOR)
        screen.blit(turn_text, (WIDTH // 2 - 50, score_y))
        
        status_y = score_y + 40
        
        diff_text = small_font.render(f"Difficulty: {['Easy', 'Medium', 'Hard'][difficulty-1]}", True, TEXT_COLOR)
        screen.blit(diff_text, (40, status_y))
        
        elapsed_time = int(time.time() - game_start_time)
        minutes = elapsed_time // 60
        seconds = elapsed_time % 60
        time_text = small_font.render(f"Time: {minutes:02d}:{seconds:02d}", True, TEXT_COLOR)
        screen.blit(time_text, (WIDTH - 120, status_y))
        
        hint_y = status_y + 40
        hint_text = small_font.render("Click on any empty cell to place your node", True, TEXT_COLOR)
        screen.blit(hint_text, (WIDTH // 2 - hint_text.get_width() // 2, hint_y))

    else:
        result = "Game Over!"
        if player_score > ai_score:
            result += " Player Wins!"
            result_color = PLAYER_COLOR
        elif ai_score > player_score:
            result += " AI Wins!"
            result_color = AI_COLOR
        else:
            result += " It's a Draw!"
            result_color = TEXT_COLOR
        
        result_text = font.render(result, True, result_color)
        screen.blit(result_text, (WIDTH // 2 - result_text.get_width() // 2, score_y))
        
        stats_y = score_y + 40
        stats_text = small_font.render(f"Games: {games_played} | Wins: {player_wins} | Losses: {ai_wins} | Draws: {draws}", True, TEXT_COLOR)
        screen.blit(stats_text, (WIDTH // 2 - stats_text.get_width() // 2, stats_y))
        
        new_game_button.draw(screen)
        easy_button.draw(screen)
        medium_button.draw(screen)
        hard_button.draw(screen)

def calculate_score():
    global player_score, ai_score
    player_score = 0
    ai_score = 0
    
    connections = {1: 0, 2: 0}
    node_count = {1: 0, 2: 0}
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] == 0:
                continue
                
            current_player = board[row][col]
            node_count[current_player] += 1
            
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                        
                    r, c = row + dr, col + dc
                    if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                        if board[r][c] == current_player:
                            connections[current_player] += 1

    for player_id in [1, 2]:
        connection_score = connections[player_id] // 2
        occupation_score = node_count[player_id]
        
        if node_count[player_id] > 1:
            max_possible_connections = (node_count[player_id] * (node_count[player_id] - 1)) // 2
            density = connection_score / max(1, max_possible_connections)
            density_bonus = int(3 * density)
        else:
            density_bonus = 0
            
        position_bonus = 0
        for row in range(GRID_SIZE):
            for col in range(GRID_SIZE):
                if board[row][col] == player_id:
                    if row == GRID_SIZE // 2 and col == GRID_SIZE // 2:
                        position_bonus += 2
                    elif (row == 0 or row == GRID_SIZE - 1) and (col == 0 or col == GRID_SIZE - 1):
                        position_bonus += 1
                    
        total_score = occupation_score + connection_score + density_bonus + position_bonus
        
        if player_id == 1:
            player_score = total_score
        else:
            ai_score = total_score

def evaluate_board():
    calculate_score()
    
    score_diff = ai_score - player_score
    strategic_value = 0
    
    center = GRID_SIZE // 2
    if board[center][center] == 2:
        strategic_value += 3
    elif board[center][center] == 1:
        strategic_value -= 3
    
    corners = [(0, 0), (0, GRID_SIZE-1), (GRID_SIZE-1, 0), (GRID_SIZE-1, GRID_SIZE-1)]
    for r, c in corners:
        if board[r][c] == 2:
            strategic_value += 2
        elif board[r][c] == 1:
            strategic_value -= 2

    ai_potential = 0
    player_potential = 0
    
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] != 0:
                continue
                
            ai_adjacent = 0
            player_adjacent = 0
            
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                        
                    r, c = row + dr, col + dc
                    if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                        if board[r][c] == 2:
                            ai_adjacent += 1
                        elif board[r][c] == 1:
                            player_adjacent += 1
            
            if ai_adjacent > 0:
                ai_potential += ai_adjacent
            if player_adjacent > 0:
                player_potential += player_adjacent
    
    potential_diff = ai_potential - player_potential
    
    return score_diff + strategic_value + potential_diff * 0.5

def is_board_full():
    return not np.any(board == 0)

def get_available_moves():
    moves = []
    for row in range(GRID_SIZE):
        for col in range(GRID_SIZE):
            if board[row][col] == 0:
                moves.append((row, col))
    return moves

def evaluate_move_quick(move, player):
    row, col = move
    
    board[row][col] = player
    
    adj_count = 0
    for dr in [-1, 0, 1]:
        for dc in [-1, 0, 1]:
            if dr == 0 and dc == 0:
                continue
                
            r, c = row + dr, col + dc
            if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE:
                if board[r][c] == player:
                    adj_count += 1
    
    strat_value = 0
    if row == GRID_SIZE // 2 and col == GRID_SIZE // 2:
        strat_value += 3
    elif (row == 0 or row == GRID_SIZE - 1) and (col == 0 or col == GRID_SIZE - 1):
        strat_value += 2
        
    board[row][col] = 0
    
    return adj_count + strat_value

def minimax(depth, is_maximizing, alpha, beta, use_noise=False):
    if depth == 0 or is_board_full():
        noise = random.uniform(-5, 5) if use_noise else 0
        return evaluate_board() + noise, None
    
    available_moves = get_available_moves()
    
    if len(available_moves) == 0:
        return evaluate_board(), None
    
    if is_maximizing:
        available_moves.sort(key=lambda move: evaluate_move_quick(move, 2), reverse=True)
    else:
        available_moves.sort(key=lambda move: evaluate_move_quick(move, 1))

    best_move = None
    
    if is_maximizing:
        max_eval = float('-inf')
        for move in available_moves:
            row, col = move
            board[row][col] = 2
            current_eval, _ = minimax(depth-1, False, alpha, beta, use_noise)
            board[row][col] = 0
            
            if current_eval > max_eval:
                max_eval = current_eval
                best_move = move
            
            alpha = max(alpha, current_eval)
            if beta <= alpha:
                break
        
        return max_eval, best_move
    
    else:
        min_eval = float('inf')
        for move in available_moves:
            row, col = move
            board[row][col] = 1
            current_eval, _ = minimax(depth-1, True, alpha, beta, use_noise)
            board[row][col] = 0
            
            if current_eval < min_eval:
                min_eval = current_eval
                best_move = move
            
            beta = min(beta, current_eval)
            if beta <= alpha:
                break
        
        return min_eval, best_move

def nash_equilibrium_strategy():
    calculate_score()
    score_diff = ai_score - player_score
    
    available_moves = get_available_moves()
    if not available_moves:
        return None
    
    if score_diff > 5:
        best_value = float('-inf')
        best_move = None
        for move in available_moves:
            row, col = move
            min_opponent_gain = float('inf')
            
            board[row][col] = 2
            our_score_gain = evaluate_board() - score_diff
            
            for opp_move in get_available_moves():
                o_row, o_col = opp_move
                board[o_row][o_col] = 1
                new_score_diff = evaluate_board()
                opponent_gain = score_diff - new_score_diff
                min_opponent_gain = min(min_opponent_gain, opponent_gain)
                board[o_row][o_col] = 0
            
            board[row][col] = 0
            
            move_value = our_score_gain - min_opponent_gain
            if move_value > best_value:
                best_value = move_value
                best_move = move
        
        return best_move

    else:
        best_expected_value = float('-inf')
        best_move = None
        
        for move in available_moves:
            row, col = move
            board[row][col] = 2
            
            immediate_gain = evaluate_board() - score_diff
            
            future_potential = 0
            for dr in [-1, 0, 1]:
                for dc in [-1, 0, 1]:
                    if dr == 0 and dc == 0:
                        continue
                        
                    r, c = row + dr, col + dc
                    if 0 <= r < GRID_SIZE and 0 <= c < GRID_SIZE and board[r][c] == 0:
                        board[r][c] = 2
                        future_potential += (evaluate_board() - score_diff - immediate_gain) * 0.5
                        board[r][c] = 0
            
            risk_factor = 0
            player_moves = get_available_moves()
            if player_moves:
                best_player_gain = float('-inf')
                for p_move in player_moves:
                    p_row, p_col = p_move
                    board[p_row][p_col] = 1
                    player_gain = score_diff - evaluate_board()
                    best_player_gain = max(best_player_gain, player_gain)
                    board[p_row][p_col] = 0
                
                risk_factor = best_player_gain * 0.7
            
            board[row][col] = 0
            
            expected_value = immediate_gain + future_potential - risk_factor
            
            if expected_value > best_expected_value:
                best_expected_value = expected_value
                best_move = move
        
        return best_move

def ai_move():
    global last_move
    
    if random.random() < 0.5 and difficulty > 1:
        best_move = nash_equilibrium_strategy()
    else:
        search_depth = {
            1: 1,
            2: 2,
            3: 3
        }[difficulty]
        
        use_noise = (difficulty == 1)
        
        _, best_move = minimax(search_depth, True, float('-inf'), float('inf'), use_noise)
    
    if best_move:
        row, col = best_move
        board[row][col] = 2
        last_move = (row, col)

def check_game_over():
    return is_board_full()

def set_difficulty(level):
    global difficulty
    difficulty = level

def restart_game():
    global board, game_over, player_score, ai_score, turn, last_move, game_start_time
    global games_played, player_wins, ai_wins, draws
    
    board = np.zeros((GRID_SIZE, GRID_SIZE), dtype=int)
    game_over = False
    player_score = 0
    ai_score = 0
    turn = 1
    last_move = None
    game_start_time = time.time()
    
    easy_button.selected = (difficulty == 1)
    medium_button.selected = (difficulty == 2)
    hard_button.selected = (difficulty == 3)

def handle_click(pos):
    global turn, game_over, games_played, player_wins, ai_wins, draws, last_move
    
    if game_over:
        if new_game_button.check_click(pos):
            restart_game()
            return
        if easy_button.check_click(pos):
            set_difficulty(1)
            restart_game()
            return
        if medium_button.check_click(pos):
            set_difficulty(2)
            restart_game()
            return
        if hard_button.check_click(pos):
            set_difficulty(3)
            restart_game()
            return
        return
    
    x, y = pos
    if (BOARD_OFFSET_X <= x <= BOARD_OFFSET_X + BOARD_SIZE and 
        BOARD_OFFSET_Y <= y <= BOARD_OFFSET_Y + BOARD_SIZE):
        
        col = (x - BOARD_OFFSET_X) // CELL_SIZE
        row = (y - BOARD_OFFSET_Y) // CELL_SIZE
        
        if 0 <= row < GRID_SIZE and 0 <= col < GRID_SIZE:
            if board[row][col] == 0 and turn == 1:
                board[row][col] = 1
                last_move = (row, col)
                
                calculate_score()
                
                turn = 2

def main():
    global game_over, games_played, player_wins, ai_wins, draws, turn
    global new_game_button, easy_button, medium_button, hard_button
    
    buttons_y = BOARD_OFFSET_Y + BOARD_SIZE + 120
    new_game_button = Button(WIDTH // 2 - 75, buttons_y, 150, 40, "New Game", font, restart_game)
    
    diff_buttons_y = buttons_y + 60
    easy_button = Button(WIDTH // 4 - 40, diff_buttons_y, 80, 30, "Easy", small_font, lambda: set_difficulty(1), difficulty == 1)
    medium_button = Button(WIDTH // 2 - 50, diff_buttons_y, 100, 30, "Medium", small_font, lambda: set_difficulty(2), difficulty == 2)
    hard_button = Button(3 * WIDTH // 4 - 40, diff_buttons_y, 80, 30, "Hard", small_font, lambda: set_difficulty(3), difficulty == 3)
    
    restart_game()
    
    running = True
    while running:
        clock.tick(FPS)
        
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                handle_click(event.pos)
        
        screen.fill(BG_COLOR)
        
        draw_grid()
        draw_nodes()
        draw_scoreboard()
        
        if turn == 2 and not game_over:
            ai_move()
            turn = 1
            
            if check_game_over():
                game_over = True
                games_played += 1
                if player_score > ai_score:
                    player_wins += 1
                elif ai_score > player_score:
                    ai_wins += 1
                else:
                    draws += 1
        
        pygame.display.flip()
    
    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    main()

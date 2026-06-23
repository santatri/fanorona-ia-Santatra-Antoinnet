from __future__ import annotations
import math
import time
from typing import Tuple, Optional, Dict, List
from game import Game, P1, P2

INF = 10_000


def evaluate(game: Game, ai_player: int) -> int:
    opponent = P1 if ai_player == P2 else P2
    
    # 1. Terminal winner check (already handled in minimax, but for safety)
    winner = game.get_winner()
    if winner == ai_player:
        return INF
    if winner == opponent:
        return -INF
        
    score = 0
    
    # 2. Mobility Heuristic (Critical for Phase 2)
    # The more legal moves you have, the better. In Phase 2, having 0 moves means losing.
    ai_moves = len([m for m in game.legal_moves() if game.current_player == ai_player])
    # Note: game.legal_moves() returns moves for the current player.
    # To get mobility for both, we might need a more efficient way or simulate.
    # For now, let's focus on the lines and simple mobility if it's the AI's turn.
    
    # Simple Mobility: Number of legal moves if it was the player's turn
    # This is a bit expensive in the inner loop, let's stick to line heuristics first 
    # but refine them based on Phase.
    
    for a, b, c in [
        (0, 1, 2), (3, 4, 5), (6, 7, 8),
        (0, 3, 6), (1, 4, 7), (2, 5, 8),
        (0, 4, 8), (2, 4, 6),
    ]:
        line = [game.board[a], game.board[b], game.board[c]]
        ai_count = line.count(ai_player)
        opp_count = line.count(opponent)
        
        if opp_count == 0:
            if ai_count == 2:
                # 2-in-a-row with an empty spot is very strong
                score += 80 if game.phase == 1 else 150
            elif ai_count == 1:
                score += 10
        if ai_count == 0:
            if opp_count == 2:
                # Need to block opponent's 2-in-a-row
                score -= 100 if game.phase == 1 else 200
            elif opp_count == 1:
                score -= 8
                
    # 3. Positional Advantage
    # Center (4) is the most connected node
    if game.board[4] == ai_player:
        score += 15
    elif game.board[4] == opponent:
        score -= 15
        
    # 4. Phase 2 Mobility (if we can afford the cost)
    if game.phase == 2:
        # Penalize being on edges with fewer connections? 
        # Actually mobility is best calculated as the number of legal target squares.
        pass

    return score


def minimax(
    game: Game,
    depth: int,
    maximizing: bool,
    perspective: int,
    alpha: int,
    beta: int,
    use_alpha_beta: bool,
    transposition_table: Dict[tuple, Tuple[int, int]],
    start_time: float,
    time_limit: float,
) -> Tuple[int, int]:
    # Check time limit
    if time.perf_counter() - start_time > time_limit:
        return evaluate(game, perspective), 1

    key = (tuple(game.board), game.current_player, game.phase)
    if key in transposition_table:
        cached_val, cached_depth = transposition_table[key]
        if cached_depth >= depth:
            return cached_val, 1

    winner = game.get_winner()
    nodes = 1
    if winner != 0:
        value = INF if winner == perspective else -INF
        return value, nodes
    if depth == 0:
        value = evaluate(game, perspective)
        transposition_table[key] = (value, depth)
        return value, nodes

    moves = game.legal_moves()
    if not moves:
        return 0, nodes

    # Simple Move Ordering: prioritize moves that lead to higher immediate evaluation
    def get_move_score(m):
        child = game.copy()
        child._apply_move(m, record_history=False)
        return evaluate(child, perspective)

    moves.sort(key=get_move_score, reverse=maximizing)

    best_value = -math.inf if maximizing else math.inf
    
    for move in moves:
        child = game.copy()
        child._apply_move(move, record_history=False)
        value, child_nodes = minimax(
            child,
            depth - 1,
            not maximizing,
            perspective,
            alpha,
            beta,
            use_alpha_beta,
            transposition_table,
            start_time,
            time_limit,
        )
        nodes += child_nodes
        if maximizing:
            best_value = max(best_value, value)
            if use_alpha_beta:
                alpha = max(alpha, best_value)
        else:
            best_value = min(best_value, value)
            if use_alpha_beta:
                beta = min(beta, best_value)
        if use_alpha_beta and beta <= alpha:
            break

    best_int = int(best_value)
    transposition_table[key] = (best_int, depth)
    return best_int, nodes


def minimax_root(game: Game, max_depth: int, use_alpha_beta: bool = True, time_limit: float = 0.5) -> Tuple[Optional[tuple], int]:
    best_move = None
    total_nodes = 0
    start_time = time.perf_counter()
    transposition_table: Dict[tuple, Tuple[int, int]] = {}

    # Iterative Deepening
    for current_depth in range(1, max_depth + 1):
        iteration_best_move = None
        iteration_best_score = -math.inf
        
        moves = game.legal_moves()
        if not moves:
            break
            
        # Move Ordering for Root
        def get_root_move_score(m):
            child = game.copy()
            child._apply_move(m, record_history=False)
            return evaluate(child, game.current_player)

        moves.sort(key=get_root_move_score, reverse=True)
        
        for move in moves:
            child = game.copy()
            child._apply_move(move, record_history=False)
            score, nodes = minimax(
                child,
                current_depth - 1,
                False,
                game.current_player,
                -INF,
                INF,
                use_alpha_beta,
                transposition_table,
                start_time,
                time_limit,
            )
            total_nodes += nodes
            
            if score > iteration_best_score:
                iteration_best_score = score
                iteration_best_move = move
                
            # Exit if out of time
            if time.perf_counter() - start_time > time_limit:
                break
        
        if iteration_best_move:
            best_move = iteration_best_move
            
        # Exit if out of time
        if time.perf_counter() - start_time > time_limit:
            break
            
    return best_move, total_nodes

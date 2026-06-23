from __future__ import annotations
from typing import Tuple, Optional
import math
from game import Game


def evaluate(game: Game, perspective: int) -> int:
    # Simple heuristic: win/loss, plus counts nearer to lines
    winner = game.check_win()
    if winner == perspective:
        return 1000
    if winner == -perspective:
        return -1000
    score = 0
    # count two-in-line with open third
    for a,b,c in Game.LINES:
        line = [game.board[a], game.board[b], game.board[c]]
        s = sum(line)
        if s == 2*perspective:
            score += 50
        if s == -2*perspective:
            score -= 50
    # proximity: center control
    score += 3 * game.board[4] * perspective
    return score


def minimax(game: Game, depth: int, maximizing: bool, perspective: int, alpha: int, beta: int, use_alpha_beta: bool) -> Tuple[int, Optional[Tuple], int]:
    nodes = 1
    winner = game.check_win()
    if depth == 0 or winner != 0:
        return evaluate(game, perspective), None, nodes

    best_move = None
    if maximizing:
        max_eval = -math.inf
        for mv in game.legal_moves():
            g2 = game.copy()
            if mv[0] == 'place':
                g2.place(mv[1])
            else:
                g2.move(mv[1], mv[2])
            val, _, sub_nodes = minimax(g2, depth-1, False, perspective, alpha, beta, use_alpha_beta)
            nodes += sub_nodes
            if val > max_eval:
                max_eval = val
                best_move = mv
            if use_alpha_beta:
                alpha = max(alpha, val)
                if beta <= alpha:
                    break
        return int(max_eval), best_move, nodes
    else:
        min_eval = math.inf
        for mv in game.legal_moves():
            g2 = game.copy()
            if mv[0] == 'place':
                g2.place(mv[1])
            else:
                g2.move(mv[1], mv[2])
            val, _, sub_nodes = minimax(g2, depth-1, True, perspective, alpha, beta, use_alpha_beta)
            nodes += sub_nodes
            if val < min_eval:
                min_eval = val
                best_move = mv
            if use_alpha_beta:
                beta = min(beta, val)
                if beta <= alpha:
                    break
        return int(min_eval), best_move, nodes


def minimax_root(game: Game, depth: int, use_alpha_beta: bool = True) -> Tuple[Optional[Tuple], int]:
    perspective = game.current_player
    best_move = None
    best_val = -math.inf
    total_nodes = 0
    for mv in game.legal_moves():
        g2 = game.copy()
        if mv[0] == 'place':
            g2.place(mv[1])
        else:
            g2.move(mv[1], mv[2])
        val, _, nodes = minimax(g2, depth-1, False, perspective, -math.inf, math.inf, use_alpha_beta)
        total_nodes += nodes
        if val > best_val:
            best_val = val
            best_move = mv
    return best_move, total_nodes

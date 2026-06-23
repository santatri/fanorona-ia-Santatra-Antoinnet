from __future__ import annotations
from typing import Tuple, Dict, Any, Optional
import random
from game import Game
from minimax import minimax_root


class AIPlayer:
    def __init__(self, level: str = 'Facile') -> None:
        self.level = level

    def select_move(self, game: Game) -> Tuple[Optional[tuple], Dict[str, Any]]:
        stats: Dict[str, Any] = {'nodes': 0}
        moves = game.legal_moves()
        if not moves:
            return None, stats
            
        if self.level == 'Facile':
            # Add a small delay for natural feel
            move = random.choice(moves)
            return move, stats
            
        if self.level == 'Moyen':
            # Search moderately deep with a short time limit
            move, nodes = minimax_root(game, max_depth=4, use_alpha_beta=True, time_limit=0.2)
            stats['nodes'] = nodes
            return move, stats
            
        # Difficile: Deeper search with more time
        move, nodes = minimax_root(game, max_depth=15, use_alpha_beta=True, time_limit=0.8)
        stats['nodes'] = nodes
        return move, stats

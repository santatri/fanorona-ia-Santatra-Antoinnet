from __future__ import annotations
from typing import Tuple, Dict, Any, Optional
import random
from minimax import minimax_root
from game import Game


class AIPlayer:
    def __init__(self, level: str = "Easy") -> None:
        self.level = level

    def select_move(self, game: Game) -> Tuple[Optional[Tuple], Dict[str, Any]]:
        stats: Dict[str, Any] = {'nodes': 0}
        if self.level == "Easy":
            moves = game.legal_moves()
            if not moves:
                return None, stats
            mv = random.choice(moves)
            return mv, stats
        elif self.level == "Medium":
            depth = 3
            mv, nodes = minimax_root(game, depth, use_alpha_beta=False)
            stats['nodes'] = nodes
            return mv, stats
        else:  # Hard
            depth = 6
            mv, nodes = minimax_root(game, depth, use_alpha_beta=True)
            stats['nodes'] = nodes
            return mv, stats

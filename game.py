from __future__ import annotations
from typing import List, Tuple, Optional, Dict, Any
import copy

EMPTY = 0
P1 = 1
P2 = 2

WIN_LINES = [
    (0, 1, 2), (3, 4, 5), (6, 7, 8),
    (0, 3, 6), (1, 4, 7), (2, 5, 8),
    (0, 4, 8), (2, 4, 6),
]

ADJ = {
    0: [1, 3, 4],
    1: [0, 2, 4],
    2: [1, 5, 4],
    3: [0, 6, 4],
    4: [0, 1, 2, 3, 5, 6, 7, 8],
    5: [2, 8, 4],
    6: [3, 7, 4],
    7: [6, 8, 4],
    8: [5, 7, 4],
}

LABELS = [
    'a1', 'b1', 'c1',
    'a2', 'b2', 'c2',
    'a3', 'b3', 'c3',
]

Move = Tuple[str, int, Optional[int]]


def describe_move(move: Move) -> str:
    if move[0] == 'place':
        return f'Pose {LABELS[move[1]]}'
    return f'{LABELS[move[1]]} → {LABELS[move[2]]}'


class Game:
    """Moteur de jeu Fanoron-telo 3x3.

    Le plateau est une liste de 9 cases. 0=vide, 1=J1, 2=J2.
    """

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.board: List[int] = [EMPTY] * 9
        self.current_player: int = P1
        self.phase: int = 1
        self.placed: List[int] = [0, 0]
        self.selected: int = -1
        self.winner: int = EMPTY
        self.last_move: str = 'Aucun coup'
        self.history_stack: List[Dict[str, Any]] = []
        self.future_stack: List[Dict[str, Any]] = []
        self._push_history('Début de la partie')

    def copy(self) -> 'Game':
        return copy.deepcopy(self)

    def _snapshot(self, description: str) -> Dict[str, Any]:
        return {
            'board': self.board.copy(),
            'current_player': self.current_player,
            'phase': self.phase,
            'placed': self.placed.copy(),
            'selected': self.selected,
            'winner': self.winner,
            'last_move': self.last_move,
            'description': description,
        }

    def _push_history(self, description: str) -> None:
        self.history_stack.append(self._snapshot(description))
        self.future_stack.clear()

    def history_descriptions(self) -> List[str]:
        return [item['description'] for item in self.history_stack]

    def is_phase1(self) -> bool:
        return self.phase == 1

    def check_win(self) -> int:
        for a, b, c in WIN_LINES:
            if self.board[a] != EMPTY and self.board[a] == self.board[b] == self.board[c]:
                return self.board[a]
        return EMPTY

    def has_legal_moves(self, player: int) -> bool:
        for idx in range(9):
            if self.board[idx] == player:
                for neighbor in ADJ[idx]:
                    if self.board[neighbor] == EMPTY:
                        return True
        return False

    def get_winner(self) -> int:
        winner = self.check_win()
        if winner != EMPTY:
            return winner
        if self.phase == 2 and not self.has_legal_moves(self.current_player):
            return P1 if self.current_player == P2 else P2
        return EMPTY

    def is_terminal(self) -> bool:
        return self.get_winner() != EMPTY

    def legal_moves(self) -> List[Move]:
        moves: List[Move] = []
        if self.phase == 1:
            for idx in range(9):
                if self.board[idx] == EMPTY:
                    moves.append(('place', idx, None))
            return moves
        for idx in range(9):
            if self.board[idx] == self.current_player:
                for neighbor in ADJ[idx]:
                    if self.board[neighbor] == EMPTY:
                        moves.append(('move', idx, neighbor))
        return moves

    def switch_player(self) -> None:
        self.current_player = P2 if self.current_player == P1 else P1

    def _apply_move(self, move: Move, record_history: bool = True) -> bool:
        if move[0] == 'place':
            pos = move[1]
            if self.phase != 1 or self.board[pos] != EMPTY:
                return False
            self.board[pos] = self.current_player
            self.placed[self.current_player - 1] += 1
            if self.placed == [3, 3]:
                self.phase = 2
        elif move[0] == 'move':
            src, dst = move[1], move[2]
            if self.phase != 2 or self.board[src] != self.current_player:
                return False
            if self.board[dst] != EMPTY or dst not in ADJ[src]:
                return False
            self.board[src] = EMPTY
            self.board[dst] = self.current_player
        else:
            return False

        self.last_move = describe_move(move)
        if record_history:
            self._push_history(self.last_move)
        self.winner = self.check_win()
        if self.winner == EMPTY:
            self.switch_player()
        return True

    def place(self, idx: int) -> bool:
        return self._apply_move(('place', idx, None), record_history=True)

    def move(self, src: int, dst: int) -> bool:
        return self._apply_move(('move', src, dst), record_history=True)

    def undo(self) -> bool:
        if len(self.history_stack) <= 1:
            return False
        self.future_stack.append(self.history_stack.pop())
        self._restore(self.history_stack[-1])
        return True

    def redo(self) -> bool:
        if not self.future_stack:
            return False
        snapshot = self.future_stack.pop()
        self.history_stack.append(snapshot)
        self._restore(snapshot)
        return True

    def _restore(self, snapshot: Dict[str, Any]) -> None:
        self.board = snapshot['board'].copy()
        self.current_player = snapshot['current_player']
        self.phase = snapshot['phase']
        self.placed = snapshot['placed'].copy()
        self.selected = snapshot['selected']
        self.winner = snapshot['winner']
        self.last_move = snapshot['last_move']

    def __repr__(self) -> str:
        rows = []
        for r in range(3):
            rows.append(' '.join(['.' if v == EMPTY else ('X' if v == P1 else 'O') for v in self.board[r*3:r*3+3]]))
        return '\n'.join(rows)

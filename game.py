from __future__ import annotations
from typing import List, Optional, Tuple, Dict, Any
import copy


class Game:
    """Game engine for Fanoron-telo (3x3).

    Board representation: list of 9 ints: 0 empty, 1 player X, -1 player O.
    Players: 1 (X) and -1 (O).
    """

    LINES = [
        (0,1,2),(3,4,5),(6,7,8),
        (0,3,6),(1,4,7),(2,5,8),
        (0,4,8),(2,4,6)
    ]

    def __init__(self) -> None:
        self.reset()

    def reset(self) -> None:
        self.board: List[int] = [0]*9
        self.current_player: int = 1
        self._history: List[Dict[str, Any]] = []
        self._future: List[Dict[str, Any]] = []
        self._push_history("start")

    def copy(self) -> "Game":
        return copy.deepcopy(self)

    def _push_history(self, desc: str) -> None:
        self._history.append({
            'board': self.board.copy(),
            'player': self.current_player,
            'desc': desc
        })
        self._future.clear()

    def get_history(self) -> List[str]:
        return [h['desc'] for h in self._history]

    def is_phase1(self) -> bool:
        return sum(1 for v in self.board if v != 0) < 6

    def place(self, pos: int) -> bool:
        """Place a pawn for current player at pos during phase1."""
        if not (0 <= pos < 9):
            return False
        if self.board[pos] != 0:
            return False
        if not self.is_phase1():
            return False
        self.board[pos] = self.current_player
        self._push_history(f"place {self.current_player} @ {pos}")
        if not self.check_win():
            self.current_player *= -1
        return True

    def move(self, src: int, dst: int) -> bool:
        """Move a pawn from src to dst during phase2. Returns True if moved."""
        if not (0 <= src < 9 and 0 <= dst < 9):
            return False
        if self.board[src] != self.current_player:
            return False
        if self.board[dst] != 0:
            return False
        if self.is_phase1():
            return False
        if not self._is_adjacent(src, dst):
            return False
        self.board[src] = 0
        self.board[dst] = self.current_player
        self._push_history(f"move {self.current_player} {src}->{dst}")
        if not self.check_win():
            self.current_player *= -1
        return True

    def _is_adjacent(self, a: int, b: int) -> bool:
        ar, ac = divmod(a, 3)
        br, bc = divmod(b, 3)
        return abs(ar-br) + abs(ac-bc) == 1

    def legal_moves(self) -> List[Tuple[str, int, Optional[int]]]:
        """Return list of legal moves.

        Moves are tuples: ('place', pos, None) or ('move', src, dst)
        """
        moves: List[Tuple[str,int,Optional[int]]] = []
        if self.is_phase1():
            for i in range(9):
                if self.board[i] == 0:
                    moves.append(('place', i, None))
        else:
            for src in range(9):
                if self.board[src] == self.current_player:
                    for dr, dc in ((1,0),(-1,0),(0,1),(0,-1)):
                        r,c = divmod(src,3)
                        nr, nc = r+dr, c+dc
                        if 0 <= nr < 3 and 0 <= nc < 3:
                            dst = nr*3 + nc
                            if self.board[dst]==0:
                                moves.append(('move', src, dst))
        return moves

    def check_win(self) -> int:
        """Return winning player (1 or -1) or 0 if none."""
        for a,b,c in self.LINES:
            s = self.board[a] + self.board[b] + self.board[c]
            if s == 3:
                return 1
            if s == -3:
                return -1
        return 0

    def is_draw(self) -> bool:
        # Draw only possible if repeating or stalemate; for this simple game
        # consider draw if no legal moves for current player
        if self.check_win() != 0:
            return False
        return len(self.legal_moves()) == 0

    def undo(self) -> bool:
        if len(self._history) <= 1:
            return False
        last = self._history.pop()
        self._future.append(last)
        prev = self._history[-1]
        self.board = prev['board'].copy()
        self.current_player = prev['player']
        return True

    def redo(self) -> bool:
        if not self._future:
            return False
        nxt = self._future.pop()
        self._history.append(nxt)
        self.board = nxt['board'].copy()
        self.current_player = nxt['player']
        return True

    def get_history(self) -> List[str]:
        return [h['desc'] for h in self._history]

    def __repr__(self) -> str:
        rows = []
        for r in range(3):
            rows.append(' '.join(['.' if v==0 else ('X' if v==1 else 'O') for v in self.board[r*3:r*3+3]]))
        return '\n'.join(rows)

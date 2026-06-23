from typing import List


def pretty_board(board: List[int]) -> str:
    rows = []
    for r in range(3):
        rows.append(' '.join(['.' if v==0 else ('X' if v==1 else 'O') for v in board[r*3:r*3+3]]))
    return '\n'.join(rows)

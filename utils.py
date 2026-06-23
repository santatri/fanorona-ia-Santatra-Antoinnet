from typing import List
from game import LABELS


def move_label(move: tuple) -> str:
    if move is None:
        return 'Aucun coup'
    if move[0] == 'place':
        return f'Pose {LABELS[move[1]]}'
    return f'Déplace {LABELS[move[1]]} → {LABELS[move[2]]}'


def ascii_board(board: List[int]) -> str:
    sym = {0: '.', 1: 'X', 2: 'O'}
    return (
        '0---1---2\n'
        '|\\ /|\\ /|\n'
        f'| {sym[board[0]]} | {sym[board[1]]} | {sym[board[2]]} |\n'
        '|/ \\|/ \\|\n'
        '3---4---5\n'
        '|\\ /|\\ /|\n'
        f'| {sym[board[3]]} | {sym[board[4]]} | {sym[board[5]]} |\n'
        '|/ \\|/ \\|\n'
        '6---7---8'
    )


def legal_moves_labels(moves: List[tuple]) -> List[str]:
    labels: List[str] = []
    for move in moves:
        if move[0] == 'place':
            labels.append(f'Pose {LABELS[move[1]]}')
        else:
            labels.append(f'{LABELS[move[1]]} → {LABELS[move[2]]}')
    return labels

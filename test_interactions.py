from game import Game, P1, P2, EMPTY
from ai import AIPlayer
from utils import move_label

def test_interaction():
    game = Game()
    print(f"Initial Phase: {game.phase}, Player: {game.current_player}")
    
    # Simulate P1 (Human) move at idx 0
    idx = 0
    if game.phase == 1:
        if game.board[idx] == EMPTY:
            if game.place(idx):
                print(f"P1 placed at {idx}")
                
    print(f"Phase: {game.phase}, Player: {game.current_player}, Board: {game.board}")
    
    # Simulate AI turn if it's P2
    if game.current_player == P2:
        ai = AIPlayer(level='Moyen')
        move, stats = ai.select_move(game.copy())
        if move:
            game._apply_move(move)
            print(f"AI moved: {move_label(move)}")
            
    print(f"Phase: {game.phase}, Player: {game.current_player}, Board: {game.board}")

if __name__ == "__main__":
    test_interaction()

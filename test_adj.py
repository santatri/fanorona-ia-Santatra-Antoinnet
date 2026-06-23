from game import Game, ADJ

def test_adjacency():
    game = Game()
    
    # Test mid-edge 1 (b1)
    adj_1 = ADJ[1]
    expected_1 = [0, 2, 4] # a1, c1, b2
    print(f"Mid-edge 1 neighbors: {adj_1}, Expected: {expected_1}")
    assert set(adj_1) == set(expected_1)
    
    # Test center 4 (b2)
    adj_4 = ADJ[4]
    expected_4 = [0, 1, 2, 3, 5, 6, 7, 8]
    print(f"Center 4 neighbors: {len(adj_4)}, Expected: 8")
    assert len(adj_4) == 8
    
    print("Adjacency tests passed!")

if __name__ == "__main__":
    test_adjacency()

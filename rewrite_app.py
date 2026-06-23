from pathlib import Path

content = '''from __future__ import annotations
import streamlit as st
import time
from typing import Optional
from game import Game, P1, P2, EMPTY
from ai import AIPlayer
from utils import ascii_board, legal_moves_labels, move_label


def init_state() -> None:
    if 'game' not in st.session_state:
        st.session_state.game = Game()
    st.session_state.mode = st.session_state.get('mode', 'Humain vs IA')
    st.session_state.difficulty = st.session_state.get('difficulty', 'Moyen')
    st.session_state.selected = st.session_state.get('selected', -1)
    st.session_state.ai_time_ms = st.session_state.get('ai_time_ms', 0.0)
    st.session_state.nodes_explored = st.session_state.get('nodes_explored', 0)
    st.session_state.total_nodes = st.session_state.get('total_nodes', 0)
    st.session_state.last_move = st.session_state.get('last_move', 'Aucun coup')
    st.session_state.scores = st.session_state.get('scores', [0, 0])


def reset_game(keep_scores: bool = True) -> None:
    if not keep_scores:
        st.session_state.scores = [0, 0]
    st.session_state.game = Game()
    st.session_state.selected = -1
    st.session_state.ai_time_ms = 0.0
    st.session_state.nodes_explored = 0
    st.session_state.total_nodes = 0
    st.session_state.last_move = 'Aucun coup'


def player_name(player: int) -> str:
    mode = st.session_state.mode
    if mode == 'Humain vs IA':
        return 'Humain' if player == P1 else 'IA'
    if mode == 'IA vs IA':
        return 'IA X' if player == P1 else 'IA O'
    return 'Joueur 1' if player == P1 else 'Joueur 2'


def status_text() -> str:
    game = st.session_state.game
    if game.winner != EMPTY:
        return f'🎉 Victoire : {player_name(game.winner)}'
    phase_label = 'Placement' if game.phase == 1 else 'Mouvement'
    return f'Phase {game.phase} — {phase_label} : tour de {player_name(game.current_player)}'


def handle_click(idx: int) -> None:
    game = st.session_state.game
    if game.winner != EMPTY or game.is_terminal():
        return
    if st.session_state.mode == 'IA vs IA':
        return
    if st.session_state.mode == 'Humain vs IA' and game.current_player == P2:
        return

    if game.phase == 1:
        if game.board[idx] != EMPTY:
            return
        if game.place(idx):
            st.session_state.last_move = move_label(('place', idx, None))
            post_move()
            if game.current_player == P2 and st.session_state.mode == 'Humain vs IA' and game.winner == EMPTY:
                ai_turn()
    else:
        if st.session_state.selected == -1:
            if game.board[idx] == game.current_player:
                st.session_state.selected = idx
            return
        if idx == st.session_state.selected:
            st.session_state.selected = -1
            return
        legal_targets = [move[2] for move in game.legal_moves() if move[0] == 'move' and move[1] == st.session_state.selected]
        if idx in legal_targets:
            if game.move(st.session_state.selected, idx):
                st.session_state.last_move = move_label(('move', st.session_state.selected, idx))
                st.session_state.selected = -1
                post_move()
                if game.current_player == P2 and st.session_state.mode == 'Humain vs IA' and game.winner == EMPTY:
                    ai_turn()
            return
        st.session_state.selected = -1


def post_move() -> None:
    game = st.session_state.game
    winner = game.get_winner()
    if winner != EMPTY:
        game.winner = winner
        if winner == P1:
            st.session_state.scores[0] += 1
        else:
            st.session_state.scores[1] += 1
        return
    st.session_state.selected = -1


def ai_turn() -> None:
    game = st.session_state.game
    if game.winner != EMPTY or game.is_terminal():
        return
    ai = AIPlayer(level=st.session_state.difficulty)
    start = time.perf_counter()
    move, stats = ai.select_move(game.copy())
    end = time.perf_counter()
    st.session_state.ai_time_ms = (end - start) * 1000
    st.session_state.nodes_explored = stats['nodes']
    st.session_state.total_nodes += stats['nodes']
    if move is None:
        return
    if game._apply_move(move, record_history=True):
        st.session_state.last_move = move_label(move)
        post_move()


def render_board() -> None:
    game = st.session_state.game
    for row in range(3):
        cols = st.columns(3)
        for col in range(3):
            idx = row * 3 + col
            token = '·'
            if game.board[idx] == P1:
                token = 'X'
            elif game.board[idx] == P2:
                token = 'O'
            if st.session_state.selected == idx:
                token = '⭕'
            elif game.phase == 2 and st.session_state.selected >= 0:
                legal_targets = [move[2] for move in game.legal_moves() if move[0] == 'move' and move[1] == st.session_state.selected]
                if idx in legal_targets:
                    token = '🟢'
            with cols[col]:
                if st.button(token, key=f'cell-{idx}', disabled=(game.winner != EMPTY)):
                    handle_click(idx)


def main() -> None:
    st.set_page_config(page_title='Fanoron-telo IA', page_icon='♟', layout='wide')
    init_state()

    st.markdown(
        '<style>'
        'body, .stApp { background: #0d1117; color: #e8e8f0; }'
        '.stButton > button { background: #16202a; color: #f1f5f9; border: 1px solid #2c4f73; border-radius: 12px; padding: 0.65rem 0.9rem; }'
        '.stButton > button:hover { background: #1f3a57; }'
        '.status-panel, .score-panel, .history-panel, .legal-panel { background: #111827; border: 1px solid #24344e; border-radius: 16px; padding: 18px; }'
        '.small-text { color: #9fb6d6; font-size: 0.92rem; }'
        '</style>',
        unsafe_allow_html=True,
    )

    st.title('♟ Fanoron-telo IA')
    st.markdown('Jeu 3×3 avec phase de placement et phase de mouvement. Modes Humain vs Humain, Humain vs IA et IA vs IA.')

    with st.sidebar:
        st.header('Configuration')
        st.session_state.mode = st.selectbox('Mode de jeu', ['Humain vs Humain', 'Humain vs IA', 'IA vs IA'], index=['Humain vs Humain', 'Humain vs IA', 'IA vs IA'].index(st.session_state.mode))
        if st.session_state.mode != 'Humain vs Humain':
            st.session_state.difficulty = st.selectbox('Difficulté IA', ['Facile', 'Moyen', 'Difficile'], index=['Facile', 'Moyen', 'Difficile'].index(st.session_state.difficulty))
        if st.button('Nouvelle partie'):
            reset_game(keep_scores=True)
        if st.button('↩ Undo'):
            st.session_state.game.undo()
            st.session_state.selected = -1
        if st.button('↪ Redo'):
            st.session_state.game.redo()
            st.session_state.selected = -1
        st.markdown('---')
        st.markdown('### Statistiques IA')
        st.markdown(f'- Temps du dernier coup : **{st.session_state.ai_time_ms:.1f} ms**')
        st.markdown(f'- Nœuds explorés : **{st.session_state.nodes_explored}**')
        st.markdown(f'- Nœuds totaux : **{st.session_state.total_nodes}**')
        st.markdown('---')
        st.markdown('### Informations de jeu')
        st.markdown(f'- Mode : **{st.session_state.mode}**')
        st.markdown(f'- Dernier coup : **{st.session_state.last_move}**')

    current = st.session_state.game.current_player
    col1, col2, col3 = st.columns([2, 1, 2])
    with col1:
        st.markdown(f'<div class="score-panel"><strong>{player_name(P1)}</strong><br>Score : {st.session_state.scores[0]}</div>', unsafe_allow_html=True)
    with col2:
        st.markdown(f'<div class="score-panel"><strong>{status_text()}</strong><br><span class="small-text">Phase {st.session_state.game.phase}</span></div>', unsafe_allow_html=True)
    with col3:
        st.markdown(f'<div class="score-panel"><strong>{player_name(P2)}</strong><br>Score : {st.session_state.scores[1]}</div>', unsafe_allow_html=True)

    board_col, panel_col = st.columns([2, 1])
    with board_col:
        st.subheader('Plateau')
        render_board()
        if st.session_state.mode == 'IA vs IA' and st.session_state.game.winner == EMPTY:
            if st.button('▶ Coup IA suivant'):
                ai_turn()
            if st.button('⏩ Auto'):
                for _ in range(25):
                    if st.session_state.game.winner != EMPTY or st.session_state.game.is_terminal():
                        break
                    ai_turn()

    with panel_col:
        st.subheader('Historique')
        st.markdown('<div class="history-panel">', unsafe_allow_html=True)
        history = st.session_state.game.history_descriptions()
        for item in history[-10:]:
            st.markdown(f'- {item}')
        st.markdown('</div>', unsafe_allow_html=True)
        st.subheader('Coups légaux')
        legal = st.session_state.game.legal_moves()
        labels = legal_moves_labels(legal)
        st.markdown('<div class="legal-panel">', unsafe_allow_html=True)
        if labels:
            for label in labels:
                st.markdown(f'- {label}')
        else:
            st.markdown('- Aucun coup légal')
        st.markdown('</div>', unsafe_allow_html=True)

    st.markdown('---')
    with st.expander('🗺 Représentation ASCII du plateau'):
        st.code(ascii_board(st.session_state.game.board))
        st.write(f'Joueur actif : {player_name(current)}')
        st.write(f'Pions placés : X={st.session_state.game.placed[0]} / O={st.session_state.game.placed[1]}')

    st.markdown('''<div style="color:#9fb6d6;font-size:0.85rem;text-align:center;">Développé pour un hackathon universitaire d'Algorithmique Avancée.</div>''', unsafe_allow_html=True)


if __name__ == '__main__':
    main()
'@
[System.IO.File]::WriteAllText('D:\fanoron-streamlit\app.py',$code,[System.Text.Encoding]::UTF8)

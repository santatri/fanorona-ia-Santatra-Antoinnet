from __future__ import annotations
import streamlit as st
import time
import textwrap
from typing import Optional
from game import Game, P1, P2, EMPTY
from ai import AIPlayer
from utils import ascii_board, legal_moves_labels, move_label


@st.cache_data(show_spinner=False)
def _css_block() -> str:
    """CSS mis en cache — injecté une seule fois par session, pas à chaque rerun."""
    return """
        <style>
            /* ── Variables globales ─────────────────────────────── */
            :root {
                --p1-color: #00f2ff;
                --p1-bg: rgba(0, 242, 255, 0.08);
                --p1-glow: rgba(0, 242, 255, 0.2);
                --p2-color: #bd00ff;
                --p2-bg: rgba(189, 0, 255, 0.08);
                --p2-glow: rgba(189, 0, 255, 0.2);
                --target-color: #ffd700;
                --bg-card: rgba(22, 32, 42, 0.6);
                --border-subtle: rgba(255, 255, 255, 0.08);

                /* Tailles par défaut (desktop) */
                --btn-size: 80px;
                --btn-font: 28px;
                --btn-radius: 16px;
                --btn-gap: 10px;
            }

            /* ── Viewport / scroll fix ──────────────────────────── */
            .main .block-container {
                padding-top: 0.3rem !important;
                padding-bottom: 0.3rem !important;
                padding-left: clamp(0.2rem, 1.5vw, 3rem) !important;
                padding-right: clamp(0.2rem, 1.5vw, 3rem) !important;
                max-width: 100% !important;
            }

            /* ── Score banner ───────────────────────────────────── */
            .score-container {
                display: flex;
                gap: clamp(3px, 1vw, 12px);
                margin-bottom: clamp(3px, 0.8vw, 12px);
                width: 100%;
            }
            .score-card {
                flex: 1;
                background: var(--bg-card);
                border: 1px solid var(--border-subtle);
                border-radius: clamp(4px, 1.2vw, 14px);
                padding: clamp(3px, 0.8vw, 10px);
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                min-width: 0;
            }
            .border-p1 { border-bottom: 2px solid var(--p1-color); }
            .border-p2 { border-bottom: 2px solid var(--p2-color); }
            .border-phase { border-bottom: 2px solid #6c7a89; }
            
            .score-icon { 
                font-size: clamp(0.5rem, 1.8vw, 1.2rem); 
                font-weight: bold; 
            }
            .score-val { 
                font-size: clamp(0.6rem, 2.2vw, 1.6rem); 
                font-weight: 800; 
                line-height: 1.1; 
            }
            .score-user { 
                font-size: clamp(0.35rem, 1vw, 0.75rem); 
                color: #8a99ad; 
                margin-top: 1px; 
                white-space: nowrap; 
                overflow: hidden; 
                text-overflow: ellipsis; 
                max-width: 100%; 
            }
            .color-p1 { color: var(--p1-color); text-shadow: 0 0 8px var(--p1-glow); }
            .color-p2 { color: var(--p2-color); text-shadow: 0 0 8px var(--p2-glow); }

            /* ── Statut de jeu ──────────────────────────────────── */
            .status-banner {
                text-align: center;
                padding: clamp(3px, 0.8vw, 10px);
                background: var(--bg-card);
                border-radius: clamp(3px, 0.8vw, 10px);
                border: 1px solid var(--border-subtle);
                font-size: clamp(0.45rem, 1.4vw, 0.9rem);
                font-weight: 600;
                margin-bottom: clamp(4px, 1vw, 20px);
                color: #e8e8f0;
                letter-spacing: 0.3px;
                line-height: 1.3;
            }

            /* ── Grille Streamlit (plateau 3×3) ─────────────────── */
            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(3)) {
                display: flex !important;
                flex-direction: row !important;
                flex-wrap: nowrap !important;
                gap: var(--btn-gap) !important;
                margin-bottom: var(--btn-gap) !important;
                justify-content: center !important;
                width: 100% !important;
            }

            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(3)) > div,
            [data-testid="stHorizontalBlock"]:has(> [data-testid="stColumn"]:nth-child(3)) > [data-testid="stColumn"] {
                display: flex !important;
                flex-direction: column !important;
                flex: 0 0 var(--btn-size) !important;
                min-width: var(--btn-size) !important;
                max-width: var(--btn-size) !important;
                width: var(--btn-size) !important;
                padding: 0 !important;
            }

            /* ── Boutons de jeu ─────────────────────────────────── */
            .stButton > button {
                width: 100% !important;
                height: var(--btn-size) !important;
                aspect-ratio: 1 / 1 !important;
                padding: 0 !important;
                font-size: var(--btn-font) !important;
                border-radius: var(--btn-radius) !important;
                min-height: unset !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                background: var(--bg-card) !important;
                border: 1px solid var(--border-subtle) !important;
                color: #e8e8f0 !important;
                transition: all 0.2s cubic-bezier(0.4, 0, 0.2, 1) !important;
                line-height: 1 !important;
            }

            .cell-p1 button { 
                color: var(--p1-color) !important; 
                background: var(--p1-bg) !important; 
                border-color: rgba(0, 242, 255, 0.3) !important; 
                text-shadow: 0 0 15px var(--p1-glow);
                box-shadow: inset 0 0 10px var(--p1-glow) !important;
            }
            .cell-p2 button { 
                color: var(--p2-color) !important; 
                background: var(--p2-bg) !important; 
                border-color: rgba(189, 0, 255, 0.3) !important; 
                text-shadow: 0 0 15px var(--p2-glow);
                box-shadow: inset 0 0 10px var(--p2-glow) !important;
            }
            .cell-selected button { 
                border: 2px solid var(--p1-color) !important; 
                box-shadow: 0 0 20px var(--p1-glow) !important; 
                transform: scale(0.95);
            }
            .cell-target button { 
                color: var(--target-color) !important; 
                border: 2px dashed rgba(255, 215, 0, 0.4) !important; 
                font-size: clamp(6px, 2vw, 18px) !important;
                background: rgba(255, 215, 0, 0.05) !important;
            }

            .stButton > button:hover:not(:disabled) {
                border-color: rgba(255,255,255,0.4) !important;
                transform: translateY(-2px) scale(1.03);
                box-shadow: 0 6px 16px rgba(0,0,0,0.4);
                z-index: 10;
            }
            .stButton > button:active:not(:disabled) {
                transform: scale(0.92) !important;
            }

            /* ── Titre principal ────────────────────────────────── */
            h1, h2, h3, h4, h5, h6 {
                margin-bottom: 0.05rem !important;
            }
            .main-title {
                font-size: clamp(0.9rem, 3.5vw, 2rem) !important;
                font-weight: 700 !important;
                text-align: center !important;
                margin-bottom: 0.05rem !important;
            }
            .subtitle {
                font-size: clamp(0.4rem, 1.5vw, 0.9rem) !important;
                text-align: center !important;
                color: #8a99ad !important;
                margin-bottom: 0.5rem !important;
            }

            /* ── Sidebar ──────────────────────────────────────────── */
            [data-testid="stSidebar"] {
                min-width: clamp(120px, 18vw, 280px) !important;
                max-width: clamp(120px, 18vw, 280px) !important;
            }
            [data-testid="stSidebar"] .stMarkdown h3 {
                font-size: clamp(0.7rem, 1.6vw, 1.2rem) !important;
                margin-top: 0 !important;
            }
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"],
            [data-testid="stSidebar"] .row-widget.stHorizontalBlock {
                flex-wrap: wrap !important;
                justify-content: flex-start !important;
                width: 100% !important;
            }
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > div,
            [data-testid="stSidebar"] [data-testid="stHorizontalBlock"] > [data-testid="stColumn"],
            [data-testid="stSidebar"] .row-widget.stHorizontalBlock > div {
                flex: 1 1 0 !important;
                min-width: 0 !important;
                max-width: 100% !important;
                width: auto !important;
            }
            [data-testid="stSidebar"] .stButton > button {
                width: 100% !important;
                height: auto !important;
                aspect-ratio: unset !important;
                font-size: clamp(0.45rem, 1.2vw, 0.8rem) !important;
                padding: 3px 2px !important;
                min-height: unset !important;
                border-radius: 6px !important;
            }
            [data-testid="stSidebar"] .stSelectbox label {
                font-size: clamp(0.45rem, 1.1vw, 0.8rem) !important;
            }
            [data-testid="stSidebar"] .stSelectbox div {
                font-size: clamp(0.45rem, 1.1vw, 0.8rem) !important;
            }
            [data-testid="stSidebar"] hr {
                margin: 6px 0 !important;
            }
            [data-testid="stSidebar"] .stMetric label {
                font-size: clamp(0.4rem, 1vw, 0.7rem) !important;
            }
            [data-testid="stSidebar"] .stMetric div {
                font-size: clamp(0.5rem, 1.2vw, 0.9rem) !important;
            }

            /* ── Tabs ─────────────────────────────────────────────── */
            .stTabs [data-baseweb="tab-list"] {
                gap: clamp(2px, 0.8vw, 8px) !important;
            }
            .stTabs [data-baseweb="tab"] {
                font-size: clamp(0.4rem, 1.3vw, 0.85rem) !important;
                padding: clamp(2px, 0.6vw, 8px) clamp(4px, 1.2vw, 16px) !important;
            }

            /* ── Logs et historique ──────────────────────────────── */
            .log-entry {
                font-size: clamp(0.4rem, 1.2vw, 0.85rem) !important;
                padding: clamp(2px, 0.5vw, 6px) 0 !important;
                line-height: 1.3 !important;
            }
            .legal-move-tag {
                font-size: clamp(0.35rem, 1vw, 0.85rem) !important;
                padding: clamp(1px, 0.4vw, 4px) clamp(3px, 0.8vw, 8px) !important;
                border-radius: 3px !important;
                margin-right: clamp(2px, 0.5vw, 4px) !important;
                margin-bottom: clamp(2px, 0.5vw, 4px) !important;
            }

            /* ── Expander ─────────────────────────────────────────── */
            .streamlit-expanderHeader {
                font-size: clamp(0.5rem, 1.2vw, 0.85rem) !important;
                padding: clamp(2px, 0.5vw, 8px) !important;
            }
            .streamlit-expanderContent {
                font-size: clamp(0.4rem, 1vw, 0.75rem) !important;
            }
            .streamlit-expanderContent pre {
                font-size: clamp(0.4rem, 1vw, 0.7rem) !important;
            }

            /* ── Caption ──────────────────────────────────────────── */
            .stCaption, caption {
                font-size: clamp(0.35rem, 0.9vw, 0.7rem) !important;
            }

            /* ── Footer ───────────────────────────────────────────── */
            .footer-text {
                font-size: clamp(0.35rem, 0.9vw, 0.75rem) !important;
                margin-top: clamp(0.5rem, 1.5vw, 3rem) !important;
                padding: clamp(4px, 1vw, 15px) !important;
                text-align: center !important;
                color: #6c7a89 !important;
                border-top: 1px solid rgba(255,255,255,0.03) !important;
            }

            /* ── Breakpoint : très petit téléphone (<380px) ────── */
            @media (max-width: 380px) {
                :root {
                    --btn-size: clamp(38px, 16vw, 50px);
                    --btn-font: clamp(12px, 3.8vw, 16px);
                    --btn-gap: clamp(3px, 1.2vw, 5px);
                    --btn-radius: clamp(4px, 1.2vw, 8px);
                }
                .score-val { font-size: 0.55rem; }
                .score-icon { font-size: 0.45rem; }
                .score-user { display: none; }
                .status-banner { 
                    font-size: 0.4rem; 
                    padding: 2px 6px;
                    letter-spacing: 0.2px;
                }
                .main-title { font-size: 0.8rem !important; }
                .subtitle { font-size: 0.35rem !important; }
            }

            /* ── Breakpoint : téléphone (380-480px) ────────────── */
            @media (min-width: 381px) and (max-width: 480px) {
                :root {
                    --btn-size: clamp(45px, 20vw, 65px);
                    --btn-font: clamp(14px, 4.5vw, 20px);
                    --btn-gap: clamp(4px, 1.8vw, 6px);
                    --btn-radius: clamp(5px, 1.5vw, 10px);
                }
                .score-val { font-size: 0.7rem; }
                .score-icon { font-size: 0.55rem; }
                .score-user { display: none; }
                .status-banner { 
                    font-size: 0.5rem; 
                    padding: 3px 8px;
                }
                .main-title { font-size: 0.9rem !important; }
                .subtitle { font-size: 0.4rem !important; }
            }

            /* ── Breakpoint : petit smartphone (481-600px) ──────── */
            @media (min-width: 481px) and (max-width: 600px) {
                :root {
                    --btn-size: clamp(50px, 14vw, 70px);
                    --btn-font: clamp(16px, 4vw, 22px);
                    --btn-gap: clamp(5px, 1.5vw, 8px);
                }
                .score-val { font-size: 0.8rem; }
                .score-icon { font-size: 0.65rem; }
                .status-banner { font-size: 0.55rem; }
                .main-title { font-size: 1rem !important; }
            }

            /* ── Breakpoint : tablette (601-768px) ──────────────── */
            @media (min-width: 601px) and (max-width: 768px) {
                :root {
                    --btn-size: clamp(55px, 11vw, 75px);
                    --btn-font: clamp(18px, 3.5vw, 24px);
                }
                .score-val { font-size: 0.9rem; }
                .score-icon { font-size: 0.75rem; }
            }

            /* ── Breakpoint : grand écran ≥ 1400px ──────────────── */
            @media (min-width: 1400px) {
                :root {
                    --btn-size: 88px;
                    --btn-font: 30px;
                    --btn-gap: 12px;
                }
            }

            /* ── Panel desktop ───────────────────────────────────── */
            .panel-title {
                font-size: clamp(0.7rem, 1.4vw, 1rem) !important;
                margin-top: 0 !important;
                padding-left: clamp(6px, 1vw, 10px) !important;
                font-weight: 700 !important;
                letter-spacing: 0.5px !important;
            }
            .panel-content {
                max-height: clamp(120px, 25vh, 200px) !important;
                overflow-y: auto !important;
                padding-right: clamp(4px, 0.8vw, 8px) !important;
            }

            /* ── Boutons IA vs IA ────────────────────────────────── */
            .ia-controls {
                margin-top: clamp(8px, 1.5vw, 20px) !important;
                background: rgba(255,255,255,0.03) !important;
                padding: clamp(6px, 1vw, 15px) !important;
                border-radius: clamp(8px, 1.5vw, 12px) !important;
                border: 1px solid var(--border-subtle) !important;
            }
            .ia-controls .stButton > button {
                font-size: clamp(0.4rem, 1vw, 0.75rem) !important;
                padding: 2px 4px !important;
                height: auto !important;
                aspect-ratio: unset !important;
            }

            /* ── Désactiver le hover sur mobile ──────────────────── */
            @media (max-width: 768px) {
                .stButton > button:hover:not(:disabled) {
                    transform: none !important;
                    box-shadow: none !important;
                }
            }
        </style>
    """


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
    st.session_state.is_mobile = st.session_state.get('is_mobile', False)
    st.session_state._legal_moves_cache = None


def reset_game(keep_scores: bool = True) -> None:
    if not keep_scores:
        st.session_state.scores = [0, 0]
    st.session_state.game = Game()
    st.session_state.selected = -1
    st.session_state.ai_time_ms = 0.0
    st.session_state.nodes_explored = 0
    st.session_state.total_nodes = 0
    st.session_state.last_move = 'Aucun coup'
    st.session_state._legal_moves_cache = None


def get_legal_moves():
    if st.session_state._legal_moves_cache is None:
        st.session_state._legal_moves_cache = st.session_state.game.legal_moves()
    return st.session_state._legal_moves_cache


def player_name(player: int) -> str:
    mode = st.session_state.mode
    is_mobile = st.session_state.get('is_mobile', False)
    
    if is_mobile:
        if mode == 'Humain vs IA':
            return '👤' if player == P1 else '🤖'
        if mode == 'IA vs IA':
            return '🤖X' if player == P1 else '🤖O'
        return 'J1' if player == P1 else 'J2'
    
    if mode == 'Humain vs IA':
        return '👤 Humain' if player == P1 else '🤖 IA'
    if mode == 'IA vs IA':
        return '🤖 IA X' if player == P1 else '🤖 IA O'
    return '👤 Joueur 1' if player == P1 else '👤 Joueur 2'


def status_text() -> str:
    game = st.session_state.game
    is_mobile = st.session_state.get('is_mobile', False)
    
    if game.winner != EMPTY:
        winner_emoji = '✖' if game.winner == P1 else '〇'
        if is_mobile:
            return f'🎉 {winner_emoji} gagne!'
        return f'🎉 Victoire : {player_name(game.winner)} {winner_emoji}'
    
    phase_label = '📌' if game.phase == 1 else '🔄'
    current_emoji = '✖' if game.current_player == P1 else '〇'
    if is_mobile:
        return f'{phase_label} {current_emoji} {player_name(game.current_player)}'
    phase_text = 'Placement' if game.phase == 1 else 'Mouvement'
    return f'{phase_label} {phase_text} — {current_emoji} {player_name(game.current_player)}'


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
            st.session_state._legal_moves_cache = None
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
        legal_targets = [move[2] for move in get_legal_moves() if move[0] == 'move' and move[1] == st.session_state.selected]
        if idx in legal_targets:
            if game.move(st.session_state.selected, idx):
                st.session_state.last_move = move_label(('move', st.session_state.selected, idx))
                st.session_state.selected = -1
                st.session_state._legal_moves_cache = None
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
    disabled = (game.winner != EMPTY or game.is_terminal())
    
    legal_targets = []
    if game.phase == 2 and st.session_state.selected >= 0:
        legal_targets = [move[2] for move in get_legal_moves() if move[0] == 'move' and move[1] == st.session_state.selected]

    for row in range(3):
        cols = st.columns(3, gap="small")
        for col in range(3):
            idx = row * 3 + col
            
            label = " "
            cell_class = "cell-empty"
            
            if game.board[idx] == P1:
                label = "✖"
                cell_class = "cell-p1"
            elif game.board[idx] == P2:
                label = "〇"
                cell_class = "cell-p2"
            
            if st.session_state.selected == idx and game.board[idx] != EMPTY:
                cell_class += " cell-selected"
            elif idx in legal_targets and game.board[idx] == EMPTY:
                label = "●"
                cell_class = "cell-target"
            
            with cols[col]:
                st.markdown(f'<div class="{cell_class}">', unsafe_allow_html=True)
                st.button(
                    label,
                    key=f"cell-{idx}",
                    disabled=disabled,
                    on_click=handle_click,
                    args=(idx,),
                    use_container_width=True
                )
                st.markdown('</div>', unsafe_allow_html=True)


def render_score_banner() -> None:
    game = st.session_state.game
    is_mobile = st.session_state.get('is_mobile', False)
    phase_emoji = '📌' if game.phase == 1 else '🔄'
    
    if is_mobile:
        st.markdown(f"""
            <div class="score-container">
                <div class="score-card border-p1" style="background: #1e293b; color: white;">
                    <span class="score-icon color-p1">✖</span>
                    <span class="score-val color-p1">{st.session_state.scores[0]}</span>
                    <span class="score-user">{player_name(P1)}</span>
                </div>
                <div class="score-card border-phase" style="background: #334155; color: white;">
                    <span class="score-icon">{phase_emoji}</span>
                    <span class="score-val" style="font-size: clamp(0.5rem, 1.8vw, 0.9rem); color: #f8fafc;">P{game.phase}</span>
                    <span class="score-user" style="color: #cbd5e1;">FANORON</span>
                </div>
                <div class="score-card border-p2" style="background: #1e293b; color: white;">
                    <span class="score-icon color-p2">〇</span>
                    <span class="score-val color-p2">{st.session_state.scores[1]}</span>
                    <span class="score-user">{player_name(P2)}</span>
                </div>
            </div>
            <div class="status-banner" style="background: #0f172a; border: 1px solid rgba(0, 242, 255, 0.12); color: #e2e8f0;">
                {status_text()}
            </div>
        """, unsafe_allow_html=True)
    else:
        st.markdown(f"""
            <div class="score-container">
                <div class="score-card border-p1" style="background: linear-gradient(145deg, #1e293b, #0f172a); color: white;">
                    <span class="score-icon color-p1">✖</span>
                    <span class="score-val color-p1">{st.session_state.scores[0]}</span>
                    <span class="score-user" style="color: rgba(0, 242, 255, 0.7); font-weight: 600;">{player_name(P1)}</span>
                </div>
                <div class="score-card border-phase" style="background: #334155; color: white;">
                    <span class="score-icon" style="opacity: 0.9;">{phase_emoji}</span>
                    <span class="score-val" style="font-size: clamp(0.7rem, 2vw, 1.1rem); margin-top: 2px; letter-spacing: 0.5px; color: #f8fafc;">PHASE {game.phase}</span>
                    <span class="score-user" style="color: #cbd5e1;">FANORON-TELO</span>
                </div>
                <div class="score-card border-p2" style="background: linear-gradient(145deg, #1e293b, #0f172a); color: white;">
                    <span class="score-icon color-p2">〇</span>
                    <span class="score-val color-p2">{st.session_state.scores[1]}</span>
                    <span class="score-user" style="color: rgba(189, 0, 255, 0.7); font-weight: 600;">{player_name(P2)}</span>
                </div>
            </div>
            <div class="status-banner" style="background: #0f172a; border: 1px solid rgba(0, 242, 255, 0.15); text-transform: uppercase; color: #e2e8f0;">
                {status_text()}
            </div>
        """, unsafe_allow_html=True)


def main() -> None:
    is_mobile = False
    try:
        if hasattr(st, 'browser') and hasattr(st.browser, 'user_agent'):
            user_agent = st.browser.user_agent
            if user_agent:
                is_mobile = any(device in user_agent.lower() for device in ['mobile', 'android', 'iphone', 'ipad', 'phone'])
    except:
        pass
    
    st.set_page_config(
        page_title='Fanoron-telo IA', 
        page_icon='♟', 
        layout='centered' if is_mobile else 'wide',
        initial_sidebar_state='expanded'
    )
    init_state()
    st.session_state.is_mobile = is_mobile
    
    st.markdown(_css_block(), unsafe_allow_html=True)

    if is_mobile:
        st.markdown(
            '<div class="main-title">♟ Fanoron-telo</div>'
            '<div class="subtitle">Alignez 3 pions</div>',
            unsafe_allow_html=True
        )
    else:
        st.markdown(
            '<div class="main-title">♟ Fanoron-telo IA</div>'
            '<div class="subtitle">Alignez 3 pions pour remporter la partie</div>',
            unsafe_allow_html=True
        )

    with st.sidebar:
        st.markdown('<h3>⚙️ Config</h3>', unsafe_allow_html=True)
        
        if is_mobile:
            modes = ['H vs H', 'H vs IA', 'IA vs IA']
            mode_values = ['Humain vs Humain', 'Humain vs IA', 'IA vs IA']
        else:
            modes = ['👥 Humain vs Humain', '🤖 Humain vs IA', '🤖 IA vs IA']
            mode_values = ['Humain vs Humain', 'Humain vs IA', 'IA vs IA']
            
        current_mode = st.session_state.mode
        mode_index = mode_values.index(current_mode) if current_mode in mode_values else 0
        
        selected_mode_display = st.selectbox('🎮 Mode', modes, index=mode_index)
        st.session_state.mode = mode_values[modes.index(selected_mode_display)]
        
        if st.session_state.mode != 'Humain vs Humain':
            if is_mobile:
                difficulties = ['Facile', 'Moyen', 'Difficile']
                diff_emojis = ['🟢', '🟡', '🔴']
                diff_values = ['Facile', 'Moyen', 'Difficile']
            else:
                difficulties = ['🟢 Facile', '🟡 Moyen', '🔴 Difficile']
                diff_values = ['Facile', 'Moyen', 'Difficile']
                
            current_diff = st.session_state.difficulty
            diff_index = diff_values.index(current_diff) if current_diff in diff_values else 1
            
            selected_diff_display = st.selectbox('🎯 IA', difficulties, index=diff_index)
            st.session_state.difficulty = diff_values[difficulties.index(selected_diff_display)]
        
        st.markdown('<hr>', unsafe_allow_html=True)
        
        c1, c2 = st.columns(2)
        with c1:
            if st.button('🔄 Nouveau', use_container_width=True):
                reset_game(keep_scores=True)
        with c2:
            if st.button('↩ Annuler', use_container_width=True):
                st.session_state.game.undo()
                st.session_state.selected = -1
        
        c3, c4 = st.columns(2)
        with c3:
            if st.button('↪ Refaire', use_container_width=True):
                st.session_state.game.redo()
                st.session_state.selected = -1
        with c4:
            if st.button('🗑 Reset', use_container_width=True):
                reset_game(keep_scores=False)
        
        st.markdown('<hr>', unsafe_allow_html=True)
        
        with st.expander('📊 IA Stats', expanded=not is_mobile):
            st.metric('⏱ Temps', f'{st.session_state.ai_time_ms:.1f} ms')
            st.metric('🔍 Nœuds', f'{st.session_state.nodes_explored:,}')
            st.metric('📈 Total', f'{st.session_state.total_nodes:,}')

    if is_mobile:
        render_score_banner()
        render_board()
        
        if st.session_state.mode == 'IA vs IA' and st.session_state.game.winner == EMPTY:
            col1, col2 = st.columns(2)
            with col1:
                if st.button('▶ Suivant', use_container_width=True):
                    ai_turn()
            with col2:
                if st.button('⏩ Auto 5', use_container_width=True):
                    for _ in range(5):
                        if st.session_state.game.winner != EMPTY or st.session_state.game.is_terminal(): break
                        ai_turn()
                    st.rerun()
                    
        tab1, tab2 = st.tabs(['📜 Historique', '📋 Coups'])
        with tab1:
            history = st.session_state.game.history_descriptions()
            if history:
                rows = ''.join(f'<span class="log-entry" style="display:block;">• {item}</span>' for item in history[-5:])
                st.markdown(rows, unsafe_allow_html=True)
            else:
                st.caption('Aucun coup')
        with tab2:
            legal = get_legal_moves()
            labels = legal_moves_labels(legal)
            if labels:
                rows = ''.join(f'<span class="legal-move-tag" style="display:inline-block;background:rgba(255,215,0,0.1);border:1px solid rgba(255,215,0,0.2);color:#ffd700;">{label}</span>' for label in labels[:6])
                st.markdown(rows, unsafe_allow_html=True)
            else:
                st.caption('Aucun coup possible')
    else:
        board_col, panel_col = st.columns([1.5, 1], gap="large")
        
        with board_col:
            render_score_banner()
            st.markdown('<div style="padding:8px 0;">', unsafe_allow_html=True)
            render_board()
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.session_state.mode == 'IA vs IA' and st.session_state.game.winner == EMPTY:
                st.markdown('<div class="ia-controls">', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('▶ Coup IA', use_container_width=True):
                        ai_turn()
                with col2:
                    if st.button('⏩ Auto 10', use_container_width=True):
                        for _ in range(10):
                            if st.session_state.game.winner != EMPTY or st.session_state.game.is_terminal(): break
                            ai_turn()
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        with panel_col:
            history = st.session_state.game.history_descriptions()
            if history:
                history_html = ''.join(f'<div class="log-entry" style="padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.06); color:#e0e6ed;">• {item}</div>' for item in history[-10:])
            else:
                history_html = '<div style="color:#8a99ad; font-style:italic; font-size:0.8rem;">Aucun coup</div>'
            
            legal = get_legal_moves()
            labels = legal_moves_labels(legal)
            if labels:
                legal_html = ''.join(f'<span class="legal-move-tag" style="display:inline-block;background:rgba(255,215,0,0.1);border:1px solid rgba(255,215,0,0.2);color:#ffd700;">{label}</span>' for label in labels)
            else:
                legal_html = '<div style="color:#8a99ad; font-style:italic; font-size:0.8rem;">Aucun coup</div>'

            panel_html = f'<div style="background: #1e293b; padding:16px 18px; border-radius:14px; border:1px solid rgba(255,255,255,0.06); height:100%; box-shadow: 0 6px 20px rgba(0,0,0,0.3); color: white;">'
            panel_html += f'<h4 class="panel-title" style="color:#00f2ff; border-left: 3px solid #00f2ff;">📜 HISTORIQUE</h4>'
            panel_html += f'<div class="panel-content">{history_html}</div>'
            panel_html += f'<h4 class="panel-title" style="color:#ffd700; border-left: 3px solid #ffd700; margin-top:20px;">📋 COUPS LÉGAUX</h4>'
            panel_html += f'<div class="panel-content">{legal_html}</div>'
            panel_html += '</div>'
            st.markdown(panel_html, unsafe_allow_html=True)

    with st.expander('🗺 ASCII'):
        st.code(ascii_board(st.session_state.game.board), language='text')
        st.caption(f"Joueur: {st.session_state.game.current_player} | Pions: {st.session_state.game.placed}")

    st.markdown('<div class="footer-text">♟ Hackathon Algorithmique Avancée • IA Fanoron-telo</div>', unsafe_allow_html=True)


if __name__ == '__main__':
    main()
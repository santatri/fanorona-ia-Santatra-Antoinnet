from __future__ import annotations
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
    st.session_state.is_mobile = st.session_state.get('is_mobile', False)


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
        return '👤 Humain' if player == P1 else '🤖 IA'
    if mode == 'IA vs IA':
        return '🤖 IA X' if player == P1 else '🤖 IA O'
    return '👤 Joueur 1' if player == P1 else '👤 Joueur 2'


def status_text() -> str:
    game = st.session_state.game
    if game.winner != EMPTY:
        winner_emoji = '✖' if game.winner == P1 else '〇'
        return f'🎉 Victoire : {player_name(game.winner)} {winner_emoji}'
    phase_label = '📌 Placement' if game.phase == 1 else '🔄 Mouvement'
    current_emoji = '✖' if game.current_player == P1 else '〇'
    return f'{phase_label} — Tour {current_emoji} {player_name(game.current_player)}'


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
    """Rendu du plateau 3x3 hautement stylisé et responsive"""
    game = st.session_state.game
    disabled = (game.winner != EMPTY or game.is_terminal())
    
    # Calcul des coups légaux pour la surbrillance
    legal_targets = []
    if game.phase == 2 and st.session_state.selected >= 0:
        legal_targets = [move[2] for move in game.legal_moves() if move[0] == 'move' and move[1] == st.session_state.selected]

    for row in range(3):
        cols = st.columns(3, gap="small")
        for col in range(3):
            idx = row * 3 + col
            
            # Configuration par défaut de la cellule
            label = " "
            cell_class = "cell-empty"
            
            if game.board[idx] == P1:
                label = "✖"
                cell_class = "cell-p1"
            elif game.board[idx] == P2:
                label = "〇"
                cell_class = "cell-p2"
            
            # États spéciaux (Sélectionné et Cible légale)
            if st.session_state.selected == idx and game.board[idx] != EMPTY:
                cell_class += " cell-selected"
            elif idx in legal_targets and game.board[idx] == EMPTY:
                label = "●"
                cell_class = "cell-target"
            
            with cols[col]:
                # On utilise un div conteneur personnalisé injecté dynamiquement pour cibler précisément le bouton
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
    """Bannière de score universelle au design épuré (Glassmorphism)"""
    game = st.session_state.game
    phase_emoji = '📌' if game.phase == 1 else '🔄'
    
    st.markdown(f"""
        <div class="score-container">
            <div class="score-card border-p1">
                <span class="score-icon color-p1">✖</span>
                <span class="score-val color-p1">{st.session_state.scores[0]}</span>
                <span class="score-user">{player_name(P1)}</span>
            </div>
            <div class="score-card border-phase">
                <span class="score-icon">{phase_emoji}</span>
                <span class="score-val" style="font-size: 1.1rem; margin-top: 4px;">Phase {game.phase}</span>
                <span class="score-user">Fanoron-telo</span>
            </div>
            <div class="score-card border-p2">
                <span class="score-icon color-p2">〇</span>
                <span class="score-val color-p2">{st.session_state.scores[1]}</span>
                <span class="score-user">{player_name(P2)}</span>
            </div>
        </div>
        <div class="status-banner">
            {status_text()}
        </div>
    """, unsafe_allow_html=True)


def main() -> None:
    # Détection mobile basique
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
    
    # Injection de la feuille de style CSS principale (Moderne, Neon-Dark Theme)
    st.markdown("""
        <style>
            /* Reset global & variables */
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
            }
            
            /* Conteneur de Score Moderne (Flexbox fluide) */
            .score-container {
                display: flex;
                gap: 12px;
                margin-bottom: 12px;
                width: 100%;
            }
            .score-card {
                flex: 1;
                background: var(--bg-card);
                border: 1px solid var(--border-subtle);
                border-radius: 14px;
                padding: 10px;
                text-align: center;
                display: flex;
                flex-direction: column;
                align-items: center;
                backdrop-filter: blur(10px);
            }
            .border-p1 { border-bottom: 3px solid var(--p1-color); }
            .border-p2 { border-bottom: 3px solid var(--p2-color); }
            .border-phase { border-bottom: 3px solid #6c7a89; }
            .score-icon { font-size: 1.2rem; font-weight: bold; }
            .score-val { font-size: 1.6rem; font-weight: 800; line-height: 1.2; }
            .score-user { font-size: 0.75rem; color: #8a99ad; margin-top: 2px; }
            .color-p1 { color: var(--p1-color); text-shadow: 0 0 8px var(--p1-glow); }
            .color-p2 { color: var(--p2-color); text-shadow: 0 0 8px var(--p2-glow); }
            
            /* Bannière de statut de jeu */
            .status-banner {
                text-align: center;
                padding: 10px;
                background: var(--bg-card);
                border-radius: 10px;
                border: 1px solid var(--border-subtle);
                font-size: 0.9rem;
                font-weight: 600;
                margin-bottom: 20px;
                color: #e8e8f0;
                box-shadow: inset 0 0 10px rgba(255,255,255,0.02);
            }

            /* Customisation stricte de la Grille de Boutons Streamlit */
            .row-widget.stHorizontalBlock {
                flex-wrap: nowrap !important;
                gap: 8px !important;
                margin-bottom: 8px;
            }
            .row-widget.stHorizontalBlock > div {
                flex: 1 1 0 !important;
                min-width: 0 !important;
            }
            
            .stButton button {
                width: 100% !important;
                aspect-ratio: 1 / 1 !important;
                padding: 0 !important;
                font-size: 32px !important;
                border-radius: 16px !important;
                min-height: 75px !important;
                display: flex !important;
                align-items: center !important;
                justify-content: center !important;
                background: var(--bg-card) !important;
                border: 1px solid var(--border-subtle) !important;
                color: #e8e8f0 !important;
                transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
                backdrop-filter: blur(8px) !important;
            }
            
            /* Injection de style contextuel via le div parent */
            .cell-p1 button { color: var(--p1-color) !important; background: var(--p1-bg) !important; border-color: rgba(0, 242, 255, 0.3) !important; text-shadow: 0 0 12px var(--p1-glow); }
            .cell-p2 button { color: var(--p2-color) !important; background: var(--p2-bg) !important; border-color: rgba(189, 0, 255, 0.3) !important; text-shadow: 0 0 12px var(--p2-glow); }
            .cell-selected button { border: 2px solid var(--p1-color) !important; box-shadow: 0 0 15px var(--p1-glow) !important; transform: scale(0.98); }
            .cell-target button { color: var(--target-color) !important; border: 2px dashed rgba(255, 215, 0, 0.4) !important; font-size: 20px !important; }
            
            .stButton button:hover:not(:disabled) {
                border-color: #ffffff33 !important;
                transform: translateY(-2px);
                box-shadow: 0 4px 12px rgba(0,0,0,0.3);
            }
            .stButton button:active:not(:disabled) {
                transform: scale(0.95) !important;
            }

            /* Overrides pour Tablettes et Mobiles */
            @media (max-width: 480px) {
                .stButton button { font-size: 24px !important; min-height: 55px !important; border-radius: 12px !important; }
                .row-widget.stHorizontalBlock { gap: 6px !important; }
                .score-val { font-size: 1.3rem; }
                .score-icon { font-size: 1rem; }
            }
        </style>
    """, unsafe_allow_html=True)

    # En-tête de la page principale
    st.markdown('<h2 style="text-align:center; font-weight:700; margin-bottom:0.2rem;">♟ Fanoron-telo IA</h2>', unsafe_allow_html=True)
    st.markdown('<p style="text-align:center; color:#8a99ad; font-size:0.9rem; margin-bottom:1.5rem;">Alignez 3 pions pour remporter la partie</p>', unsafe_allow_html=True)

    # Barre latérale (Sidebar de Configuration)
    with st.sidebar:
        st.markdown('<h3 style="margin-top:0;">⚙️ Configuration</h3>', unsafe_allow_html=True)
        
        modes = ['👥 Humain vs Humain', '🤖 Humain vs IA', '🤖 IA vs IA']
        mode_values = ['Humain vs Humain', 'Humain vs IA', 'IA vs IA']
        current_mode = st.session_state.mode
        mode_index = mode_values.index(current_mode) if current_mode in mode_values else 0
        
        selected_mode_display = st.selectbox('🎮 Mode de jeu', modes, index=mode_index)
        st.session_state.mode = mode_values[modes.index(selected_mode_display)]
        
        if st.session_state.mode != 'Humain vs Humain':
            difficulties = ['🟢 Facile', '🟡 Moyen', '🔴 Difficile']
            diff_values = ['Facile', 'Moyen', 'Difficile']
            current_diff = st.session_state.difficulty
            diff_index = diff_values.index(current_diff) if current_diff in diff_values else 1
            
            selected_diff_display = st.selectbox('🎯 Difficulté IA', difficulties, index=diff_index)
            st.session_state.difficulty = diff_values[difficulties.index(selected_diff_display)]
        
        st.markdown('<hr style="margin:15px 0; opacity:0.1;">', unsafe_allow_html=True)
        
        # Section d'actions rapides sous forme de grille compacte
        c1, c2 = st.columns(2)
        with c1:
            if st.button('🔄 Nouvelle', use_container_width=True):
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
            if st.button('🗑 Reset Absolu', use_container_width=True):
                reset_game(keep_scores=False)
        
        st.markdown('<hr style="margin:15px 0; opacity:0.1;">', unsafe_allow_html=True)
        
        # Métriques de performance de l'IA
        with st.expander('📊 Performances IA', expanded=not is_mobile):
            st.metric('⏱ Temps de calcul', f'{st.session_state.ai_time_ms:.1f} ms')
            st.metric('🔍 Nœuds visités', f'{st.session_state.nodes_explored:,}')
            st.metric('📈 Total des nœuds', f'{st.session_state.total_nodes:,}')

    # Zone de jeu principale
    if is_mobile:
        # Ordre Mobile : Score -> Plateau -> Logs
        render_score_banner()
        render_board()
        
        if st.session_state.mode == 'IA vs IA' and st.session_state.game.winner == EMPTY:
            col1, col2 = st.columns(2)
            with col1:
                if st.button('▶ Coup suivant', use_container_width=True):
                    ai_turn()
            with col2:
                if st.button('⏩ Auto 5', use_container_width=True):
                    for _ in range(5):
                        if st.session_state.game.winner != EMPTY or st.session_state.game.is_terminal(): break
                        ai_turn()
                    st.rerun()
                    
        tab1, tab2 = st.tabs(['📜 Historique', '📋 Coups légaux'])
        with tab1:
            history = st.session_state.game.history_descriptions()
            if history:
                for item in history[-6:]: st.markdown(f'<span style="font-size:0.85rem;">• {item}</span>', unsafe_allow_html=True)
            else: st.caption('Aucun coup joué')
        with tab2:
            legal = st.session_state.game.legal_moves()
            labels = legal_moves_labels(legal)
            if labels:
                for label in labels[:6]: st.markdown(f'<span style="font-size:0.85rem;">• {label}</span>', unsafe_allow_html=True)
            else: st.caption('Aucun coup possible')
    else:
        # Ordre Desktop : Colonne gauche (Plateau) | Colonne droite (Stats & Logs)
        board_col, panel_col = st.columns([1.2, 1])
        
        with board_col:
            render_score_banner()
            st.markdown('<div style="padding:10px 20px;">', unsafe_allow_html=True)
            render_board()
            st.markdown('</div>', unsafe_allow_html=True)
            
            if st.session_state.mode == 'IA vs IA' and st.session_state.game.winner == EMPTY:
                st.markdown('<div style="margin-top:15px;">', unsafe_allow_html=True)
                col1, col2 = st.columns(2)
                with col1:
                    if st.button('▶ Exécuter le coup IA', use_container_width=True):
                        ai_turn()
                with col2:
                    if st.button('⏩ Automatiser (10 coups)', use_container_width=True):
                        for _ in range(10):
                            if st.session_state.game.winner != EMPTY or st.session_state.game.is_terminal(): break
                            ai_turn()
                        st.rerun()
                st.markdown('</div>', unsafe_allow_html=True)
        
        with panel_col:
            # Panneau d'informations de jeu
            st.markdown('<div style="background:var(--bg-card); padding:20px; border-radius:16px; border:1px solid var(--border-subtle); height:100%;">', unsafe_allow_html=True)
            
            st.markdown('<h4 style="margin-top:0;">📜 Historique de la partie</h4>', unsafe_allow_html=True)
            history = st.session_state.game.history_descriptions()
            if history:
                st.markdown('<div style="max-height:150px; overflow-y:auto; font-size:0.9rem; padding-right:5px;">', unsafe_allow_html=True)
                for item in history[-8:]:
                    st.markdown(f'<div style="padding:4px 0; border-bottom:1px solid rgba(255,255,255,0.02)">• {item}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.caption('Le match n\'a pas encore débuté.')
                
            st.markdown('<h4 style="margin-top:20px;">📋 Actions légales disponibles</h4>', unsafe_allow_html=True)
            legal = st.session_state.game.legal_moves()
            labels = legal_moves_labels(legal)
            if labels:
                st.markdown('<div style="max-height:150px; overflow-y:auto; font-size:0.9rem; padding-right:5px; color:#a3b8cc;">', unsafe_allow_html=True)
                for label in labels:
                    st.markdown(f'<div style="padding:3px 0;">→ {label}</div>', unsafe_allow_html=True)
                st.markdown('</div>', unsafe_allow_html=True)
            else:
                st.caption('Aucun coup légal détecté.')
                
            st.markdown('</div>', unsafe_allow_html=True)

    # Vue Développeur / Console ASCII en bas
    with st.expander('🗺 Vue Terminal Matrix (ASCII)'):
        st.code(ascii_board(st.session_state.game.board), language='text')
        st.caption(f"Joueur courant id: {st.session_state.game.current_player} | Pions posés: {st.session_state.game.placed}")

    # Footer discret
    st.markdown("""
        <div style="margin-top:3rem; padding:15px; text-align:center; font-size:0.75rem; color:#6c7a89; border-top:1px solid rgba(255,255,255,0.03);">
            ♟ Hackathon Algorithmique Avancée • Interface Premium Core
        </div>
    """, unsafe_allow_html=True)


if __name__ == '__main__':
    main()
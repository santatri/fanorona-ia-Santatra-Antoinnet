import streamlit as st
import time
import math
import random
from typing import List, Tuple, Dict, Any, Optional

# ─────────────────────────────────────────────────────────────
# CONSTANTES ET CONFIGURATION DU PLATEAU
# ─────────────────────────────────────────────────────────────
EMPTY, P1, P2 = 0, 1, 2

WIN_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8], # H
    [0, 3, 6], [1, 4, 7], [2, 5, 8], # V
    [0, 4, 8], [2, 4, 6],           # D
]

# Adjacence Fanoron-telo (3x3) : H, V et Diagonales passant par le centre
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

DEPTH_MAP = {"Facile": 1, "Moyen": 3, "Difficile": 6}

# ─────────────────────────────────────────────────────────────
# MOTEUR DE JEU (LOGIQUE)
# ─────────────────────────────────────────────────────────────

def check_winner(board: List[int]) -> int:
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return EMPTY

def has_legal_moves(board: List[int], player: int, phase: int) -> bool:
    if phase == 1: return board.count(EMPTY) > 0
    for i in range(9):
        if board[i] == player:
            if any(board[nb] == EMPTY for nb in ADJ[i]): return True
    return False

def get_legal_moves(board: List[int], player: int, phase: int) -> List[Dict[str, Any]]:
    moves = []
    if phase == 1:
        for i in range(9):
            if board[i] == EMPTY: moves.append({"type": "place", "to": i})
    else:
        for i in range(9):
            if board[i] == player:
                for nb in ADJ[i]:
                    if board[nb] == EMPTY: moves.append({"type": "move", "from": i, "to": nb})
    return moves

def apply_move(board: List[int], move: Dict[str, Any], player: int, phase: int, placed: List[int]):
    nb, npl, nph = board[:], placed[:], phase
    if move["type"] == "place":
        nb[move["to"]] = player
        npl[player - 1] += 1
        if npl[0] == 3 and npl[1] == 3: nph = 2
    else:
        nb[move["from"]] = EMPTY
        nb[move["to"]] = player
    return nb, nph, npl

def get_game_result(board: List[int], current_player: int, phase: int) -> Optional[int]:
    w = check_winner(board)
    if w: return w
    if phase == 2 and not has_legal_moves(board, current_player, phase):
        return P1 if current_player == P2 else P2
    return None

# ─────────────────────────────────────────────────────────────
# IA (MINIMAX + ALPHA-BETA)
# ─────────────────────────────────────────────────────────────

def evaluate(board, ai_p, curr_p, phase):
    opp = P1 if ai_p == P2 else P2
    res = get_game_result(board, curr_p, phase)
    if res == ai_p: return 10000
    if res == opp: return -10000
    score = 0
    for a, b, c in WIN_LINES:
        l = [board[a], board[b], board[c]]
        ac, oc = l.count(ai_p), l.count(opp)
        if oc == 0:
            if ac == 2: score += 100
            elif ac == 1: score += 10
        if ac == 0:
            if oc == 2: score -= 200
            elif oc == 1: score -= 10
    if board[4] == ai_p: score += 30
    elif board[4] == opp: score -= 30
    return score

def minimax(board, depth, alpha, beta, maximizing, ai_p, curr_p, phase, placed, trans, stats):
    stats["nodes"] += 1
    key = (tuple(board), curr_p, phase, depth)
    if key in trans: return trans[key]
    res = get_game_result(board, curr_p, phase)
    if res is not None or depth == 0:
        v = evaluate(board, ai_p, curr_p, phase)
        trans[key] = v
        return v
    moves = get_legal_moves(board, curr_p, phase)
    if not moves: return evaluate(board, ai_p, curr_p, phase)
    next_p = P1 if curr_p == P2 else P2
    if maximizing:
        me = -math.inf
        for m in moves:
            nb, np, npl = apply_move(board, m, curr_p, phase, placed)
            ev = minimax(nb, depth-1, alpha, beta, False, ai_p, next_p, np, npl, trans, stats)
            me = max(me, ev); alpha = max(alpha, ev)
            if beta <= alpha: break
        trans[key] = me
        return me
    else:
        me = math.inf
        for m in moves:
            nb, np, npl = apply_move(board, m, curr_p, phase, placed)
            ev = minimax(nb, depth-1, alpha, beta, True, ai_p, next_p, np, npl, trans, stats)
            me = min(me, ev); beta = min(beta, ev)
            if beta <= alpha: break
        trans[key] = me
        return me

def get_best_move(board, player, phase, placed, level):
    moves = get_legal_moves(board, player, phase)
    if not moves: return None, 0
    if level == "Facile": return random.choice(moves), 1
    depth = DEPTH_MAP.get(level, 3)
    bm, bv = None, -math.inf
    trans, stats = {}, {"nodes": 0}
    next_p = P1 if player == P2 else P2
    moves.sort(key=lambda m: 1 if m["to"] == 4 else 0, reverse=True)
    for m in moves:
        nb, np, npl = apply_move(board, m, player, phase, placed)
        v = minimax(nb, depth-1, -math.inf, math.inf, False, player, next_p, np, npl, trans, stats)
        if v > bv: bv, bm = v, m
    return bm, stats["nodes"]

# ─────────────────────────────────────────────────────────────
# UI STREAMLIT
# ─────────────────────────────────────────────────────────────

def init_game():
    st.session_state.update({
        'board': [EMPTY]*9, 'current_player': P1, 'phase': 1, 'placed': [0,0],
        'winner': None, 'history_stack': [], 'move_history': [], 'selected_pawn': None,
        'last_ai_time': 0.0, 'last_ai_nodes': 0, 'game_over': False, 'auto_play': False
    })

if 'board' not in st.session_state: init_game()

st.set_page_config(page_title="Fanoron-telo ISPM Hackathon", layout="wide", page_icon="♟")

st.markdown("""
<style>
    .main { background-color: #0f172a; color: #f8fafc; }
    .stButton>button {
        width: 100%; border-radius: 12px;
        background-color: #1e293b; color: white;
        border: 2px solid #334155; height: 4em;
        font-weight: 800; font-size: 1.2rem;
        transition: all 0.2s ease;
    }
    .stButton>button:hover { border-color: #38bdf8; color: #38bdf8; transform: translateY(-2px); }
    .stat-card { background-color: #1e293b; padding: 15px; border-radius: 12px; border-left: 5px solid #38bdf8; margin-bottom: 15px; }
    .stat-label { font-size: 0.8rem; color: #94a3b8; text-transform: uppercase; }
    .stat-val { font-size: 1.8rem; font-weight: bold; color: #f8fafc; }
    .player-indicator { padding: 15px; border-radius: 12px; text-align: center; margin-bottom: 25px; font-weight: bold; font-size: 1.1rem; }
    .p1-active { background: linear-gradient(135deg, #0369a1 0%, #075985 100%); color: white; }
    .p2-active { background: linear-gradient(135deg, #b45309 0%, #92400e 100%); color: white; }
    .legal-moves, .move-history { background: #1e293b; padding: 15px; border-radius: 12px; max-height: 250px; overflow-y: auto; border: 1px solid #334155; }
    .move-item { padding: 5px 0; border-bottom: 1px solid #334155; font-size: 0.9rem; color: #cbd5e1; }
</style>
""", unsafe_allow_html=True)

def format_move_text(player, move):
    p_name = f"Joueur {player}"
    if move["type"] == "place": return f" {p_name}: Pose en {move['to']}"
    return f" {p_name}: {move['from']} ➔ {move['to']}"

def update_game(nb, nph, npl, move):
    st.session_state.move_history.append(format_move_text(st.session_state.current_player, move))
    st.session_state.update({'board': nb, 'phase': nph, 'placed': npl})
    w = get_game_result(nb, P1 if st.session_state.current_player == P2 else P2, nph)
    if w: st.session_state.update({'winner': w, 'game_over': True})
    else:
        st.session_state.current_player = P1 if st.session_state.current_player == P2 else P2
        if not has_legal_moves(nb, st.session_state.current_player, nph):
            st.session_state.update({'winner': (P1 if st.session_state.current_player == P2 else P2), 'game_over': True})

def ai_step():
    if st.session_state.game_over: return
    st.session_state.history_stack.append({'board': st.session_state.board[:], 'current_player': st.session_state.current_player, 'phase': st.session_state.phase, 'placed': st.session_state.placed[:]})
    t0 = time.perf_counter()
    m, n = get_best_move(st.session_state.board, st.session_state.current_player, st.session_state.phase, st.session_state.placed, level)
    st.session_state.update({'last_ai_time': (time.perf_counter()-t0)*1000, 'last_ai_nodes': n})
    if m:
        nb, nph, npl = apply_move(st.session_state.board, m, st.session_state.current_player, st.session_state.phase, st.session_state.placed)
        update_game(nb, nph, npl, m)

with st.sidebar:
    st.markdown("# ♟ Fanoron-telo")
    st.markdown("---")
    mode = st.selectbox("Mode de jeu", ["Humain vs Humain", "Humain vs IA", "IA vs IA"], index=1)
    level = st.selectbox("Niveau IA", ["Facile", "Moyen", "Difficile"], index=2)
    st.markdown("---")
    if st.button("🔄 Nouvelle Partie"): init_game(); st.rerun()
    if st.button("↩ Undo (Annuler)"):
        if st.session_state.history_stack:
            pop_count = 2 if mode == "Humain vs IA" and len(st.session_state.history_stack) >= 2 else 1
            for _ in range(pop_count):
                if st.session_state.history_stack:
                    s = st.session_state.history_stack.pop()
                    st.session_state.move_history.pop() if st.session_state.move_history else None
                    st.session_state.update({'board': s['board'], 'current_player': s['current_player'], 'phase': s['phase'], 'placed': s['placed']})
            st.session_state.update({'winner': None, 'game_over': False, 'selected_pawn': None})
            st.rerun()

    st.markdown("### 📜 Historique")
    hist_html = "".join([f'<div class="move-item">{m}</div>' for m in st.session_state.move_history[::-1]])
    st.markdown(f'<div class="move-history">{hist_html}</div>', unsafe_allow_html=True)

# Trigger AI if needed BEFORE rendering to ensure UI sync
if not st.session_state.game_over:
    if (mode == "Humain vs IA" and st.session_state.current_player == P2) or \
       (mode == "IA vs IA" and st.session_state.auto_play):
        ai_step()

def handle_click(idx):
    if st.session_state.game_over: return
    board, curr, phase, placed = st.session_state.board, st.session_state.current_player, st.session_state.phase, st.session_state.placed
    if phase == 1:
        if board[idx] == EMPTY:
            st.session_state.history_stack.append({'board': board[:], 'current_player': curr, 'phase': phase, 'placed': placed[:]})
            nb, nph, npl = apply_move(board, {"type": "place", "to": idx}, curr, phase, placed)
            update_game(nb, nph, npl, {"type": "place", "to": idx})
            st.rerun()
    else:
        sel = st.session_state.selected_pawn
        if sel is None:
            if board[idx] == curr: st.session_state.selected_pawn = idx; st.rerun()
        elif idx == sel: st.session_state.selected_pawn = None; st.rerun()
        elif board[idx] == EMPTY and idx in ADJ[sel]:
            st.session_state.history_stack.append({'board': board[:], 'current_player': curr, 'phase': phase, 'placed': placed[:]})
            m = {"type": "move", "from": sel, "to": idx}
            nb, nph, npl = apply_move(board, m, curr, phase, placed)
            st.session_state.selected_pawn = None; update_game(nb, nph, npl, m)
            st.rerun()
        elif board[idx] == curr: st.session_state.selected_pawn = idx; st.rerun()

st.markdown(f"## Fanoron-telo - ISPM Hackathon")
c1, c2 = st.columns([1.5, 1])

with c1:
    if st.session_state.winner: st.balloons(); st.success(f"🏆 Victoire Joueur {st.session_state.winner} !")
    else:
        p_act = "p1-active" if st.session_state.current_player == P1 else "p2-active"
        st.markdown(f'<div class="player-indicator {p_act}">Tour Joueur {st.session_state.current_player} (Phase {st.session_state.phase})</div>', unsafe_allow_html=True)

    for r in range(3):
        cols = st.columns([1,1,1,2])
        for c in range(3):
            idx = r*3 + c
            p = st.session_state.board[idx]
            label = "·" if p == EMPTY else ("X" if p == P1 else "O")
            if st.session_state.selected_pawn == idx: label = f"[{label}]"
            if cols[c].button(label, key=f"btn_{idx}", disabled=st.session_state.game_over): handle_click(idx)

    st.markdown("### 🖥 Représentation ASCII")
    b = [("X" if x == P1 else ("O" if x == P2 else ".")) for x in st.session_state.board]
    ascii_art = f"""{b[0]}---{b[1]}---{b[2]}
|\\ /|\\ /|
| {b[3]} | {b[4]} | {b[5]} |
|/ \\|/ \\|
{b[6]}---{b[7]}---{b[8]}"""
    st.code(ascii_art, language=None)

with c2:
    st.markdown("### 📊 Statistiques IA")
    st.markdown(f"""
    <div class="stat-card"><div class="stat-label">Temps de réflexion</div><div class="stat-val">{st.session_state.last_ai_time:.2f} ms</div></div>
    <div class="stat-card"><div class="stat-label">Nœuds explorés</div><div class="stat-val">{st.session_state.last_ai_nodes}</div></div>
    """, unsafe_allow_html=True)
    
    st.markdown("### 💡 Coups légaux")
    mvs = get_legal_moves(st.session_state.board, st.session_state.current_player, st.session_state.phase)
    ml = "".join([f'<div class="move-item">{"Pose en " + str(m["to"]) if m["type"]=="place" else "Glisser " + str(m["from"]) + " ➔ " + str(m["to"])}</div>' for m in mvs])
    st.markdown(f'<div class="legal-moves">{ml}</div>', unsafe_allow_html=True)

    if mode == "IA vs IA" and not st.session_state.game_over:
        st.markdown("---")
        if st.button("⏩ Jouer coup suivant"): ai_step(); st.rerun()
        if st.button("🔥 Auto-Play"): st.session_state.auto_play = True; st.rerun()

    if st.session_state.get('auto_play') and not st.session_state.game_over:
        time.sleep(0.2); st.rerun()
    elif st.session_state.game_over: st.session_state.auto_play = False

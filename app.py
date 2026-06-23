"""
Fanoron-telo avec IA – Streamlit
Institut Supérieur Polytechnique de Madagascar
www.ispm-edu.com

Architecture :
  - Plateau  : tableau de 9 cases (liste Python), 0=vide, 1=J1, 2=J2
  - Phase 1  : placement des 3 pions par joueur
  - Phase 2  : déplacement vers intersection adjacente libre
  - IA       : Minimax + élagage Alpha-Bêta + table de transposition
"""

import streamlit as st
import time
import math

# ─────────────────────────────────────────────────────────────
# CONSTANTES
# ─────────────────────────────────────────────────────────────
EMPTY, P1, P2 = 0, 1, 2

WIN_LINES = [
    [0, 1, 2], [3, 4, 5], [6, 7, 8],   # lignes
    [0, 3, 6], [1, 4, 7], [2, 5, 8],   # colonnes
    [0, 4, 8], [2, 4, 6],               # diagonales
]

# Adjacences (orthogonales + diagonales, comme sur le plateau Fanoron)
ADJ = {
    0: [1, 3, 4],
    1: [0, 2, 3, 4, 5],
    2: [1, 4, 5],
    3: [0, 1, 4, 6, 7],
    4: [0, 1, 2, 3, 5, 6, 7, 8],
    5: [1, 2, 4, 7, 8],
    6: [3, 4, 7],
    7: [3, 4, 5, 6, 8],
    8: [4, 5, 7],
}

DEPTH_MAP = {"Facile": 1, "Moyen": 3, "Difficile": 7}

LABELS = ["a1", "b1", "c1", "a2", "b2", "c2", "a3", "b3", "c3"]

# ─────────────────────────────────────────────────────────────
# RÈGLES DU JEU
# ─────────────────────────────────────────────────────────────

def check_winner(board: list) -> int:
    for a, b, c in WIN_LINES:
        if board[a] != EMPTY and board[a] == board[b] == board[c]:
            return board[a]
    return EMPTY

def has_legal_move(board: list, player: int) -> bool:
    for i in range(9):
        if board[i] == player:
            if any(board[nb] == EMPTY for nb in ADJ[i]):
                return True
    return False

def is_terminal(board: list, current_player: int, phase: int) -> bool:
    if check_winner(board):
        return True
    if phase == 2 and not has_legal_move(board, current_player):
        return True
    return False

def get_winner(board: list, current_player: int, phase: int) -> int:
    w = check_winner(board)
    if w:
        return w
    if phase == 2 and not has_legal_move(board, current_player):
        return P1 if current_player == P2 else P2
    return EMPTY

def get_moves(board: list, player: int, phase: int, placed: list) -> list:
    """Retourne la liste des coups légaux sous forme de dict."""
    moves = []
    if phase == 1:
        for i in range(9):
            if board[i] == EMPTY:
                moves.append({"type": "place", "to": i})
    else:
        for i in range(9):
            if board[i] == player:
                for nb in ADJ[i]:
                    if board[nb] == EMPTY:
                        moves.append({"type": "move", "from": i, "to": nb})
    return moves

def apply_move(board: list, move: dict, player: int, phase: int, placed: list):
    """Applique un coup, retourne (new_board, new_phase, new_placed)."""
    b = board[:]
    p = placed[:]
    if move["type"] == "place":
        b[move["to"]] = player
        p[player - 1] += 1
        if p[0] == 3 and p[1] == 3:
            phase = 2
    else:
        b[move["from"]] = EMPTY
        b[move["to"]] = player
    return b, phase, p

# ─────────────────────────────────────────────────────────────
# IA – MINIMAX + ALPHA-BÊTA + TABLE DE TRANSPOSITION
# ─────────────────────────────────────────────────────────────

def evaluate(board: list, ai_player: int) -> int:
    """Heuristique : somme pondérée des lignes."""
    opponent = P1 if ai_player == P2 else P2
    score = 0
    weights = [0, 1, 10, 1000]
    for a, b, c in WIN_LINES:
        line = [board[a], board[b], board[c]]
        ai_count  = line.count(ai_player)
        opp_count = line.count(opponent)
        if opp_count == 0:
            score += weights[ai_count]
        if ai_count == 0:
            score -= weights[opp_count]
    # Bonus centre
    if board[4] == ai_player:
        score += 3
    elif board[4] == opponent:
        score -= 3
    return score

def minimax(
    board: list, depth: int, alpha: int, beta: int,
    maximizing: bool, ai_player: int,
    current_player: int, phase: int, placed: list,
    trans_table: dict,
) -> int:
    """Minimax récursif avec élagage Alpha-Bêta et table de transposition."""
    key = (tuple(board), current_player, phase, depth)
    if key in trans_table:
        return trans_table[key]

    w = get_winner(board, current_player, phase)
    if w == ai_player:
        return 10000 + depth
    if w and w != ai_player:
        return -10000 - depth
    if depth == 0:
        return evaluate(board, ai_player)

    moves = get_moves(board, current_player, phase, placed)
    if not moves:
        return 0

    next_player = P1 if current_player == P2 else P2
    best = -math.inf if maximizing else math.inf

    for move in moves:
        nb, np, npl = apply_move(board, move, current_player, phase, placed)
        val = minimax(nb, depth - 1, alpha, beta, not maximizing,
                      ai_player, next_player, np, npl, trans_table)
        if maximizing:
            best = max(best, val)
            alpha = max(alpha, val)
        else:
            best = min(best, val)
            beta = min(beta, val)
        if beta <= alpha:
            break  # élagage α-β

    trans_table[key] = best
    return best

def get_best_move(board: list, player: int, phase: int, placed: list, level: str) -> dict:
    """Retourne le meilleur coup pour le joueur IA."""
    depth = DEPTH_MAP.get(level, 3)
    moves = get_moves(board, player, phase, placed)
    if not moves:
        return None

    # Facile : 40% de hasard
    if level == "Facile":
        import random
        if random.random() < 0.4:
            return random.choice(moves)

    trans_table = {}
    best_val  = -math.inf
    best_move = moves[0]
    next_player = P1 if player == P2 else P2

    for move in moves:
        nb, np, npl = apply_move(board, move, player, phase, placed)
        val = minimax(nb, depth - 1, -math.inf, math.inf,
                      False, player, next_player, np, npl, trans_table)
        if val > best_val:
            best_val  = val
            best_move = move

    return best_move

# ─────────────────────────────────────────────────────────────
# INITIALISATION SESSION STATE
# ─────────────────────────────────────────────────────────────

def init_state():
    st.session_state.board        = [EMPTY] * 9
    st.session_state.current      = P1
    st.session_state.phase        = 1
    st.session_state.placed       = [0, 0]
    st.session_state.selected     = -1
    st.session_state.winner       = EMPTY
    st.session_state.status_msg   = "Phase 1 – Placement : Joueur 1 place un pion"
    st.session_state.ai_time_ms   = None
    st.session_state.history      = []   # pour undo
    st.session_state.scores       = st.session_state.get("scores", [0, 0])

def save_history():
    import copy
    st.session_state.history.append({
        "board":   st.session_state.board[:],
        "current": st.session_state.current,
        "phase":   st.session_state.phase,
        "placed":  st.session_state.placed[:],
        "selected": st.session_state.selected,
        "winner":  st.session_state.winner,
    })

def undo():
    if not st.session_state.history:
        return
    snap = st.session_state.history.pop()
    for k, v in snap.items():
        st.session_state[k] = v
    st.session_state.status_msg = "↩ Coup annulé"
    st.session_state.ai_time_ms = None

# ─────────────────────────────────────────────────────────────
# LOGIQUE D'UN COUP HUMAIN
# ─────────────────────────────────────────────────────────────

def human_click(idx: int):
    s = st.session_state
    if s.winner or is_terminal(s.board, s.current, s.phase):
        return
    mode = s.mode
    if mode == "IA vs IA":
        return
    if mode == "Humain vs IA" and s.current == P2:
        return

    if s.phase == 1:
        if s.board[idx] != EMPTY:
            return
        save_history()
        s.board, s.phase, s.placed = apply_move(s.board, {"type": "place", "to": idx}, s.current, s.phase, s.placed)
        _post_move()

    else:  # phase 2
        if s.selected == -1:
            if s.board[idx] != s.current:
                return
            s.selected = idx
        else:
            if idx == s.selected:
                s.selected = -1
                return
            if s.board[idx] == s.current:
                s.selected = idx
                return
            if idx in ADJ[s.selected] and s.board[idx] == EMPTY:
                save_history()
                s.board, s.phase, s.placed = apply_move(
                    s.board, {"type": "move", "from": s.selected, "to": idx},
                    s.current, s.phase, s.placed
                )
                s.selected = -1
                _post_move()
            else:
                s.selected = -1

def _post_move():
    s = st.session_state
    w = get_winner(s.board, s.current, s.phase)
    if w:
        s.winner = w
        names = _player_names()
        s.status_msg = f"🏆 {names[w-1]} remporte la partie !"
        s.scores[w - 1] += 1
        return
    s.current = P1 if s.current == P2 else P2
    names = _player_names()
    ph = "Placement" if s.phase == 1 else "Mouvement"
    s.status_msg = f"Phase {s.phase} – {ph} : tour de {names[s.current-1]}"

def _player_names():
    mode = st.session_state.mode
    return ["Joueur 1", "IA" if mode != "Humain vs Humain" else "Joueur 2"]

# ─────────────────────────────────────────────────────────────
# LOGIQUE COUP IA
# ─────────────────────────────────────────────────────────────

def ai_play():
    s = st.session_state
    if s.winner or is_terminal(s.board, s.current, s.phase):
        return
    t0 = time.perf_counter()
    move = get_best_move(s.board, s.current, s.phase, s.placed, s.difficulty)
    t1 = time.perf_counter()
    s.ai_time_ms = (t1 - t0) * 1000
    if move is None:
        return
    s.board, s.phase, s.placed = apply_move(s.board, move, s.current, s.phase, s.placed)
    s.selected = -1
    _post_move()

# ─────────────────────────────────────────────────────────────
# RENDU HTML DU PLATEAU
# ─────────────────────────────────────────────────────────────

def render_board_html() -> str:
    s = st.session_state
    board    = s.board
    selected = s.selected
    phase    = s.phase

    # Cibles légales (phase 2)
    legal_targets = set()
    if selected >= 0 and phase == 2:
        for nb in ADJ[selected]:
            if board[nb] == EMPTY:
                legal_targets.add(nb)

    # Lignes SVG (connexions)
    drawn = set()
    lines_svg = ""
    for i in range(9):
        for j in ADJ[i]:
            key = (min(i, j), max(i, j))
            if key in drawn:
                continue
            drawn.add(key)
            x1, y1 = (i % 3) * 100 + 50, (i // 3) * 100 + 50
            x2, y2 = (j % 3) * 100 + 50, (j // 3) * 100 + 50
            lines_svg += f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="#3a5570" stroke-width="2" stroke-linecap="round"/>'

    # Nœuds + pions
    nodes_svg = ""
    for i in range(9):
        cx = (i % 3) * 100 + 50
        cy = (i // 3) * 100 + 50

        # Couleur fond du nœud
        if i == selected:
            fill, stroke = "#2a1e1e", "#e85050"
        elif i in legal_targets:
            fill, stroke = "#1e3f28", "#27ae60"
        else:
            fill, stroke = "#1e2f42", "#3a5570"

        nodes_svg += (
            f'<circle cx="{cx}" cy="{cy}" r="18" fill="{fill}" stroke="{stroke}" '
            f'stroke-width="2" class="node" data-idx="{i}" style="cursor:pointer"/>'
        )

        # Pion
        if board[i] == P1:
            color, glow = "#e8b44a", "#e8b44a"
            nodes_svg += (
                f'<circle cx="{cx}" cy="{cy}" r="13" fill="{color}" stroke="{glow}" stroke-width="2" '
                f'class="node" data-idx="{i}" style="cursor:pointer"/>'
                f'<circle cx="{cx-3}" cy="{cy-3}" r="4" fill="white" opacity="0.25" pointer-events="none"/>'
            )
        elif board[i] == P2:
            color, glow = "#4aa8e8", "#4aa8e8"
            nodes_svg += (
                f'<circle cx="{cx}" cy="{cy}" r="13" fill="{color}" stroke="{glow}" stroke-width="2" '
                f'class="node" data-idx="{i}" style="cursor:pointer"/>'
                f'<circle cx="{cx-3}" cy="{cy-3}" r="4" fill="white" opacity="0.25" pointer-events="none"/>'
            )

    # Labels a-c / 1-3
    labels_svg = ""
    for i in range(9):
        cx = (i % 3) * 100 + 50
        cy = (i // 3) * 100 + 50
        col = ["a", "b", "c"][i % 3]
        row = [3, 2, 1][i // 3]
        if i >= 6:
            labels_svg += f'<text x="{cx}" y="{cy+32}" text-anchor="middle" fill="#3a5570" font-size="11" pointer-events="none">{col}</text>'
        if i % 3 == 0:
            labels_svg += f'<text x="{cx-30}" y="{cy+4}" text-anchor="middle" fill="#3a5570" font-size="11" pointer-events="none">{row}</text>'

    return f"""
    <svg viewBox="0 0 300 300" xmlns="http://www.w3.org/2000/svg" style="width:100%;max-width:320px;background:#152230;border-radius:12px;padding:10px;">
      {lines_svg}
      {nodes_svg}
      {labels_svg}
    </svg>
    """

# ─────────────────────────────────────────────────────────────
# PAGE STREAMLIT
# ─────────────────────────────────────────────────────────────

st.set_page_config(
    page_title="Fanoron-telo · ISPM",
    page_icon="♟",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── CSS global ───────────────────────────────────────────────
st.markdown("""
<style>
  body, .stApp { background: #0f1923; color: #e8edf2; }
  section.main { background: #0f1923; }
  div[data-testid="stVerticalBlock"] { gap: 0.4rem; }
  .stButton > button {
    background: #1a2636;
    border: 1px solid #2a3f55;
    color: #e8edf2;
    border-radius: 8px;
    font-weight: 500;
    transition: border-color .2s;
    width: 100%;
  }
  .stButton > button:hover { border-color: #e8b44a; color: #e8b44a; }
  .stSelectbox label, .stRadio label { color: #6b8099 !important; font-size: 0.85rem; }
  div[data-testid="stSelectbox"] > div { background: #1a2636; border-color: #2a3f55; }
  .status-card {
    background: #1a2636;
    border: 1px solid #2a3f55;
    border-radius: 10px;
    padding: 10px 16px;
    text-align: center;
    font-size: 0.9rem;
    color: #e8edf2;
    margin: 6px 0;
  }
  .score-card {
    background: #1a2636;
    border: 1px solid #2a3f55;
    border-radius: 10px;
    padding: 12px;
    text-align: center;
  }
  .p1-name { color: #e8b44a; font-weight: 700; font-size: 1rem; }
  .p2-name { color: #4aa8e8; font-weight: 700; font-size: 1rem; }
  .score-num { font-size: 1.8rem; font-weight: 700; }
  .perf-tag {
    background: #1a2636;
    border: 1px solid #2a3f55;
    border-radius: 8px;
    padding: 5px 12px;
    font-size: 0.78rem;
    color: #6b8099;
    text-align: center;
    margin-top: 4px;
  }
  .win-banner {
    background: linear-gradient(135deg, #1a2636, #152230);
    border: 1px solid #e8b44a;
    border-radius: 12px;
    padding: 18px;
    text-align: center;
    font-size: 1.3rem;
    font-weight: 700;
    color: #e8b44a;
    margin: 8px 0;
  }
  h1 { color: #e8b44a !important; text-align: center; }
  .subtitle { text-align: center; color: #6b8099; font-size: 0.85rem; margin-top: -10px; margin-bottom: 16px; }
  /* masquer header Streamlit */
  header[data-testid="stHeader"] { display: none; }
  footer { display: none; }
</style>
""", unsafe_allow_html=True)

# ── Initialisation ───────────────────────────────────────────
if "board" not in st.session_state:
    st.session_state.mode       = "Humain vs IA"
    st.session_state.difficulty = "Moyen"
    st.session_state.scores     = [0, 0]
    init_state()

s = st.session_state

# ── En-tête ──────────────────────────────────────────────────
st.markdown("# ♟ Fanoron-telo")
st.markdown('<p class="subtitle"><a href="https://www.ispm-edu.com" style="color:#6b8099;text-decoration:none;">Institut Supérieur Polytechnique de Madagascar</a></p>', unsafe_allow_html=True)

# ── Sidebar – configuration ──────────────────────────────────
with st.sidebar:
    st.markdown("### ⚙️ Configuration")
    mode = st.selectbox("Mode de jeu", ["Humain vs Humain", "Humain vs IA", "IA vs IA"], index=1,
                        key="mode_select")
    if mode != "Humain vs Humain":
        diff = st.selectbox("Difficulté IA", ["Facile", "Moyen", "Difficile"], index=1,
                            key="diff_select")
    else:
        diff = "Moyen"

    if st.button("▶ Nouvelle partie"):
        s.mode       = mode
        s.difficulty = diff
        s.scores     = [0, 0]
        init_state()
        st.rerun()

    if st.button("↩ Undo"):
        undo()
        st.rerun()

    st.markdown("---")
    st.markdown("### 📖 Règles")
    st.markdown("""
**Phase 1 – Placement**  
Posez vos 3 pions tour à tour.  
Aligner 3 pions = victoire immédiate.

**Phase 2 – Mouvement**  
Déplacez un pion vers une case adjacente libre.  
Premier à aligner 3 pions gagne.  
Sans coup possible = défaite.
    """)

# ── Scoreboard ───────────────────────────────────────────────
names = _player_names()
col1, col2, col3 = st.columns([2, 1, 2])
with col1:
    active = "✦ " if s.current == P1 and not s.winner else ""
    st.markdown(
        f'<div class="score-card"><div class="p1-name">{active}{names[0]}</div>'
        f'<div class="score-num" style="color:#e8b44a">{s.scores[0]}</div></div>',
        unsafe_allow_html=True,
    )
with col2:
    st.markdown('<div style="display:flex;align-items:center;justify-content:center;height:80px;color:#6b8099;font-weight:700;">VS</div>', unsafe_allow_html=True)
with col3:
    active = "✦ " if s.current == P2 and not s.winner else ""
    st.markdown(
        f'<div class="score-card"><div class="p2-name">{active}{names[1]}</div>'
        f'<div class="score-num" style="color:#4aa8e8">{s.scores[1]}</div></div>',
        unsafe_allow_html=True,
    )

# ── Bannière victoire ─────────────────────────────────────────
if s.winner:
    st.markdown(
        f'<div class="win-banner">🏆 {names[s.winner-1]} remporte la partie !</div>',
        unsafe_allow_html=True,
    )
    if st.button("🔄 Rejouer"):
        init_state()
        st.rerun()

# ── Status ────────────────────────────────────────────────────
st.markdown(f'<div class="status-card">{s.status_msg}</div>', unsafe_allow_html=True)

# ── Plateau : 9 boutons dans grille 3×3 ──────────────────────
st.markdown("**Plateau :**")

PIECE_DISPLAY = {EMPTY: "·", P1: "🟡", P2: "🔵"}

for row in range(3):
    cols = st.columns(3)
    for col in range(3):
        idx = row * 3 + col
        p   = s.board[idx]
        is_selected = (s.selected == idx)
        is_legal    = (idx in (ADJ[s.selected] if s.selected >= 0 else []) and p == EMPTY and s.phase == 2)

        label_map = {EMPTY: "·", P1: "🟡", P2: "🔵"}
        label = label_map[p]
        if is_selected:
            label = "⭕"
        elif is_legal:
            label = "🟢"

        with cols[col]:
            if st.button(label, key=f"cell_{idx}", disabled=(bool(s.winner))):
                human_click(idx)
                # Après coup humain, vérifier si IA doit jouer
                if not s.winner:
                    if s.mode == "Humain vs IA" and s.current == P2:
                        ai_play()

# ── IA vs IA – bouton suivant ─────────────────────────────────
if s.mode == "IA vs IA" and not s.winner:
    if st.button("▶ Coup IA suivant"):
        ai_play()
        st.rerun()
    # Auto-play
    if st.button("⏩ Jouer jusqu'à la fin"):
        max_moves = 50
        count = 0
        while not s.winner and not is_terminal(s.board, s.current, s.phase) and count < max_moves:
            ai_play()
            count += 1
        st.rerun()

# ── Performance IA ─────────────────────────────────────────────
if s.ai_time_ms is not None and s.mode != "Humain vs Humain":
    st.markdown(
        f'<div class="perf-tag">⏱ Temps IA dernier coup : <b>{s.ai_time_ms:.2f} ms</b> '
        f'(niveau {s.difficulty}, profondeur {DEPTH_MAP[s.difficulty]})</div>',
        unsafe_allow_html=True,
    )

# ── Représentation ASCII du plateau ──────────────────────────
st.markdown("---")
with st.expander("🗺 Représentation ASCII + infos internes"):
    b = s.board
    sym = {EMPTY: ".", P1: "X", P2: "O"}
    ascii_board = f"""
    ```
    Plateau (X=J1/🟡, O=J2/🔵, .=vide)
    
       a    b    c
    3  {sym[b[0]]} -- {sym[b[1]]} -- {sym[b[2]]}
       |\\  |  /|
    2  {sym[b[3]]} -- {sym[b[4]]} -- {sym[b[5]]}
       |/  |  \\|
    1  {sym[b[6]]} -- {sym[b[7]]} -- {sym[b[8]]}
    
    Phase    : {s.phase}  |  Tour : Joueur {s.current}
    Placés   : J1={s.placed[0]}/3  J2={s.placed[1]}/3
    Sélect.  : case {s.selected}
    Historiq.: {len(s.history)} coups
    ```
    """
    st.markdown(ascii_board)

    # Détail des coups légaux
    moves = get_moves(s.board, s.current, s.phase, s.placed)
    move_strs = []
    for m in moves:
        if m["type"] == "place":
            move_strs.append(f"pose→{LABELS[m['to']]}")
        else:
            move_strs.append(f"{LABELS[m['from']]}→{LABELS[m['to']]}")
    st.code(f"Coups légaux ({len(moves)}) : {', '.join(move_strs)}")

# ── Footer ────────────────────────────────────────────────────
st.markdown('<div style="text-align:center;color:#3a5570;font-size:0.75rem;margin-top:20px;">ISPM Madagascar · Algorithmique Avancée · Fanoron-telo avec IA</div>', unsafe_allow_html=True)

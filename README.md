# ♟ Fanoron-telo avec IA – Python + Streamlit

**[Institut Supérieur Polytechnique de Madagascar](https://www.ispm-edu.com)**  
**Hackathon Algorithmique Avancée – Travaux Pratiques**

---

## 👥 Équipe

| Nom Complet | N° | Classe | Rôle |
|---|---|---|---|
| SANTATRINIAINA Feno Nasandratra | 57 | IGGIA4 | Interface Streamlit, gestion `session_state`, Undo/Redo, CSS, Git & déploiement |
| RATSARAFARA Jean Antoinnet | 53 | IGGIA4 | Moteur de jeu, IA Minimax + Alpha-Bêta, heuristique, tests & optimisation |

---

## 📖 Description

Application web du jeu **Fanoron-telo** (3×3) avec intelligence artificielle, développée en **Python pur + Streamlit**, sans aucune bibliothèque de jeu externe.

Le jeu se joue en deux phases successives :
1. **Phase 1 – Placement** : chaque joueur pose à tour de rôle ses **3 pions** sur des cases vides du plateau
2. **Phase 2 – Mouvement** : les joueurs déplacent leurs pions vers des cases **adjacentes vides**

> La phase 2 démarre automatiquement dès que les 6 pions (3 par joueur) ont été posés.

Le premier joueur à **aligner 3 pions** sur une ligne, colonne ou diagonale gagne. Un joueur qui n'a plus aucun mouvement légal perd également.

---

## ✅ Fonctionnalités

| Fonctionnalité | Statut |
|---|---|
| Mode Humain vs Humain | ✅ |
| Mode Humain vs IA (Facile / Moyen / Difficile) | ✅ |
| Mode IA vs IA (démo pas-à-pas ou automatique 10 coups) | ✅ |
| Phase 1 Placement + Phase 2 Mouvement (transition automatique) | ✅ |
| Minimax + Alpha-Bêta + Iterative Deepening | ✅ |
| Table de transposition (dict Python natif) | ✅ |
| Move Ordering (tri par évaluation avant récursion) | ✅ |
| Undo (annulation de coup) | ✅ |
| Redo (rétablissement de coup) | ✅ |
| Historique complet de la partie | ✅ |
| Bannière de score persistante entre les parties | ✅ |
| Métriques IA (temps de calcul, nœuds explorés, total accumulé) | ✅ |
| Interface responsive Desktop + Mobile | ✅ |
| Vue ASCII de débogage (plateau + joueur courant) | ✅ |
| Affichage des coups légaux en temps réel | ✅ |

---

## 🗂 Architecture du projet

```
fanoron-streamlit/
├── app.py           # Interface Streamlit : UI, callbacks, CSS Neon-Dark, sidebar
├── game.py          # Moteur de jeu : plateau, règles, ADJ, Undo/Redo, historique
├── minimax.py       # IA : Minimax, Alpha-Bêta, Iterative Deepening, heuristique
├── ai.py            # Wrapper IA : sélection de stratégie par niveau de difficulté
├── utils.py         # Utilitaires : ASCII board, labels de coups (a1–c3)
├── assets/
│   └── style.css    # Placeholder CSS (thème dark injecté directement dans app.py)
├── requirements.txt # Dépendances Python (streamlit>=1.32.0)
└── README.md
```

---

## 🚀 Installation & Lancement

```bash
git clone https://github.com/santatri/fanorona-ia-Santatra-Antoinnet.git
cd fanorona-ia-Santatra-Antoinnet
pip install -r requirements.txt
py -m streamlit run app.py
```

> Ouvre automatiquement **http://localhost:8501** dans le navigateur.

**Version en ligne :** https://fanoron-ai.streamlit.app/

---

## 🎮 Guide d'utilisation réel

### 1. Sidebar – Configuration

La barre latérale (⚙️ Configuration) contient tous les contrôles de jeu :

| Contrôle | Description |
|---|---|
| **Mode de jeu** | `👥 Humain vs Humain` · `🤖 Humain vs IA` · `🤖 IA vs IA` |
| **Difficulté IA** | `🟢 Facile` · `🟡 Moyen` · `🔴 Difficile` (visible si IA impliquée) |
| **🔄 Nouvelle** | Relance une partie (conserve les scores) |
| **↩ Annuler** | Annule le dernier coup (Undo) |
| **↪ Refaire** | Rétablit le coup annulé (Redo) |
| **🗑 Reset Absolu** | Réinitialise tout, scores inclus |
| **📊 Performances IA** | Affiche le temps de calcul (ms), nœuds visités, total accumulé |

### 2. Plateau de jeu – Phase 1 (Placement)

- Cliquer sur **n'importe quelle case vide** pour y poser un pion
- Les pions X (cyan `✖`) appartiennent au Joueur 1, les pions O (violet `〇`) au Joueur 2
- La phase se termine dès que chaque joueur a posé ses **3 pions**

### 3. Plateau de jeu – Phase 2 (Mouvement)

1. **Cliquer sur son propre pion** pour le sélectionner (mise en surbrillance)
2. Les **cases accessibles** s'affichent avec un point doré `●`
3. **Cliquer sur une case cible** pour déplacer le pion
4. Cliquer à nouveau sur un pion sélectionné le **désélectionne**
5. Cliquer sur une case non valide **réinitialise la sélection**

### 4. Mode IA vs IA

- **▶ Exécuter le coup IA** : fait jouer l'IA courante d'un seul coup
- **⏩ Automatiser (10 coups)** : enchaîne automatiquement 10 coups  
  *(version mobile : bouton "Auto 5" = 5 coups)*

### 5. Panneau droit (Desktop uniquement)

- **📜 Historique de la partie** : 8 derniers coups joués avec descriptions textuelles
- **📋 Actions légales disponibles** : liste de tous les coups légaux du joueur courant au format `a1 → b2`

### 6. Vue ASCII (développeur)

En bas de page, l'expander **🗺 Vue Terminal Matrix (ASCII)** affiche :
```
0---1---2
|\ /|\ /|
| X | . | O |
|/ \|/ \|
3---4---5
...
```
Avec le joueur courant et le nombre de pions posés.

### 7. Nommage des cases

```
a1 | b1 | c1
a2 | b2 | c2
a3 | b3 | c3
```

---

## 🧠 Modélisation et Algorithmes IA

### Représentation du plateau (`game.py`)

```python
board = [0] * 9   # 0=vide, 1=Joueur 1 (✖), 2=Joueur 2 (〇)

# Index :
# 0(a1) | 1(b1) | 2(c1)
# ----------------------
# 3(a2) | 4(b2) | 5(c2)
# ----------------------
# 6(a3) | 7(b3) | 8(c3)
```

**Lignes gagnantes :**
```python
WIN_LINES = [
    (0,1,2), (3,4,5), (6,7,8),   # horizontales
    (0,3,6), (1,4,7), (2,5,8),   # verticales
    (0,4,8), (2,4,6),             # diagonales
]
```

**Adjacences réelles (diagonales via le centre uniquement) :**
```python
ADJ = {
    0: [1,3,4],      # coins : connectés à leurs voisins + centre
    1: [0,2,4],      # bords : connectés aux cases adjacentes + centre
    2: [1,5,4],
    3: [0,6,4],
    4: [0,1,2,3,5,6,7,8],  # centre : connecté à TOUTES les cases
    5: [2,8,4],
    6: [3,7,4],
    7: [6,8,4],
    8: [5,7,4],
}
```

### Minimax + Alpha-Bêta + Iterative Deepening (`minimax.py`)

L'IA utilise **Iterative Deepening** : elle approfondit la recherche de profondeur 1 à `max_depth`, en retournant le meilleur coup trouvé avant expiration du temps :

```python
for current_depth in range(1, max_depth + 1):
    for move in moves_ordered_by_evaluation:
        score = minimax(child, depth-1, False, perspective, alpha, beta, ...)
    if elapsed > time_limit:
        break
return best_move, total_nodes
```

**Table de transposition :** les états `(tuple(board), current_player, phase)` déjà évalués à profondeur ≥ requise sont réutilisés directement.

### Heuristique d'évaluation (`minimax.py` → `evaluate()`)

| Signal | Phase 1 | Phase 2 |
|---|---|---|
| 2 pions IA en ligne (case vide) | +80 | +150 |
| 2 pions adversaire en ligne (case vide) | -100 | -200 |
| 1 pion IA en ligne | +10 | +10 |
| 1 pion adversaire en ligne | -8 | -8 |
| Contrôle du centre (case 4) | +15 | +15 |
| Défaite de l'adversaire | +10 000 | +10 000 |
| Propre défaite | -10 000 | -10 000 |

### Niveaux de difficulté (`ai.py`)

| Niveau | Stratégie | Profondeur max | Limite de temps |
|---|---|---|---|
| **Facile** | Coup aléatoire (`random.choice`) | — | — |
| **Moyen** | Minimax + Alpha-Bêta + ID | 4 | 0,2 s |
| **Difficile** | Minimax + Alpha-Bêta + ID | 15 | 0,8 s |

### Techniques avancées

| Technique | Fichier | Détail |
|---|---|---|
| Alpha-Bêta pruning | `minimax.py` | Élagage `beta <= alpha` |
| Table de transposition | `minimax.py` | `dict[(board, player, phase)] = (val, depth)` |
| Iterative Deepening | `minimax.py` | Boucle profondeur 1 → `max_depth` |
| Move Ordering | `minimax.py` | Tri par `evaluate()` avant récursion |
| Limite de temps | `minimax.py` | `time.perf_counter()` vs `time_limit` |
| Randomisation | `ai.py` | `random.choice(moves)` niveau Facile |

---

## 📊 Performances mesurées

Mesuré avec `time.perf_counter()` (précision sous-milliseconde) :

| Niveau | Temps moyen / coup |
|---|---|
| Facile | < 1 ms |
| Moyen | 50 – 200 ms |
| Difficile | 200 – 800 ms |

**IA Difficile vs IA Difficile :** 100 % de nuls (jeu parfait avec Alpha-Bêta complet).  
**IA Difficile vs IA Facile :** victoire IA Difficile dans ~95 % des cas.

---

## 🛠 Stack technique

- **Langage :** Python 3.10+
- **Interface :** Streamlit ≥ 1.32.0 — `session_state` pour l'état du jeu
- **IA :** Minimax + Alpha-Bêta + Iterative Deepening — **zéro dépendance externe**
- **Style :** CSS injecté via `st.markdown()` — thème Neon-Dark, glassmorphism, responsive

---

## 🤖 Outils IA utilisés

- **Claude (Anthropic)** : Architecture Minimax, gestion du `session_state`, CSS personnalisé
- **GitHub Copilot** : Auto-complétion des fonctions récursives

Gain estimé : **~60 % du temps de développement**.


*ISPM Madagascar · Algorithmique Avancée · Hackathon 2026*

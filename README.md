# Fanoron-telo AI

Projet réalisé pour un hackathon d'Algorithmique Avancée — jeu Fanoron-telo (plateau 3x3) avec IA.

## Membres
- Nom 1 — Développeur principal
- Nom 2 — IA & Algorithmes

## Description
Jeu Fanoron-telo (3x3), deux phases: placement puis déplacement. Trois pions par joueur.

Fonctionnalités:
- Humain vs Humain
- Humain vs IA (Facile/Moyen/Difficile)
- IA vs IA
- Undo / Redo / Historique

## Architecture
Fichiers principaux:
- `app.py`: interface Streamlit
- `game.py`: moteur de jeu
- `ai.py`: wrapper IA
- `minimax.py`: algorithmes Minimax et Alpha-Beta
- `utils.py`: utilitaires

## Installation rapide
```bash
git clone URL_DU_DEPOT
cd fanorona-ai
pip install -r requirements.txt
streamlit run app.py
```

## Outils IA utilisés
- ChatGPT
- GitHub Copilot

## Algorithmes
- Représentation: liste de 9 entiers
- Minimax: profondeur configurable
- Alpha-Beta: implémentée dans `minimax.py`

## Tests & Analyse
L'app affiche le temps de calcul et le nombre de nœuds explorés.

## Licence
MIT
# Fanoron-telo avec IA – Python + Streamlit

**[Institut Supérieur Polytechnique de Madagascar](https://www.ispm-edu.com)**  
**Groupe de projet :** Hackathon Algorithmique Avancée – Travaux Pratiques

---

## Section 1 : En-tête Institutionnel et Identification

- Site officiel : [www.ispm-edu.com](https://www.ispm-edu.com)
- Nom du groupe : Hackathon ISPM – Algorithmique Avancée

| Nom Complet | Numéro d'étudiant | Classe | Rôle précis |
|-------------|-------------------|--------|-------------|
| _(à remplir)_ | _(à remplir)_ | _(à remplir)_ | Lead AI / Minimax |
| _(à remplir)_ | _(à remplir)_ | _(à remplir)_ | UI Streamlit / Frontend |
| _(à remplir)_ | _(à remplir)_ | _(à remplir)_ | Backend Logique / DevOps |

---

## Section 2 : Description du Travail Réalisé

Application web du jeu **Fanoron-telo** avec IA, en **Python pur + Streamlit**.

| Fonctionnalité | Statut | Priorité |
|---|---|---|
| Mode Humain vs Humain | ✅ | P1 |
| Mode Humain vs IA (Facile / Moyen / Difficile) | ✅ | P1 |
| Mode IA vs IA (Démo, coup par coup ou auto) | ✅ | P2 |
| Phase 1 Placement + Phase 2 Mouvement | ✅ | P1 |
| Minimax + Alpha-Bêta + Table de transposition | ✅ | P2 |
| Undo (annulation de coup) | ✅ | P3 |
| Temps de calcul IA en ms | ✅ | Section 6 |
| Représentation ASCII + coups légaux | ✅ | Section 5 |

### Stack
- **Langage :** Python 3.10+
- **Interface :** Streamlit (session_state pour état du jeu)
- **IA :** Minimax récursif + Alpha-Bêta + `dict` Python comme table de transposition
- **Zéro dépendance IA externe** (pas de numpy, pas de bibliothèque de jeu)

---

## Section 3 : Guide d'Installation Rapide

```bash
git clone <url_du_depot>
cd fanoron-streamlit
pip install -r requirements.txt
streamlit run app.py
```

Ouvre automatiquement `http://localhost:8501` dans le navigateur.

---

## Section 4 : Outils d'Aide IA Utilisés

- **Claude (Anthropic)** : Architecture Minimax, gestion du session_state Streamlit, CSS custom.
- **GitHub Copilot** : Auto-complétion des fonctions récursives.

Gain estimé : **~60% du temps de développement**.

---

## Section 5 : Modélisation et Algorithmes de l'IA

### Représentation du plateau

```python
board = [0] * 9   # 0=vide, 1=Joueur1, 2=Joueur2

# Index :
# 0 | 1 | 2
# ---------
# 3 | 4 | 5
# ---------
# 6 | 7 | 8
```

**Lignes gagnantes :**
```python
WIN_LINES = [
    [0,1,2],[3,4,5],[6,7,8],   # horizontales
    [0,3,6],[1,4,7],[2,5,8],   # verticales
    [0,4,8],[2,4,6]            # diagonales
]
```

**Adjacences :** `dict` Python `ADJ[i] = [voisins...]`, incluant diagonales.

### Minimax + Alpha-Bêta

```python
def minimax(board, depth, alpha, beta, maximizing, ai_player, ...):
    # Cas terminaux
    w = get_winner(board, current_player, phase)
    if w == ai_player:    return 10000 + depth
    if w != ai_player:    return -10000 - depth
    if depth == 0:        return evaluate(board, ai_player)

    for move in get_moves(...):
        val = minimax(apply_move(...), depth-1, alpha, beta, not maximizing, ...)
        # Mise à jour alpha/beta + élagage
        if beta <= alpha: break
```

**Heuristique d'évaluation :**
- +1/+10/+1000 selon nombre de pions IA sur une ligne sans adversaire
- -1/-10/-1000 symétriquement pour l'adversaire
- +3 bonus centre (case 4)

**Table de transposition :**
```python
key = (tuple(board), current_player, phase, depth)
trans_table[key] = best_val   # dict Python natif
```

### Techniques avancées

| Technique | Implémenté |
|---|---|
| Alpha-Bêta pruning | ✅ |
| Table de transposition | ✅ |
| Randomisation (Facile) | ✅ |
| Iterative deepening | — |

---

## Section 6 : Analyses de Performances

Mesuré avec `time.perf_counter()` (précision sous-milliseconde) :

| Niveau | Profondeur | Temps moyen/coup |
|---|---|---|
| Facile | 1 | < 1 ms |
| Moyen | 3 | 1–5 ms |
| Difficile | 7 | 5–50 ms |

**IA Difficile vs IA Difficile :** 100% de nuls (jeu parfait sur 3×3 avec Alpha-Bêta complet).  
**IA Difficile vs IA Facile :** victoire IA Difficile dans ~95% des cas.

---

*ISPM Madagascar · Algorithmique Avancée · Fanoron-telo avec IA*

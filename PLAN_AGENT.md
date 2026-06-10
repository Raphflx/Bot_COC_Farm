# Plan détaillé — Agent Claude Code pour Bot CoC

## Prérequis avant de lancer l'agent

```bash
# 1. Installer Claude Code
npm install -g @anthropic-ai/claude-code

# 2. Se connecter
claude login

# 3. Se placer dans le projet
cd /chemin/vers/Bot_COC

# 4. Lancer l'agent
claude
```

---

## Phase 1 — Setup de l'environnement ADB

**Objectif :** Python peut se connecter à BlueStacks, prendre un screenshot et simuler un clic.

### Prompt à donner à l'agent

```
Crée la structure complète du projet selon CLAUDE.md.
Ensuite implémente src/adb/controller.py avec une classe ADBController qui :
- Se connecte à BlueStacks sur 127.0.0.1:5555
- Prend un screenshot et le retourne comme image numpy (OpenCV)
- Simule un tap aux coordonnées (x, y) avec un délai aléatoire
- Simule un swipe entre deux points
- Logue toutes les actions avec le module logging

Crée aussi requirements.txt avec toutes les dépendances nécessaires.
Crée tests/test_adb.py avec des tests unitaires mockant ADB.
```

### Fichiers attendus après cette phase
```
src/adb/__init__.py
src/adb/controller.py
requirements.txt
tests/test_adb.py
```

### Validation
```bash
pip install -r requirements.txt
pytest tests/test_adb.py -v
adb connect 127.0.0.1:5555 && python -c "from src.adb.controller import ADBController; print('OK')"
```

---

## Phase 2 — Reconnaissance visuelle OpenCV

**Objectif :** Détecter les éléments du jeu (collecteurs pleins, bouton Attaquer, etc.)

### Prompt à donner à l'agent

```
Implémente src/vision/detector.py avec une classe VisionDetector qui :
- Prend un screenshot numpy en entrée
- Fait du template matching OpenCV avec un seuil configurable (défaut 0.85)
- Expose ces méthodes :
    find(template_name) -> (x, y) | None
    find_all(template_name) -> list[(x, y)]
    is_visible(template_name) -> bool
- Charge les templates PNG depuis src/vision/templates/
- Logue les détections avec leur score de confiance

Crée des templates PNG placeholder (10x10 pixels rouge) pour :
- gold_collector_full.png
- elixir_collector_full.png
- attack_button.png
- next_button.png
- deploy_zone.png

Crée tests/test_vision.py avec des tests utilisant de vraies images de test.
```

### Fichiers attendus
```
src/vision/__init__.py
src/vision/detector.py
src/vision/templates/gold_collector_full.png
src/vision/templates/elixir_collector_full.png
src/vision/templates/attack_button.png
src/vision/templates/next_button.png
src/vision/templates/deploy_zone.png
tests/test_vision.py
```

### Validation
```bash
pytest tests/test_vision.py -v
```

---

## Phase 3a — Farming automatique

**Objectif :** Collecter automatiquement or, élixir et élixir sombre.

### Prompt à donner à l'agent

```
Implémente src/bot/farming.py avec une classe FarmingBot qui :
- Utilise ADBController et VisionDetector
- Détecte les collecteurs pleins (gold, elixir, dark elixir)
- Clique dessus pour collecter avec délais aléatoires entre chaque
- Attend que l'animation de collecte soit terminée avant de passer au suivant
- Retourne un rapport : {gold: X, elixir: Y, dark_elixir: Z}
- Gère le cas où aucun collecteur n'est plein

Implémente aussi src/bot/state.py avec une machine à états simple :
- États : IDLE, FARMING, ATTACKING, WAITING, ERROR
- Transitions entre états
- Log de chaque changement d'état
```

### Fichiers attendus
```
src/bot/__init__.py
src/bot/farming.py
src/bot/state.py
tests/test_farming.py
```

---

## Phase 3b — Attaque automatique

**Objectif :** Rechercher une base, déployer les troupes, récupérer les ressources.

### Prompt à donner à l'agent

```
Implémente src/bot/attack.py avec une classe AttackBot qui :
- Clique sur le bouton "Attaquer"
- Clique sur "Trouver une correspondance" pour chercher une base
- Vérifie si les ressources de la base dépassent les seuils configurés
  (config: farming.min_gold, farming.min_elixir)
- Si oui : déploie les troupes en ligne horizontale sur le bord de la carte
- Si non : clique "Suivant" et recommence (max 10 tentatives)
- Attend la fin du combat (détection de l'écran de résultats)
- Retourne les ressources pillées

Gère les erreurs : connexion perdue, jeu crashé, troupes insuffisantes.
```

---

## Phase 3c — Notifications

**Objectif :** Alertes Discord/Telegram après chaque session.

### Prompt à donner à l'agent

```
Implémente src/notifications/notifier.py avec une classe Notifier qui :
- Lit discord_webhook et telegram_token / telegram_chat_id depuis config.json
- Méthode send(message: str) qui envoie sur Discord ET Telegram si configurés
- Méthode send_report(session_stats: dict) qui formate un rapport lisible :
    "Session terminée : +150k or, +200k élixir, 3 attaques gagnées"
- Gère les erreurs réseau sans crasher le bot principal
- Désactivée silencieusement si les webhooks ne sont pas configurés
```

---

## Phase 4 — Boucle principale + robustesse

**Objectif :** Assembler tout en un bot stable qui tourne en autonomie.

### Prompt à donner à l'agent

```
Crée main.py qui :
1. Charge config.json (avec validation des champs requis)
2. Initialise ADBController, VisionDetector, FarmingBot, AttackBot, Notifier
3. Vérifie la connexion ADB au démarrage — arrêt propre si échec
4. Lance la boucle principale :
   - Farming si farming.enabled = true
   - Attaque si attack.enabled = true et trophées < attack.max_trophies
   - Pause aléatoire entre les cycles (config: loop_delay_min / max)
   - Envoi d'un rapport toutes les X minutes (config: report_interval_minutes)
5. Gère les exceptions :
   - Reconnexion ADB automatique si connexion perdue
   - Redémarrage BlueStacks si le jeu crashe (via subprocess)
   - Arrêt propre sur Ctrl+C avec rapport final

Crée config.example.json complet avec tous les champs et leurs valeurs par défaut.
Crée un système de logs rotatifs dans logs/ (max 5 fichiers de 1MB).
```

---

## Commandes agent utiles pendant le développement

```bash
# Demander à l'agent de débugger un problème spécifique
"Le template matching ne trouve pas le bouton Attaquer, 
 voici le screenshot : [glisser l'image]. Ajuste le seuil ou le template."

# Demander à l'agent d'ajouter un nouveau template
"Ajoute la détection du bouton 'Retour au village' après une attaque."

# Demander un refactor
"Refactorise farming.py pour supporter l'élixir sombre en plus de l'or et l'élixir."

# Lancer tous les tests
"Lance les tests et corrige les erreurs."
```

---

## Structure finale du projet

```
Bot_COC/
├── CLAUDE.md
├── PLAN_AGENT.md
├── README.md
├── LICENSE
├── .gitignore
├── main.py
├── requirements.txt
├── config.example.json
├── config.json              ← gitignorée
├── src/
│   ├── adb/controller.py
│   ├── vision/detector.py
│   ├── vision/templates/*.png
│   ├── bot/farming.py
│   ├── bot/attack.py
│   ├── bot/state.py
│   └── notifications/notifier.py
├── tests/
│   ├── test_adb.py
│   ├── test_vision.py
│   └── test_farming.py
└── logs/                    ← gitignorée
```

---

## Tips pour travailler avec l'agent Claude Code

- **Un prompt = une phase.** Ne pas tout demander d'un coup.
- **Montrer des screenshots** quand la détection OpenCV échoue — glisser l'image dans le terminal.
- **Après chaque phase**, lancer les tests avant de passer à la suivante.
- **Si l'agent dévie**, lui rappeler : "Consulte CLAUDE.md pour les conventions."
- **Pour les coordonnées**, toujours préciser la résolution BlueStacks utilisée (1280x720).

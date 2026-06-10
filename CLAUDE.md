# CLAUDE.md — Bot Clash of Clans

## Contexte du projet

Bot d'automatisation pour Clash of Clans tournant via BlueStacks sur Windows.
L'agent contrôle le jeu par ADB (Android Debug Bridge) et OpenCV pour la vision.

**Stack :** Python 3.10+ · OpenCV · ADB · PyAutoGUI · BlueStacks 5

---

## Architecture du projet

```
Bot_COC/
├── CLAUDE.md
├── README.md
├── LICENSE
├── .gitignore
├── config.example.json      # Template de config (jamais de vraies valeurs ici)
├── config.json              # Config locale (gitignorée)
├── main.py                  # Point d'entrée — boucle principale
├── requirements.txt
│
├── src/
│   ├── adb/
│   │   ├── __init__.py
│   │   └── controller.py    # Connexion ADB, screenshot, tap, swipe
│   │
│   ├── vision/
│   │   ├── __init__.py
│   │   ├── detector.py      # Détection OpenCV (template matching)
│   │   └── templates/       # Images de référence (.png)
│   │
│   ├── bot/
│   │   ├── __init__.py
│   │   ├── farming.py       # Logique de farming (collecteurs, mines)
│   │   ├── attack.py        # Logique d'attaque (recherche base, déploiement)
│   │   └── state.py         # Machine à états du bot
│   │
│   └── notifications/
│       ├── __init__.py
│       └── notifier.py      # Discord / Telegram webhooks
│
├── tests/
│   ├── test_adb.py
│   ├── test_vision.py
│   └── test_farming.py
│
└── logs/                    # Gitignorés
```

---

## Conventions de code

- **Python** : snake_case pour les variables et fonctions, PascalCase pour les classes
- **Imports** : absolus uniquement (`from src.adb.controller import ADBController`)
- **Typage** : annotations de type obligatoires sur toutes les fonctions publiques
- **Docstrings** : Google style sur toutes les classes et méthodes publiques
- **Logs** : utiliser `logging` standard, jamais `print()` en production
- **Config** : toutes les valeurs configurables passent par `config.json`, jamais hardcodées

---

## Règles importantes

### Sécurité
- Ne jamais écrire de vraies valeurs (tokens, IDs) dans le code ou dans `config.example.json`
- `config.json` est gitignorée — toujours vérifier avant un commit
- Les screenshots temporaires vont dans `screenshots/` (gitignorée)

### ADB / BlueStacks
- BlueStacks expose ADB sur `127.0.0.1:5555` par défaut
- Toujours vérifier la connexion ADB avant de lancer le bot (`adb devices`)
- Les coordonnées de clic dépendent de la résolution BlueStacks (1280x720 par défaut)
- Ajouter un délai aléatoire entre chaque action (`random.uniform(0.5, 1.5)`)

### OpenCV
- Les templates PNG sont en `src/vision/templates/`
- Seuil de confiance par défaut : `0.85` — ajuster par template
- Toujours vérifier que le screenshot est bien chargé avant de lancer la détection

### Anti-ban
- Délais aléatoires obligatoires entre toutes les actions
- Ne jamais faire tourner le bot plus de 6h d'affilée
- Simuler des pauses humaines (variation de vitesse de clic)

---

## Commandes utiles

```bash
# Vérifier la connexion BlueStacks
adb connect 127.0.0.1:5555
adb devices

# Lancer le bot
python main.py

# Lancer les tests
pytest tests/ -v

# Prendre un screenshot manuel via ADB
adb exec-out screencap -p > screenshot.png
```

---

## État d'avancement

- [ ] Phase 1 — Connexion ADB + screenshot + tap
- [ ] Phase 2 — Détection OpenCV (ressources, boutons)
- [ ] Phase 3 — Farming automatique
- [ ] Phase 3 — Attaque automatique
- [ ] Phase 3 — Notifications Discord/Telegram
- [ ] Phase 4 — Anti-ban + gestion d'erreurs + logs

---

## Ce que l'agent NE doit PAS faire

- Modifier `config.json` (fichier local, gitignorée)
- Hardcoder des coordonnées sans commentaire expliquant la résolution cible
- Utiliser `time.sleep()` avec une valeur fixe — toujours `random.uniform()`
- Commiter des fichiers dans `screenshots/` ou `logs/`

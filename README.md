# 🏰 CoC Bot

Bot d'automatisation pour Clash of Clans via BlueStacks, développé en Python.

## Fonctionnalités

- **Farming automatique** — collecte d'or, d'élixir et d'élixir sombre
- **Attaque automatique** — recherche de bases et déploiement des troupes
- **Notifications** — alertes Discord / Telegram via webhooks

## Stack technique

| Outil | Rôle |
|-------|------|
| Python 3.10+ | Langage principal |
| OpenCV | Reconnaissance visuelle (détection d'éléments) |
| ADB (Android Debug Bridge) | Contrôle de BlueStacks |
| PyAutoGUI | Simulation de clics et saisie clavier |
| BlueStacks | Émulateur Android |

## Prérequis

- [BlueStacks 5](https://www.bluestacks.com/) installé
- [ADB](https://developer.android.com/tools/adb) disponible dans le PATH
- Python 3.10+

## Installation

```bash
# Cloner le repo
git clone https://github.com/TON_USERNAME/coc-bot.git
cd coc-bot

# Créer un environnement virtuel
python -m venv venv
source venv/bin/activate  # Windows : venv\Scripts\activate

# Installer les dépendances
pip install -r requirements.txt
```

## Configuration

Copie le fichier d'exemple et remplis tes valeurs :

```bash
cp config.example.json config.json
```

```json
{
  "adb_port": 5555,
  "discord_webhook": "",
  "telegram_token": "",
  "telegram_chat_id": "",
  "farming": {
    "enabled": true,
    "min_gold": 100000,
    "min_elixir": 100000
  },
  "attack": {
    "enabled": false,
    "max_trophies": 1200
  }
}
```

## Utilisation

```bash
python main.py
```

## Avertissement

Ce bot est un projet éducatif. L'utilisation de bots dans Clash of Clans est contraire aux conditions d'utilisation de Supercell et peut entraîner un ban de ton compte. Utilise-le à tes propres risques.

## Licence

MIT — voir [LICENSE](LICENSE)

# 📝 Agent de Productivité Atlas

Un agent conversationnel intelligent avec **mémoire longue** capable de sauvegarder, lire et supprimer des notes de façon permanente.

## ✨ Fonctionnalités
- **Mémoire longue** : Les notes sont sauvegardées dans `notes.json` et persistent après redémarrage
- **7 outils intégrés** :
  - `ajouter_note` : Sauvegarde une note
  - `lire_notes` : Affiche toutes les notes
  - `supprimer_note` : Supprime une note par ID
  - `calculer` : Calculs mathématiques
  - `heure_actuelle` : Heure et date
  - `rechercher_internet` : Recherche via DuckDuckGo
  - `rechercher_wikipedia` : Informations via Wikipedia
- **Gestion d'erreurs robuste** : Rate limits, modèles indisponibles, réponses vides
- **100% Gratuit** : Via OpenRouter

## 🛠️ Installation
```bash
pip install wikipediaapi ddgs python-dotenv
# Jeu de Pions - Client de Jeu en Python

## Description

Ce projet implémente un client de jeu en Python qui se connecte à un serveur de jeu, envoie des données de connexion, gère les communications via des sockets et décide des mouvements des pions sur un plateau de jeu. Le client peut également interagir avec un modèle de machine learning hébergé sur Google Cloud AI pour obtenir des prédictions de mouvements.

## Fonctionnalités

- **Connexion au serveur de jeu :** Le client envoie les informations d'abonnement au serveur pour s'inscrire au jeu.
- **Réponse aux requêtes de ping :** Le client répond aux requêtes de ping du serveur avec un message pong.
- **Gestion des mouvements des pions :** Le client décide des mouvements des pions et des placements de bloqueurs en fonction de l'état actuel du plateau de jeu.
- **Interaction avec Google Cloud AI :** Le client peut appeler un modèle de machine learning pour obtenir des prédictions de mouvements.

## Installation

### Prérequis

- Python 3.x
- Bibliothèques Python suivantes :
  - `socket`
  - `json`
  - `random`
  - `googleapiclient`
  - `simpleai`

### Installation des dépendances

```bash
pip install google-api-python-client simpleai

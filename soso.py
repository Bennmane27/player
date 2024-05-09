import socket
import json
import random
import googleapiclient.discovery

API_PROJECT_ID = "soso-22272"
API_MODEL_NAME = "sheets"
API_VERSION = "v4"



def send_json_data(json_data, server_address):
    # On crée un socket pour la communication réseau
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        # On se connecte à l'adresse du serveur spécifiée
        s.connect(server_address)
        # On convertit les données JSON en une chaîne de caractères
        json_string = json.dumps(json_data)
        # On envoie la chaîne de caractères au serveur
        s.sendall(json_string.encode())
        # On affiche un message indiquant que les données ont été envoyées avec succès
        print("Données JSON envoyées au serveur avec succès.")
        # On reçoit la réponse du serveur
        response = s.recv(20480)
        # On affiche la réponse du serveur
        print("Réponse du serveur:", response.decode())




def get_api_prediction(current_state):
    """Appelle le modèle ML sur Google Cloud AI pour obtenir un mouvement prédit."""
    service = googleapiclient.discovery.build('ml', API_VERSION)
    name = f'projects/{API_PROJECT_ID}/models/{API_MODEL_NAME}'

    response = service.projects().predict(
        name=name,
        body={'instances': [current_state]}
    ).execute()

    if 'error' in response:
        print("Erreur lors de la prédiction:", response['error'])
        return None
    return response['predictions'][0]  # Supposons que le modèle renvoie la meilleure action

def format_state_for_api(server_json):
    """Formate l'état actuel du jeu pour l'API, selon le format attendu par le modèle."""
    # Transforme le plateau en liste plate, extrait positions des joueurs, etc.
    return {
        "board": [cell for row in server_json["state"]["board"] for cell in row],
        "player_position": get_position(server_json),
        # Ajoute d'autres caractéristiques nécessaires selon ton modèle
    }




def blocker_mover(server_json):
    global blockers
    # On initialise une liste vide pour stocker les positions possibles des bloqueurs
    possible_blocker_positions = []
    # On parcourt le plateau de jeu
    for i in range(len(server_json["state"]["board"])):
        for j in range(len(server_json["state"]["board"][i])):
            # On vérifie si la case courante est un bloqueur car une case d'état 3 = possibilité de placer un blockers
            if server_json["state"]["board"][i][j] == 3:
                # On vérifie si la case est sur une colonne paire et non sur les deux premières colonnes
                if j%2 == 0 and j>1:
                    # On vérifie si la case deux positions à gauche n'est pas un obstacle pour pas que ca mette de demi mure
                    if server_json["state"]["board"][i][j-2] != 4:
                        # On initialise une variable pour ajouter ou non le bloqueur
                        add_blocker = True
                        # On vérifie si le bloqueur est déjà dans la liste des bloqueurs
                        for blocker in blockers:
                            if blocker == [[i-1,j-1],[i+1,j-1]] or blocker == [[i+1,j-1],[i-1,j-1]]:
                                add_blocker = False
                        # Si le bloqueur n'est pas déjà dans la liste, on l'ajoute
                        if add_blocker:                   
                            possible_blocker_positions.append([[i,j],[i,j-2]])
                # On fait la même chose pour les cases sur une colonne impaire et non sur les deux premières lignes
                elif j%2 == 1 and i>1:
                    if server_json["state"]["board"][i-2][j] != 4:
                        add_blocker = True
                        for blocker in blockers:
                            if blocker == [[i-1,j-1],[i-1,j+1]] or blocker == [[i-1,j+1],[i-1,j-1]]:
                                add_blocker = False
                        if add_blocker:                   
                            possible_blocker_positions.append([[i,j],[i-2,j]])

    # On ajoute les positions possibles des bloqueurs à la liste globale
    blockers.append(possible_blocker_positions)
    # On retourne un dictionnaire avec le type de mouvement et la position choisie aléatoirement parmi les positions possibles
    return {
        "type": "blocker",
        "position": random.choice(possible_blocker_positions)
    }
# On déclare une liste globale vide pour stocker les bloqueurs
blockers = []

# On définit une fonction pour obtenir les bloqueurs utilisés sur le nouveau plateau de jeu
def get_blockers_used(new_board):
    global blockers
    # On parcourt le plateau de jeu
    for i in range(len(new_board)):
        for j in range(len(new_board[i])):
            # On vérifie si la case courante est un bloqueur
            if new_board[i][j] == 4:
                # On initialise une variable pour vérifier si le bloqueur est déjà utilisé
                is_used = False
                # On parcourt la liste des bloqueurs
                for blocker in blockers:
                    # On vérifie si le bloqueur est déjà dans la liste
                    if [i, j] in blocker[0] or [i,j] in blocker[1]:
                        is_used = True
                # Si le bloqueur n'est pas déjà utilisé
                if not is_used:
                    # On vérifie si on peut ajouter un bloqueur en bas
                    if i+2 < len(new_board):
                        if new_board[i+2][j] == 4:
                            blockers.append([[i,j],[i+2,j]])
                    # Sinon, on vérifie si on peut ajouter un bloqueur à droite
                    elif j+2 < len(new_board[i]):
                        if new_board[i][j+2] == 4:
                            blockers.append([[i,j],[i,j+2]])

    
def get_position(server_json): 
    # On récupère le plateau de jeu à partir du JSON du serveur
    board = server_json["state"]["board"]
    # On récupère le joueur courant à partir du JSON du serveur
    joueur = server_json["state"]["current"]
    # On parcourt le plateau de jeu
    for i, elem in enumerate(board):
        # Si le joueur courant est dans la ligne courante du plateau
        if joueur in elem:
            # On trouve l'index du joueur dans la ligne
            pos_in_list = elem.index(joueur)  
            # On retourne la position du joueur sous forme de liste [ligne, colonne]
            return [i, pos_in_list]  
        

def player_mover(server_json):
    # On initialise une liste vide pour stocker les positions possibles du pion
    possible_pawn_positions = []
    # On initialise une variable pour stocker le numéro du pion
    pawn = 0
    # Si le deuxième joueur est "Niall", on change le numéro du pion à 1
    if server_json["state"]["players"][1] == "Niall":
        pawn = 1

    # On récupère la position actuelle du joueur
    i, j = get_position(server_json)

    # On parcourt toutes les directions possibles pour le mouvement du pion
    for y in [-2, 0, 2]:
        for x in [-2, 0, 2]:
            # On vérifie si la direction est valide (pas de mouvement en diagonale et pas de mouvement sur place)
            if not(x == 0 and y == 0) and x*y == 0:
                # On vérifie si la nouvelle position est dans les limites du plateau de jeu
                if 0 <= i+y < len(server_json["state"]["board"]) and 0 <= j+x < len(server_json["state"]["board"][0]):
                    # Si la nouvelle position est libre et qu'il n'y a pas de bloqueur sur le chemin
                    if server_json["state"]["board"][i+y][j+x] == 2 and server_json["state"]["board"][i+y//2][j+x//2] != 4:
                        # On ajoute la nouvelle position à la liste des positions possibles
                        possible_pawn_positions.append([[i+y, j+x]])
                    # Si la nouvelle position est occupée par le pion adverse et que la case derrière est libre
                    elif server_json["state"]["board"][i+y][j+x] == 1-pawn and server_json["state"]["board"][i+2*y][j+2*x] == 2 :
                        # On vérifie si la case derrière est dans les limites du plateau de jeu
                        if 0 <= i+2*y < len(server_json["state"]["board"]) and 0 <= j+2*x < len(server_json["state"]["board"][0]):
                            # Si il n'y a pas de bloqueur sur le chemin
                            if server_json["state"]["board"][i+y//2][j+x//2] != 4 and server_json["state"]["board"][i+3*y//2][j+3*x//2] != 4:
                                # On ajoute la case derrière à la liste des positions possibles
                                possible_pawn_positions.append([[i+2*y, j+2*x]])
                                
    # On retourne un mouvement aléatoire parmi les mouvements possibles
    return {
        "type": "pawn",
        "position": random.choice(possible_pawn_positions)
    }

def handle_ping_pong():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 9000))
        s.listen()
        while True:
            player, address = s.accept()
            with player:
                server_request = player.recv(20480).decode()
                server_json = json.loads(server_request)
                print("Requête du serveur:", server_json)
                if server_json["request"] == "ping":
                    response_pong = {"response": "pong"}
                    response_pong_json = json.dumps(response_pong)
                    player.sendall(response_pong_json.encode())
                    print("Pong envoyé au serveur en réponse à la requête de ping.")
                elif server_json["request"] == "play":
                    pawn = int("Niall"==server_json["state"]["players"][1])
                    get_blockers_used(server_json["state"]["board"])
                    if server_json["state"]["blockers"][pawn] != 0:
                        if random.randint(0, 1) == 0 :
                            player_move = player_mover(server_json)
                        else:
                            player_move = blocker_mover(server_json)
                    else:
                            player_move = player_mover(server_json)
                    response_move_string = {"response": "move", "move": player_move, "message": "J'attends ton coup"}
                    print(response_move_string)
                    response_move_json = json.dumps(response_move_string)
                    player.sendall(response_move_json.encode())
                    print("Coup joué et réponse envoyée au serveur.")

# Les données JSON que je dois envoyer
json_data = {
    "request": "subscribe",
    "port": 9000,
    "name": "Niall",
    "matricules": ["22272"]
}

# Définir l'adresse IP et le port du serveur local
server_address = ('localhost', 3000)

send_json_data(json_data, server_address)
handle_ping_pong()
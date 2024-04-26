import socket
import json
import random

def send_json_data(json_data, server_address):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(server_address)
        json_string = json.dumps(json_data)
        s.sendall(json_string.encode())
        print("Données JSON envoyées au serveur avec succès.")
        response = s.recv(20480)
        print("Réponse du serveur:", response.decode())

# Variable globale pour garder une trace de la direction du joueur
always_move_down = False

def player_mover(server_json):
    global always_move_down
    board = server_json["state"]["board"]
    position = get_position(server_json)
    move_available = callfunction(board, position)

    # Si c'est le premier mouvement et que le mouvement vers le haut n'est pas disponible
    if not always_move_down and not move_available[2]:
        always_move_down = True

    # Si le joueur doit toujours se déplacer vers le bas ou si le mouvement vers le haut n'est pas disponible
    if always_move_down or not move_available[2]:
        return down_move(position)
    else:
        return up_move(position)

#block any position
def blocker_mover(server_json):
    possible_blocker_positions = []
    for i in range(len(server_json["state"]["board"])):
        for j in range(len(server_json["state"]["board"][i])):
            if server_json["state"]["board"][i][j] == 3:
                if j%2 == 0:
                    possible_blocker_positions.append( [[i,j],[i,j-2]])
                else:
                    possible_blocker_positions.append( [[i,j],[i-2,j]])
                 
    return {
        "type": "blocker",
        "position": random.choice(possible_blocker_positions)
    }



def right_move(position):

    return {
    "type": "pawn", 
    "position": [[position[0], position[1] + 2]]
  }

def left_move(position):

    return {
    "type": "pawn", 
    "position": [[position[0], position[1] - 2]]
  }
    
def up_move(position):

    return {
    "type": "pawn", 
    "position": [[position[0] - 2, position[1]]]
  }
    
def down_move(position):

    return {
    "type": "pawn", 
    "position": [[position[0] + 2, position[1]]]
  }

  
def get_random_true_index(move_available):
    true_indices = [i for i, val in enumerate(move_available) if val]  # Obtient les indices des éléments True
    return random.choice(true_indices)  # Retourne un indice aléatoire parmi les éléments True

def right_available(board, position):
    if position[1] + 2 > 16 : # Si je suis à la fin de la liste je ne peux pas me déplacer à droite
        return False
    listcase = board[position[0]] # Je récupère la liste dans laquelle je me trouve mais dans logique du jeu je regarde le déplacement horizontale 
    if listcase[position[1]+ 1] == 3 and listcase[position[1]+ 2] == 2: # Si je me déplaces à droite et que c'est un blocker vide et que c'est une case vide 
        return True
    else:
        return False
    
def left_available(board, position):
    if position[1] - 2 < 0 : # Si je suis au début de la liste je ne peux pas me déplacer à gauche
        return False
    listcase = board[position[0]] # Je récupère la liste dans laquelle je me trouve mais dans logique du jeu je regarde le déplacement horizontale 
    if listcase[position[1]- 1] == 3 and listcase[position[1]- 2] == 2: # Si je me déplaces à gauche et que c'est un blocker vide et que c'est une case vide 
        return True
    else:
        return False

def up_available(board, position):
    if position[0] - 2 < 0 : # Si je suis au début de la liste je ne peux pas me déplacer en haut
        return False
    listcase = board[position[0]-2] # Je récupère la liste dans laquelle je me trouve mais dans logique du jeu je regarde le déplacement verticale 
    listblocker = board[position[0]-1] # La liste où il y'a le blocker
    if listblocker[position[0]] == 3 and listcase[position[0]] == 2: # Si je me déplaces en haut et que c'est un blocker vide et que c'est une case vide 
        return True
    else:
        return False

def down_available(board, position):
    if position[0] + 2 > 16 : # Si je suis à la fin de la liste je ne peux pas me déplacer en bas
        return False
    listcase = board[position[0]+2] # Je récupère la liste dans laquelle je me trouve mais dans logique du jeu je regarde le déplacement verticale 
    listblocker = board[position[0]+1] # La liste où il y'a le blocker
    if listblocker[position[0]] == 3 and listcase[position[0]] == 2: # Si je me déplaces en bas et que c'est un blocker vide et que c'est une case vide 
        return True
    else:
        return False
      
def callfunction(board, position):
    listefunction = []
    listefunction.append(right_available(board, position))
    listefunction.append(left_available(board, position))
    listefunction.append(up_available(board, position))
    listefunction.append(down_available(board, position))
    return listefunction


def get_position(server_json): # Indique position de où je suis 
    board = server_json["state"]["board"]
    joueur = server_json["state"]["current"]
    
    for i, elem in enumerate(board):  # Parcourt les 17 listes 
        if joueur in elem:  # Vérifie si zéro est présent dans la liste
            pos_in_list = elem.index(joueur)  # Obtient la position de zéro dans la liste
            return [i, pos_in_list]  # Renvoie le numéro de la liste et la position de zéro dans cette liste

def handle_ping_pong():
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(('', 9000))
        s.listen()
        while True:
            try: 
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
                        lives = server_json["lives"]
                        state = server_json["state"]
                        errors = server_json["errors"]
                        player_move = blocker_mover(server_json)
                        print(player_move)  
                        response_move_string = {"response": "move", "move": player_move, "message": "J'attends ton coup"}
                        print(response_move_string)
                        response_move_json = json.dumps(response_move_string)
                        player.sendall(response_move_json.encode())
                        print("Coup joué et réponse envoyée au serveur.")
            except Exception as e:
                print("Exception:", e)
                break




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




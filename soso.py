import socket
import json
import random

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



def blocker_mover(server_json):
    global  blockers
    possible_blocker_positions = []
    for i in range(len(server_json["state"]["board"])):
        for j in range(len(server_json["state"]["board"][i])):
            if server_json["state"]["board"][i][j] == 3:
                if j%2 == 0 and j>1:
                    if server_json["state"]["board"][i][j-2] != 4:
                        add_blocker = True
                        for blocker in blockers:
                            if blocker == [[i-1,j-1],[i+1,j-1]] or blocker == [[i+1,j-1],[i-1,j-1]]:
                                add_blocker = False
                        if add_blocker:                   
                            possible_blocker_positions.append([[i,j],[i,j-2]])
                elif j%2 == 1 and i>1:
                    if server_json["state"]["board"][i-2][j] != 4:
                        add_blocker = True
                        for blocker in blockers:
                            if blocker == [[i-1,j-1],[i-1,j+1]] or blocker == [[i-1,j+1],[i-1,j-1]]:
                                add_blocker = False
                        if add_blocker:                   
                            possible_blocker_positions.append([[i,j],[i-2,j]])

  
    blockers.append(possible_blocker_positions)
    return {
        "type": "blocker",
        "position": random.choice(possible_blocker_positions)
    }

blockers = []

def get_blockers_used(new_board):
    global blockers
    for i in range(len(new_board)):
        for j in range(len(new_board[i])):
            if new_board[i][j] == 4:
                is_used = False
                for blocker in blockers:
                    if [i, j] in blocker[0] or [i,j] in blocker[1]:
                        is_used = True
                if not is_used:
                    if i+2 < len(new_board):
                        if new_board[i+2][j] == 4:
                            blockers.append([[i,j],[i+2,j]])
                    elif j+2 < len(new_board[i]):
                        if new_board[i][j+2] == 4:
                            blockers.append([[i,j],[i,j+2]])

    

def get_position(server_json): 
    board = server_json["state"]["board"]
    joueur = server_json["state"]["current"]
    for i, elem in enumerate(board):
        if joueur in elem:
            pos_in_list = elem.index(joueur)  
            return [i, pos_in_list]  
        
def player_mover(server_json):
    possible_pawn_positions = []
    pawn = 0
    if server_json["state"]["players"][1] == "Niall":
        pawn = 1

    # Get the current player position
    i, j = get_position(server_json)

    for y in [-2, 0, 2]:
        for x in [-2, 0, 2]:
            if not(x == 0 and y == 0) and x*y == 0:
                if 0 <= i+y < len(server_json["state"]["board"]) and 0 <= j+x < len(server_json["state"]["board"][0]):
                    if server_json["state"]["board"][i+y][j+x] == 2 and server_json["state"]["board"][i+y//2][j+x//2] != 4:
                        possible_pawn_positions.append([[i+y, j+x]])
                    elif server_json["state"]["board"][i+y][j+x] == 1-pawn and server_json["state"]["board"][i+2*y][j+2*x] == 2 :
                        if 0 <= i+2*y < len(server_json["state"]["board"]) and 0 <= j+2*x < len(server_json["state"]["board"][0]):
                            if server_json["state"]["board"][i+y//2][j+x//2] != 4 and server_json["state"]["board"][i+3*y//2][j+3*x//2] != 4:
                                possible_pawn_positions.append([[i+2*y, j+2*x]])

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

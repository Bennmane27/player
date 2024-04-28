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




def blocker_mover(server_json):
    possible_blocker_positions = []
    for i in range(len(server_json["state"]["board"])):
        for j in range(len(server_json["state"]["board"][i])):
            if server_json["state"]["board"][i][j] == 3:
                if j%2 == 0 and j>1:
                    if server_json["state"]["board"][i][j-1] != 4 and server_json["state"]["board"][i][j-2] != 4:  # Check if there is already a blocker in the position
                        if [i,j] not in [pos[0] for pos in possible_blocker_positions] and [i,j-2] not in [pos[1] for pos in possible_blocker_positions]:
                            possible_blocker_positions.append([[i,j],[i,j-2]])
                elif j%2 == 1 and i>1:
                    if server_json["state"]["board"][i-1][j] != 4 and server_json["state"]["board"][i-2][j] != 4:  # Check if there is already a blocker in the position
                        if [i,j] not in [pos[0] for pos in possible_blocker_positions] and [i-2,j] not in [pos[1] for pos in possible_blocker_positions]:
                            possible_blocker_positions.append([[i,j],[i-2,j]])

  
    return {
        "type": "blocker",
        "position": random.choice(possible_blocker_positions)
    }


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
                    elif server_json["state"]["board"][i+y][j+x] == 1-pawn and server_json["state"]["board"][i+2*y][j+2*x] == 2:
                        if 0 <= i+2*y < len(server_json["state"]["board"]) and 0 <= j+2*x < len(server_json["state"]["board"][0]) and server_json["state"]["board"][i+y][j+x] != 4:
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
                        if random.randint(0, 1) == 0:
                            player_move = player_mover(server_json)
                        else:
                            player_move = blocker_mover(server_json)
                        if player_move is None:
                            player_move = player_mover(server_json)
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

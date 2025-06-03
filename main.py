
import random
import time
import threading
import uuid
import socket
import json
import struct
import uuid

global_players = {}

global_addr_db = {}
class Player():
    def __init__(self, name, ip):
        self.name = name
        #self.id = force_id if force_id else max(list(global_players.keys()) + [0]) + 1 ### set ID
        self.uuid = uuid.uuid4()
        self.uuid = str(self.uuid) # convert to string, for convenience
        global_players[self.uuid] = self
        self.conn = None
        self.addr = None

        self.reset()


    def reset(self):
        self.isInGame = False
        self.hand = []
        self.played_move = False
        self.score = 0


global_card_db = {}
class Card():
    def __init__(self, text, color = False, help: str = "", answers = 1): #False color = white, True = black
        global global_card_db
        self.text = text
        self.help = help
        self.color = color
        
        self.answers = answers

        self.uuid = uuid.uuid4()
        self.uuid = str(self.uuid) # for convenience
        global_card_db[self.uuid] = self

        self.blank = not self.text # if no text; = True; else; = False





black_cards = [Card(f"Black card test{i}", True, "Blackhelp", answers=2) for i in range(20)]
white_cards = [Card(f"White card test{i}", False, "Whitehelp") for i in range(30)]
white_cards = white_cards + [Card("", False, "Blank") for _ in range(30)]
#white_cards = white_cards + [Card("", False) for _ in range(20)]



class Server(): #AI

    clients = [] 
    handlers = {}
    def __init__(self, host: str = "0.0.0.0", port: int = 12345, autostart: bool = True, max_points = 7, black_cards = [], white_cards = [], max_cards = 8, deck_rules = False, hand_duplicate = False):
        self.change_settings(max_points, black_cards, white_cards, max_cards, deck_rules, hand_duplicate)
        self.started = False
        
        self.scoreboard = {} #playeruuid: score

        self._register_handlers()
        
        
        self.players = {} #playeruuid: playerobj
        self.uuids = {} #playeruuid: name

        self.HOST = host
        self.PORT = port

        if autostart:
            conn_init_thread = threading.Thread(target=self.start_server, daemon=True)
            conn_init_thread.start()

            #self.start_server()
        
        # call self.game_start() to start the game loop


    
    def broadcast(self, data, exclude_sock=None):
        for client_sock in self.clients:
            if client_sock == exclude_sock:
                continue  # Optional: skip the sender
            try:
                self.send_packet(client_sock, data)
            except Exception as e:
                print(f"[!] Failed to send to client: {e}")


    def send_packet(self, sock, data):
        msg = json.dumps(data).encode()
        sock.sendall(struct.pack('!I', len(msg)) + msg)

    def recv_packet(self, sock):
        raw_len = self.recv_exact(sock, 4)
        if not raw_len:
            return None
        msg_len = struct.unpack('!I', raw_len)[0]
        data = self.recv_exact(sock, msg_len)
        if data is None:
            return None
        return json.loads(data.decode())

    def recv_exact(self, sock, n):
        data = b''
        while len(data) < n:
            chunk = sock.recv(n - len(data))
            if not chunk:
                return None
            data += chunk
        return data

    def handle_client(self, conn, addr):
        print(f"[+] Client connected: {addr}")
        self.clients.append(conn)
        try:
            while True:
                packet = self.recv_packet(conn)
                if packet is None:
                    break
                print(f"[{addr}] {packet}")

                packet_type = packet["type"]
                data = packet["data"]
                if handler := self.handlers[packet_type]:
                    handler(data, conn, addr)

                

                # Echo back or broadcast to all clients
                #response = {"type": "echo", "data": packet}
                #self.send_packet(conn, response)

        except Exception as e:
            print(f"[{addr}] Error:", e)
        finally:
            print(f"[-] Client disconnected: {addr}")
            self.remove_player(global_addr_db[addr]) # removes player obj and references
            self.clients.remove(conn)
            conn.close()

    def remove_player(self, player): 
        global global_addr_db # removes player obj and references
        self.uuids.pop(player.uuid)
        self.players.pop(player.uuid)
        self.scoreboard.pop(player.uuid)
        print(global_addr_db)
        global_addr_db.pop(player.addr)
        del player
        


    def start_server(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_sock:
            server_sock.bind((self.HOST, self.PORT))
            server_sock.listen()
            print(f"[Server] Listening on {self.HOST}:{self.PORT}...")
            while True:
                conn, addr = server_sock.accept()
                handler = threading.Thread(target=self.handle_client, args=(conn, addr), daemon=True)
                handler.start()

    
    # --------------


    def packet_handler(packet_type):
        def decorator(func):
            func._packet_type = packet_type
            return func
        return decorator
    
    def _register_handlers(self):
        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if callable(method) and hasattr(method, "_packet_type"):
                self.handlers[method._packet_type] = method
    
    # ------------------


    def game_start(self):
        self.started = True
        if "process" not in vars(self):
            self.process = threading.Thread(target=self.start)
            self.process.start()
            return self.process
        else:
            print("NOT FATAL: Process already started, returning original process")
            return self.process


    def get_game_process(self):
        if "process" in vars(self):
            return self.process
        else:
            return None



    def change_settings(self, nmax_points = 0, nblack_cards = [], nwhite_cards = [], nmax_cards = 8, ndeck_rules = False, nhand_duplicate = False):
        self.max_points = nmax_points if nmax_points else self.max_points
        self.max_cards = nmax_cards if nmax_cards else self.max_cards
        self.black_cards = nblack_cards if nblack_cards else self.black_cards
        self.white_cards = nwhite_cards if nwhite_cards else self.white_cards
        self.all_white_cards = self.white_cards  #clone for deck_rules
        self.all_black_cards = self.black_cards  #clone for deck_rules
         
        self.deck_rules = ndeck_rules
        self.hand_duplicate = nhand_duplicate

        self.game_info = {"max_points": self.max_points, "max_cards": self.max_cards, "deck_rules": self.deck_rules, "hand_duplicate": self.hand_duplicate}
        

    def give_card(self, player): #appends card to hand, returns appended card, 
        if self.deck_rules:
            card = self.white_cards.pop()
            player.hand.append(card)
            return card
        elif not self.hand_duplicate:
            self.shuffle() #deck shuffled

            player_held_cards = []
            for i in self.players.values():
                player_held_cards = player_held_cards + i.hand

            for card in self.white_cards:
                if card not in player_held_cards:
                    player.hand.append(card)
                    return card
                
            print(f"NOT FATAL: Not enough cards, ignoring rules") #
        ### can't be else
        card = random.choice(self.white_cards)
        player.hand.append(card)
        return card
        ###

    
            
    def start(self):
        for player in list(self.players.values())*self.max_cards:
            print(self.give_card(player))
        
        self.tsar = list(self.players.values())[-1] #player id
        self.rounds = 0
        winner = self.round()

        time.sleep(2) #####
        self.finish()

        return winner
        

    def finish(self):
        print("Resetting...")

        for player in self.players.values():
            player.reset()
        self.started = False

    
    def shuffle(self):
        random.shuffle(self.black_cards)
        random.shuffle(self.white_cards)


    @packet_handler("log_in")
    def log_in(self, data, conn, addr):
        ip = addr[0] ###################################
        name = data["name"]

        new_player = Player(name, ip)
        self.players[new_player.uuid] = new_player
        global_addr_db[addr] = new_player

        new_player.conn = conn
        new_player.addr = addr

        self.scoreboard[new_player.uuid] = 0
        self.uuids[new_player.uuid] = new_player.name

        self.send_packet(conn, {"type": "game_info", "data": self.game_info})
        #self.send_packet(conn, {"type": "uuid_echo", "data": {"uuid": new_player.uuid}})

        print(f"player {new_player.name} joined! {addr}")



        #self.send_packet(conn, {"type": "player_info", "data": None}) #send player ifno WIP




    @packet_handler("submit_white")
    def submit_card(self, data, conn, addr):
        card_data = data["cards"]
        player = global_addr_db[addr]
        card_dict = {}
        for i in card_data:
            card = global_card_db[card_data[i]["uuid"]]
            card_dict[i] = card
            
            custom_text = card_data[i]["text"]

            if card not in player.hand or player.played_move or player is self.tsar: 
                print(f"NOT FATAL: Can't submit card, stolen card: {card not in player.hand}, has played: {player.played_move}, is tsar: {self.tsar == player}")
                return None


            if not card.text:
                card.text = custom_text


            
            player.hand.remove(card)
            print(f"player {player.name} submitted card {card.text}")
        player.played_move = True
        self.submitted_cards[player.uuid] = card_dict



    def get_winner(self):
        winner = None
        for player in self.players.values():
            if player.score >= self.max_points:
                winner = player
        
        return winner
    
    def add_score(self, player):
        player.score = player.score + 1
        self.scoreboard[player.uuid] = player.score


    @packet_handler("submit_rate")
    def rate(self, data, conn, addr):
        player_uuid = data["uuid"]

        #player = data["player"]
        sender = global_addr_db[addr]

        player = self.players[player_uuid]


        # tsar has to pick a card
        if self.tsar is not sender or not self.submitted_cards: 
            print(F"NOT FATAL: player {sender.name} is not the tsar; OR it wasn't rating phase")
            return None
        elif not player:
            raise "FATAL: Player not found"

        self.round_winner = player
        self.add_score(self.round_winner)
        self.winning_card = self.submitted_cards[player_uuid]
        return player
    
    def broadcast_round_info(self): # can/should be made individual access, for client calls
        data = {"scoreboard": self.scoreboard, "uuids": self.uuids}

        print(f"Broadcasting round info")
        for player in self.players.values(): 
            print(f"-broadcasting to {player.name}")
            if player is self.tsar:

                data.update({"cards": [], "black": {"text": self.current_black_card.text, "help": self.current_black_card.help, "answers": self.current_black_card.answers}, "tsar": True})
                self.send_packet(player.conn, {"type": "round_info", "data": data})
            else:
                card_data = [{"text": card.text, "help": card.help, "uuid": card.uuid} for card in player.hand]

                data.update({"cards": card_data, "black": {"text": self.current_black_card.text, "help": self.current_black_card.help, "answers": self.current_black_card.answers}, "tsar": False})
                self.send_packet(player.conn, {"type": "round_info", "data": data})
        print(f"Finished broadcasting round info")
        
    
    def broadcast_rate_info(self):
        print(f"broadcasting rate info")

        card_data = {}
        for player_id in self.submitted_cards:
            card_data[player_id] = {}
            for card_id in self.submitted_cards[player_id]:
                card = self.submitted_cards[player_id][card_id]
                card_data[player_id][card_id] = {"text": card.text, "help": card.help, "uuid": card.uuid}

        self.broadcast({"type": "rate_info", "data": card_data})


    def round(self):
        self.rounds = self.rounds + 1


        # ----------------------------------------------------TSAR PICK
        #print([i.name for i in list(self.players.values())])
        print(self.players)
        self.tsar = list(self.players.values())[list(self.players.values()).index(self.tsar)+1 if list(self.players.values()).index(self.tsar)+1 < len(self.players) else 0]
        self.current_black_card = random.choice(self.black_cards)

        # ----------------------------------------------------GIVE CARDS
        for player in self.players.values(): 
            while len(player.hand) < self.max_cards:
                self.give_card(player)
        
        self.broadcast_round_info() #--------------- call TCP

        
        print(f"Round no. {self.rounds}")
        print(f"{self.tsar.name} is the tsar!")

        # ----------------------------------------------------ROUND PHASE

        self.submitted_cards = {} # player: card

        print(f"awaiting Cards")
        while len(self.submitted_cards) < len(self.players)-1: #-1 for tsar
            #print(f"awaiting Cards, submitted cards: {self.submitted_cards}")
            if len(self.players) < 2: raise Exception("player left")
            time.sleep(1)

        if len(self.players) < 2: raise Exception("Not enough players")

        # ----------------------------------------------------RATE PHASE
        print(f"cards submitted!")
        print(self.submitted_cards)

        self.broadcast_rate_info() #--------------- call TCP

        self.round_winner = None #placeholder
        print(f"awating Rating, ")
        while not self.round_winner:
            if len(self.players) < 2: raise Exception("player left")
            time.sleep(1)

        # ----------------------------------------------------ANNOUNCE ROUND WINNERS
        print(f"{self.round_winner.name} won this round")
        print(f"broadcasting round winner")
        self.broadcast({"type": "round_winner", "data": {"winner": self.round_winner.name, "uuid": self.round_winner.uuid}}) # , "winner_uuid": self.round_winner.uuid

        for player in self.players.values(): #----RESET MOVES
            player.played_move = False

        time.sleep(1)

        # ---------------------------------------------------- CALL FOR WINNER
        if winner := self.get_winner():
            print(f"Player {winner.name} won the Game!")

            print(f"broadcasting game winner")
            self.broadcast({"type": "game_end", "data": {"winner": winner.name}}) # , "winner_uuid": winner.uuid
            return winner
        return self.round()
    


    


    

import sys
if __name__ == "__main__":

    game = Server(black_cards=black_cards, white_cards=white_cards)


    print("Hey")

    while len(game.players) < 3:
        time.sleep(1)

        #print(game.players)
        #print(global_addr_db)
    game.game_start()






    exit() ########---------------


    l = []
    for i in range(1,4):
        l.append(Player(f"Player{i}"))

    for i in global_players:
        print(global_players[i].name)


    #t1 = threading.Thread(target=Game, args=(global_players, 7, black_cards, white_cards, 8, False, False, True))
    #t1.start()



    game = Game(global_players, 2, black_cards, white_cards, 8, False, False, True)

    time.sleep(1)



    while True:
        game.submit_card(global_players[1].hand[0], global_players[1])
        game.submit_card(global_players[2].hand[0], global_players[2])
        game.submit_card(global_players[3].hand[0], global_players[3])
        time.sleep(3)
        game.rate(global_players[3])

        time.sleep(3)

    time.sleep(2)








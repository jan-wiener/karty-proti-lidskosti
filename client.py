import socket
import json
import struct
import uuid

#SERVER_IP = 'localhost'  # replace with IP
#PORT = 12345




class Client(): #AI

    handlers = {}
    def __init__(self, name, SERVER_IP, PORT, autostart = True):
        self.SERVER_IP = SERVER_IP
        self.PORT = PORT
        self.name= name
        self._register_handlers()
        self.connected = False
        if autostart:
            self.client_start()
    

    def send_packet(self, data):
        msg = json.dumps(data).encode()
        self.sock.sendall(struct.pack('!I', len(msg)) + msg)
    
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
    


    def client_start(self):
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as self.sock:
            self.sock.connect((self.SERVER_IP, self.PORT))
            self.connected = True
            print("Connected to server!")

            # self.send_packet({
            #     "type": "greeting",
            #     "data": {
            #         "name": name,
            #         "msg": "Hello from client!"
            #     }
            # })
            self.log_in()

            while True:
                try:
                    packet = self.recv_packet(self.sock)
                    if packet:
                        print("Received:", packet)
                        self.last_packet = packet
                        packet_type = packet["type"]
                        data = packet["data"]
                        if handler := self.handlers[packet_type]:
                            handler(data)
                    else:
                        print("Server closed the connection.")
                        break
                except Exception as e:
                    self.connected = False
                    print("Error:", e)
                    break        

    
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

    

    # ----------------------

    @packet_handler("uuid_echo")
    def recv_uuid_echo(self, data):
        self.player_id = data["uuid"]

    @packet_handler("game_info")
    def recv_game_info(self, data):
        self.game_info = data
        print(f"Login successful!")
    
    @packet_handler("round_info")
    def recv_round_info(self, data):
        self.current_black_card = data["black"]
        print(f"Current black card: {self.current_black_card["text"]}")
        if data["tsar"]:
            self.is_tsar = True
            print(f"You are the TSAR")
        else:
            self.is_tsar = False
            cards = data["cards"]
            self.hand = {i: cards[i] for i in range(len(cards))}

            # ------------------------------------Terminal access
            print(f"Pick a card!")
            for i in self.hand:
                card = self.hand[i]
                print(f"Card {i}: {card["text"]} ({card["help"]})")
            picked = int(input("picked (index): "))
            picked = self.hand[picked]
            if not picked["text"]:
                picked["text"] = input("Enter card text: ")
            self.submit_white(picked["uuid"], picked["text"])

        #for i in range(len(cards)):
        #    self.hand[i] = cards[i]

    
    @packet_handler("rate_info")
    def recv_rate_info(self, data):
        cards = data["cards"]
        self.cards_to_rate = {i: cards[i] for i in range(len(cards))}

        # ------------------------------------Terminal access
        print(f"Submitted cards:")
        for i in self.cards_to_rate:
            card = self.cards_to_rate[i]
            print(f"Card {i}: {card["text"]} ({card["help"]})")

        if self.is_tsar:
            print(f"You are the tsar! Pick a card!")
        
            picked = int(input("picked (index): "))
            picked = self.cards_to_rate[picked]
            self.submit_rate(picked["uuid"])
        else:
            print(f"Wait for the tsar to pick a card")


    @packet_handler("round_winner")
    def recv_round_winner(self, data):
        self.round_winner = data["winner"]
        self.winning_card = data["card"]

        # ------------------------------------Terminal access
        print(f"Player {self.round_winner} won this round with his card\n{self.winning_card["text"]} ({self.winning_card["help"]})")

    
    @packet_handler("game_end")
    def recv_game_end(self, data):
        self.winner = data["winner"]
        

        # ------------------------------------Terminal access
        print(f"-----\nPlayer {self.winner} won the game !!\n")
        

    # ---------------------

    def log_in(self):
        self.send_packet({
            "type": "log_in",
            "data": {
                "name": self.name
            }
        })


    
    def submit_white(self, carduuid, custom_text = ""):
        self.send_packet({"type": "submit_white", "data": {"uuid": carduuid, "custom_text": custom_text}})
    
    def submit_rate(self, carduuid):
        self.send_packet({"type": "submit_rate", "data": {"uuid": carduuid}})



    


name = input("Enter player name: ")
try:
    client = Client(name=name)
except Exception as e:
    print(e)
    exit()




import time

while True:
    time.sleep(1)

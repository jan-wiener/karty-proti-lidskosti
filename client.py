import socket
import json
import struct
import uuid
import threading

#SERVER_IP = 'localhost'  # replace with IP
#PORT = 12345




class Client(): #AI

    handlers = {}
    def __init__(self, name, SERVER_IP = "localhost", PORT = 12345, autostart = True, force_console = False):
        self.force_console = force_console
        self.SERVER_IP = SERVER_IP
        self.PORT = PORT
        self.name= name
        self._register_handlers()
        self.connected = False
        if autostart:
            client_thread = threading.Thread(target=self.client_start)
            client_thread.start()
            # self.client_start()
    

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
                # try:
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
                # except Exception as e:
                #     self.connected = False
                #     print("Error:", e)
                #     break        

    
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
        self.answers = self.current_black_card["answers"]
        print(f"Current black card: {self.current_black_card["text"]}")
        if data["tsar"]:
            self.is_tsar = True
            print(f"You are the TSAR")
        else:
            self.is_tsar = False
            cards = data["cards"]
            self.hand = {i: cards[i] for i in range(len(cards))}


            if not self.force_console: return
            # ------------------------------------Terminal access
            print(f"Pick a card!")
            crds = []
            
            for i in self.hand:
                card = self.hand[i]
                print(f"Card {i}: {card["text"]} ({card["help"]})")
            for i in range(self.answers):

                picked = int(input(f"picked (index) [{i}]: "))
                picked = self.hand[picked]
                if not picked["text"]:
                    picked["text"] = input("Enter card text: ")

                crds.append({"uuid": picked["uuid"], "text": picked["text"]})
            self.submit_white(crds)

        #for i in range(len(cards)):
        #    self.hand[i] = cards[i]

    
    @packet_handler("rate_info")
    def recv_rate_info(self, data):
        # cards = data
        # self.cards_to_rate = {i: cards[i] for i in range(len(cards))}
        self.cards_to_rate = data

        self.uuiddict = {i: v for i, v in enumerate(list(self.cards_to_rate.keys()))}
        # self.cards_indexed = {i: {self.cards_to_rate[v]} for i, v in enumerate(list(self.cards_to_rate.keys()))}
        self.cards_indexed = {}
        for i, uuid in enumerate(self.cards_to_rate):
            self.cards_indexed[i] = self.cards_to_rate[uuid]
        # {playeruuid: {i: cardinfo, ...}, ...}


        if not self.force_console: return
        # ------------------------------------Terminal access
        print(f"Submitted cards:")
        for i in self.cards_indexed:
            cards = self.cards_indexed[i]
            for cardid in cards:
                crd = cards[cardid]
                print(f"Card set {i} card {cardid}: {crd["text"]} ({crd["help"]})")

        if self.is_tsar:
            print(f"You are the tsar! Pick a set!")
        
            picked = int(input("picked (index): "))
            self.submit_rate(self.uuiddict[picked])
        else:
            print(f"Wait for the tsar to pick a card")


    @packet_handler("round_winner")
    def recv_round_winner(self, data):
        self.round_winner = data["winner"]
        self.round_winner_uuid = data["uuid"]
        # self.winning_card = data["card"]

        # ------------------------------------Terminal access
        print(f"Player {self.round_winner} won this round ")

    
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


    
    def submit_white(self, cards, custom_text = ""): # cards = [{"uuid": uuid, "custom_text": custom_text}]
        data = {"cards": {i: v for i,v in enumerate(cards)}}
        self.send_packet({"type": "submit_white", "data": data})
        #self.send_packet({"type": "submit_white", "data": {"uuid": carduuid, "custom_text": custom_text}})
    
    def submit_rate(self, playeruuid):
        self.send_packet({"type": "submit_rate", "data": {"uuid": playeruuid}})



    
if __name__ == "__main__":
    name = "ConsoleClientName"
    try:
        client = Client(name=name, force_console=True)
    except Exception as e:
        print(e)
        exit()




    import time

    while True:
        time.sleep(1)

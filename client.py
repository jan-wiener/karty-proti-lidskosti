import socket
import json
import struct
import uuid

SERVER_IP = 'localhost'  # replace with IP
PORT = 12345




class Client(): #AI

    def __init__(self, autostart = True):
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
            self.sock.connect((SERVER_IP, PORT))
            self.connected = True
            print("Connected to server!")

            self.send_packet({
                "type": "greeting",
                "data": {
                    "name": name,
                    "msg": "Hello from client!"
                }
            })

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
        self.game_info = data["game_info"]
    
    @packet_handler("round_info")
    def recv_round_info(self, data):
        self.current_black_card = data["black"]
        if data["tsar"]:
            self.is_tsar = True
        else:
            self.is_tsar = False
            cards = data["cards"]
            self.hand = {i: cards[i] for i in range(len(cards))}
        
        #for i in range(len(cards)):
        #    self.hand[i] = cards[i]

    
    @packet_handler("rate_info")
    def recv_rate_info(self, data):
        cards = data["cards"]
        self.cards_to_rate = {i: cards[i] for i in range(len(cards))}

    @packet_handler("round_winner")
    def recv_round_winner(self):
        pass
    
    @packet_handler("game_end")
    def recv_game_end(self):
        pass

    # ---------------------

    def log_in(self):
        self.send_packet({
            "type": "log_in",
            "data": {
                "name": name
            }
        })


    
    def submit_white(self):
        pass
    
    def submit_rate(self):
        pass



    


name = "Honza"
client = Client()




import time

while True:
    time.sleep(1)

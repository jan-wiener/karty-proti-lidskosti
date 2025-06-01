import socket
import json
import struct
import uuid
import threading

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
)
from PyQt6.QtGui import (
    QIcon
)
from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt, QTimer
import sys


from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
import sys

from PyQt6.QtCore import QObject, QThread, pyqtSignal
#SERVER_IP = 'localhost'  # replace with IP
#PORT = 12345










# Import your custom widget
# from scoreboard_widget import ScoreboardWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.client = Client(name="Honza", ui=self)
        self.setWindowTitle("Card Game")
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: #343536;")

        layout = QVBoxLayout()
        # Add scoreboard

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(1000)
        print(f"--------")
        #-----------------------------------------------
        self.scoreboard = QLabel("Score: --")

        self.black_card_area = QHBoxLayout()
        self.black_card = QPushButton()
        self.black_card.setFixedSize(100,150)
        self.black_card_area.addWidget(self.black_card)

        self.status_message = QLabel("Status")
        self.status_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_message.setMargin(12)
        self.status_message.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
            }
            """)
        
        self.selected_label = QLabel("Selected Cards")
        self.selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_label.setMargin(8)
        self.selected_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
            }
            """)
        self.no_selected = QLabel("-- No cards selected --")
        self.no_selected.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_selected.setMargin(20)
        self.no_selected.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
            }
            """)
        
        self.no_cards_in_hand = QLabel("-- No cards in hand --")
        self.no_cards_in_hand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_cards_in_hand.setMargin(20)
        self.no_cards_in_hand.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
            }
            """)
        
        self.hand_label = QLabel("Your cards")
        self.hand_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.hand_label.setMargin(8)
        self.hand_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
            }
            """)
        
        self.selected_card_area = QHBoxLayout()
        self.selected_cards = {}
        
        self.white_card_area = QHBoxLayout()
        self.white_cards = []

        self.send_button = QPushButton("Send")
        self.send_button.setFixedSize(150,80)
        self.send_button.setStyleSheet("""
            QPushButton {
                background-color: grey;
                font-size: 18px;
                color: white;
            }
            """)
        self.send_button.clicked.connect(self.submit_action)




        layout.addWidget(self.scoreboard)
        layout.addLayout(self.black_card_area)
        layout.addWidget(self.status_message)
        layout.addWidget(self.selected_label)
        layout.addWidget(self.no_selected)
        layout.addLayout(self.selected_card_area)
        layout.addWidget(self.hand_label)
        layout.addLayout(self.white_card_area)
        layout.addWidget(self.no_cards_in_hand)
        layout.addWidget(self.status_message)
        layout.addWidget(self.send_button, alignment=Qt.AlignmentFlag.AlignHCenter)

        self.black_card.setStyleSheet("""
            QPushButton {
                background-color: black;
                border: 2px solid black;
                border-radius: 10px;
                font-size: 12px;
                color: white;
                                 
            }
            QPushButton:hover {
                background-color: black;
            }
            """)

        self.hand = {0: {"text": "the black ones the black ones the black ones", "custom_text": ""}, 1: {"text": "Chuck Norris", "custom_text": ""}}
        self.set_cards(self.hand)

        self.current_black_card = {"text": "I hate ____"}
        self.set_black_card(self.current_black_card)
        # Later, you could call:


        self.setLayout(layout)

    def update_scoreboard(self):
        pass
    
    @staticmethod
    def format_card_text(text):
        lines = {i: "" for i in range(10)}
        spacecount = 0
        cline = 0
        for i, char in enumerate(text):
            if char == " ":
                spacecount += 1
            if spacecount >= 3 and len(lines[cline]) >= 10:
                cline += 1
                spacecount = 0
            lines[cline] = lines[cline] + char
        lines = {i: lines[i] for i in lines if lines[i]}
        return "\n".join(list(lines.values()))

    def select_card(self, card):
        if len(self.selected_cards) >= self.client.answers: return
        
        self.selected_cards[card.objectName()] = card
        self.white_cards.pop(card.objectName())
        card.setParent(None)
        self.selected_card_area.addWidget(card)

        card.clicked.disconnect()
        card.clicked.connect(lambda: self.deselect_card(card))
        print(self.white_cards)

        self.tick()



    def deselect_card(self, card):
        
        self.white_cards[card.objectName()] = card
        self.selected_cards.pop(card.objectName())
        card.setParent(None)
        self.white_card_area.addWidget(card)

        card.clicked.disconnect()
        card.clicked.connect(lambda: self.select_card(card))
        print(self.white_cards)

        self.tick()




    def set_cards(self, cards):
        self.clear_layout(self.white_card_area)

        self.white_cards = {}
        for i in cards:
            cardui = QPushButton()
            cardui.setObjectName(f"{i}")

            self.white_cards[cardui.objectName()] = cardui
            
            cardui.setText(self.format_card_text(cards[i]["text"]))#cards[i]["text"]
            cardui.clicked.connect(lambda _, crd = cardui: self.select_card(crd))


            
            cardui.setFixedSize(100,150)    
            cardui.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 2px solid black;
                border-radius: 10px;
                font-size: 12px;
                color: black;
                                 
            }
            QPushButton:hover {
                background-color: lightgray;
            }
            """)
            self.white_card_area.addWidget(cardui)
        

    def set_black_card(self, black_card_data):
        self.black_card.setText(self.format_card_text(black_card_data["text"]))

    def clear_layout(self, layout):
        while layout.count():
            item = layout.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.setParent(None)
                widget.deleteLater()   
    
    def tick(self):
        print("Tick")
        if not len(self.selected_cards):
            self.no_selected.setVisible(True)
            self.send_button.setVisible(False)
        else:
            self.no_selected.setVisible(False)
            self.send_button.setVisible(True)

        if not len(self.white_cards):
            self.no_cards_in_hand.setVisible(True)
        else:
            self.no_cards_in_hand.setVisible(False)

        
        #--Client
        if self.client.hand != self.hand:
            self.hand = self.client.hand
            self.set_cards(self.hand)
        
        if self.current_black_card != self.client.current_black_card:
            self.current_black_card = self.client.current_black_card
            self.set_black_card(self.current_black_card)
        
        
        




    def submit_action(self):
        #
        cards = [self.hand[int(i)] for i in self.selected_cards]
        self.client.submit_white(cards)















class Client(): #AI

    handlers = {}
    def __init__(self, name, ui, SERVER_IP = "localhost", PORT = 12345, autostart = True, force_console = False):
        self.current_black_card = {"text": "I hate ____"}
        self.answers = 1
        self.hand = {0: {"text": "the black ones the black ones the black ones", "custom_text": ""}, 1: {"text": "Chuck Norris", "custom_text": ""}} #testing hdand
        self.ui = ui
        self.force_console = force_console
        self.SERVER_IP = SERVER_IP
        self.PORT = PORT
        self.name= name
        self._register_handlers()
        self.connected = False

        if autostart:
            client_thread = threading.Thread(target=self.client_start, daemon=True)
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

            #self.ui.set_cards(self.hand) #----------------------------------------------------------------------------------------

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

                crds.append({"uuid": picked["uuid"], "custom_text": picked["text"]})
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


    
    def submit_white(self, cards): # cards = [{"uuid": uuid, "custom_text": custom_text}]
        data = {"cards": {i: v for i,v in enumerate(cards)}}
        self.send_packet({"type": "submit_white", "data": data})
        #self.send_packet({"type": "submit_white", "data": {"uuid": carduuid, "custom_text": custom_text}})
    
    def submit_rate(self, playeruuid):
        self.send_packet({"type": "submit_rate", "data": {"uuid": playeruuid}})




app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())

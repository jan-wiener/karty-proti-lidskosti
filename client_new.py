import socket
import json
import struct
import uuid
import threading
import time
import sys

from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton, QVBoxLayout, QLineEdit, QPushButton, QLayout, QLayoutItem,
    QLabel, QHBoxLayout, QGridLayout,
)
from PyQt6.QtCore import QSize, Qt, QTimer, pyqtSignal


class TextInputPopup(QWidget):
    text_submitted = pyqtSignal(str)  # Signal to emit the entered text

    def __init__(self, prompt: str, parent=None):
        super().__init__(parent)

        self.setWindowTitle("Input")
        self.setFixedSize(300, 120)

        layout = QVBoxLayout(self)

        self.label = QLabel(prompt)
        self.textbox = QLineEdit()
        self.button = QPushButton("Submit")

        layout.addWidget(self.label)
        layout.addWidget(self.textbox)
        layout.addWidget(self.button)

        self.button.clicked.connect(self.submit)

    def submit(self):
        text = self.textbox.text()
        self.text_submitted.emit(text)  # Emit the signal
        self.close()



class MainWindow(QWidget):

    def __init__(self, name = "Honza"):
        super().__init__()
        self.previous_game_stage = -1
        self.name = name
        self.client = Client(name=self.name, ui=self)
        self.setWindowTitle("Card Game")
        self.setMinimumSize(750, 900)
        self.setStyleSheet("background-color: #343536;")

        layout = QVBoxLayout()
        # Add scoreboard

        self.timer = QTimer()
        self.timer.timeout.connect(self.tick)
        self.timer.start(100)
        print(f"--------")
        #-----------------------------------------------
        self.scoreboard = QLabel("Scores:\n")
        self.scoreboard.setMargin(1)
        self.scoreboard.setStyleSheet("""
            QLabel {
                font-size: 15px;
                color: white;
            }
        """)
        # self.scoreboard.setVisible(False)

        self.black_card_area = QHBoxLayout()
        self.black_card = QPushButton()
        self.black_card.setFixedSize(100,150)
        self.black_card_area.addWidget(self.black_card)

        self.status_message = QLabel("Waiting for game")
        self.status_message.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.status_message.setMargin(12)
        self.status_message.setStyleSheet("""
            QLabel {
                font-size: 30px;
                color: white;
            }
            """)
        
        self.selected_label = QLabel("Selected Cards")
        self.selected_label.setVisible(False)
        self.selected_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.selected_label.setMargin(8)
        self.selected_label.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
            }
            """)
        self.no_selected = QLabel("-- No cards selected --")
        self.no_selected.setVisible(False)
        self.no_selected.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_selected.setMargin(20)
        self.no_selected.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
            }
            """)
        
        self.no_cards_in_hand = QLabel("-- No cards in hand --")
        self.no_cards_in_hand.setVisible(False)
        self.no_cards_in_hand.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_cards_in_hand.setMargin(20)
        self.no_cards_in_hand.setStyleSheet("""
            QLabel {
                font-size: 18px;
                color: white;
            }
            """)
        
        self.hand_label = QLabel("Your cards")
        self.hand_label.setVisible(False)
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

        self.rate_card_area = QGridLayout()

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




        
        layout.addLayout(self.black_card_area)
        layout.addWidget(self.scoreboard)
        layout.addWidget(self.status_message)
        layout.addWidget(self.selected_label)
        layout.addWidget(self.no_selected)
        layout.addLayout(self.selected_card_area)
        layout.addWidget(self.hand_label)
        layout.addLayout(self.white_card_area)
        layout.addWidget(self.no_cards_in_hand)
        #layout.addWidget(self.status_message)
        layout.addLayout(self.rate_card_area)
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
        self.logged = False
        self.feedback = None
        self.selected_for_rate = False
        
        self.hand = {0:0} #cant be {}
        self.scores = {}
        # self.hand = {0: {"text": "testing white card", "custom_text": ""}, 1: {"text": "testing white card2222222", "custom_text": ""}}
        # self.set_cards(self.hand)

        self.current_black_card = {"text": "Waiting for game"}
        self.set_black_card(self.current_black_card)

        
        # Later, you could call:


        self.setLayout(layout)

        

    def update_scoreboard(self, scoreboard, uuids):
        print("-*-----*--*-*-*-*-*-*-*")
        print(scoreboard)
        print(uuids)
        # player_score_dict = {uuids[uuid]:scoreboard[uuid] for uuid in uuids}
        player_score_dict = {}
        for uuid, playername, score in zip(uuids.keys(), uuids.values(), scoreboard.values()):
            if playername in player_score_dict.keys():
                newplayername = playername
                i = 1
                while newplayername in player_score_dict.keys() and (i := i+1):
                    newplayername = playername
                    newplayername += str(i)
                playername = newplayername
            player_score_dict[playername] = score

        print(player_score_dict)
        text = "Score:\n"
        for player, score in player_score_dict.items():
            text += f"{player}: {score}\n"
        self.scoreboard.setText(text)
        

    
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
        
        if self.client.game_stage == 1:
            self.selected_cards[card.objectName()] = card
            self.white_cards.pop(card.objectName())
            card.setParent(None)
            self.selected_card_area.addWidget(card)

            card.clicked.disconnect()
            card.clicked.connect(lambda: self.deselect_card(card))
            print(self.white_cards)


        elif self.client.game_stage == 2 and not self.selected_cards:
            cards = self.rate_cards.pop(card.objectName())
            self.selected_cards[card.objectName()] = cards
            # self.hand[int(card.objectName())]
            for ncardid in cards:
                ncard = cards[ncardid]
                ncard.setParent(None)
                self.selected_card_area.addWidget(ncard)

                ncard.clicked.disconnect()
                ncard.clicked.connect(lambda: self.deselect_card(card))
        # self.tick()
            




    def deselect_card(self, card):
        
        if self.client.game_stage == 1:
            self.white_cards[card.objectName()] = card
            self.selected_cards.pop(card.objectName())
            card.setParent(None)
            self.white_card_area.addWidget(card)

            card.clicked.disconnect()
            card.clicked.connect(lambda _, crd = card: self.select_card(crd))
            print(self.white_cards)


        elif self.client.game_stage == 2:
            cards = self.selected_cards.pop(card.objectName())
            self.rate_cards[card.objectName()] = cards
            for ncardid in cards:
                ncard = cards[ncardid]
                ncard.setParent(None)
                ncard.deleteLater()

                
                # self.rate_card_area.addWidget(card)
                # ncard.clicked.disconnect()
                # ncard.clicked.connect(lambda: self.select_card(card))

                print(self.white_cards)
            self.set_rate_cards(self.hand, connect=self.client.is_tsar, reactive=self.client.is_tsar)

        # self.tick()



    def set_cards(self, cards, reactive = True, connect = True):
        self.clear_layout(self.white_card_area)

        self.white_cards = {}
        for i in cards:
            cardui = QPushButton()
            cardui.setObjectName(f"{i}")

            self.white_cards[cardui.objectName()] = cardui
            
            card_text = cards[i]["text"]
            if card_text:
                cardui.setText(self.format_card_text(cards[i]["text"]))#cards[i]["text"]
            else:
                cardui.setText("<Žolík>")#cards[i]["text"]

                
            if connect:
                cardui.clicked.connect(lambda _, crd = cardui: self.select_card(crd))


            
            cardui.setFixedSize(100,150)    
            if reactive:
                if card_text:
                    cardui.setStyleSheet(f"""
                    QPushButton {{
                        background-color: white;
                        border: 2px solid black;
                        border-radius: 10px;
                        font-size: 12px;
                        color: black;

                    }}
                    QPushButton:hover {{
                        background-color: lightgray;
                    }}
                    """)
                else:
                    cardui.setStyleSheet(f"""
                    QPushButton {{
                        background-color: white;
                                         
                        background-image: url('stripes.png');
                        background-repeat: no-repeat;
                        background-position: center;
                                         
                        border: 2px solid black;
                        border-radius: 10px;
                        font-size: 12px;
                        color: black;

                    }}
                    QPushButton:hover {{
                        background-color: lightgray;
                    }}
                                         

                    """)
            else:
                cardui.setStyleSheet(f"""
                QPushButton {{
                    background-color: {"white" if card_text else "yellow"};
                    border: 2px solid black;
                    border-radius: 10px;
                    font-size: 12px;
                    color: black;

                }}
                QPushButton:hover {{
                    background-color: white;
                }}
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
    
    

    def clear_grid_layout(self, grid_layout):
        if not isinstance(grid_layout, QLayout):
            return

        while grid_layout.count():
            item: QLayoutItem | None = grid_layout.takeAt(0)
            assert item is not None

            if widget := item.widget():
                widget.setParent(None)
            elif item.layout():
                self.clear_grid_layout(item.layout())  

            del item  

    

    def set_rate_cards(self, cards, reactive = True, connect = True):
        self.selected_cards = {}
        self.clear_grid_layout(self.rate_card_area)
        print(f"---------------------------setting rate cards")

        self.rate_cards = {}
        for player_index in cards:
            dictname = f"{player_index}"
            self.rate_cards[dictname] = {}
            for cardid in cards[player_index]:
                card = cards[player_index][cardid]

                cardui = QPushButton()
                cardui.setObjectName(dictname)

                self.rate_cards[dictname][cardid] = cardui

                if connect:
                    cardui.clicked.connect(lambda _, crd = cardui: self.select_card(crd))


                cardui.setText(self.format_card_text(card["text"]))#cards[i]["text"]
                cardui.setFixedSize(100,150)    
                if reactive:
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
                else:
                    cardui.setStyleSheet("""
                    QPushButton {
                        background-color: white;
                        border: 2px solid black;
                        border-radius: 10px;
                        font-size: 12px;
                        color: black;

                    }
                    QPushButton:hover {
                        background-color: white;
                    }
                    """)
                self.rate_card_area.addWidget(cardui, int(cardid), int(player_index))


    def change_status(self, message):
        self.status_message.setText(message)

    def tick(self):
        # print("Tick")
        
        if not len(self.selected_cards):
            self.no_selected.setVisible(True if (not self.client.is_tsar and self.client.game_stage == 1) or (self.client.is_tsar and self.client.game_stage == 2) else False)
            self.send_button.setVisible(False)
        else:
            self.no_selected.setVisible(False)
            self.send_button.setVisible(True)

        if not len(self.white_cards):
            self.no_cards_in_hand.setVisible(True if (not self.client.is_tsar and self.client.game_stage == 1) else False)
        else:
            self.no_cards_in_hand.setVisible(False)


        
        #--Client
        if not self.client.connected and self.logged:
            self.logged = False
            self.change_status("Game server connection broken.\nTrying to reconnect..")
            self.clear_layout(self.white_card_area)
            self.clear_layout(self.selected_card_area)
            self.clear_grid_layout(self.rate_card_area)
            self.selected_label.setVisible(False)
            self.hand_label.setVisible(False)
            self.hand = {}

            self.client.__init__(name=self.name, ui=self)

        if self.client.connected and not self.logged:
            self.logged = True
            self.change_status("Game server found!\nWaiting for the game to start!")
        

        
        if self.client.feedback != self.feedback:
            self.feedback = self.client.feedback
            if self.feedback == True:
                self.change_status("CARDS SUBMITTED")
            elif self.feedback == False:
                self.change_status("There was a server error..\n Trying to reset cards..")



        if self.client.hand != self.hand and self.client.game_stage == 1:
            print(f"Game Stage: {self.client.game_stage}")
            if self.client.is_tsar:
                self.change_status("You are the tsar\nWait for the others' turn!")
                self.selected_label.setVisible(False)
                self.hand_label.setVisible(False)
            else:
                self.change_status(f"Pick {self.client.answers} cards!")
                self.selected_label.setVisible(True)
                self.hand_label.setVisible(True)


            self.hand = self.client.hand

            self.clear_layout(self.white_card_area)
            self.clear_layout(self.selected_card_area)
            self.clear_grid_layout(self.rate_card_area)

            self.selected_cards = {}

            self.set_cards(self.hand, connect=not self.client.is_tsar, reactive=not self.client.is_tsar)

        elif (self.client.cards_indexed != self.hand or self.previous_game_stage != self.client.game_stage) and self.client.game_stage == 2:
            print(f"Game Stage: {self.client.game_stage}")
            if self.client.is_tsar:
                self.change_status(f"You are the tsar\nPick the best combo! ({self.client.answers} cards)")
                self.selected_label.setVisible(True)
                self.hand_label.setVisible(True)
            else:
                self.change_status(f"Wait for the tsar to pick a card!")
                self.selected_label.setVisible(False)
                self.hand_label.setVisible(False)
            self.hand = self.client.cards_indexed

            self.clear_layout(self.white_card_area)
            self.clear_layout(self.selected_card_area)

            self.selected_cards = {}
            
            self.set_rate_cards(self.hand, connect=self.client.is_tsar, reactive=self.client.is_tsar)


        if self.client.scores != self.scores:
            self.scores = self.client.scores
            self.update_scoreboard(self.client.scores, self.client.uuids)
        

        if self.current_black_card != self.client.current_black_card:
            self.current_black_card = self.client.current_black_card
            self.set_black_card(self.current_black_card)


        if self.client.winner:
            self.change_status(f"Player {self.client.winner} won the game!")
            self.client.winner = None

        self.previous_game_stage = self.client.game_stage
        
        


    def fill(self, cards, index=None, text=""):

        if text:
            cards[index]["text"] = text
        for card in enumerate(cards):
            if not card[1]["text"]:
                self.popup = TextInputPopup(f"Fill text for card {card[0]}")
                self.popup.text_submitted.connect(lambda text, cards=cards, index=card[0]: self.fill(cards, index, text))
                self.popup.show()
                return
        self.client.submit_white(cards)


    def submit_action(self):

        if self.client.game_stage == 1:
            cards = [self.hand[int(i)] for i in self.selected_cards]
            
            for card in cards:
                assert type(card) == dict
                if not card["text"]:
                    self.fill(cards)
                    return

            self.client.submit_white(cards)
        elif self.client.game_stage == 2:
            self.client.submit_rate(self.client.uuiddict[int(list(self.selected_cards.keys())[0])])





























class Client(): #AI

    handlers = {}
    def __init__(self, name, ui, SERVER_IP = "localhost", PORT = 12345, autostart = True, force_console = False):
        self.feedback = None
        self.scores = {}
        self.uuids = {}
        self.winner = None
        self.cards_indexed = {}
        self.uuiddict = {}
        self.game_stage = 0 # 0 = before login, 1 = round, 2 = rating, 3 = round end, 4 = game end
        self.is_tsar = False
        self.current_black_card = {"text": "Waiting for game"}
        self.answers = 1
        self.hand = {0: {"text": "the black ones the black ones the black ones", "custom_text": ""}, 1: {"text": "Chuck Norris", "custom_text": ""}} #testing hdand
        self.ui = ui
        self.force_console = force_console
        self.SERVER_IP = SERVER_IP
        self.PORT = PORT
        self.name= name

        self.once = False
        if not self.once:
            self._register_handlers()
            self.once = True

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
            while True:
                try:
                    self.sock.connect((self.SERVER_IP, self.PORT))
                except:
                    print("Server not found, reconnecting in 2s")
                    time.sleep(2)
                    continue
                break

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

    @staticmethod
    def packet_handler(packet_type):
        def decorator(func):
            func._packet_type = packet_type
            return func
        return decorator
    
    def _register_handlers(self):
        for attr_name in dir(self):
            method = getattr(self, attr_name)
            if callable(method) and hasattr(method, "_packet_type"):
                self.handlers[method._packet_type] = method # type: ignore



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
        self.is_tsar = False
        self.feedback = None
        self.game_stage = 1
        self.current_black_card = data["black"]
        self.answers = self.current_black_card["answers"]
        self.scores = data["scoreboard"]
        self.uuids = data["uuids"]
        print(f"Current black card: {self.current_black_card["text"]}")
        if data["tsar"]:
            self.is_tsar = True
            self.hand = {}
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

                crds.append({"uuid": picked["uuid"], "text": picked["text"]})
            self.submit_white(crds)

        #for i in range(len(cards)):
        #    self.hand[i] = cards[i]
    

    @packet_handler("round_rate_feedback")
    def recv_round_feedback(self, data):
        self.feedback = data["status"]
        print(self.feedback)

    
    @packet_handler("rate_info")
    def recv_rate_info(self, data):
        self.game_stage = 2
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
        self.game_stage = 3
        self.round_winner = data["winner"]
        self.round_winner_uuid = data["uuid"]
        # self.winning_card = data["card"]

        # ------------------------------------Terminal access
        print(f"Player {self.round_winner} won this round ")

    
    @packet_handler("game_end")
    def recv_game_end(self, data):
        self.game_stage = 4
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


    
    def submit_white(self, cards): # cards = [{"uuid": uuid, "text": custom_text}]
        data = {"cards": {i: v for i,v in enumerate(cards)}}
        self.send_packet({"type": "submit_white", "data": data})
        #self.send_packet({"type": "submit_white", "data": {"uuid": carduuid, "custom_text": custom_text}})
    
    def submit_rate(self, playeruuid):
        self.send_packet({"type": "submit_rate", "data": {"uuid": playeruuid}})




app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())

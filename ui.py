from PyQt6.QtWidgets import (
    QApplication, QWidget, QPushButton,
    QLabel, QVBoxLayout, QHBoxLayout, QGridLayout,
)
from PyQt6.QtGui import (
    QIcon
)
from PyQt6.QtCore import QSize
from PyQt6.QtCore import Qt
import sys


from PyQt6.QtWidgets import QApplication, QWidget, QVBoxLayout
import sys

from client import *


# Import your custom widget
# from scoreboard_widget import ScoreboardWidget

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Card Game")
        self.setMinimumSize(600, 400)
        self.setStyleSheet("background-color: #343536;")

        layout = QVBoxLayout()
        # Add scoreboard



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

        self.hand = {0: {"text": "the black ones the black ones the black ones"}, 1: {"text": "Chuck Norris"}}
        self.set_cards(self.hand)

        black_card = {"text": "I hate ____"}
        self.set_black_card(black_card)
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
        
        self.selected_cards[card.objectName()] = card
        self.white_cards.pop(card.objectName())
        card.setParent(None)
        self.selected_card_area.addWidget(card)

        card.clicked.disconnect()
        card.clicked.connect(lambda: self.deselect_card(card))
        print(self.white_cards)

        if len(self.selected_cards):
            self.no_selected.setVisible(False)
        if not len(self.white_cards):
            self.no_cards_in_hand.setVisible(True)

    def deselect_card(self, card):
        
        self.white_cards[card.objectName()] = card
        self.selected_cards.pop(card.objectName())
        card.setParent(None)
        self.white_card_area.addWidget(card)

        card.clicked.disconnect()
        card.clicked.connect(lambda: self.select_card(card))
        print(self.white_cards)

        if not len(self.selected_cards):
            self.no_selected.setVisible(True)
        if len(self.white_cards):
            self.no_cards_in_hand.setVisible(False)


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
    
    def submit_action(self):
        cards = None




app = QApplication(sys.argv)
window = MainWindow()
window.show()
sys.exit(app.exec())




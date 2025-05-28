
import random
import time
import threading



global_players = {}


class Player():
    def __init__(self, name, force_id = 0):
        self.name = name
        self.id = force_id if force_id else max(list(global_players.keys()) + [0]) + 1 ### set ID
        global_players[self.id] = self

        self.reset()


    def reset(self):
        self.isInGame = False
        self.hand = []
        self.played_move = False
        self.score = 0



class Card():
    def __init__(self, text, color = False, help: str = ""): #False color = white, True = black
        self.text = text
        self.help = help
        self.color = color





black_cards = [f"Hey, ___{i}" for i in range(20)]
white_cards = [Card(f"jews{i}", False, "Nigga") for i in range(22)]



class Game():
    def __init__(self, players, max_points, black_cards, white_cards, max_cards = 8, deck_rules = False, hand_duplicate = False, auto_start = True): # deck_rules and hand_duplicate are mutually exclusive
        self.players = players # {playerid: playerobject}, self.players.values() for playerobjects, self.players for ids/keys 

        for i in self.players:
            self.players[i].isInGame = True

        self.change_settings(max_points, black_cards, white_cards, max_cards, deck_rules, hand_duplicate)

        self.started = False
        
        if auto_start: 
            self.game_start()
    

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


    def submit_card(self, card, player):
        if card not in player.hand or player.played_move or self.tsar == player: 
            print(f"NOT FATAL: Can't submit card, stolen card: {card not in player.hand}, has played: {player.played_move}, is tsar: {self.tsar == player}")
            return None

        self.submitted_cards[player.id] = card
        player.hand.remove(card)
        player.played_move = True



    def get_winner(self):
        for player in self.players.values():
            if player.score >= self.max_points:
                return player
        return None

    def rate(self, player):
        # tsar has to pick a card
        if self.tsar == player or not self.submitted_cards: 
            print(F"NOT FATAL: tsar {player.name}? picked himself; OR it wasn't rating phase")
            return None #cant pick himself

        self.round_winner = player
        self.round_winner.score = self.round_winner.score + 1
        return player

    def round(self):
        self.rounds = self.rounds + 1

        for i in global_players[1].hand:             ###TESTING
            print(f"{i.text} {i.help} {i.color}")    ###---
        
        # print(F"testing")
        # self.game_start()


        #pick a tsar
        #print([i.name for i in list(self.players.values())])
        self.tsar = list(self.players.values())[list(self.players.values()).index(self.tsar)+1 if list(self.players.values()).index(self.tsar)+1 < len(self.players) else 0]
        
        print(f"Round no. {self.rounds}")
        print(f"{self.tsar.name} is the tsar!")



        self.submitted_cards = {} # player: card

        print(f"awaiting Cards")
        while len(self.submitted_cards) < len(self.players)-1: #-1 for tsar
            #print(f"awaiting Cards, submitted cards: {self.submitted_cards}")
            time.sleep(1)
        print(f"cards submitted!")
        

        print(self.submitted_cards)


        self.round_winner = False #placeholder
        print(f"awating Rating, ")
        while not self.round_winner:
            time.sleep(1)

        print(f"{self.round_winner.name} won this round")

        for player in self.players.values():
            player.played_move = False

        time.sleep(1)

        if winner := self.get_winner():
            print(f"Player {winner.name} won the Game!")
            return winner
        return self.round()

    


    


if __name__ == "__main__":

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








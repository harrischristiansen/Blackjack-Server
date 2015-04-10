'''
	@ Harris Christiansen (Harris@HarrisChristiansen.com)
	2015-04-05
	For: Purdue Hackers Recursion - Blackjack Server
'''

import socket
import time
from thread import start_new_thread
import threading
import random

port = 9999

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
s.bind(('', port))
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) # Make Address Reusable - No Lockout
s.listen(10)

players = []
gameInProgress = False

cards = {'Ace Of Spades': 11, 'Two Of Spades': 2, 'Three Of Spades': 3, 'Four Of Spades': 4,
		'Five Of Spades': 5, 'Six Of Spades': 6, 'Seven Of Spades': 7, 'Eight Of Spades': 8,
		'Nine Of Spades': 9, 'Ten Of Spades': 10, 'Jack Of Spades': 10, 'Queen Of Spades': 10, 'King Of Spades': 10,
		'Ace Of Hearts': 11, 'Two Of Hearts': 2, 'Three Of Hearts': 3, 'Four Of Hearts': 4,
		'Five Of Hearts': 5, 'Six Of Hearts': 6, 'Seven Of Hearts': 7, 'Eight Of Hearts': 8,
		'Nine Of Hearts': 9, 'Ten Of Hearts': 10, 'Jack Of Hearts': 10, 'Queen Of Hearts': 10, 'King Of Hearts': 10,
		'Ace Of Clubs': 11, 'Two Of Clubs': 2, 'Three Of Clubs': 3, 'Four Of Clubs': 4,
		'Five Of Clubs': 5, 'Six Of Clubs': 6, 'Seven Of Clubs': 7, 'Eight Of Clubs': 8,
		'Nine Of Clubs': 9, 'Ten Of Clubs': 10, 'Jack Of Clubs': 10, 'Queen Of Clubs': 10, 'King Of Clubs': 10,
		'Ace Of Diamonds': 11, 'Two Of Diamonds': 2, 'Three Of Diamonds': 3, 'Four Of Diamonds': 4,
		'Five Of Diamonds': 5, 'Six Of Diamonds': 6, 'Seven Of Diamonds': 7, 'Eight Of Diamonds': 8,
		'Nine Of Diamonds': 9, 'Ten Of Diamonds': 10, 'Jack Of Diamonds': 10, 'Queen Of Diamonds': 10, 'King Of Diamonds': 10
		}

deck = []
def shuffledDeck(numDecks):
	global deck, cards
	deck = []
	for i in range(numDecks):
		for key, value in cards.iteritems():
			deck.append(key)
	random.shuffle(deck)

def requestBets():
	global players

	for p in players:
		p.acceptingBets = True

	NotifyAllPlayers("Please Make Your Bet")

	for p in players: # Wait For All Players To Place Bet
		while(p.acceptingBets):
			time.sleep(1)

def initialDeal():
	global deck, players

	for p in players: # Deal First Card
		p.hand.append(deck.pop())
	for p in players: # Deal Second Card
		p.hand.append(deck.pop())
	
	NotifyAllPlayersHands()

def handAmount(hand):
	total = 0
	for c in hand:
		total += cards[c]
	for c in hand:
		if ('Ace' in c) and total > 21:
			total -= 10

	return total

def NotifyAllPlayersHands():
	for p in players:
		p.sendMsg("You: "+str(handAmount(p.hand))+": "+','.join(p.hand))
		for p2 in players:
			if p != p2:
				p2.sendMsg("Other Player: "+str(handAmount(p.hand))+": "+','.join(p.hand))

def NotifyAllPlayers(msg):
	print "Message Sent To All Players: "+msg
	for p in players:
		p.sendMsg(msg)

def BlackjackGame():
	global players, gameInProgress

	# Game Logic Goes Here
	while(True):
		gameInProgress = False
		while(len(players) < 2): # Wait For Players To Join Game
			if(len(players) == 1):
				NotifyAllPlayers("Waiting For Another Player To Join The Game")
			time.sleep(1)
		time.sleep(5) # Give All Player Threads Time To Join
		gameInProgress = True

		NotifyAllPlayers("The Game Has Started")

		##### Request Bets #####
		requestBets()

		##### Deal Initial Hands #####
		if len(deck) < len(players)*10: # Make Sure Deck Is Large Enough
			NotifyAllPlayers("Dealing A New Deck")
			shuffledDeck(2)
		initialDeal()

		time.sleep(1)
		NotifyAllPlayers("Playing The Game...")
		time.sleep(2)
		NotifyAllPlayers("Playing The Game...")
		time.sleep(3)
		NotifyAllPlayers("Playing The Game...")
		time.sleep(4)
		NotifyAllPlayers("Game Over")

class BlackjackPlayer(threading.Thread):
	def __init__(self,c):
		super(self.__class__, self).__init__()
		self.c = c
		self.hand = []
		self.chips = 1000
		self.acceptingBets = False
		self.bet = 0
		self.acceptingRequests = False
		self.request = ""

	def sendMsg(self,msg):
		self.c.sendall(msg+"\n")

	def run(self):
		global players, gameInProgress
		
		while(gameInProgress):
			self.sendMsg("Please wait for current round to finish")
			time.sleep(1)

		NotifyAllPlayers("A Player Has Joined The Game")
		players.append(self)
		self.sendMsg("Welcome To Blackjack!")

		while True:
			data = self.c.recv(1024)
			if not data: # Client Closed Connection
				self.acceptingBets = False
				players.remove(self)
				print "Player Left Game"
				break

			if(self.acceptingBets):
				try:
					self.bet = int(data)
					if (self.chips - self.bet) < 0:
						self.sendMsg("Invalid Bet. You Only Have: "+str(self.chips))
					else:
						self.chips = self.chips - self.bet
						self.acceptingBets = False
				except ValueError:
					self.sendMsg("Invalid Bet")

			if(self.acceptingRequests):
				if "hit" in data.lower():
					self.request = "hit"


		self.c.close()

start_new_thread(BlackjackGame, ()) # Start Blackjack Game Thread

while True:
	# blocking call, waits to accept a connection
	c, addr = s.accept()
	print "Client Connected: " + addr[0] + ":" + str(addr[1])

	thread = BlackjackPlayer(c)
	thread.setDaemon(True) # Set as background thread
	thread.start()

s.close()
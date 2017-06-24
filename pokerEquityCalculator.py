import random
import time

"""
	Defining a function with

	@executionTime
	def myFunction():
		...

	will print out the runtime of myFunction every
	time it is called
"""
def executionTime(func):
	def returnFunc(*args):
		start = time.clock()
		func(*args)
		end = time.clock()
		print("Execution Time: " + str(end - start) + " seconds")
	return returnFunc

# a list with the four suits, so it's easy to fill the deck with iteration
suits = []
suits.append("hearts")
suits.append("diamonds")
suits.append("clubs")
suits.append("spades")

# a dictionary for translating back and forth between royal card name and value
royals = dict()
royals["11"] = "jack"
royals["12"] = "queen"
royals["13"] = "king"
royals["14"] = "ace"
royals["jack"] = 11
royals["queen"] = 12
royals["king"] = 13
royals["ace"] = 14

# given a card's value, return its name
def setCardName(value):
	try:
		return royals[str(value)]
	except:
		return str(value)

# given a card's name, return its value
def setCardValue(name):
	try:
		return royals[name]
	except:
		return int(name)

# a dictionary for easy hand comparison
handRank = dict()
handRank["highCard"] = 0
handRank["onePair"] = 1
handRank["twoPair"] = 2
handRank["threeOfAKind"] = 3
handRank["straight"] = 4
handRank["flush"] = 5
handRank["fullHouse"] = 6
handRank["quads"] = 7
handRank["straightFlush"] = 8

# called when hand1 and hand2 are of the same type; compares the kickers of hand1 and hand2
def compareRanks(hand1, hand2, numKickers):
	for i in range(numKickers):
			if hand1.finalHand["ranks"][i] > hand2.finalHand["ranks"][i]:
				return hand1
			elif hand1.finalHand["ranks"][i] < hand2.finalHand["ranks"][i]:
				return hand2
	return

"""
	The following functions compare hand1 and hand2 when they have the same type
"""

def compareHighCard(hand1, hand2):
	for i in range(6, 1, -1):
		if hand1.cards[i].value > hand2.cards[i].value:
			return hand1
		elif hand1.cards[i].value < hand2.cards[i].value:
			return hand2
	return 

def compareOnePair(hand1, hand2):
	if hand1.finalHand["card"] > hand2.finalHand["card"]:
		return hand1
	elif hand1.finalHand["card"] < hand2.finalHand["card"]:
		return hand2
	else:
		return compareRanks(hand1, hand2, 3)

def compareTwoPair(hand1, hand2):
	if hand1.finalHand["firstPair"] > hand2.finalHand["firstPair"]:
		return hand1
	elif hand1.finalHand["firstPair"] < hand2.finalHand["firstPair"]:
		return hand2
	elif hand1.finalHand["secondPair"] > hand2.finalHand["secondPair"]:
		return hand1
	elif hand1.finalHand["secondPair"] < hand2.finalHand["secondPair"]:
		return hand2
	else:
		return compareRanks(hand1, hand2, 1)

def compareThreeOfAKind(hand1, hand2):
	if hand1.finalHand["card"] > hand2.finalHand["card"]:
		return hand1
	elif hand1.finalHand["card"] < hand2.finalHand["card"]:
		return hand2
	else:
		return compareRanks(hand1, hand2, 2)

def compareStraight(hand1, hand2):
	if hand1.finalHand["highCard"] > hand2.finalHand["highCard"]:
		return hand1
	elif hand1.finalHand["highCard"] < hand2.finalHand["highCard"]:
		return hand2
	return

def compareFlush(hand1, hand2):
	for i in range(5):
		if hand1.finalHand["flush"][i].value > hand2.finalHand["flush"][i].value:
			return hand1
		elif hand1.finalHand["flush"][i].value < hand2.finalHand["flush"][i].value:
			return hand2
	return

def compareFullHouse(hand1, hand2):
	if hand1.finalHand["over"] > hand2.finalHand["over"]:
		return hand1
	elif hand1.finalHand["over"] < hand2.finalHand["over"]:
		return hand2
	elif hand1.finalHand["under"] > hand2.finalHand["under"]:
		return hand1
	elif hand1.finalHand["under"] < hand2.finalHand["under"]:
		return hand2
	return

def compareQuads(hand1, hand2):
	if hand1.finalHand["card"] > hand2.finalHand["card"]:
		return hand1
	elif hand1.finalHand["card"] < hand2.finalHand["card"]:
		return hand2
	else:
		return compareRanks(hand1, hand2, 1)

def compareStraightFlush(hand1, hand2):
	if hand1.finalHand["highCard"] > hand2.finalHand["highCard"]:
		return hand1
	elif hand1.finalHand["highCard"] > hand2.finalHand["highCard"]:
		return hand2
	return

"""
	The list of functions 'compareFunctions' makes a nasty if-statement
	unnecessary later. If two hands are of the same type, we can compare them 
	simply with

		compareFunctions[handRank[hand1.finalHand["handName"]]](hand1, hand2)

"""
compareFunctions = []
compareFunctions.append(compareHighCard)
compareFunctions.append(compareOnePair)
compareFunctions.append(compareTwoPair)
compareFunctions.append(compareThreeOfAKind)
compareFunctions.append(compareStraight)
compareFunctions.append(compareFlush)
compareFunctions.append(compareFullHouse)
compareFunctions.append(compareQuads)
compareFunctions.append(compareStraightFlush)

# prints a list of cards
def printCardList(cards):
	for card in cards:
		card.printCard()

class Card:

	"""
		The Card class is an object that represents an individual card.
		It stores card value, card name, and card suit, and provides a 
		function for printing an object of type Card.
	"""

	def __init__(self, val, suit, name):
		self.value = val
		self.name = str(name)
		self.suit = suit

	def printCard(self):
		print(self.name + ", " + self.suit)

class Hand:

	"""
		The Hand class is an object that represents a poker hand. Each
		instance of the Hand class stores an individual player's 7 possible
		cards, and processes these cards as inputs to find the best 5-card hand.
	"""

	def __init__(self, cards):
		# the original 7 cards, sorted in ascending order
		self.cards = self.sortCards(cards)
		# a list for storing how many cards of each value there are (starts at 0 for all values)
		self.cardQuantities = [0] * 15
		# information about each possible hand
		self.straightFlushHighCard = None
		self.flushDraws = dict(
			hearts = [],
			diamonds = [],
			spades = [],
			clubs = []
		)
		self.flush = []
		self.straightHighCard = None
		self.quads = None
		self.trips = None
		self.bestPair = None
		self.secondPair = None
		# stores the information about the final hand in a dictionary
		self.finalHand = dict()
		# determine the best 5 cards
		self.getHandInfo()
		self.getFinal()

	# sort a list of cards by value
	def sortCards(self, cards):
		return sorted(cards, key = lambda x: x.value)

	# determines a player's possible hands
	def getHandInfo(self):
		cards = self.cards
		cardsLength = len(cards)
		aceInserted = False
		# if a player has an ace, copy it and put it at the beginning of cards
		# this makes it easier to determine if a player has a straight
		if cards[cardsLength - 1].name == "ace":
			cards.insert(0, Card(1, cards[cardsLength - 1].suit, "ace"))
			cardsLength = len(cards)
			aceInserted = True
		# 'run' will store the longest run of consecutive cards in the hand
		run = [cards[0]]
		# if straightFlushCount == 5 at the end of the loop, then the player
		# has a straight flush
		straightFlushCount = 1
		# remembers the current suit (for determining straight flush)
		curSuit = cards[0].suit
		# iterate once over the seven cards
		for i in range(cardsLength):
			# building a consecutive run of cards
			# checks only to the second-to-last card to prevent a 'list index out of range' error
			if i < cardsLength - 1:
				runLength = len(run)
				# if the next card is consecutive
				if cards[i + 1].value - run[runLength - 1].value == 1:
					# add the next card to the potential straight
					run.append(cards[i + 1])
					# if the suit is the same, add 1 toward a straight flush
					if cards[i + 1].suit == curSuit:
						straightFlushCount += 1
					# otherwise reset the straight flush counter and the current suit
					else:
						straightFlushCount = 1
						curSuit = cards[i + 1].suit
					# if the hand has more than 5 cards to a straight, remove the lowest card 
					if len(run) > 5:
						run.pop(0)
				# if the next card isn't consecutive, reset the straight draw
				elif runLength < 5:
					run = [cards[i + 1]]
			# ignore the copied ace, if there is one
			if cards[i].value != 1:
				# add 1 to the number of cards in the hand with the same value
				self.cardQuantities[cards[i].value] += 1
				# add the card to the list of cards of the same suit
				self.flushDraws[cards[i].suit].append(cards[i])
		# if there are at least 5 consecutive cards, the player has a straight
		if len(run) >= 5:
			self.straightHighCard = run[len(run) - 1]
		# if there are at least 5 cards to a straight flush, the player has a straight flush
		if straightFlushCount >= 5:
			self.straightFlushHighCard = self.straightHighCard
		# if there are at least 5 cards of a given suit, the player has a flush
		heartsLength = len(self.flushDraws["hearts"])
		diamondsLength = len(self.flushDraws["diamonds"])
		spadesLength = len(self.flushDraws["spades"])
		clubsLength = len(self.flushDraws["clubs"])
		if heartsLength >= 5:
			self.flush = self.flushDraws["hearts"][(heartsLength - 5):heartsLength]
		elif diamondsLength >= 5:
			self.flush = self.flushDraws["diamonds"][(diamondsLength - 5):diamondsLength]
		elif spadesLength >= 5:
			self.flush = self.flushDraws["spades"][(spadesLength - 5):spadesLength]
		elif clubsLength >= 5:
			self.flush = self.flushDraws["clubs"][(clubsLength - 5):clubsLength]
		# if there is a copied ace, remove it from the hand
		if aceInserted:
			cards.pop(0)
		# Iterate from highest to lowest over the list containing the quantity of each card value.
		# This is very bad design; the inclusion of this extra loop slows the program down by ~25%.
		# I could probably fix it by adjusting the first loop to iterate in descending order, but
		# I don't care enough.
		for i in range(len(self.cardQuantities) - 1, 1, -1):
			# check for quads
			if self.cardQuantities[i] == 4:
				self.quads = i
			# check for trips
			if self.cardQuantities[i] == 3 and self.trips == None:
				self.trips = i
			# set the highest pair
			if self.cardQuantities[i] == 2 and self.bestPair == None:
				self.bestPair = i
			# set the second pair
			elif self.cardQuantities[i] == 2 and self.secondPair == None:
				self.secondPair = i

	# determine all the necessary info about the final 5-card hand
	def getFinal(self):
		if self.straightFlushHighCard != None:
			self.finalHand["handName"] = "straightFlush"
			self.finalHand["highCard"] = self.straightFlushHighCard.value
		elif self.quads != None:
			self.finalHand["handName"] = "quads"
			self.finalHand["card"] = self.quads
			# by "ranks" I really mean "kickers" but I'm too lazy to go change it everywhere
			self.finalHand["ranks"] = []
			for i in range(6, 1, -1):
				if self.cards[i].value != self.quads:
					self.finalHand["ranks"].append(self.cards[i].value)
					break
		elif self.trips != None and self.bestPair != None:
			self.finalHand["handName"] = "fullHouse"
			self.finalHand["over"] = self.trips
			self.finalHand["under"] = self.bestPair
		elif self.flush != []:
			self.finalHand["handName"] = "flush"
			self.finalHand["flush"] = self.flush
		elif self.straightHighCard != None:
			self.finalHand["handName"] = "straight"
			self.finalHand["highCard"] = self.straightHighCard.value
		elif self.trips != None:
			self.finalHand["handName"] = "threeOfAKind"
			self.finalHand["card"] = self.trips
			self.finalHand["ranks"] = []
			for i in range(6, 1, -1):
				if self.cards[i].value != self.trips:
					if len(self.finalHand["ranks"]) < 2:
						self.finalHand["ranks"].append(self.cards[i].value)
					elif len(self.finalHand["ranks"]) == 2:
						break
		elif self.bestPair != None and self.secondPair != None:
			self.finalHand["handName"] = "twoPair"
			self.finalHand["firstPair"] = self.bestPair
			self.finalHand["secondPair"] = self.secondPair
			self.finalHand["ranks"] = []
			for i in range(6, 1, -1):
				if self.cards[i].value != self.bestPair and self.cards[i].value != self.secondPair:
					self.finalHand["ranks"].append(self.cards[i].value)
					break
		elif self.bestPair != None:
			self.finalHand["handName"] = "onePair"
			self.finalHand["card"] = self.bestPair
			self.finalHand["ranks"] = []
			for i in range(6, 1, -1):
				if self.cards[i].value != self.bestPair:
					if len(self.finalHand["ranks"]) < 3:
						self.finalHand["ranks"].append(self.cards[i].value)
					elif len(self.finalHand["ranks"]) == 3:
						break
		else:
			self.finalHand["handName"] = "highCard"

# compare the hands
def compareHands(hand1, hand2):
	rank1 = handRank[hand1.finalHand["handName"]]
	rank2 = handRank[hand2.finalHand["handName"]]
	if rank1 > rank2:
		return hand1
	elif rank2 > rank1:
		return hand2
	else: 
		return compareFunctions[rank1](hand1, hand2)

class Deck:

	"""
		The Deck class is an object that contains the 52 cards of a standard
		deck. Each instance provides functions for drawing a random card and adding or removing
		a specific card.
	"""

	def __init__(self):
		self.cards = []
		self.fillDeck()
		self.deckSize = len(self.cards) - 1

	def fillDeck(self):
		for value in range(2, 15):
			for suit in range(4):
				self.cards.append(Card(value, suits[suit], setCardName(value)))

	def drawCard(self):
		if (self.deckSize > 0):
			returnCard = self.cards.pop(random.randint(0, self.deckSize))
			self.deckSize = len(self.cards) - 1
			return returnCard
		return

	def addCard(self, card):
		self.cards.append(card)
		self.deckSize += 1

	def removeCard(self, card):
		self.cards.remove(card)
		self.deckSize -= 1

# given two hands and a deck, calculate the equity of each hand
@executionTime
def calculateOdds(hand1, hand2, deck):
	equity1 = 0
	equity2 = 0
	tie = 0
	# the number of times to run the calculator
	runs = 100000
	for i in range(runs):
		board = []
		# draw 5 cards for the board
		for j in range(5):
			board.append(deck.drawCard())
		# build the first hand
		hand1Final = Hand(hand1 + board)
		# build the second hand
		hand2Final = Hand(hand2 + board)
		# determine the winner
		winner = compareHands(hand1Final, hand2Final)
		# adjust the equity appropriately
		if winner == hand1Final:
			equity1 += 1
		elif winner == hand2Final:
			equity2 += 1
		else:
			tie += 1
		# add the cards on the board back into the deck
		for card in board:
			deck.addCard(card)
	print("Equity (Hand 1): " + str(equity1 / runs))
	print("Equity (Hand 2): " + str(equity2 / runs))
	print("Tie: " + str(tie / runs))
	print()

# get a card as an input from the user
def inputCard(prompt):
	cardStr = input(prompt).lower()
	cardInfo = cardStr.split(" ")
	return Card(setCardValue(cardInfo[0]), cardInfo[1], cardInfo[0])

hand1 = []
hand2 = []
# get the deck and the hands
deck = Deck()
print("Enter all cards exactly as <value> <suit>")
hand1.append(inputCard("Your 1st card: "))
hand1.append(inputCard("Your 2nd card: "))
hand2.append(inputCard("Your opponent's 1st card: "))
hand2.append(inputCard("Your opponent's 2nd card: "))
print("Hand 1:\n")
printCardList(hand1)
print("\nHand 2:\n")
printCardList(hand2)
print()
board = []
# draw 5 cards for the board
for i in range(5):
	board.append(deck.drawCard())
# calculate the odds
calculateOdds(hand1, hand2, deck)





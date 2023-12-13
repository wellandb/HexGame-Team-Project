from random import choice
from re import X

class Board:
	def __init__(self, size=11, red_first=True):
		self.__board_size = size
		self.__board = []

		self.red_turn = red_first

		self.__red_value = 'R'
		self.__blue_value = 'B'
		self.__empty_value = '0'

		self.neighbour_offsets = [ (0, -1), (1, -1), (-1, 0), (1, 0), (-1, 1), (0, 1) ]
		self.populate()

	def getBoardSize(self):
		return self.__board_size

	def getRedValue(self):
		return self.__red_value

	def getBlueValue(self):
		return self.__blue_value

	def getEmptyValue(self):
		return self.__empty_value

	def setRedTurn(self):
		self.red_turn = True

	def setBlueTurn(self):
		self.red_turn = False

	def togglePlayerTurn(self):
		self.red_turn = not self.red_turn
		
	def populate(self):
		for i in range(self.__board_size ** 2):
			self.__board.append(self.__empty_value)

	def getNeighbours(self, x, y):
		return [(x + i, y + j) for i, j in self.neighbour_offsets]

	def __getIndex(self, x, y):
		if x < 0:
			raise IndexError(f"Expected x >= 0. Got x = {x}.")

		if y < 0:
			raise IndexError(f"Expected y >= 0. Got y = {y}.")

		if x >= self.__board_size:
			raise IndexError(f"Expected x < {self.__board_size}. Got x = {x}.")

		if y >= self.__board_size:
			raise IndexError(f"Expected y < {self.__board_size}. Got y = {y}.")


		return y * self.__board_size + x

	def __setPiece(self, x, y, value):
		if self.getPiece(x, y) != self.__empty_value:
			self.printBoard()
			raise ValueError(f"There is already a piece at ({x}, {y}).")
		
		self.__board[self.__getIndex(x, y)] = value
	
	def setRedPiece(self, x, y):
		self.__setPiece(x, y, self.__red_value)

	def setBluePiece(self, x, y):
		self.__setPiece(x, y, self.__blue_value)

	def getPiece(self, x, y):
		return self.__board[self.__getIndex(x, y)]

	def isRed(self, x, y):
		return self.getPiece(x, y) == self.__red_value

	def isBlue(self, x, y):
		return self.getPiece(x, y) == self.__blue_value

	def isEmpty(self, x, y):
		return self.getPiece(x, y) == self.__empty_value

	def hexDist(self, x0, y0, x1, y1):
		dx = x0 - x1
		dy = y0 - y1

		if (dx < 0 and dy < 0) or (dx > 0 and dy > 0):
			return abs(dx + dy)

		return max(abs(dx), abs(dy))

	def __shortestPath(self, x0, y0, x1, y1):
		found = PriorityQueue(lowest_to_highest=False)
		searched = []
		path = []

		colour = self.getPiece(x0, y0)

		if self.getPiece(x1, y1) != colour:
			return None, None

		found.add((x0, y0, None, None), self.hexDist(x0, y0, x1, y1))
		
		while not found.isEmpty():
			x, y, px, py = found.pop()
			searched.append((x, y))
			path.append((px, py))

			if (x, y) == (x1, y1):
				return searched, path

			for i, j in self.getNeighbours(x, y):
				try:
					c = self.getPiece(i, j)
				except IndexError:
					c = None

				if c == colour and (i, j) not in searched:
					found.add((i, j, x, y), self.hexDist(i, j, x1, y1))

		return searched, None

	def shortestPath(self, x0, y0, x1, y1):
		searched, path = self.__shortestPath(x0, y0, x1, y1)

		if path == None:
			return None

		order = [(x0, y0)]
		current = (x1, y1)

		while current != (x0, y0):
			order.insert(1, current)
			i = searched.index(current)
			current = path[i]

		return order


	def connected(self, x0, y0, x1, y1):
		path = self.__shortestPath(x0, y0, x1, y1)

		if path == None:
			return False

		return True

	def __getColour(self, colour):
		array = []

		for x in range(self.__board_size):
			for y in range(self.__board_size):
				if self.getPiece(x, y) == colour:
					array.append((x, y))

		return array
	
	def groupBridges(self, colour):
		def addToBridgeGroup(found, group):
			"""
			"""
			searched = [] # Instantiate an array of searched nodes (that have been grouped with all possible neighbours).

			while (len(group) > 0):
				x, y = group.pop(0)
				for i, j in self.getNeighbours(x, y):
					if (i, j) in found:
						found.remove((i, j))
						group.append((i, j))

				searched.append((x, y))

			return searched, found


		found = self.__getColour(colour)
		groups = []

		while len(found) > 0:
			group, found = addToBridgeGroup(found, [found.pop(0)])
			groups.append(group)

		return groups

	def isRedWinner(self):
		groups = self.groupBridges(self.__red_value)

		for group in groups:
			sideA, sideB = False, False

			for x,_ in group:
				if x == 0:
					sideA = True

				elif x == self.__board_size - 1:
					sideB = True

			if sideA and sideB:
				return True

		return False

	def isBlueWinner(self):
		groups = self.groupBridges(self.__blue_value)

		for group in groups:
			sideA, sideB = False, False

			for _,y in group:
				if y == 0:
					sideA = True

				elif y == self.__board_size - 1:
					sideB = True

			if sideA and sideB:
				return True

		return False

	def getWinner(self):
		if self.isRedWinner():
			return self.__red_value

		elif self.isBlueWinner():
			return self.__blue_value

		return self.__empty_value

	def isWinner(self):
		return not self.getWinner() == self.__empty_value

	def printBoard(self):
		s = ""
		for x in range(self.__board_size):
			s += " " * x
			for y in range(self.__board_size):
				s += self.getPiece(x, y) + " "
			s += "\n"
		print(s)


	def makeMove(self, move):
		x, y = move

		if self.red_turn:
			self.setRedPiece(x, y)
		else:
			self.setBluePiece(x, y)

		self.togglePlayerTurn()

	def turn(self):
		if self.red_turn:
			return self.__red_value
		return self.__blue_value

	def moves(self):
		return self.__getColour(self.__empty_value)

	def copy(self):
		new_board = Board(self.__board_size)

		for x in range(self.__board_size):
			for y in range(self.__board_size):
				colour = self.getPiece(x, y)
				new_board.__setPiece(x, y, colour)

		return new_board

class PriorityQueue:
	def __init__(self, lowest_to_highest=True):
		self.__score_values = {}
		self.__scores = []
		self.__lowest_to_highest = lowest_to_highest

	def add(self, value, score):
		if score not in self.__scores:
			self.__score_values[score] = []
			self.__scores.append(score)

		self.__score_values[score].append(value)

	def pop(self):
		score = max(self.__scores)

		if self.__lowest_to_highest:
			score = min(self.__scores)

		values = self.__score_values[score]

		if len(values) == 1:
			self.__scores.remove(score)
			self.__score_values.pop(score)

			return values[0]

		value = choice(values)
		self.__score_values[score].remove(value)
		return value

	def isEmpty(self):
		return len(self.__scores) == 0
	
	


if __name__ == "__main__":
	board = Board()

	

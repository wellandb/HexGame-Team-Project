import math, Board
from random import choice
from time import time

class MCTSNode:
	def __init__(self, default_outcome, move=None, parent=None):
		self.move = move
		self.parent = parent
		self.visits = 0
		self.q_value = 0
		self.q_rave = 0
		self.visits_rave = 0
		self.children = {}
		self.outcome = default_outcome

	def addChildren(self, children):
		for child in children:
			self.children[child.move] = child

	def value(self, explore, crit):
		if self.visits == 0:
			if explore == 0:
				return 0
			else:
				return math.inf

		alpha = max(0, (crit - self.visits) / crit)
		return self.q_value * (1 - alpha) / self.visits + self.q_rave * alpha / self.visits_rave


class MCTS:
	EXPL_CONST = 1
	RAVE_CONST = 300

	def __init__(self, board):
		self.board = board.copy()
		self.root = self.newNode()

	def newNode(self, move=None, parent=None):
		return MCTSNode(self.board.getEmptyValue(), move, parent)

	def bestMove(self):
		children = self.root.children.values()

		max_value = max(children, key = lambda n: n.visits).visits
		max_nodes = [n for n in children if n.visits == max_value]

		best_child = choice(max_nodes)

		return best_child.move

	def makeMove(self, move):
		if move in self.root.children:
			child = self.root.children[move]
			child.parent = None
			self.root = child
			self.board.makeMove(child.move)
			return

		self.board.makeMove(move)
		self.root = self.newNode()

	def search(self, time_budget):
		start_time = time()
		num_rollouts = 0

		while time() - start_time < time_budget:
			node, state = self.select_node()
			turn = state.turn()
			outcome, red_rave_pts, blue_rave_pts = self.roll_out(state)
			self.backup(node, turn, outcome, red_rave_pts, blue_rave_pts)
			num_rollouts += 1
			
		count, depth = self.treeSize()
		return num_rollouts, count, depth

	def select_node(self):
		node = self.root
		state = self.board.copy()

		while len(node.children) > 0:
			children = node.children.values()

			max_value = max(children, key = lambda n: n.value(self.EXPL_CONST, self.RAVE_CONST)).value(self.EXPL_CONST, self.RAVE_CONST)
			max_nodes = [n for n in children if n.value(self.EXPL_CONST, self.RAVE_CONST) == max_value]
			node = choice(max_nodes)
			state.makeMove(node.move)

			if node.visits == 0:
				return (node, state)

		if self.expand(node, state):
			node = choice(list(node.children.values()))
			state.makeMove(node.move)

		return (node, state)

	def roll_out(self, state):
		moves = state.moves()

		red_rave_pts = []
		blue_rave_pts = []

		for x in range(state.getBoardSize()):
			for y in range(state.getBoardSize()):
				if state.isRed(x, y):
					red_rave_pts.append((x, y))
				elif state.isBlue(x, y):
					blue_rave_pts.append((x, y))

		return state.getWinner(), red_rave_pts, blue_rave_pts

	def backup(self, node, turn, outcome, red_rave_pts, blue_rave_pts):
		reward = -1 if outcome == turn else 1

		while node != None:
			if turn == self.board.getRedValue():
				for point in red_rave_pts:
					if point in node.children:
						node.children[point].q_rave -= reward
						node.children[point].visits_rave += 1

			else:
				for point in blue_rave_pts:
					if point in node.children:
						node.children[point].q_rave -= reward
						node.children[point].visits_rave += 1

			node.visits += 1
			node.q_value += reward

			if turn == self.board.getRedValue():
				turn = self.board.getBlueValue()
			else:
				turn = self.board.getRedValue()

			reward = -reward
			node = node.parent

	def expand(self, parent, state):
		children = []
		if state.isWinner():
			return False

		for move in state.moves():
			children.append(self.newNode(move, parent))

		parent.addChildren(children)
		return True

	def swap(self):
		self.board.togglePlayerTurn()

	def setGamestate(self, state):
		self.board = state.copy()
		self.root = self.newNode()

	def treeSize(self):
		q = []
		count = 0
		q.append((self.root, 1))

		max_depth = 0

		while len(q) > 0:
			node, depth = q.pop(0)
			count += 1

			if max_depth < depth:
				max_depth = depth

			children = node.children.values()

			for child in children:
				q.append((child, depth + 1))

		return count, depth
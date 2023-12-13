import math, random
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
from Board import Board

class Node:
    def __init__(self, board, parent=None, action=None, color="R"):
        self.visits = 0
        self.reward = 0.0
        self.board = board
        self.children = []
        self.parent = parent
        self.action = action
        self.color = color

    def is_expanded(self):
        action = available(self.board)
        return len(self.children) == len(action)

class MCTS_Player:

    def __init__(self, color):

        self.color = color

    def search(self, rollout_times, root):
        """
        enter point - return best move based on usb
        """
        for _ in range(rollout_times):
            leave = self.select(root)
            reward = self.simulate(leave)
            self.backup(leave, reward)
            best_child = self.ucb(root, 0)
        return best_child.action

    def select(self, node):

        while not (node.board.has_ended()):

            if len(node.children) == 0:
                new_node = self.expand(node)
                return new_node
            else:
                if not node.is_expanded():
                    return self.expand(node)
                else:
                    node = self.ucb(node, 1)
        return node
    

    def expand(self, node):

        actions = available(node.board)
        action = random.choice(actions)
        tried_action = [c.action for c in node.children]

        while action in tried_action:
            action = random.choice(actions)

        child_board = move(node.board, node.color, action)

        if node.color == 'R':
            child_color = 'B'
        else:
            child_color = 'R'
        
        # add a child node
        child_node = Node(child_board, parent=node, action=action, color=child_color)
        node.children.append(child_node)

        return node.children[-1]

    def ucb(self, node, param):
        """
        Ucb to choose from best child
        """
        best_score = 0
        best_children = []

        for child in node.children:

            score = (child.reward / child.visits) + param * math.sqrt(2.0 * math.log(node.visits) / float(child.visits))
            if score > best_score:
                best_children = []
                best_children.append(child)
                best_score = score
            elif score == best_score:
                best_children.append(child)

        return random.choice(best_children)

    def simulate(self, node):

        board = node.board
        color = node.color
        while not board.has_ended():

            actions = available(board)
            action = random.choice(actions)
            board = move(board, color, action)
            if color == 'R':
                color = 'B'
            else:
                color = 'R'
        
        winner = board.get_winner()
        if winner.get_char() == self.color:
            reward = 1
        else:
            reward = 0
        return reward

    def backup(self, node, reward):
        while node is not None:
            node.visits += 1
            node.reward += reward
            node = node.parent
        return 0


def available(board):
    """
    choose available moves from a board
    """
    tiles = board.get_tiles()
    available = []
    for tt in tiles:
        for t in tt:
            if (t.get_colour()==None):
                x = t.get_x()
                y = t.get_y()
                available.append((x,y))
    return available

def move(board, player, move):
    """
    make a move and return a board
    """
    str = board.print_board()
    (x,y) = move
    ss = str.split(",")
    s = ss[x] 
    s = s[:y] + player + s[y+1:]
    ss[x] = s
    ss = ','.join(ss)
    board = Board.from_string(ss)
    return board
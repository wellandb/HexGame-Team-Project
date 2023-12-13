import socket
from random import choice
from time import sleep

from mcts_ucb import Node, MCTS_Player
import sys
import os
sys.path.append(os.path.join(os.path.dirname(__file__), '../../src'))
from Board import Board


class MCTS_Agent():
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """
        
        self._board_size = 0
        self._board = None
        self._colour = ""
        self._turn_count = 1
        self._choices = []
        self._last_move = None
        
        states = {
            1: MCTS_Agent._connect,
            2: MCTS_Agent._wait_start,
            3: MCTS_Agent._make_move,
            4: MCTS_Agent._wait_message,
            5: MCTS_Agent._close
        }

        res = states[1](self)
        while (res != 0):
            res = states[res](self)

    def _connect(self):
        """Connects to the socket and jumps to waiting for the start
        message.
        """
        
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((MCTS_Agent.HOST, MCTS_Agent.PORT))

        return 2

    def _wait_start(self):
        """Initialises itself when receiving the start message, then
        answers if it is Red or waits if it is Blue.
        """
        
        data = self._s.recv(1024).decode("utf-8").strip().split(";")

        if (data[0] == "START"):

            self._board_size = int(data[1])
            for i in range(self._board_size):
                for j in range(self._board_size):
                    self._choices.append((i, j))
                    
            self._colour = data[2]

            if (self._colour == "R"):
                return 3
            else:
                return 4

        else:
            print("ERROR: No START message received.")
            return 0
    
    def _is_swap(self):

        return False

    def _make_move(self):
        """Makes a random valid move. It will choose to swap with
        a coinflip.
        """
        # if opponents good then swap
        # Todo: when to swap
        if (self._turn_count == 2 and choice([0, 1]) == 1):
            msg = "SWAP\n"

        if(self._turn_count == 1):
            # move = (5,7)
            self._board = Board(11)

        root = Node(self._board,None,None,self._colour)
        ai = MCTS_Player(self._colour)
        move = ai.search(150,root)

        msg = f"{move[0]},{move[1]}\n"
        self._s.sendall(bytes(msg, "utf-8"))

        return 4

    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "END" or data[-1] == "END"):
            return 5
        else:
            board = data[2]
            self._board = Board.from_string(board, bnf=True)

            if (data[1] == "SWAP"):
                self._colour = self.opp_colour()
            else:
                x, y = data[1].split(",")
                self._choices.remove((int(x), int(y)))

            if (data[-1] == self._colour):
                return 3

        return 4

    def _close(self):
        """Closes the socket."""
        self._s.close()
        return 0

    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        if self._colour == "R":
            return "B"
        elif self._colour == "B":
            return "R"
        else:
            return "None"


if (__name__ == "__main__"):
    agent = MCTS_Agent()
    agent.run()

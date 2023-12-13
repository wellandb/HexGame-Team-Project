import socket
from MCTS import MCTS
from Board import Board
from random import choice

class MCTSAgent:
    """This class describes base hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def run(self):
        """A finite-state machine that cycles through waiting for input
        and sending moves.
        """
        
        # Set the strings to be used to represent each colour.
        self._red_value = "R"
        self._blue_value = "B"
        self._empty_value = "0"
        
        # Initialize the board size.
        self._board_size = None

        # Initialize the MCTS.
        self.mcts = None

        self._colour = ""
        self._turn_count = 1
        
        states = {
            1: MCTSAgent._connect,
            2: MCTSAgent._wait_start,
            3: MCTSAgent._make_move,
            4: MCTSAgent._wait_message,
            5: MCTSAgent._close
        }

        res = states[1](self)
        while (res != 0):
            res = states[res](self)

    def _connect(self):
        """Connects to the socket and jumps to waiting for the start
        message.
        """
        
        self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._s.connect((MCTSAgent.HOST, MCTSAgent.PORT))

        return 2

    def _wait_start(self):
        """Initialises itself when receiving the start message, then
        answers if it is Red or waits if it is Blue.
        """
        
        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "START"):
            self._board_size = int(data[1])
            self._colour = data[2]

            # Instantiate a new MCTS containing a new board.
            self.mcts = MCTS(Board(size=self._board_size))

            if (self._colour == self._red_value):
                return 3
            else:
                return 4

        else:
            print("ERROR: No START message received.")
            return 0

    def _make_move(self):
        """Makes a random valid move. It will choose to swap with
        a coinflip.
        """

        if (self._turn_count == 2 and choice([0, 1]) == 1):
            return self._make_move_swap()

        # Use a default time of 2 seconds.
        time = 2

        # Use 10 seconds for the first 15 moves.
        if self._turn_count < 30:
            time = 10

        # Use 5 seconds for the second set of 15 moves.
        elif self._turn_count < 60:
            time = 5

        # Search the MCTS tree.
        self.mcts.search(time)

        # Find the best move.
        coords = self.mcts.bestMove()
        return self._make_move_coords(coords)

    def _make_move_coords(self, coords):
        """Makes a move at the specified coordinates.
        """

        self._s.sendall(bytes(f"{coords[0]},{coords[1]}\n", "utf-8"))

        return 4

    def _make_move_swap(self):
        """Makes a swap move.
        """
        self._s.sendall(bytes("SWAP\n", "utf-8"))
        return 4


    def _wait_message(self):
        """Waits for a new change message when it is not its turn."""

        self._turn_count += 1

        data = self._s.recv(1024).decode("utf-8").strip().split(";")
        if (data[0] == "END" or data[-1] == "END"):
            return 5
        else:

            if (data[1] == "SWAP"):
                self._colour = self.opp_colour()

                # Swap player colours on our MCTS board.
                self.mcts.swap()

            else:
                x, y = data[1].split(",")
                coords = (int(x), int(y))

                # Copy the move made on our MCTS board.
                self.mcts.makeMove(coords)
                    

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
        
        if self._colour == self._red_value:
            return self._blue_value
        elif self._colour == self._blue_value:
            return self._red_value
        else:
            return self._empty_value


if (__name__ == "__main__"):
    agent = MCTSAgent()
    agent.run()

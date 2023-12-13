import socket
from random import choice
from time import sleep
import numpy as np

class NaiveAgent():
    """This class describes the default Hex agent. It will randomly send a
    valid move at each turn, and it will choose to swap with a 50% chance.
    """

    HOST = "127.0.0.1"
    PORT = 1234

    def __init__(self, board_size=11):
        self.s = socket.socket(
            socket.AF_INET, socket.SOCK_STREAM
        )

        self.s.connect((self.HOST, self.PORT))

        self.board_size = board_size
        self.board = []
        self.colour = ""
        self.turn_count = 0

        # self.startWeights = [
        #                     [0,0,0,1,1,1,2,2,3,4,4],
        #                     [0,1,2,3,4,5,5,5,5,5,4],
        #                     [0,2,3,4,5,5,5,5,5,5,3],
        #                     [1,3,4,5,5,5,5,5,5,5,2],
        #                     [1,4,5,5,5,5,5,5,5,5,2],
        #                     [1,5,5,5,5,6,5,5,5,5,1],
        #                     [2,5,5,5,5,5,5,5,5,4,1],
        #                     [2,5,5,5,5,5,5,5,4,3,1],
        #                     [3,5,5,5,5,5,5,4,3,2,0],
        #                     [4,5,5,5,5,5,4,3,2,1,0],
        #                     [4,4,3,2,2,1,1,1,0,0,0]]


    def run(self):
        """Reads data until it receives an END message or the socket closes."""

        while True:
            data = self.s.recv(1024)
            if not data:
                break
            # print(f"{self.colour} {data.decode('utf-8')}", end="")
            if (self.interpret_data(data)):
                break

        # print(f"Naive agent {self.colour} terminated")

    def interpret_data(self, data):
        """Checks the type of message and responds accordingly. Returns True
        if the game ended, False otherwise.
        """

        messages = data.decode("utf-8").strip().split("\n")
        messages = [x.split(";") for x in messages]
        # print(messages)
        for s in messages:
            if s[0] == "START":
                self.board_size = int(s[1])
                self.colour = s[2]
                self.board = [
                    [0]*self.board_size for i in range(self.board_size)]

                if self.colour == "R":
                    self.make_move()

            elif s[0] == "END":
                return True

            elif s[0] == "CHANGE":
                if s[3] == "END":
                    return True

                elif s[1] == "SWAP":
                    self.colour = self.opp_colour()
                    if s[3] == self.colour:
                        self.make_move()

                elif s[3] == self.colour:
                    action = [int(x) for x in s[1].split(",")]
                    self.board[action[0]][action[1]] = self.opp_colour()

                    self.make_move()

        return False

    def choose_move(self, choices):
        """Choses a move based on available moves"""
        # Currently chooses random out of available
        return choice(choices)

    def make_move(self):
        """Makes a random move from the available pool of choices. If it can
        swap, chooses to do so 50% of the time.
        """

        # print(f"{self.colour} making move")

        if self.colour == "B" and self.turn_count == 0:
            if choice([0, 1]) == 1:
                self.s.sendall(bytes("SWAP\n", "utf-8"))
            else:
                # same as below
                choices = []
                for i in range(self.board_size):
                    for j in range(self.board_size):
                        if self.board[i][j] == 0:
                            choices.append((i, j))
                pos = self.choose_move(choices)
                self.s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
                self.board[pos[0]][pos[1]] = self.colour
        else:
            choices = []
            for i in range(self.board_size):
                for j in range(self.board_size):
                    if self.board[i][j] == 0:
                        choices.append((i, j))
            pos = self.choose_move(choices)

            self.s.sendall(bytes(f"{pos[0]},{pos[1]}\n", "utf-8"))
            self.board[pos[0]][pos[1]] = self.colour
        self.turn_count += 1


    def is_empty(self, cords):
        "Checks whether board position is empty"
        (x,y) = cords
        return self.board[x][y] == 0

    def is_colour(self, cords, colour):
        "Checks colour for a board position"
        (x,y) = cords
        return self.board[x][y] == colour


    def get_neighbours(self, cords):
        "Gets neighbours for a board position checking that they are within the range of the board"
        (x, y) = cords
        neighbours = []
        if x-1 >=0:
            neighbours.append((x-1,y))
        if x+1 < self.board_size:
            neighbours.append((x+1,y))
        if x-1 >= 0 and y+1 < self.board_size:
            neighbours.append((x-1,y+1))
        if x+1 < self.board_size and y-1 >= 0:
            neighbours.append((x+1,y-1))
        if y+1 < self.board_size:
            neighbours.append((x,y+1))
        if y-1 >= 0:
             neighbours.append((x,y-1))
        return neighbours


    def get_heuristic(self, colour):
        "Computes board state score"
        playerScore = self.get_player_score(colour)
        oppScore = self.get_player_score(self.opp_colour())
        return playerScore - oppScore


    def get_player_score(self, colour):
        "Gets board state score for a specified player from the weights found in dijkstra"
        weights = self.dijkstra(colour)
        if colour == "R": # Search the end of the board for shortest path to win for Red (bottom of the board)
            score = min([weights[self.board_size-1][i] for i in range(self.board_size)])
        else:  # Search the end of the board for shortest path to win for Black (right of the board)
            score = min([weights[i][self.board_size-1] for i in range(self.board_size)])

        return score

    def dijkstra(self, colour):
        "Gets weights for a the whole board as an array"
        weights = np.full((self.board_size, self.board_size), 5000)
        search = np.full((self.board_size, self.board_size), True)
        # Loop thrpugh the start of the board for that colour
        for i in range(self.board_size):
            if colour == "R": # Start at the top of the board is red
                initial = tuple([0,i]) 
            else:  # Start at the left of the board if blue
                initial = tuple([i,0])

            # Set the first collumn/row to has been visited
            search[initial] = False
            # Set the weights for the start of that colour's board, same colour = 0, empty = 1, other colour = 5000
            if self.is_colour(initial, colour):
                weights[initial] = 0
            elif self.is_empty(initial):
                weights[initial] = 1
            else:
                weights[initial] = 5000

        # Starting from one side of the board calculates the shortest path to the other side in the shortest amount of moves
        shortest_path_found = False
        while shortest_path_found == False:
            # Loop until there are no changes to the weights of the board
            shortest_path_found = True
            for i, x in enumerate(weights):
                for j, y in enumerate(x):
                    if not search[i][j]:
                        neighbours = self.get_neighbours((i,j))
                        for n in neighbours:
                            n_cord = tuple(n)
                            (x,y) = n_cord
                            # It costs 1 to move to an empty space
                            if self.is_empty(n_cord):
                                cost = 1
                            # It costs nothing to move to your own space
                            elif self.is_colour(n_cord, colour):
                                cost = 0
                            # It costs 5000 to move to the opponents space (cuts off possibility)
                            else:
                                cost = 5000
                            # If it costs less to get to this tile from i,j then replace the weight
                            if weights[n_cord] > weights[i][j] + cost:
                                weights[n_cord] = weights[i][j] + cost
                                search[n_cord] = False  # Set tile to visited
                                shortest_path_found = False # a change has been made so loop again
        return weights


    def opp_colour(self):
        """Returns the char representation of the colour opposite to the
        current one.
        """
        if self.colour == "R":
            return "B"
        elif self.colour == "B":
            return "R"
        else:
            return "None"


if (__name__ == "__main__"):
    agent = NaiveAgent()
    agent.run()

import random
from collections import Counter
from typing import Callable, List, Tuple
from copy import deepcopy
from math import inf

Locations = List[Tuple[int, int]]
Moves = List[Tuple[Tuple[int, int], Locations]]   # Moves = [start position, target position]


class Pieces(object):
    """
    Pieces class contains the checker playing methods
    """

    WHITE = 1  # White checker constant
    WHITE_NORMAL = 1  # White normal checker constant
    WHITE_KING = 3  # White king checker constant
    BLACK = 0  # Black checker constant
    BLACK_NORMAL = 2  # Black normal checker constant
    BLACK_KING = 4  # Black king checker constant
    X_DIRECTION = [1, 1, -1, -1]  # Increment of x-coordinate in the direction of movement
    Y_DIRECTION = [1, -1, 1, -1]  # Increment of y-coordinate in the direction of movement
    INFINITE = inf  # infinite constant


    def __init__(self, size=8):
        """
        Set and initialize the game board.

        :param size: Size of the checkers board. Defaults to 8.
        """
        self.size = size
        self.board = []  # Initialize an empty board
        piece = self.WHITE_NORMAL  # Set the starting piece type to white normal piece

        for i in range(size):
            row = []  # Initialize an empty row
            is_odd_row = i % 2 == 1  # Check if it is an odd row

            if i == size / 2 - 1:
                piece = 0  # Set the piece type to empty when reaching the middle row
            elif i == size / 2 + 1:
                piece = self.BLACK_NORMAL  # Set the piece type to black normal piece after the middle row

            for _ in range(size):
                if is_odd_row:
                    row.append(piece)  # Add the current piece to the row
                else:
                    row.append(0)  # Add an empty square to the row
                is_odd_row = not is_odd_row  # Alternate the square type within the row

            self.board.append(row)  # Add the row to the game board

        self.stateCounter = Counter()  # Initialize a counter for game states

    def encodeBoard(self):
        """
        Encode the game board to represent each state with a unique integer.

        Returns:
            int: The value of the encoded game board.
        """
        value = 0  # Initialize the encoded value to 0

        for i in range(self.size):
            for j in range(self.size):
                # Encode each square on the board as a unique integer value
                # by adding 7 to the row and column indices
                # to ensure the minimum value is greater than the greatest value of the board (4)
                num = i * self.size + j + 7
                value += num * self.board[i][j]  # Add the encoded value to the total

        return value


    def getBoard(self):
        """
        Get a copy of the game board.
        :return: Board: A copy of the game board.
        """
        return deepcopy(self.board)

    def isAvailable(self, x: int, y: int):
        """
        True if the given position is available, False otherwise.
        :param x: X position
        :param y: Y position
        :return: True if the given position is valid, False otherwise.
        """
        return 0 <= x < self.size and 0 <= y < self.size


    def nextPositions(self, x: int, y: int) :
        """Get the possible next positions for a given position

        Args:
            x (int): x position
            y (int): y position

        Returns:
            (Locations, Locations): next normal positions, next capture positions
        """
        if self.board[x][y] == 0:
            return []

        player = self.board[x][y] % 2
        captureMoves = []
        normalMoves = []
        sign = 1 if player == self.WHITE else -1
        # only forward for normals and both forward and backward for Kings
        rng = 2 if self.board[x][y] <= 2 else 4
        for i in range(rng):
            nx = x + sign * self.X_DIRECTION[i]  # next X coordinate
            ny = y + sign * self.Y_DIRECTION[i]  # next y coordinate
            if self.isAvailable(nx, ny):
                if self.board[nx][ny] == 0:
                    normalMoves.append((nx, ny))
                elif self.board[nx][ny] % 2 == 1 - player:
                    nx += sign * self.X_DIRECTION[i]
                    ny += sign * self.Y_DIRECTION[i]
                    if self.isAvailable(nx, ny) and self.board[nx][ny] == 0:
                        captureMoves.append((nx, ny))
        return normalMoves, captureMoves


    def nextMoves(self, player: int):
        """
        Obtain the subsequent available moves on the game board for a specific player.
        
        :param player:  The type of player (WHITE, BLACK)
        :return: Valid moves for the player.
        """
        captureMoves = []  
        normalMoves = []
        for x in range(self.size):
            for y in range(self.size):
                # Check if the current square contains a piece of the given player
                if self.board[x][y] != 0 and self.board[x][y] % 2 == player:
                    # Get the next positions for the piece at (x, y)
                    normal, capture = self.nextPositions(x, y)

                    # If there are normal moves available, add them to normalMoves
                    if len(normal) != 0:
                        normalMoves.append(((x, y), normal))

                    # If there are capture moves available, add them to captureMoves
                    if len(capture) != 0:
                        captureMoves.append(((x, y), capture))

        # Implement forced capture move by checking if captureMoves is not empty
        if len(captureMoves) != 0:
            return captureMoves
        else:
            return normalMoves

    def playMove(self, x: int, y: int, nx: int, ny: int):
        """
        Update the game board by executing a move from (x, y) to (nx, ny)

        :param x: The old x position
        :param y: The old y position
        :param nx: The new x position
        :param ny: The new y position
        :return: canCapture (bool): Indicates whether the player can capture more pieces.
            removed (int): The piece removed during the move (if any).
            promoted (bool): Indicates whether the current piece has been promoted.
        """
        # Move the piece to the new position
        self.board[nx][ny] = self.board[x][y]
        self.board[x][y] = 0

        removed = 0  # Stores the removed piece (if any)

        if abs(nx - x) == 2:  # Capture move
            dx = nx - x
            dy = ny - y
            removed = self.board[x + dx // 2][y + dy // 2]
            self.board[x + dx // 2][y + dy // 2] = 0  # Remove the captured piece

        # Promote to king if necessary
        if self.board[nx][ny] == self.WHITE_NORMAL and nx == self.size - 1:
            self.board[nx][ny] = self.WHITE_KING
            return False, removed, True
        if self.board[nx][ny] == self.BLACK_NORMAL and nx == 0:
            self.board[nx][ny] = self.BLACK_KING
            return False, removed, True

        if abs(nx - x) != 2:
            return False, removed, False

        return True, removed, False


    def revokeMove(self, x: int, y: int, nx: int, ny: int, removed=0, promoted=False):
        """
        revoke a move and restore the game board to its previous state.
        :param x: :param y: :param nx: :param ny:  old/new x/y position of the played move.
        :param removed: The removed piece (if any). Defaults is 0.
        :param promoted: Indicates if the played piece was recently promoted. Defaults is False.
        """
        if promoted:
            # Revert the promoted piece back to its original type
            if self.board[nx][ny] == self.WHITE_KING:
                self.board[nx][ny] = self.WHITE_NORMAL
            elif self.board[nx][ny] == self.BLACK_KING:
                self.board[nx][ny] = self.BLACK_NORMAL

        # Restore the original positions of the pieces
        self.board[x][y] = self.board[nx][ny]
        self.board[nx][ny] = 0

        if abs(nx - x) == 2:
            # Restore the removed piece to its original position
            dx = nx - x
            dy = ny - y
            self.board[x + dx // 2][y + dy // 2] = removed


    # evaluate with heuristic method, it takes into account piece position and piece value (normal or king)
    def evaluate_heuristic(self, maximizer: int):
        """
    Evaluate the current state of the board using a heuristic approach.

    :param themax: WHITE or BLACK type themax player (int)
    :return: board score (int)
    """
        normals = 0  # number of normal pieces
        kings = 0  # number of king pieces
        edgeRow = 0  # number of pieces on the edge row (aka king row), they're safe

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != 0:
                    # max player: sign=1, min player: sign=-1
                    sign = 1 if self.board[i][j] % 2 == maximizer else -1
                    if self.board[i][j] <= 2:
                        normals += sign * 1
                    else:
                        kings += sign * 1
                    if sign == 1 and ((i == 0 and maximizer == self.WHITE) or (
                            i == self.size - 1 and maximizer == self.BLACK)):
                        edgeRow += 1
        return normals * 1000 + kings * 3000 + edgeRow * 300


    def stateValue(self, themax: int):
        """
        Get the value of the board state. Penalize repeating the same state when the number of themax's pieces
        is greater than the number of themini's pieces.

        :param themax: The type of the themax player (WHITE/BLACK).
        :return:  The value of the board state.
        """
        maxPieces = 0  # Number of pieces belonging to themax player
        minPieces = 0  # Number of pieces belonging to themini player

        for i in range(self.size):
            for j in range(self.size):
                if self.board[i][j] != 0:
                    if self.board[i][j] % 2 == themax:
                        maxPieces += 1
                    else:
                        minPieces += 1
        # The value of the board state indicates the desirability of the state for the player,
        # with penalization for repeating states in favor of the player with more pieces.
        if maxPieces > minPieces:
            return -self.stateCounter[self.encodeBoard()]  # Penalize repeating the same state if themax has more pieces
        return 0


    def minimax_calculate(
            self,
            player: int,
            themax: int,
            depth: int = 0,
            alpha: int = -INFINITE,
            beta: int = INFINITE,
            depthLimit: int = 4,
            evaluate: Callable[[int], int] = evaluate_heuristic,
            moves: Moves = None,
    ) :
        """
         Calculate the board score using the minimax algorithm with alpha-beta pruning.

        :param player: the type of the current player (WHITE, BLACK)
        :param themax: the type of the themax player (WHITE, BLACK)
        :param depth: the current depth of the algorithm. Defaults is 0
        :param alpha: the value of alpha. Defaults to -INFINITE.
        :param beta: the value of beta of the algorithm. Defaults to INFINITE
        :param depthLimit: The maximum depth of the minimax_calculate algorithm.
            Higher depth results in stronger play but takes more time. Defaults to 4.
        :param evaluate: evaluate_heuristic function
        :param moves: the next capture moves if any, none default

        :return: board score
        """

        if moves is None:
            moves = self.nextMoves(player)

        # Check termination conditions
        if len(moves) == 0 or depth == depthLimit:
            score = evaluate(self, themax)
            return score

        # Initialize the highestValue based on the current player
        highestValue = self.INFINITE if player != themax else -self.INFINITE

        # Sort moves by the minimum next positions for pruning
        moves.sort(key=lambda move: len(move[1]))

        # Iterate over each move
        for position in moves:
            x, y = position[0]
            for nx, ny in position[1]:
                # Play the move and check if capturing is possible
                canCapture, removed, promoted = self.playMove(x, y, nx, ny)
                played = False

                if canCapture:
                    _, nextCaptures = self.nextPositions(nx, ny)
                    if len(nextCaptures) != 0:
                        played = True
                        nMoves = [((nx, ny), nextCaptures)]
                        # Recursive call with pruning
                        if player == themax:
                            highestValue = max(
                                highestValue,
                                self.minimax_calculate(player, themax, depth + 1, alpha, beta, depthLimit, evaluate,
                                                       nMoves)
                            )
                            alpha = max(alpha, highestValue)
                        else:
                            highestValue = min(
                                highestValue,
                                self.minimax_calculate(player, themax, depth + 1, alpha, beta, depthLimit, evaluate,
                                                       nMoves)
                            )
                            beta = min(beta, highestValue)

                # Recursive call if no capturing move is played
                if not played:
                    if player == themax:
                        highestValue = max(
                            highestValue,
                            self.minimax_calculate(1 - player, themax, depth + 1, alpha, beta, depthLimit, evaluate)
                        )
                        alpha = max(alpha, highestValue)
                    else:
                        highestValue = min(
                            highestValue,
                            self.minimax_calculate(1 - player, themax, depth + 1, alpha, beta, depthLimit, evaluate)
                        )
                        beta = min(beta, highestValue)

                self.revokeMove(x, y, nx, ny, removed, promoted)

                # Prune: early stop searching
                if alpha >= beta:
                    break

            # Prune: early stop searching
            if alpha >= beta:
                break

        return highestValue


    def minimax_play(
        self,
        player: int,
        moves: Moves = None,
        depthLimit: int = 4,
        evaluate: Callable[[int], int] = evaluate_heuristic,
    ) :
        """
            Play a move with the minimax_calculate method algorithm.
            Make the player continue capturing if could.

            :param player: The type of the player (WHITE, BLACK).
            :param moves: The next capture moves if has, defaults None.
            :param depthLimit: The depthLimit parameter determines the maximum depth of the minimax_calculate algorithm.
                Increasing the depth allows for stronger gameplay, but it also requires more computation time.
                By default, the depthLimit is set to 4, which provides a moderate level of gameplay.
            :param evaluate:  evaluate_heuristic function

            :return: (boolean, boolean)
                    whether there are further plays.
                    whether a piece was captured and should reset the draw condition counter, for reset counter.
            """

        if moves is None:
            moves = self.nextMoves(player)

        if len(moves) == 0:
            print(("WHITE" if player == self.BLACK else "BLACK") + " Player wins")
            return False, False

        self.stateCounter[self.encodeBoard()] += 1

        # random.shuffle(moves)
        highestValue = -self.INFINITE    # player == WHITE -> MIN
        bestMove = None

        for position in moves:
            x, y = position[0]
            for nx, ny in position[1]:
                _, removed, promoted = self.playMove(x, y, nx, ny)
                value = self.minimax_calculate(1 - player, player, depthLimit=depthLimit, evaluate=evaluate)
                value += 2*self.stateValue(player)  
                self.revokeMove(x, y, nx, ny, removed, promoted)
                # Choose the move with the highest score as the best move
                if value > highestValue:
                    highestValue = value
                    bestMove = (x, y, nx, ny)

        x, y, nx, ny = bestMove
        print(f"AI Move from ({x}, {y}) to ({nx}, {ny})")
        canCapture, removed, _ = self.playMove(x, y, nx, ny)

        # after move, if can capture, continue capture
        if canCapture:
            _, captures = self.nextPositions(nx, ny)
            if len(captures) != 0:
                self.minimax_play(player, [((nx, ny), captures)], depthLimit, evaluate)

        self.stateCounter[self.encodeBoard()] += 1
        reset = removed != 0
        return (True, reset)



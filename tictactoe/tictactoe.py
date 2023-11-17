"""
Tic Tac Toe Player
"""

import math
import copy

X = "X"
O = "O"
EMPTY = None


def initial_state():
    """
    Returns starting state of the board.
    """
    return [[EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY],
            [EMPTY, EMPTY, EMPTY]]


def player(board):
    """
    Returns player who has the next turn on a board.
    """
    if board == initial_state():
        return X

    x_counter = 0
    o_counter = 0

    for i in range(0, len(board)):
            for j in range(0, len(board[0])):
                if board[i][j] == X:
                    x_counter += 1
                elif board[i][j] == O:
                    o_counter += 1
                    
    if x_counter > o_counter:
        return O
    else:
        return X
    



def actions(board):
    """
    Returns set of all possible actions (i, j) available on the board.
    """
    possible_actions = set()

    for i in range(len(board)):
        for j in range(len(board[0])):
            if board[i][j] == EMPTY:
                possible_actions.add((i,j))

    return possible_actions


def result(board, action):
    """
    Returns the board that results from making move (i, j) on the board.
    """
    if action not in actions(board):
        raise Exception("Invalid action")
    
    new_board = copy.deepcopy(board)
    new_board[action[0]][action[1]] = player(board)
    return new_board



def winner(board):
    """
    Returns the winner of the game, if there is one.
    """

    for i in range(len(board)):
         if board[i][0] == board[i][1] == board[i][2]:
            return board[i][0]
    for j in range(len(board[0])):
        if board[0][j] == board[1][j] == board[2][j]:
            return board[0][j]
    if board[0][0] == board[1][1] == board[2][2]:
        return board[0][0]
    elif board[0][2] == board[1][1] == board[2][0]:
        return board[0][2]
    return None


def terminal(board):
    """
    Returns True if game is over, False otherwise.
    """
    if winner(board) != None:
        return True
    for row in board:
        if EMPTY in row:
            return False
    return True


def utility(board):
    """
    Returns 1 if X has won the game, -1 if O has won, 0 otherwise.
    """
    if winner(board) == X:
        return 1
    elif winner(board) == O:
        return -1
    else:
        return 0
    


def minimax(board):
    """
    Returns the optimal action for the current player on the board.
    """
    if terminal(board):
        return None
    if player(board) == X:
        v, move = max_value(board, -math.inf, math.inf)
    else:
        v, move = min_value(board, -math.inf, math.inf)
    return move

def max_value(board, alpha, beta):
    if terminal(board):
        return utility(board), None
    v = -math.inf
    move = None
    for action in actions(board):
        new_v, _ = min_value(result(board, action), alpha, beta)
        if new_v > v:
            v = new_v
            move = action
        alpha = max(alpha, v)
        if alpha >= beta:
            break
    return v, move

def min_value(board, alpha, beta):
    if terminal(board):
        return utility(board), None
    v = math.inf
    move = None
    for action in actions(board):
        new_v, _ = max_value(result(board, action), alpha, beta)
        if new_v < v:
            v = new_v
            move = action
        beta = min(beta, v)
        if beta <= alpha:
            break
    return v, move

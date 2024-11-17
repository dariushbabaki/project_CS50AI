import math
from copy import deepcopy

X = "X"
O = "O"
EMPTY = None

def initial_state():
    return [[EMPTY] * 3 for _ in range(3)]

def player(board):
    x_count = sum(row.count(X) for row in board)
    o_count = sum(row.count(O) for row in board)
    return O if x_count > o_count else X

def actions(board):
    return {(i, j) for i in range(3) for j in range(3) if board[i][j] == EMPTY}

def result(board, action):
    if not (0 <= action[0] < 3 and 0 <= action[1] < 3):
        raise InvalidMove("Move is out of bounds!")
    if board[action[0]][action[1]] is not EMPTY:
        raise InvalidMove("Box is already filled!")
    new_board = deepcopy(board)
    new_board[action[0]][action[1]] = player(new_board)
    return new_board

def winner(board):
    for row in board:
        if row[0] == row[1] == row[2] != EMPTY:
            return row[0]
    for col in range(3):
        if board[0][col] == board[1][col] == board[2][col] != EMPTY:
            return board[0][col]
    if board[0][0] == board[1][1] == board[2][2] != EMPTY or board[0][2] == board[1][1] == board[2][0] != EMPTY:
        return board[1][1]
    return None

def terminal(board):
    return winner(board) is not None or all(EMPTY not in row for row in board)

def utility(board):
    result = winner(board)
    return 1 if result == X else -1 if result == O else 0

def minimax(board):
    if terminal(board):
        return None
    return min_value(board)[1] if player(board) == O else max_value(board)[1]

def max_value(board):
    if terminal(board):
        return utility(board), None
    v, move = float('-inf'), None
    for action in actions(board):
        min_val = min_value(result(board, action))[0]
        if min_val > v:
            v, move = min_val, action
    return v, move

def min_value(board):
    if terminal(board):
        return utility(board), None
    v, move = float('inf'), None
    for action in actions(board):
        max_val = max_value(result(board, action))[0]
        if max_val < v:
            v, move = max_val, action
    return v, move

class InvalidMove(Exception):
    def __init__(self, message):
        self.message = message

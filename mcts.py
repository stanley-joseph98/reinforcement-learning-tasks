import random
import math

class TicTacToe:
    def __init__(self):
        self.board = [' ' for _ in range(9)]
        self.current_winner = None

    def print_board(self):
        for row in [self.board[i*3:(i+1)*3] for i in range(3)]:
            print('| '+ ' | '.join(row) + ' |')

    def available_moves(self):
        return [i for i, spot in enumerate(self.board) if spot == ' ']

    def empty_squares(self):
        return ' ' in self.board

    def num_empty_squares(self):
        return self.board.count(' ')

    def make_move(self, square, letter):
        if self.board[square] == ' ':
            self.board[square] = letter
            if self.winner(square, letter):
                self.current_winner = letter
            return True
        return False

    def copy(self):
        new_game = TicTacToe()
        new_game.board = self.board[:]  # Make a shallow copy of the board
        new_game.current_winner = self.current_winner
        return new_game

    def winner(self, square, letter):
        row_index = square // 3
        row = self.board[row_index*3:(row_index+1)*3]
        if all([spot == letter for spot in row]):
            return True

        col_index = square % 3 #As at now, we are working with column indexed 0, the first column
        col = [self.board[col_index+i*3] for i in range(3)]
        if all([spot == letter for spot in col]):
            return True

        if square % 2 == 0:
            diagonal1 = [self.board[i] for i in [0, 4, 8]]
            if all([spot == letter for spot in diagonal1]):
                return True
            diagonal2 = [self.board[i] for i in [2, 4, 6]]
            if all([spot == letter for spot in diagonal2]):
                return True

        return False

def play(game, player1, player2, print_game=True):
    if print_game:
        game.print_board()

    letter = 'X'
    while game.empty_squares():
        if letter == 'O':
            square = player2.get_move(game)
        else:
            square = player1.get_move(game)

        if game.make_move(square, letter):
            if print_game:
                print(f'{letter} makes a move to square {square}')
                game.print_board()
                print('')

            if game.current_winner:
                if print_game:
                    print(letter + ' wins!')
                return letter

            letter = 'O' if letter == 'X' else 'X'


    if print_game:
        print('It\'s a tie!')

class HumanPlayer:
    def __init__(self, letter):
        self.letter = letter

    def get_move(self, game):
        valid_square = False
        val = None
        while not valid_square:
            square = input(f'{self.letter}\'s turn. Input move (0-8): ')
            try:
                val = int(square)
                if val not in game.available_moves():
                    raise ValueError
                valid_square = True
            except ValueError:
                print('Invalid square! Try again.')
        return val

class MCTSPlayer:
    def __init__(self, letter, num_simulations=50):
        self.letter = letter
        self.num_simulations = num_simulations

    def get_move(self, game):
        tree = MonteCarloTree(game)
        tree.simulate(self.num_simulations)
        return tree.get_best_move(self.letter)

class Node:
    def __init__(self, move=None, parent=None, game=None):
        self.move = move
        self.parent = parent
        self.children = []
        self.wins = 0
        self.visits = 0
        self.untried_moves = game.available_moves()
        self.game = game  # Store the game instance

    def expand(self, game):
        if not self.untried_moves:
            return None  # No more moves to try

        move = random.choice(self.untried_moves)
        self.untried_moves.remove(move)
        child_game = game.copy()
        current_player = child_game.current_winner  # Determine current player from game
        child_game.make_move(move, current_player)
        child_node = Node(move=move, parent=self, game=child_game)
        self.children.append(child_node)
        return child_node

    def select(self):
        return max(self.children, key=lambda c: c.wins / c.visits + math.sqrt(2 * math.log(self.visits) / c.visits))

    def update(self, result):
        self.visits += 1
        if result == self.parent.game.current_winner:
            self.wins += 1

class MonteCarloTree:
    def __init__(self, game):
        self.root = Node(game=game)

    def simulate(self, num_simulations):
        for _ in range(num_simulations):
            node = self.select_node()
            game_copy = node.game.copy()
            winner = self.simulate_playout(game_copy)
            self.backpropagate(node, winner)

    def select_node(self):
        node = self.root
        while node.children:
            node = node.select()
            if not node.expand(node.game):
                return node  # If no more moves to try, return current node
        return node

    def simulate_playout(self, game):
        current_player = 'X'  # Start with 'X' player
        while not game.current_winner and game.empty_squares():  # Check for available moves and no winner
            square = random.choice(game.available_moves())
            game.make_move(square, current_player)
            current_player = 'O' if current_player == 'X' else 'X'

        # If there's no winner and no available moves, it's a tie
        if not game.current_winner:
            return None
        else:
            return game.current_winner

    def backpropagate(self, node, winner):
        while node:
            if node.parent is None:  # Check if the current node is the root node
                return  # If so, exit the loop
            if winner is None:  # Handle tie game
                node.update(0)  # No winner, so update with 0
            else:
                node.update(1 if winner == self.root.game.current_winner else 0)  # Update based on winner
            node = node.parent

    def get_best_move(self, letter):
        if not self.root.children:  # Check if there are no children nodes under the root
            return random.choice(self.root.game.available_moves())  # Return a random move

        best_node = max(self.root.children, key=lambda c: c.wins / c.visits)
        return best_node.move


if __name__ == '__main__':
    p1 = HumanPlayer('X')
    p2 = MCTSPlayer('O', num_simulations=100)
    t = TicTacToe()
    play(t, p1, p2, print_game=True)

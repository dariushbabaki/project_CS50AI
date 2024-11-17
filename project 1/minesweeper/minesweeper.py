import itertools
import random

class Minesweeper():
    def __init__(self, height=8, width=8, mines=8):
        self.height = height
        self.width = width
        self.mines = set()
        self.board = [[False for _ in range(self.width)] for _ in range(self.height)]

        while len(self.mines) < mines:
            i, j = random.randrange(height), random.randrange(width)
            
            if not self.board[i][j]:
                self.mines.add((i, j))
                self.board[i][j] = True

        self.mines_found = set()

    def print(self):
        for i in range(self.height):
            print("--" * self.width + "-")
            
            for j in range(self.width):
                print("|X" if self.board[i][j] else "| ", end="")
            print("|")
            
        print("--" * self.width + "-")

    def is_mine(self, cell):
        return self.board[cell[0]][cell[1]]

    def nearby_mines(self, cell):
        count = 0
        
        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) != cell and 0 <= i < self.height and 0 <= j < self.width and self.board[i][j]:
                    count += 1
                    
        return count

    def won(self):
        return self.mines_found == self.mines

class Sentence():
    def __init__(self, cells, count):
        self.cells = set(cells)
        self.count = count

    def __eq__(self, other):
        return self.cells == other.cells and self.count == other.count

    def __str__(self):
        return f"{self.cells} = {self.count}"

    def known_mines(self):
        if len(self.cells) == self.count and self.count > 0:
            print('Mine Identified! - ', self.cells)
            return self.cells
            
        return set()

    def known_safes(self):
        if self.count == 0:
            return self.cells
            
        return set()

    def mark_mine(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)
            self.count -= 1

    def mark_safe(self, cell):
        if cell in self.cells:
            self.cells.remove(cell)

class MinesweeperAI():
    def __init__(self, height=8, width=8):
        self.height = height
        self.width = width
        self.moves_made = set()
        self.mines = set()
        self.safes = set()
        self.knowledge = []

    def mark_mine(self, cell):
        self.mines.add(cell)
        
        for sentence in self.knowledge:
            sentence.mark_mine(cell)

    def mark_safe(self, cell):
        self.safes.add(cell)
        
        for sentence in self.knowledge:
            sentence.mark_safe(cell)

    def add_knowledge(self, cell, count):
        self.moves_made.add(cell)
        self.mark_safe(cell)
        new_sentence_cells = set()

        for i in range(cell[0] - 1, cell[0] + 2):
            for j in range(cell[1] - 1, cell[1] + 2):
                if (i, j) != cell:
                    if (i, j) in self.safes:
                        continue
                        
                    if (i, j) in self.mines:
                        count -= 1
                        continue
                        
                    if 0 <= i < self.height and 0 <= j < self.width:
                        new_sentence_cells.add((i, j))

        print(f'Move on cell: {cell} has added sentence to knowledge {new_sentence_cells} = {count}')
        self.knowledge.append(Sentence(new_sentence_cells, count))

        knowledge_changed = True
        
        while knowledge_changed:
            knowledge_changed = False
            safes = set()
            mines = set()

            for sentence in self.knowledge:
                safes |= sentence.known_safes()
                mines |= sentence.known_mines()

            for safe in safes:
                self.mark_safe(safe)
                knowledge_changed = True
                
            for mine in mines:
                self.mark_mine(mine)
                knowledge_changed = True

            self.knowledge = [s for s in self.knowledge if s.cells]

            for s1 in self.knowledge:
                for s2 in self.knowledge:
                    if s1.cells == s2.cells or not s1.cells:
                        continue
                        
                    if s1.cells.issubset(s2.cells):
                        inferred = Sentence(s2.cells - s1.cells, s2.count - s1.count)
                        
                        if inferred not in self.knowledge:
                            self.knowledge.append(inferred)
                            knowledge_changed = True
                            print('New Inferred Knowledge: ', inferred, 'from', s1, ' and ', s2)

        print('Current AI KB length: ', len(self.knowledge))
        print('Known Mines: ', self.mines)
        print('Safe Moves Remaining: ', self.safes - self.moves_made)
        print('====================================================')

    def make_safe_move(self):
        safe_moves = self.safes - self.moves_made
        
        if safe_moves:
            print('Making a Safe Move! Safe moves available: ', len(safe_moves))
            return random.choice(list(safe_moves))
            
        return None

    def make_random_move(self):
        moves = {}
        MINES = 8
        num_mines_left = MINES - len(self.mines)
        spaces_left = (self.height * self.width) - (len(self.moves_made) + len(self.mines))
        
        if spaces_left == 0:
            return None

        basic_prob = num_mines_left / spaces_left
        
        for i in range(self.height):
            for j in range(self.width):
                if (i, j) not in self.moves_made and (i, j) not in self.mines:
                    moves[(i, j)] = basic_prob

        if moves and not self.knowledge:
            move = random.choice(list(moves))
            print('AI Selecting Random Move With Basic Probability: ', move)
            return move

        elif moves:
            for sentence in self.knowledge:
                prob = sentence.count / len(sentence.cells)
                
                for cell in sentence.cells:
                    if moves[cell] < prob:
                        moves[cell] = prob

            best_moves = sorted(moves.items(), key=lambda x: x[1])
            best_prob = best_moves[0][1]
            best_cells = [x[0] for x in best_moves if x[1] == best_prob]
            move = random.choice(best_cells)
            print('AI Selecting Random Move with lowest mine probability using KB: ', move)
            return move

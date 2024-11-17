import sys
import copy

from crossword import *


class CrosswordSolver():

    def __init__(self, crossword):
        """
        Create new CSP crossword generator.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing the assignment.
        """
        letters = [
            [None for _ in range(self.crossword.width)]
            for _ in range(self.crossword.height)
        ]
        for variable, word in assignment.items():
            direction = variable.direction
            for k in range(len(word)):
                i = variable.i + (k if direction == Variable.DOWN else 0)
                j = variable.j + (k if direction == Variable.ACROSS else 0)
                letters[i][j] = word[k]
        return letters

    def display(self, assignment):
        """
        Print crossword assignment to terminal.
        """
        letters = self.letter_grid(assignment)
        for i in range(self.crossword.height):
            for j in range(self.crossword.width):
                if self.crossword.structure[i][j]:
                    print(letters[i][j] or " ", end="")
                else:
                    print("█", end="")
            print()

    def save(self, assignment, filename):
        """
        Save crossword assignment to an image.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create canvas
        img = Image.new(
            "RGBA",
            (self.crossword.width * cell_size,
             self.crossword.height * cell_size),
            "black"
        )
        font = ImageFont.truetype("assets/fonts/OpenSans-Regular.ttf", 80)
        draw = ImageDraw.Draw(img)

        for i in range(self.crossword.height):
            for j in range(self.crossword.width):

                rect = [
                    (j * cell_size + cell_border,
                     i * cell_size + cell_border),
                    ((j + 1) * cell_size - cell_border,
                     (i + 1) * cell_size - cell_border)
                ]
                if self.crossword.structure[i][j]:
                    draw.rectangle(rect, fill="white")
                    if letters[i][j]:
                        w, h = draw.textsize(letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, then solve CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
    """
    Ensure each variable is node-consistent.
    """
    for variable in self.domains:
        length = variable.length
        self.domains[variable] = {
            word for word in self.domains[variable] if len(word) == length
        }

    def revise(self, x, y):
        """
        Make `x` arc-consistent with `y`.
        """
        overlap = self.crossword.overlaps[x, y]
    if overlap is None:
        return False
    
    xoverlap, yoverlap = overlap
    revision_made = False

    for xword in list(self.domains[x]):
        matched = any(
            xword[xoverlap] == yword[yoverlap]
            for yword in self.domains[y]
        )
        
        if not matched:
            self.domains[x].remove(xword)
            revision_made = True

    return revision_made

    def ac3(self, arcs=None):
    """
    Enforce arc consistency.
    """
queue = arcs if arcs is not None else [
        (var1, var2)
        for var1 in self.domains
        for var2 in self.crossword.neighbors(var1)
        if self.crossword.overlaps[var1, var2] is not None
    ]

    while queue:
        x, y = queue.pop(0)
        
        if self.revise(x, y):
            if not self.domains[x]:
                return False
                
            for neighbor in self.crossword.neighbors(x):
                if neighbor != y:
                    queue.append((neighbor, x))
                    
    return True

    def assignment_complete(self, assignment):
        """
        Check if `assignment` is complete.
        """
        return all(variable in assignment for variable in self.domains)

    def consistent(self, assignment):
    """
    Check if `assignment` is consistent.
    """
    words = list(assignment.values())
    
    if len(words) != len(set(words)):
        return False

    for variable in assignment:
        if variable.length != len(assignment[variable]):
            return False

        for neighbor in self.crossword.neighbors(variable):
            if neighbor in assignment:
                overlap = self.crossword.overlaps[variable, neighbor]
                
                if overlap is not None:
                    x, y = overlap
                    
                    if assignment[variable][x] != assignment[neighbor][y]:
                        return False
                        
    return True

    def order_domain_values(self, var, assignment):
        """
        Order values for `var` based on constraints.
        """
        word_dict = {}
        neighbors = self.crossword.neighbors(var)

        for word in self.domains[var]:
            eliminated = 0
            
            for neighbor in neighbors:
                if neighbor in assignment:
                    continue
                    
                xoverlap, yoverlap = self.crossword.overlaps[var, neighbor]
                
                for neighbor_word in self.domains[neighbor]:
                    if word[xoverlap] != neighbor_word[yoverlap]:
                        eliminated += 1
                        
            word_dict[word] = eliminated

        sorted_dict = {k: v for k, v in sorted(word_dict.items(), key=lambda item: item[1])}
        
        return list(sorted_dict)

    def select_unassigned_variable(self, assignment):
        """
        Choose an unassigned variable.
        """
        choice_dict = {
            var: self.domains[var]
            for var in self.domains if var not in assignment
        }
        sorted_list = sorted(choice_dict, key=lambda v: len(choice_dict[v]))
        return sorted_list[0]

    def backtrack(self, assignment):
        """
        Solve CSP via backtracking.
        """
        if self.assignment_complete(assignment):
            return assignment

        var = self.select_unassigned_variable(assignment)

        for value in self.domains[var]:
            assignment_copy = assignment.copy()
            assignment_copy[var] = value
            
            if self.consistent(assignment_copy):
                result = self.backtrack(assignment_copy)
                
                if result is not None:
                    return result
                    
        return None

def main():
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    crossword = Crossword(structure, words)
    solver = CrosswordSolver(crossword)
    assignment = solver.solve()

    if assignment is None:
        print("No solution.")
    else:
        solver.display(assignment)
        if output:
            solver.save(assignment, output)

if __name__ == "__main__":
    main()

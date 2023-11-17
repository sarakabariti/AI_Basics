
import sys

from crossword import *


class CrosswordCreator():

    def __init__(self, crossword):
        """
        Create new CSP crossword generate.
        """
        self.crossword = crossword
        self.domains = {
            var: self.crossword.words.copy()
            for var in self.crossword.variables
        }

    def letter_grid(self, assignment):
        """
        Return 2D array representing a given assignment.
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

    def print(self, assignment):
        """
        Print crossword assignment to the terminal.
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
        Save crossword assignment to an image file.
        """
        from PIL import Image, ImageDraw, ImageFont
        cell_size = 100
        cell_border = 2
        interior_size = cell_size - 2 * cell_border
        letters = self.letter_grid(assignment)

        # Create a blank canvas
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
                        _, _, w, h = draw.textbbox((0, 0), letters[i][j], font=font)
                        draw.text(
                            (rect[0][0] + ((interior_size - w) / 2),
                             rect[0][1] + ((interior_size - h) / 2) - 10),
                            letters[i][j], fill="black", font=font
                        )

        img.save(filename)

    def solve(self):
        """
        Enforce node and arc consistency, and then solve the CSP.
        """
        self.enforce_node_consistency()
        self.ac3()
        return self.backtrack(dict())

    def enforce_node_consistency(self):
        """
        Update `self.domains` such that each variable is node-consistent.
        (Remove any values that are inconsistent with a variable's unary
         constraints; in this case, the length of the word.)
        """
        for variable in self.domains:
            for value in self.crossword.words:
                if len(value) != variable.length:
                    self.domains[variable].remove(value)

    def revise(self, x, y):
        """
        Make variable `x` arc consistent with variable `y`.
        To do so, remove values from `self.domains[x]` for which there is no
        possible corresponding value for `y` in `self.domains[y]`.

        Return True if a revision was made to the domain of `x`; return
        False if no revision was made.
        """
        revised = False
        # Get the overlap between x and y
        overlap = self.crossword.overlaps.get((x, y))
        # If there's no overlap, return False
        if not overlap:
            return False
        # Iterate over each value in the domain of x
        for val_x in set(self.domains[x]):
            # Check if there's a value in the domain of y that does not cause a conflict
            if not any(val_x[overlap[0]] == val_y[overlap[1]] for val_y in self.domains[y]):
                # If there's no such value, remove the value from the domain of x
                self.domains[x].remove(val_x)
                # Set revised to True
                revised = True
        return revised

    def ac3(self, arcs=None):
        """
        Update `self.domains` such that each variable is arc consistent.
        If `arcs` is None, begin with initial list of all arcs in the problem.
        Otherwise, use `arcs` as the initial list of arcs to make consistent.

        Return True if arc consistency is enforced and no domains are empty;
        return False if one or more domains end up empty.
        """
        # If arcs is None, begin with initial list of all arcs in the problem.
        if arcs is None:
            initial_arcs = []
            for x in self.crossword.variables:
                for y in self.crossword.neighbors(x):
                    if x != y:
                        initial_arcs.append((x, y))
        else:
            initial_arcs = arcs
        # Iterate until no arcs left in queue
        while initial_arcs:
            x, y = initial_arcs.pop(0)
            # Make variable `x` arc consistent with variable `y`.
            # If a revision was made to the domain of `x`, add additional arcs to queue
            if self.revise(x, y):
                # If, in the process of enforcing arc consistency, you remove all of the remaining values 
                # from a domain, return False (this means it’s impossible to solve the problem, 
                # since there are no more possible values for the variable). Otherwise, return True.
                if len(self.domains[x]) == 0:
                    return False
                for z in self.crossword.neighbors(x) - {y}:
                    if z != x and z != y:
                        initial_arcs.append((z, x))
        return True
    
    def assignment_complete(self, assignment):
        """
        Return True if `assignment` is complete (i.e., assigns a value to each
        crossword variable); return False otherwise.
        """
        for variable in self.domains:
            if variable not in assignment:
                return False
        return True

    def consistent(self, assignment):
        """
        Return True if `assignment` is consistent (i.e., words fit in crossword
        puzzle without conflicting characters); return False otherwise.
        """
        # Check if all values are distinct
        if len(set(assignment.values())) != len(assignment.values()):
            return False
        
        for variable, value in assignment.items():
            # Check if every value is the correct length
            if len(value) != variable.length:
                return False
            # Check if there are no conflicts between neighboring variables
            for neighbor in self.crossword.neighbors(variable):
                overlap = self.crossword.overlaps[variable, neighbor]
                if neighbor in assignment and overlap is not None:
                    i, j = overlap
                    if value[i] != assignment[neighbor][j]:
                        return False
        return True


    def order_domain_values(self, var, assignment):
        """
        Return a list of values in the domain of `var`, in order by
        the number of values they rule out for neighboring variables.
        The first value in the list, for example, should be the one
        that rules out the fewest values among the neighbors of `var`.
        """
        # Create dictionary to keep track of values that rule out the fewest values
        n_values = {val : 0 for val in self.domains[var]}
        # Iterate over values in the domain of var
        for val in self.domains[var]:
            # Iterate over neighbors of var and values in their domains
            for neighbor in self.crossword.neighbors(var):
                # Check if neighbor is not in assignment
                if neighbor not in assignment:
                    # Iterate over values in the domain of neighbor
                    for neighbor_val in self.domains[neighbor]:
                        # Check if there is an overlap between val and neighboring variables
                        overlap = self.crossword.overlaps.get((var, neighbor))
                        if overlap and val[overlap[0]] != neighbor_val[overlap[1]]:
                            # Increment n_values
                            n_values[val] += 1
        # Return sorted list of values in the domain of var
        return sorted(self.domains[var], key=n_values.get)


    def select_unassigned_variable(self, assignment):
        """
        Return an unassigned variable not already part of `assignment`.
        Choose the variable with the minimum number of remaining values
        in its domain. If there is a tie, choose the variable with the highest
        degree. If there is a tie, any of the tied variables are acceptable
        return values.
        """
        # Create a list of unassigned variables
        unassigned_variables = [var for var in self.crossword.variables if var not in assignment]
        # If unassigned variables is not empty
        if unassigned_variables:
            # Sort unassigned variables by the number of remaining values in its domain
            unassigned_variables.sort(key=lambda var: len(self.domains[var]))
            # Get the minimum number of remaining values
            min_values = len(self.domains[unassigned_variables[0]])
            min_value_vars = []
            for var in unassigned_variables:
                if len(self.domains[var]) == min_values:
                    min_value_vars.append(var)
                # If there is a tie, choose the variable with the highest degree
                if len(min_value_vars) > 1:
                    min_value_vars.sort(key=lambda var: len(self.crossword.neighbors(var)), reverse=True)
                return min_value_vars[0]
        # Return None if there are no unassigned variables
        return None

    def backtrack(self, assignment):
        """
        Using Backtracking Search, take as input a partial assignment for the
        crossword and return a complete assignment if possible to do so.

        `assignment` is a mapping from variables (keys) to words (values).

        If no assignment is possible, return None.
        """
        
        if self.assignment_complete(assignment):
            return assignment
        # Select an unassigned variable
        var = self.select_unassigned_variable(assignment)
        # Iterate over values in the domain of var
        for val in self.order_domain_values(var, assignment):
            # Add value to assignment
            assignment[var] = val
            # if value is consistent with assignment
            if self.consistent(assignment):
                # Update variable domain to be assigned value
                self.domains[var] = {val}
                # Inference
                inferences = self.ac3([(neighbor_var, var) for neighbor_var in self.crossword.neighbors(var)])
                # Check if inferences are consistent
                if inferences:
                    # Recursive call to backtrack
                    result = self.backtrack(assignment)
                    # Check if result is not None
                    if result is not None:
                        return result
                # Remove value from assignment
                del assignment[var]
        # Return None if no assignment is possible
        return None

def main():

    # Check usage
    if len(sys.argv) not in [3, 4]:
        sys.exit("Usage: python generate.py structure words [output]")

    # Parse command-line arguments
    structure = sys.argv[1]
    words = sys.argv[2]
    output = sys.argv[3] if len(sys.argv) == 4 else None

    # Generate crossword
    crossword = Crossword(structure, words)
    creator = CrosswordCreator(crossword)
    assignment = creator.solve()

    # Print result
    if assignment is None:
        print("No solution.")
    else:
        creator.print(assignment)
        if output:
            creator.save(assignment, output)


if __name__ == "__main__":
    main()

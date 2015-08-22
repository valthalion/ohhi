"""
Solve an 0hh1 puzzle read from a file

Use: python ohhi.py <filename>

The puzzle file contains a puzzle specified as a grid
with one row per line, each character being 'r' for a
red cell, 'b' for a blue cell and '.' for an undefined
cell.
"""

from __future__ import division
import sys
import cp_solver


def read_problem(filename):
    """
    Read a 0hh1 puzzle from file <filename>

    Takes a filename, and returns a problem dictionary with
    the following fields:
    - 'size': the number of rows/columns (assumed to be the same;
      an error will be raised if there is a size mismatch)
    - 'variables': the puzzle itself, a dictionary with (row, column)
      tuples as keys and the corresponding value 'r', 'b', or '.'
    - 'state': initially 'unsolved', to be updated by other methods
    """
    with open(filename, 'r') as problem_file:
        problem = [['rb' if c == '.' else c for c in line if c in '.rb']
                   for line in problem_file]
    size = len(problem)
    assert all(len(v) == size for v in problem)
    cells = {(r, c): problem[r][c] for r in range(size) for c in range(size)}
    problem_dict = {'size': size, 'variables': cells, 'state': 'unsolved'}
    return problem_dict


def print_problem(problem):
    """
    Print the problem using the same specification as when
    reading it from file
    """
    size = problem['size']
    cells = problem['variables']
    for row in range(size):
        for col in range(size):
            cell = cells[(row, col)]
            if len(cell) > 1:
                cell = '.'
            print cell,
        print
    print


def determined(problem):
    """
    Check if the problem has all cells set to a colour. Returns
    True/False accordingly

    To actually assess whether the problem is satisfactorily
    solved use evaluate_state(problem)
    """
    return all(len(cell) == 1 for cell in problem['variables'].values())


def eliminate_contiguous(problem):
    """
    Update the problem by setting the cells that can be inferred due to the
    constraint of no more than two contiguous cells of the same color.

    The cells dictionary in problem is modified. The return value is True if
    changes were made, False otherwise.
    """
    changes = False
    size = problem['size']
    cells = problem['variables']
    # See eliminate_contiguous_line() for the use of masks
    # Apply column-wise, up
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(size - 2),
                                         cols=range(size),
                                         mask=((1, 0), (2, 0)))
    # Apply column-wise, down
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(2, size),
                                         cols=range(size),
                                         mask=((-1, 0), (-2, 0)))
    # Apply column-wise, gap
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(1, size - 1),
                                         cols=range(size),
                                         mask=((1, 0), (-1, 0)))
    # Apply row-wise, left
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(size),
                                         cols=range(size - 2),
                                         mask=((0, 1), (0, 2)))
    # Apply row-wise, right
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(size),
                                         cols=range(2, size),
                                         mask=((0, -1), (0, -2)))
    # Apply row-wise, gap
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(size),
                                         cols=range(1, size - 1),
                                         mask=((0, 1), (0, -1)))
    return changes


def eliminate_contiguous_line(cells, rows, cols, mask):
    """
    Apply the constraint that there may be no more than two contiguous cells of
    the same colour.

    Check each (row, column) cell as specified by the rows and columns lists,
    and using the mask ((r0, c0), (r1, c1)) to define the direction: for cell
    (r, c), cells (r+r0, c+c0) and (r+r1, c+c1) will be considered contiguous;
    if both are set to the same colour, and (r, c) is unset, (r, c) will be set
    to the other colour.

    The cells dictionary is directly updated. Returns True if any changes have
    been made, False otherwise.
    """
    changes = False
    for row in rows:
        for col in cols:
            this_cell = cells[(row, col)]
            if len(this_cell) == 1:
                continue  # skip if cell is already decided
            cell1 = cells[(row + mask[0][0], col + mask[0][1])]
            cell2 = cells[(row + mask[1][0], col + mask[1][1])]
            if cell1 == cell2 == 'r':
                cells[(row, col)] = 'b'
                changes = True
            elif cell1 == cell2 == 'b':
                cells[(row, col)] = 'r'
                changes = True
    return changes


def full_colour(problem):
    """
    Update the problem by setting the cells that can be inferred from the 
    onstraint that each row and column must have the same number of cells of
    each colour.

    The cells dictionary is directly updated. Returns True if any changes have
    been made, False otherwise.
    """
    changes = False
    size = problem['size']
    cells_same_colour = size // 2
    cells = problem['variables']

    # See if each row already has all the required cells of one colour
    for row in range(size):
        reds = sum(1 for col in range(size) if cells[(row, col)] == 'r')
        blues = sum(1 for col in range(size) if cells[(row, col)] == 'b')
        if reds == blues == cells_same_colour:
            continue  # Nothing to do here, all cells set
        if reds == cells_same_colour:
            new_colour = 'b'  # All reds set, use blue to update this row
        elif blues == cells_same_colour:
            new_colour = 'r'  # All blues set, red blue to update this row
        else:
            continue  # The required number is not reached by either colour
        for col in range(size):  # Update unset cells with new colour
            if len(cells[(row, col)]) > 1:
                cells[(row, col)] = new_colour
                changes = True

    # See if each column already has all the required cells of one colour
    for col in range(size):
        reds = sum(1 for row in range(size) if cells[(row, col)] == 'r')
        blues = sum(1 for row in range(size) if cells[(row, col)] == 'b')
        if reds == blues == cells_same_colour:
            continue  # Nothing to do here, all cells set
        if reds == cells_same_colour:
            new_colour = 'b'  # All reds set, use blue to update this row
        elif blues == cells_same_colour:
            new_colour = 'r'  # All blues set, red blue to update this row
        else:
            continue  # The required number is not reached by either colour
        for row in range(size):  # Update unset cells with new colour
            if len(cells[(row, col)]) > 1:
                cells[(row, col)] = new_colour
                changes = True
    return changes


def evaluate_state(problem, report=False):
    """
    Check the state of a problem. This function does not return anything, but
    modifies the 'state' field of the problem:
    - if a constraint is not met, it is set to 'infeasible'
    - if all constraints are met and all cells are set, the state is set to
        'solved'
    - otherwise it is left unmodified (usually this should be 'unsolved')

    If report is set to True, the function will print the first (if any)
    constraint violation it finds; since it returns at that point, it is
    possible that additional violations exist.
    """
    # helper function to print violations if report is True
    def conditional_print(*args):
        """print() wrapper for logging violations"""
        if report:
            print args
  
    cells = problem['variables']
    size = problem['size']
    max_same_colour = size // 2

    # idx will be used first as column index, then as row index
    # to avoid doing two loops
    for idx in range(size):
        # Check each column
        col = [cells[(row, idx)] for row in range(size)]
        # infeasible if colum has more than max_same_colour reds
        if sum(1 for cell in col if cell == 'r') > max_same_colour:
            problem['state'] = 'infeasible'
            conditional_print('too many reds on column', idx)
            return
        # infeasible if colum has more than max_same_colour blues
        if sum(1 for cell in col if cell == 'b') > max_same_colour:
            problem['state'] = 'infeasible'
            conditional_print('too many blues on column', idx)
            return
        # infeasible if three adjacent cells of the same colour
        for pos in range(size - 2):
            if col[pos] == col[pos+1] == col[pos+2] != 'rb':
                problem['state'] = 'infeasible'
                conditional_print('three in a row - column', idx)
                return
        # check if the rest of the columns are duplicates of this one
        for other_col in range(idx + 1, size):
            col2 = [cells[(row, other_col)] for row in range(size)]
            same_reds = sum(1 for c1, c2 in zip(col, col2) if c1 == c2 == 'r')
            same_blues = sum(1 for c1, c2 in zip(col, col2) if c1 == c2 == 'b')
            # if one colour is fully duplicated, the column must be, too,
            # even if some cells are still unset (they will be set to the
            # other colour by constraint propagation)
            if same_reds >= max_same_colour or same_blues >= max_same_colour:
                problem['state'] = 'infeasible'
                conditional_print('duplicate columns', idx, other_col)
                return

        # Check each row
        row = [cells[(idx, col)] for col in range(size)]
        # infeasible if row has more than max_same_colour reds
        if sum(1 for cell in row if cell == 'r') > max_same_colour:
            problem['state'] = 'infeasible'
            conditional_print('too many reds on row', idx)
            return
        # infeasible if row has more than max_same_colour blues
        if sum(1 for cell in row if cell == 'b') > max_same_colour:
            problem['state'] = 'infeasible'
            conditional_print('too many blues on row', idx)
            return
        for pos in range(size - 2):
            if row[pos] == row[pos+1] == row[pos+2] != 'rb':
                problem['state'] = 'infeasible'
                conditional_print('three in a row - row', idx)
                return
        # check if the rest of the rows are duplicates of this one
        for other_row in range(idx + 1, size):
            row2 = [cells[(other_row, col)] for col in range(size)]
            same_reds = sum(1 for c1, c2 in zip(row, row2) if c1 == c2 == 'r')
            same_blues = sum(1 for c1, c2 in zip(row, row2) if c1 == c2 == 'b')
            # if one colour is fully duplicated, the column must be too
            # even if some cells are still unset (they will be set to the
            # other colour by constraint propagation)
            if same_reds >= max_same_colour or same_blues >= max_same_colour:
                problem['state'] = 'infeasible'
                conditional_print('duplicate rows', idx, other_row)
                return

    # check if solved <--> feasible and determined
    # at this point feasibility is guaranteed (see doc for solved())
    if determined(problem):
        problem['state'] = 'solved'


def solve(problem):
    """
    Solve a 0hh1 problem

    Returns the problem at the last stage in the solution process. The problem
    'state' field will be set to 'solved' or 'infeasible' as adequate.
    """
    constraints = [eliminate_contiguous, full_colour]
    solution = cp_solver.solve(problem, constraints, evaluate_state)
    return solution


def main():
    """
    Read problem from file passed as argument to the script and solve it

    Show whether the problem was solved or infeasible, print out the solution
    (or the last try if infeasible); if infeasible, detail the first broken
    constraint found in the final try
    """
    if len(sys.argv) < 2:
        print "No puzzle file provided\nUsage: python ohhi.py <filename>"
        print
        exit(1)
    
    from_file = sys.argv[1]
    the_problem = read_problem(from_file)
    solution = solve(the_problem)

    print "Problem", solution['state']
    print_problem(solution)
    # If infeasible, show why
    if solution['state'] == 'infeasible':
        evaluate_state(solution, report=True)


if __name__ == '__main__':
    main()

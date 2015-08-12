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


def read_problem(filename):
    """
    Read a 0hh1 puzzle from file <filename>

    Takes a filename, and returns a problem dictionary with
    the following fields:
    - 'size': the number of rows/columns (assumed to be the same;
      an error will be raised if there is a size mismatch)
    - 'cells': the puzzle itself, a dictionary with (row, column)
      tuples as keys and the corresponding value 'r', 'b', or '.'
    - 'state': initially 'unsolved', to be updated by other methods
    """
    with open(filename, 'r') as f:
        problem = [[c for c in line if c in '.rb'] for line in f]
    size = len(problem)
    assert all(map(lambda v: len(v) == size, problem))
    cells = {(r, c): problem[r][c] for r in range(size) for c in range(size)}
    problem_dict = {'size': size, 'cells': cells, 'state': 'unsolved'}
    return problem_dict


def print_problem(problem):
    """
    Print the problem using the same specification as when
    reading it from file
    """
    n = problem['size']
    cells = problem['cells']
    for row in range(n):
      print ''.join(cells[(row, col)] for col in range(n))
    print


def solved(problem):
    """
    Check if the problem has all cells set to a colour. Returns
    True/False accordingly

    To actually assess whether the problem is satisfactorily
    solved use check_feasibility(problem)
    """
    return all(map(lambda c: c in 'rb', problem['cells'].values()))


def eliminate_contiguous(problem):
    """
    Update the problem by setting the cells that can be
    inferred due to the constraint of no more than two
    contiguous cells of the same color.

    The cells dictionary in problem is modified. The return
    value is True if changes were made, False otherwise.
    """
    changes = False
    n = problem['size']
    cells = problem['cells']
    # See eliminate_contiguous_lines() for the use of masks
    # Apply column-wise, up
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(n - 2),
                                         cols=range(n),
                                         mask=[(1, 0), (2, 0)])
    # Apply column-wise, down
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(2, n),
                                         cols=range(n),
                                         mask=[(-1, 0), (-2, 0)])
    # Apply column-wise, gap
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(1, n - 1),
                                         cols=range(n),
                                         mask=[(1, 0), (-1, 0)])
    # Apply row-wise, left
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(n),
                                         cols=range(n - 2),
                                         mask=[(0, 1), (0, 2)])
    # Apply row-wise, right
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(n),
                                         cols=range(2, n),
                                         mask=[(0, -1), (0, -2)])
    # Apply row-wise, gap
    changes |= eliminate_contiguous_line(cells,
                                         rows=range(n),
                                         cols=range(1, n - 1),
                                         mask=[(0, 1), (0, -1)])
    return changes


def eliminate_contiguous_line(cells, rows, cols, mask):
    """
    Apply the no more than two contiguous cells of the same colour

    Check each (row, column) cell as specified by the rows and
    columns lists, and using the mask ((r0, c0), (r1, c1)) to
    define the direction: for cell (r, c), cells (r+r0, c+c0) and
    (r+r1, c+c1) will be considered contiguous; if both are set to
    the same colour, and (r, c) is unset, (r, c) will be set to the
    other colour.

    The cells dictionary is directly updated. Returns True if any
    changes have been made, False otherwise.
    """
    changes = False
    for row in rows:
        for col in cols:
            this_cell = cells[(row, col)]
            if this_cell in 'rb':
                continue
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
    Update the problem by setting the cells that can be inferred
    from the constraint that each row and column must have the
    same number of cells of each colour.

    The cells dictionary is directly updated. Returns True if any
    changes have been made, False otherwise.
    """
    changes = False
    n = problem['size']
    cells_same_colour = n // 2
    cells = problem['cells']
    # See if each row already has all the erquired cells of one colour
    for row in range(n):
        reds = len(filter(lambda c: c == 'r',
                          (cells[(row, col)] for col in range(n))))
        blues = len(filter(lambda c: c == 'b',
                           (cells[(row, col)] for col in range(n))))
        if reds == blues == cells_same_colour:
            continue  # Nothing to do here, all cells set
        if reds == cells_same_colour:
            new_colour = 'b'  # All reds set, use blue to update this row
        elif blues == cells_same_colour:
            new_colour = 'r'  # All blues set, red blue to update this row
        else:
            continue  # The required number is not reached by either colour
        for col in range(n):  # Update unset cells with new colour
            if cells[(row, col)] == '.':
                cells[(row, col)] = new_colour
                changes = True
    # See if each column already has all the erquired cells of one colour
    for col in range(n):
        reds = len(filter(lambda c: c == 'r',
                          (cells[(row, col)] for row in range(n))))
        blues = len(filter(lambda c: c == 'b',
                           (cells[(row, col)] for row in range(n))))
        if reds == blues == cells_same_colour:
            continue  # Nothing to do here, all cells set
        if reds == cells_same_colour:
            new_colour = 'b'  # All reds set, use blue to update this row
        elif blues == cells_same_colour:
            new_colour = 'r'  # All blues set, red blue to update this row
        else:
            continue  # The required number is not reached by either colour
        for row in range(n):  # Update unset cells with new colour
            if cells[(row, col)] == '.':
                cells[(row, col)] = new_colour
                changes = True
    return changes


def check_feasibility(problem, report=False):
    """
    Check the state of a problem. This function does not return
    anything, but modifies the 'state' field of the problem:
    - if a constraint is not met, it is set to 'infeasible'
    - if all constraints are met and all cells are set, the
      state is set to 'solved'
    - otherwise it is left unmodified (usually this should be
      'unsolved')

    If report is set to True, the function will print the first
    (if any) constraint violation it finds; since it returns
    at that point, it is possible that additional violations
    exist.
    """
    # r(): helper function to print violations if report is True
    if report:
        def r(*args):
            print(args)
    else:
        def r(*args):
            pass
  
    cells = problem['cells']
    n = problem['size']

    # row_or_col will be used first as column index, then as row index
    # to avoid doing too loops
    for row_or_col in range(n):
        # Check each column
        col = [cells[(row, row_or_col)] for row in range(n)]
        # infeasible if colum has more than n//2 reds
        if len(filter(lambda c: c == 'r', col)) > n // 2:
            problem['state'] = 'infeasible'
            r('too many reds on column', row_or_col)
            return
        # infeasible if colum has more than n//2 blues
        if len(filter(lambda c: c == 'b', col)) > n // 2:
            problem['state'] = 'infeasible'
            r('too many blues on column', row_or_col)
            return
        # infeasible if three adjacent cells of the same colour
        for s in range(n - 2):
            if col[s] == col[s+1] == col[s+2] != '.':
                problem['state'] = 'infeasible'
                r('three in a row - column', row_or_col)
                return
        # check if the rest of the columns are duplicates of this one
        for other_col in range(row_or_col + 1, n):
            col2 = [cells[(row, other_col)] for row in range(n)]
            same_reds = sum(1 for c1, c2 in zip(col, col2) if c1 == c2 == 'r')
            same_blues = sum(1 for c1, c2 in zip(col, col2) if c1 == c2 == 'b')
            # if one colour is fully duplicated, the column must be too
            # even if some cells are still unset (they will be set to the
            # other colour by constraint propagation)
            if same_reds >= n // 2 or same_blues >= n // 2:
                problem['state'] = 'infeasible'
                r('duplicate columns', row_or_col, other_col)
                return

        # Check each row
        row = [cells[(row_or_col, col)] for col in range(n)]
        # infeasible if row has more than n//2 reds
        if len(filter(lambda c: c == 'r', row)) > n // 2:
            problem['state'] = 'infeasible'
            r('too many reds on row', row_or_col)
            return
        # infeasible if row has more than n//2 blues
        if len(filter(lambda c: c == 'b', row)) > n // 2:
            problem['state'] = 'infeasible'
            r('too many blues on row', row_or_col)
            return
        for s in range(n - 2):
            if row[s] == row[s+1] == row[s+2] != '.':
                problem['state'] = 'infeasible'
                r('three in a row - row', row_or_col)
                return
        # check if the rest of the rows are duplicates of this one
        for other_row in range(row_or_col + 1, n):
            row2 = [cells[(other_row, col)] for col in range(n)]
            same_reds = sum(1 for c1, c2 in zip(row, row2) if c1 == c2 == 'r')
            same_blues = sum(1 for c1, c2 in zip(row, row2) if c1 == c2 == 'b')
            # if one colour is fully duplicated, the column must be too
            # even if some cells are still unset (they will be set to the
            # other colour by constraint propagation)
            if same_reds >= n // 2 or same_blues >= n // 2:
                problem['state'] = 'infeasible'
                r('duplicate rows', row_or_col, other_row)
                return

    # check if solved
    # at this point feasibility is guaranteed (see doc for solved())
    if solved(problem):
        problem['state'] = 'solved'


def get_undecided_cell(problem):
    """
    Return one cell that is still unset in the problem as
    a (row, column) tuple
    """
    n = problem['size']
    for r in range(n):
        for c in range(n):
            if problem['cells'][(r, c)] == '.':
                return r, c


def choose(problem, r, c, colour):
    """
    Return a new problem that is a copy of the one provided with
    the (r, c) cell set to colour

    This function is used for branching, and prints the selection
    made.
    """
    new_problem = problem.copy()
    new_problem['cells'] = problem['cells'].copy()
    new_problem['cells'][(r, c)] = colour
    print "choosing:", r, c, colour
    return new_problem


def refine(problem):
    """
    Fill in inferrable cells by constraint propagation

    The cells dictionary is updated directly. Returns True
    if any changes were made, False otherwise.
    """
    changes = True
    while changes:
        changes = False
        changes |= eliminate_contiguous(problem)
        changes |= full_colour(problem)
    check_feasibility(problem)


def solve(problem):
    """
    Solve a 0hh1 problem

    Returns the problem at the last stage in the solution
    process. The problem 'state' field will be set to
    'solved' or 'infeasible' as adequate.
    """
    # Recursively explore the solution space:
    # - Fill in inferrable cells (constraint propagation)
    # - If this fully solves the problem, or identifies
    #   infeasibility, return the problem
    # - Otherwise select un unset cell, try to solve the
    #   problem with that cell set to 'r', if it doesn't
    #   succeed try 'b' in that cell
    # This results in a depth-first search of the solution
    # (binary) tree, with aggressive pruning (both from the
    #  leaps obtained by constraint propagation and by
    # abandoning a branch as soon as infeasibility is
    # identified, even if not all cells are set)

    refine(problem)
    if problem['state'] in ('solved', 'infeasible'):
        return problem

    # select cell to branch on
    r, c = get_undecided_cell(problem)

    # recursion on red branch
    new_problem = choose(problem, r, c, 'r')
    candidate_sol = solve(new_problem)
    if candidate_sol['state'] == 'solved':
        return candidate_sol

    # recursion on blue branch
    new_problem = choose(problem, r, c, 'b')
    candidate_sol = solve(new_problem)
    return candidate_sol  # solved or infeasible


if __name__ == '__main__':
    if len(sys.argv) < 2:
        print "No puzzle file provided\nUsage: python ohhi.py <filename>"
        print
        exit(1)
    
    filename = sys.argv[1]
    problem = read_problem(filename)
    solution = solve(problem)

    print "Problem", solution['state']
    print_problem(solution)
    # If infeasible, show why
    if solution['state'] == 'infeasible':
        check_feasibility(solution, report=True)

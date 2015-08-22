# ohhi: 0h h1 Puzzle Solver

## 0h h1 solving

Solve an [0h h1](http://0hh1.com/ "0h h1") puzzle read from a file.

Usage:

    python ohhi.py <filename>

The puzzle file `<filename>` contains a puzzle specified as a grid
with one row per line, each character being 'r' for a red cell,
'b' for a blue cell and '.' for an undefined cell.

ohhi combines constraint propagation and search. It recursively
explores the solution space:

1. It fills in inferrable cells (constraint propagation)
2. If this fully solves the problem, or identifies infeasibility,
   the problem is solved (infeasibility is an acceptable
   outcome)
3. Otherwise select an unset cell, try to solve the problem with
   that cell set as red; if it doesn't succeed try blue in that cell

This results in a depth-first search of the solution (binary) tree,
with aggressive pruning (both from the leaps obtained by constraint
propagation and by abandoning a branch as soon as infeasibility is
identified, even if not all cells are set).

## General constraint programming solving

The process described above of constraint propagation and search can
be generalized. In fact, the most recent implementation separates
both processes, and uses `cp_solver.py` for the solution procedure,
while the details specific to 0h h1 are defined in `ohhi.py`.

Solutions to additional games may come in the future. This could
be applied to solve, for instance, 0h n0 or sudoku. In fact, the
excellent recent post on
[Peter Norvig's blog](http://norvig.com/sudoku.html "Peter Norvig's blog")
about using constraint propagation for solving sudoku was the
reason for starting this.
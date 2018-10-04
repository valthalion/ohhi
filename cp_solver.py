"""
Solve a constraint programming problem
"""


def propagate_constraints(problem, constraints):
    """
    Apply the constraint propagation functions in constraints to problem.

    Each constraint in constraints should update the values in the problem
    and return True if changes were made, False otherwise.

    Apply each constraint, and repeat until no changes are made in a full
    cycle.
    """
    changes = True
    while changes:
        changes = any(constraint(problem) for constraint in constraints)


def get_undecided_variable(problem):
    """
    Return one variable that is still unset in the problem
    """
    for variable, domain in problem['variables'].items():
        if len(domain) > 1:  # Undecided if more than 1 value possible
            return variable


def fix_variable(problem, pivot, value):
    """
    Return a new problem that is a copy of the one provided with
    the pivot variable set to value

    This function is used for branching, and prints the selection
    made.
    """
    new_problem = problem.copy()
    new_problem['variables'] = problem['variables'].copy()
    new_problem['variables'][pivot] = value
    print(f'choosing: {pivot} {value}')
    return new_problem


def solve(problem, constraints, evaluate_state):
    """
    Solve a constraint programming problem

    Inputs:
    - problem: a dictionary containing the information for the problem to be
        solved. It may contain additional fields for use in the constraint
        propagation functions, or the state evaluation function (or for any
        other reason), but it must contain at least the following fields:
        * 'variables': a dictionary with the variables to be solved as keys;
            the corresponding value is the domain of the variable, an iterable
            with all currently feasible values for the variable. This function
            will assume that a variable is set (decided) if its domain is of
            length 1
        * 'state': the state of the problem; typically at call time it will be
            'unsolved'. It will be updated as appropriate to 'solved' or
            'infeasible'.
    - constraints: an iterable containing the constraint propagation functions
        available to the CP solver. Each one must accept a problem dictionary
        and apply update the domains of all variables where the constraint
        allows inference; this may mean determining one value, or reducing the
        current domain by emoving some of its elements
    - evaluate_state: a function that takes a problem as input and determines
        whether the problem is still unsolved, in an incoherent state
        (infeasible) or solved, and updates its 'state' field accordingly.

    Returns:
    - the problem at the last stage in the solution process. The problem
        'state' field will be set to 'solved' or 'infeasible' as adequate.
    """

    # Recursively explore the solution space:
    # - Fill in inferrable variables (constraint propagation)
    # - If this fully solves the problem, or identifies
    #   infeasibility, return the problem
    # - Otherwise select an undecided variable, try to solve the problem with
    #   that variable set to one of its remaining feasible values, if it
    #   doesn't succeed, iteratively try the other potential values for that
    #   variable
    # This results in a depth-first search of the solution tree, with
    # aggressive pruning (both from the leaps obtained by constraint
    # propagation and by abandoning a branch as soon as infeasibility is
    # identified, even if not all values are set)

    propagate_constraints(problem, constraints)
    evaluate_state(problem)
    if problem['state'] in ('solved', 'infeasible'):
        return problem

    # select variable to branch on
    pivot = get_undecided_variable(problem)

    # recursion on each domain value feasible for the pivot
    domain = problem['variables'][pivot]
    for value in domain:
        new_problem = fix_variable(problem, pivot, value)
        candidate_sol = solve(new_problem, constraints, evaluate_state)
        if candidate_sol['state'] == 'solved':
            return candidate_sol

    # if this point is reached, the problem must be infeasible
    return candidate_sol

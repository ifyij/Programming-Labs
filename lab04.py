# -*- coding: utf-8 -*-
"""
Created on Fri Mar  4 11:19:19 2022

@author: ifyij
"""

#!/usr/bin/env python3
"""6.009 Lab -- Six Double-Oh Mines"""

import typing
import doctest

# NO ADDITIONAL IMPORTS ALLOWED!


def dump(game):
    """
    Prints a human-readable version of a game (provided as a dictionary)
    """
    for key, val in sorted(game.items()):
        if isinstance(val, list) and val and isinstance(val[0], list):
            print(f'{key}:')
            for inner in val:
                print(f'    {inner}')
        else:
            print(f'{key}:', val)


# 2-D IMPLEMENTATION





def new_game_2d(num_rows, num_cols, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.

    Parameters:
       num_rows (int): Number of rows
       num_cols (int): Number of columns
       bombs (list): List of bombs, given in (row, column) pairs, which are
                     tuples

    Returns:
       A game state dictionary

    >>> dump(new_game_2d(2, 4, [(0, 0), (1, 0), (1, 1)]))
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: ongoing
    visible:
        [False, False, False, False]
        [False, False, False, False]
    """
    #Calling nd version to minimize code
    return new_game_nd((num_rows,num_cols), bombs)
                
    
   


def dig_2d(game, row, col):
    """
    Reveal the cell at (row, col), and, in some cases, recursively reveal its
    neighboring squares.

    Update game['visible'] to reveal (row, col).  Then, if (row, col) has no
    adjacent bombs (including diagonally), then recursively reveal (dig up) its
    eight neighbors.  Return an integer indicating how many new squares were
    revealed in total, including neighbors, and neighbors of neighbors, and so
    on.

    The state of the game should be changed to 'defeat' when at least one bomb
    is visible on the board after digging (i.e. game['visible'][bomb_location]
    == True), 'victory' when all safe squares (squares that do not contain a
    bomb) and no bombs are visible, and 'ongoing' otherwise.

    Parameters:
       game (dict): Game state
       row (int): Where to start digging (row)
       col (int): Where to start digging (col)

    Returns:
       int: the number of new squares revealed

    >>> game = {'dimensions': (2, 4),
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 3)
    4
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: (2, 4)
    state: victory
    visible:
        [False, True, True, True]
        [False, False, True, True]

    >>> game = {'dimensions': [2, 4],
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible': [[False, True, False, False],
    ...                  [False, False, False, False]],
    ...         'state': 'ongoing'}
    >>> dig_2d(game, 0, 0)
    1
    >>> dump(game)
    board:
        ['.', 3, 1, 0]
        ['.', '.', 1, 0]
    dimensions: [2, 4]
    state: defeat
    visible:
        [True, True, False, False]
        [False, False, False, False]
    """
    #calling nd version with the dimension being (row,column)
    return dig_nd(game, (row,col))
    


def render_2d_locations(game, xray=False):
    """
    Prepare a game for display.

    Returns a two-dimensional array (list of lists) of '_' (hidden squares),
    '.' (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  game['visible'] indicates which squares should be visible.  If
    xray is True (the default is False), game['visible'] is ignored and all
    cells are shown.

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A 2D array (list of lists)

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, True, False],
    ...                   [False, False, True, False]]}, False)
    [['_', '3', '1', '_'], ['_', '_', '1', '_']]

    >>> render_2d_locations({'dimensions': (2, 4),
    ...         'state': 'ongoing',
    ...         'board': [['.', 3, 1, 0],
    ...                   ['.', '.', 1, 0]],
    ...         'visible':  [[False, True, False, True],
    ...                   [False, False, False, True]]}, True)
    [['.', '3', '1', ' '], ['.', '.', '1', ' ']]
    """
    #calling nd version to minimize repeated code
    return render_nd(game,xray)
                    
        


def render_2d_board(game, xray=False):
    """
    Render a game as ASCII art.

    Returns a string-based representation of argument 'game'.  Each tile of the
    game board should be rendered as in the function
        render_2d_locations(game)

    Parameters:
       game (dict): Game state
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       A string-based representation of game

    >>> render_2d_board({'dimensions': (2, 4),
    ...                  'state': 'ongoing',
    ...                  'board': [['.', 3, 1, 0],
    ...                            ['.', '.', 1, 0]],
    ...                  'visible':  [[True, True, True, False],
    ...                            [False, False, True, False]]})
    '.31_\\n__1_'
    """
    rows = game['dimensions'][0]
    ans = ''
    locations = render_2d_locations(game,xray)
    for r in range(rows):
        ans += ''.join(locations[r])
        if r < rows-1:
            ans += '\n'
    return ans
    


# N-D IMPLEMENTATION


#Helper functions
def make_nd_board(dimensions,fill):
     """
     Parameters
     ----------
     dimensions : tuple that describes the dimensions and dimension
     fill : what I'm filling the game board with

     Returns
     -------
     embedded list representing n-dimensional board for game 
     """
     ans=[]
     list_dim = list(dimensions)
     
     #base case
     if len(list_dim) == 1: #when the dimensions is less than one
         return [fill for i in range(list_dim[0])] #makes a list of the length n, n being the last element of the dimension
     
     for x in range(list_dim.pop(0)): #makes n number of lists depending on element in the dimension
         ans.append(make_nd_board((*list_dim,), fill)) #recursive call and shrinking the dimension down
     return ans

def get_all_coords(dimensions, prev =() ):
    """
    Given:
    dimesnisons: the dimensions of the board in the form of a tuple
    prev: the previous values in the target coord before the dimension of that iteration
    returns all of the possible coordinates in the board as a set of tuples
    """
    ans = set()
    list_dim = list(dimensions)
    
    #base case
    if len(list_dim)==1: #the last element of the dimension tuple
        for x in range(list_dim[0]): 
            current_coord = prev + (x,) #adds the last number of the coordinate
            ans.add(current_coord) #adds it to the set of coordinates
        return ans
    
    #recursive case
    for x in range(list_dim.pop(0)):
        current_coord = prev + (x,) #building up a coordinate
        ans = set.union(ans,(get_all_coords((*list_dim,),current_coord)))
    return ans

def get_nd_neighbors(dimension, coord, prev = ()):
    
    """

    Parameters
    ----------
    dimension : dimension of the board in the form of a tuple
    coord : tuple coordinate that you want the neighbors of
    prev: a tuple that has the previous values in the target coordinate before the dimension of that iteration
    Returns
    -------
    list of neighbors
    """
    ans = set()
    list_dim = list(dimension)
    list_coord = list(coord)
    num = list_coord[-1] #the current coordinate value that you're getting surrounding things
    dim = list_dim[-1] #the appropiate dimensions
    
    #base case where you get neighbor coordinate corresponding with first element in coordinate
    if len(dimension)==1:
        for i in range(-1,2):
            if num+i >=0 and num+i < list_dim[0]: #checking to see if its in bounds
                ans.add((num+i,))
        return ans
    else:
        for ele in get_nd_neighbors(dimension[:-1], coord[:-1]): #iterate through the previously generated coordinates
            for i in range(-1,2): #range for getting neighbors
                if num+i >= 0 and num+i <dim: #checking if it's in bounds
                    new_coord = ele + (num+i,) #adding the next coordinate
                    ans.add(new_coord) #building list of unfinished coordinates
        return ans
    
    
def mutate_board(board,coordinate,new_value):
    """
    Parameters
    ----------
    board : board that is being mutated
    dimensions : dimensions of the board
    coordinate : coordinate that you want to change the value of
    new_value : the value you want at the given coordinate

    Returns
    -------
    None.

    """
    
    list_coord = list(coordinate) #turning tuple into a list to use pop
    
    #base case
    if len(coordinate) == 1:
        board[list_coord.pop(0)] = new_value #getting to the final index in the coordinate and changing it
        return None
    
    first_ind = list_coord.pop(0) 
    #recursive case
    mutate_board(board[first_ind], (*list_coord,), new_value) #getting deeper into the list of lists 
    
def get_value(board, coordinate):
    """
    Parameters
    ----------
    board : board in the form of list of lists
    coordinate : tuple of coordinate

    Returns
    -------
    value at that coordinate on the board
    """
    #very similar code to mutate_board except return value rather than changing it
    list_coord = list(coordinate)
    
    if len(coordinate) == 1:
        return board[list_coord.pop(0)] 
    
    first_ind = list_coord.pop(0)
    return get_value(board[first_ind], (*list_coord,))

#Lab functions,
def new_game_nd(dimensions, bombs):
    """
    Start a new game.

    Return a game state dictionary, with the 'dimensions', 'state', 'board' and
    'visible' fields adequately initialized.


    Args:
       dimensions (tuple): Dimensions of the board
       bombs (list): Bomb locations as a list of tuples, each an
                     N-dimensional coordinate

    Returns:
       A game state dictionary

    >>> g = new_game_nd((2, 4, 2), [(0, 0, 1), (1, 0, 0), (1, 1, 1)])
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, False], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
    """    
    
            
    visible = make_nd_board(dimensions, False) #making visible board
    board = make_nd_board(dimensions, 0) #making game board
    
    
    for ele in bombs:
        mutate_board(board, ele, '.') #putting a bomb in the appropiate places in the board
        for y in get_nd_neighbors(dimensions,ele): #iterating through the neighbors of bombs
            if get_value(board, y) != '.':
                mutate_board(board, y, get_value(board, y)+1) #adding 1 if the position has a bomb as a neighbor
    
    #returning game in the proper representaion
            
    return {
        'dimensions': dimensions,
        'board': board,
        'visible': visible,
        'state': 'ongoing'}
            


def dig_nd(game, coordinates, recursive = False):
    """
    Recursively dig up square at coords and neighboring squares.

    Update the visible to reveal square at coords; then recursively reveal its
    neighbors, as long as coords does not contain and is not adjacent to a
    bomb.  Return a number indicating how many squares were revealed.  No
    action should be taken and 0 returned if the incoming state of the game
    is not 'ongoing'.

    The updated state is 'defeat' when at least one bomb is visible on the
    board after digging, 'victory' when all safe squares (squares that do
    not contain a bomb) and no bombs are visible, and 'ongoing' otherwise.

    Args:
       coordinates (tuple): Where to start digging
       game (dict): current game state
       recursive (bool): whether this is a recursive call or not, set to False

    Returns:
       int: number of squares revealed

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 3, 0))
    8
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: ongoing
    visible:
        [[False, False], [False, True], [True, True], [True, True]]
        [[False, False], [False, False], [True, True], [True, True]]
    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [False, False],
    ...                [False, False]],
    ...               [[False, False], [False, False], [False, False],
    ...                [False, False]]],
    ...      'state': 'ongoing'}
    >>> dig_nd(g, (0, 0, 1))
    1
    >>> dump(g)
    board:
        [[3, '.'], [3, 3], [1, 1], [0, 0]]
        [['.', 3], [3, '.'], [1, 1], [0, 0]]
    dimensions: (2, 4, 2)
    state: defeat
    visible:
        [[False, True], [False, True], [False, False], [False, False]]
        [[False, False], [False, False], [False, False], [False, False]]
        
    
    """

    
    #helper function
    def get_game_state(game,all_coords):
        """
        Given a game and a list of all the possible coordinates in that game board
        Returns "victory", "defeat","ongoing"

        """
        covered_squares = 0
        for ele in all_coords:
            #checking to see if a bomb was revealed on that move
            if get_value(game['board'], ele) == '.':
                if get_value(game['visible'], ele) == True:
                    return 'defeat' #defeat if bomb was revealed
            else:
                #summing all the squares uncovered
                if get_value(game['visible'], ele) == False:
                    covered_squares += 1
        if covered_squares == 0:
            return 'victory' #all squares were uncovered and no bombs revealed
        else:
            return 'ongoing' #all squares were not uncovered
            
                
                    
    #boundary case to make sure the game isnt over before digging
    if game['state'] == 'defeat' or game['state'] == 'victory':
        return 0
    #uncovering a bomb
    if get_value(game['board'], coordinates) == '.':
        mutate_board(game['visible'], coordinates, True)
        game['state'] = 'defeat'
        return 1
    #uncovering a square without a bomb
    if get_value(game['visible'], coordinates) != True:
        mutate_board(game['visible'], coordinates, True)
        revealed = 1 #initializing revealed that will be added to 
    else:
        return 0 #this square was already uncovered
    
    coord_neighbors = get_nd_neighbors(game['dimensions'], coordinates) #getting neighbors of the coordinate
    if get_value(game['board'], coordinates) == 0: #if there are no surrounding bombs of digged coordinate
        for ele in coord_neighbors:
            #revealing all the spaces around coordinate that space is not a bomb and calling dig_nd on each revealed space
            if get_value(game['board'], ele) != '.': 
                revealed += dig_nd(game, ele,True) 
    
    
    if recursive == False: #recursive cases are ongoing games so only checking victory on non recursive games
        all_coords = get_all_coords(game['dimensions'])
        state = get_game_state(game,all_coords)
        game['state'] = state
        if state == 'defeat':
            return 0
        if state == 'ongoing':
            return revealed
        if state == 'victory':
            return revealed
    return revealed
    
           

    
    


def render_nd(game, xray=False):
    """
    Prepare the game for display.

    Returns an N-dimensional array (nested lists) of '_' (hidden squares), '.'
    (bombs), ' ' (empty squares), or '1', '2', etc. (squares neighboring
    bombs).  The game['visible'] array indicates which squares should be
    visible.  If xray is True (the default is False), the game['visible'] array
    is ignored and all cells are shown.

    Args:
       xray (bool): Whether to reveal all tiles or just the ones allowed by
                    game['visible']

    Returns:
       An n-dimensional array of strings (nested lists)

    >>> g = {'dimensions': (2, 4, 2),
    ...      'board': [[[3, '.'], [3, 3], [1, 1], [0, 0]],
    ...                [['.', 3], [3, '.'], [1, 1], [0, 0]]],
    ...      'visible': [[[False, False], [False, True], [True, True],
    ...                [True, True]],
    ...               [[False, False], [False, False], [True, True],
    ...                [True, True]]],
    ...      'state': 'ongoing'}
    >>> render_nd(g, False)
    [[['_', '_'], ['_', '3'], ['1', '1'], [' ', ' ']],
     [['_', '_'], ['_', '_'], ['1', '1'], [' ', ' ']]]

    >>> render_nd(g, True)
    [[['3', '.'], ['3', '3'], ['1', '1'], [' ', ' ']],
     [['.', '3'], ['3', '.'], ['1', '1'], [' ', ' ']]]
    """
        
    ans = make_nd_board(game['dimensions'], '_') #making board of all uncovered spaces
    all_coords = get_all_coords(game['dimensions'])
    
    #revealing everything
    if xray:
        for ele in all_coords:
            if get_value(game['board'], ele) == 0:
                mutate_board(ans, ele, ' ')
            else:
                mutate_board(ans, ele, str(get_value(game['board'], ele))) 
    #changing every coordinate to the appropiate string if visible
    else:
        for ele in all_coords:
            if get_value(game['visible'], ele) == True:
                if get_value(game['board'], ele) == 0:
                    mutate_board(ans, ele, ' ')
                else:
                   mutate_board(ans, ele, str(get_value(game['board'], ele)))
    return ans
                
        

if __name__ == "__main__":
    # Test with doctests. Helpful to debug individual lab.py functions.
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)  # runs ALL doctests

    # Alternatively, can run the doctests JUST for specified function/methods,
    # e.g., for render_2d_locations or any other function you might want.  To
    # do so, comment out the above line, and uncomment the below line of code.
    # This may be useful as you write/debug individual doctests or functions.
    # Also, the verbose flag can be set to True to see all test results,
    # including those that pass.
    #
    # doctest.run_docstring_examples(
    #    render_2d_locations,
    #    globals(),
    #    optionflags=_doctest_flags,
    #    verbose=False
    # )

# 6.009 Lab 2: Snekoban

import json
import typing

# NO ADDITIONAL IMPORTS!


direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}


def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, representing the
    locations of the objects on the board (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['wall'], ['computer']],
        [['target', 'player'], ['computer'], ['target']],
    ]

    Returns:
    A dictionary with 5 keys:
        * 'walls': a set of tuples, the tuples are coordinates where the walls are (row, column)
        * 'computers': a set of coordinates of computers (tuples)
        * 'player': a singe coordinate describing where the player is (a tuple)
        * 'target': a set of coordinates (tuples)
        * 'dimensions': a tuple (height,width) (rows,columns)
    """
    #getting the height and width from the list of lists
    height = len(level_description)
    width = len(level_description[0])
    
    #naming variables for key values
    wall_positions = set()
    computer_positions = set()
    player_position = ()
    target_positions = set()
    dimensions = (height, width)
    
    #iterating through the lab representation and getting the coordinates for each board element
    for y in range(height):  #going through the rows
        row = level_description[y].copy() 
        for x in range(width): #going through the columns
            if row[x] == ['wall']:
                wall_positions.add((y,x))
            if 'computer' in row[x]:
                computer_positions.add((y,x))
            if 'player' in row[x]:
                player_position = (y,x)
            if 'target' in row[x]:
                target_positions.add((y,x))
                
    #instantiating the result and setting the keys to the sets and tuples
    newgame = {
        'walls': wall_positions,
        'computers': computer_positions,
        'player': player_position,
        'target': target_positions,
        'dimensions': dimensions,
        
        }
    return newgame
    
    


def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    #testing the boundary case for when there are no targets
    if len(game['target']) == 0:
        return False
    #adding up the number of target coordinates that are also in computer coordinates
    count = 0;
    for ele in game['target']:
        if ele in game['computers']:
            count +=1
    #checking if all the computers are on targets 
    if count == len(game['target']):
        return True
    return False
        
        
    

def can_move(game,obj,proposed_position, direct):
    """
    Parameters: 
        * game: internal representation of game state as returned in new_game, dictionary
        * obj: string that states what object is moving ex. 'computers'
        * proposed_position: tuple that represents coordinate on the board that you want to move the object to
        * direct: string of direction ex. 'up'
    Returns:
        A boolean that describes whether the player, or the computer, can move
        based off of the game rools

    """
    
    
    if obj == 'player':
        if proposed_position in game['walls']: #can't move into walls
            return False
        elif proposed_position in game['computers']:
            #making a proposed position in the direction of the first one and calling the function again
            comp_new_pos = (direct[0]+proposed_position[0], direct[1]+proposed_position[1]) 
            return can_move(game,'computers', comp_new_pos, direct )
        else:
            return True
        
    if obj == 'computers':
        if proposed_position in game['walls']:
            return False
        elif proposed_position in game['computers']: #cant move computer if computer is next to it
            return False
        else:
            return True

def step_game(game, direction):
    """
    Given a game representation (of the form returned from new_game), return a
    new game representation (of that same form), representing the updated game
    after running one step of the game.  The user's input is given by
    direction, which is one of the following: {'up', 'down', 'left', 'right'}.

    This function should not mutate its input.
    """
    #instantiatiating answer and copying the passed in game values 
    game_ans = {
        
        'walls': game['walls'],
        'computers': game['computers'],
        'player': game['player'],
        'target': game['target'],
        'dimensions': game['dimensions'],
        
        }
    direct = direction_vector[direction] #tuple describing direction movement with respect to coordinates
    prev_pov = game_ans['player'] #previous position of the player
    pos_try = (direct[0]+prev_pov[0], direct[1]+prev_pov[1]) #position you want to move the player to 
    if can_move(game, 'player', pos_try, direct): #check in the player can move
        if pos_try not in game['computers']: #check if you have to move a computer as well
            game_ans['player'] = pos_try
        else:
            #move the computer
            comp_list = game_ans['computers'].copy()
            comp_list.remove(pos_try)
            comp_list.add((direct[0]+pos_try[0], direct[1]+pos_try[1]))
            game_ans['computers']= comp_list
            game_ans['player'] = pos_try
    
    return game_ans
            
            
            
    
    


def dump_game(game):
    """
    Given a game representation (of the form returned from new_game), convert
    it back into a level description that would be a suitable input to new_game
    (a list of lists of lists of strings).

    This function is used by the GUI and the tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    height, width = game['dimensions'] 
    ans = [[[] for j in range(width)] for i in range(height)] #making 2D array of the correct height and width
    #iterating through every element in the keys in the dictionary and using the coordinate to put the string in the
    #corresponding place in the 2D array
    for ele in game['walls']:
        ans[ele[0]][ele[1]] = ['wall']
    for ele in game['computers']:
       ans[ele[0]][ele[1]] = ['computer'] 
    for ele in game['target']:
       ans[ele[0]][ele[1]].append('target')
    ans[game['player'][0]][game['player'][1]].append('player')
    
    return ans
       
        
        
        
    
def get_set_representation(game, direction = None):
    """
    Given a game representation of the form return from new game and a direction in the form of a string, 
    returns a representation that is immutable and therefore a possible 
    element in a set.
    It returns a tuple with the frozenset of computer coordinates, the tuple of the player coordinate,
    and a string of the direction
    Direction is automatically set to none for the first node in the agenda
    The purpose of this method is to make visited a set for speed purposes

    """
    computer = frozenset(game['computers'])
    player = game['player']
    direc = direction
    ans = (computer,player,direc)
    return ans

def expand_node(node):
    """
    A node is a singular element in the path of different game states. It is 
    a tuple (game,direction), game is a game state from new game and direction
    is a string 
    
    Returns a list of valid next 'steps' or nodes after the one passed in.
    A list of all of the possible branches
    
    """
    expanded_nodes = []
    possible_directions = ['up','down','left','right']
    
    for ele in possible_directions:
        pro_node_game = step_game(node[0], ele) #creates new game for every direction
        if node[0] != pro_node_game: #does not add the game if it is the same as the one passed in
            expanded_nodes.append((pro_node_game,ele)) #creates node (tuple) (game,direction)
    return expanded_nodes

def path_to_moves(path):
    """
    Given a path, which is a tuple of nodes (a node is a tuple with a game and a direction)
    Returns a list of directions (strings) for the solution of solve puzzle

    """
    solution = []
    for i in range(1,len(path)):
        solution.append(path[i][1])
    return solution
            


def solve_puzzle(game):
    """
    Given a game representation (of the form returned from new game), find a
    solution.

    Return a list of strings representing the shortest sequence of moves ("up",
    "down", "left", and "right") needed to reach the victory condition.

    If the given level cannot be solved, return None.
    """
    #creating an agenda, a list of paths, paths are a tuple of nodes, nodes are tuples with game and direction
    agenda = [((game,),)]
    visited = {get_set_representation(game)} #set of nodes visited
    
    #boundary case if the game is already won
    if victory_check(game): 
        return []
    #iterate through agenda
    while agenda:
        current_path = agenda.pop(0)
        terminal_vertex = current_path[-1] #last node of the current path
        
        children = expand_node(terminal_vertex) #expanding node
        
        for child in children: #iterate through the children
            new_path = current_path + (child,) #make the current path longer 
            visit_child = get_set_representation(*child) #makes a hashable version of a node to put in the visited set
            
            if victory_check(child[0]):
                return path_to_moves(new_path) #returns winning path
            elif visit_child not in visited:
                agenda.append(new_path) #adds new path for expansion to agenda and then adds visited 
                visited.add(visit_child) 
    return None #returns none if there is no path that works

                
                
            
        
        


if __name__ == "__main__":
    sub = [
  [[], [], ["wall"], ["wall"], ["wall"], ["wall"], [], [], []],
  [
    ["wall"],
    ["wall"],
    ["wall"],
    [],
    [],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"]
  ],
  [["wall"], [], [], [], [], [], ["computer"], [], ["wall"]],
  [["wall"], [], ["wall"], [], [], ["wall"], ["computer"], [], ["wall"]],
  [
    ["wall"],
    [],
    ["target"],
    [],
    ["target"],
    ["wall"],
    ["player"],
    [],
    ["wall"]
  ],
  [
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"],
    ["wall"]
  ]
]

    gam = new_game(sub)
    print(solve_puzzle(gam))

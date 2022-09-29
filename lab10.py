"""6.009 Lab 10: Snek Is You Video Game"""

import doctest

# NO ADDITIONAL IMPORTS!

# All words mentioned in lab. You can add words to these sets,
# but only these are guaranteed to have graphics.
NOUNS = {"SNEK", "FLAG", "ROCK", "WALL", "COMPUTER", "BUG"}
PROPERTIES = {"YOU", "WIN", "STOP", "PUSH", "DEFEAT", "PULL"}
WORDS = NOUNS | PROPERTIES | {"AND", "IS"}

# Maps a keyboard direction to a (delta_row, delta_column) vector.
direction_vector = {
    "up": (-1, 0),
    "down": (+1, 0),
    "left": (0, -1),
    "right": (0, +1),
}

def get_obj(game, position):
    """
    Given: game: internal game rep, position: coordinate in the form of tuple
    returns list of game objects at that position

    """
    height = game['dimensions'][0]
    width = game['dimensions'][1]
    if 0 <= position[0] < height and 0 <= position[1] < width:
        return game["board"][position[0]][position[1]] #RETURNS LIST
def in_bounds(dimensions,position):
    """
    Given: dimensions (a tuple) and a coordinate that is a tuple
    returns boolean whether it is in bounds

    """
    height = dimensions[0]
    width = dimensions[1]
    if 0 <= position[0] < height and 0 <= position[1] < width:
        return True
    return False


class Game_Obj:
    """
    Game representation of an object on a board
    """
    def __init__(self, noun, position):
        
        self.noun = noun #string of how it appears on the board ex. "snek"
        self.position = position #tuple position
    def __repr__(self):
        return "(Noun: " + self.noun + " Position: " + str(self.position) + ")"
    
    def add_to_board(self, game, position):
        """
        Given: game: internal game rep, position: coordinate in the form of tuple
        adds the object to the board at that position

        """
        game["board"][position[0]][position[1]].append(self)

    def remove_from_board(self, game,position):
        """
        Given: game: internal game rep, position: coordinate in the form of tuple
        removes object from that position

        """
        game["board"][position[0]][position[1]].remove(self)
       
    def get_properties(self, game):
        """
        Given: game: internal game rep
        returns set of all the properties from the rule key

        """
        return set([prop for prop,nouns in game["key"].items() if self.noun in nouns])
        
    def get_noun_map(self,game):
        """
        Given: game: internal game rep, 
        returns list of all the other objects of this noun are mapped to, from the noun_key
        ex if SNEK IS WALL on the board and self.noun is snek it returns ["wall"]

        """
        return [new_noun for new_noun,nouns in game["noun_key"].items() if self.noun in nouns]
    
    def change_noun(self,game):
        """
        Given: game: internal game rep, position: coordinate in the form of tuple
        returns None, and changes the noun to represent the noun map change property
        """
        
        noun_map = self.get_noun_map(game)
        if noun_map:
            self.noun = noun_map[0].lower()
    
    def can_move(self, game, proposed_position, direct):
        """
        Given: game: internal game rep, proposed_position: coordinate in the form of tuple, direct: direction tuple
        returns boolean describing whether the obj can move or not

        """
        if not in_bounds(game["dimensions"],proposed_position):
            return False
        prev_pos = (proposed_position[0] + direct[0]*-1, proposed_position[1]+ direct[1]*-1) #position the object is moving from
        behind_pos = (prev_pos[0] + direct[0]*-1, prev_pos[1]+ direct[1]*-1) #the objects behind the object moving
        next_pos = (direct[0]+proposed_position[0], direct[1]+proposed_position[1]) #the position you would push an object into
        next_obj = get_obj(game, proposed_position) #the objects in front of the obj moving
        
        properties = self.get_properties(game) #the current object's properties
        if properties.intersection({"YOU","PUSH"}): #if one of the properties in YOU or PUSH
            if next_obj == None:
                return True #out of bounds so you are not pushing anything
            if len(next_obj)== 0:
                return True #there is nothing in front of the object
            for ele in next_obj: 
                ele_prop = ele.get_properties(game)
                if ele_prop.intersection({"PUSH"}): 
                    if not ele.can_move(game,next_pos,direct): #check if you can push the object in front
                        return False
                elif ele_prop.intersection({"STOP"}): #check if the object in front is stop
                    return False
                       
            return True #no barriers to movement
        
        elif properties.intersection({"PULL"}): #if you want to pull an object
            if len(next_obj) >1:
                for obj in next_obj:
                    if obj.get_properties(game).intersection({"STOP"}):
                        return False
                    
                return True
            else:
                return True   
        else:
            return False
        
    def move(self,game,proposed_position,direct):
        """
        Given: game: internal game rep, proposed_position: coordinate in the form of tuple, direct: direction tuple
        returns list of moves to be changed on the board 
        a move is a tuple (object, proposed_position, previous_postion)

        """
        prev_pos = (proposed_position[0] + direct[0]*-1, proposed_position[1]+ direct[1]*-1) #where the object is moving from
        behind_pos = (prev_pos[0] + direct[0]*-1, prev_pos[1]+ direct[1]*-1) #the objects behind where the object is moving from
        next_pos = (direct[0]+proposed_position[0], direct[1]+proposed_position[1]) #the position in front of where it us that you're moving to
        next_obj = get_obj(game, proposed_position) #the objects in front of where you're moving the object to
        behind_obj = get_obj(game, behind_pos) #objects behind the position you are moving from
        curr_obj = get_obj(game,prev_pos) #objects at the position you are moving from
        properties = self.get_properties(game) #properties of the object from the key
        have_pushed = False #something has been pushed
        
        #add the first change which is the tuple moving the given object to the proposed position
        list_moves = {(self,proposed_position,prev_pos)}
     
        #pulling objects behind it
        if properties.intersection({"YOU","PULL"}):
            #ensuring an object is behind it
            if behind_obj != None: 
                if len(behind_obj) != 0:
                    for obj in behind_obj:
                        if obj.get_properties(game).intersection({"PULL"}): #if you can pull the object
                            if obj.can_move(game,prev_pos,direct): #if you can pull it
                                list_moves |= obj.move(game,prev_pos,direct) #add to the set of moves
        #pushing objects
        if properties.intersection({"YOU", "PUSH", "PULL"}):
            if next_obj != None:   
                if len(next_obj) != 0:
                    for obj in next_obj:
                        if obj.get_properties(game).intersection({"PUSH"}):
                            if obj.can_move(game,next_pos,direct):
                                list_moves |= obj.move(game,next_pos,direct)
                                have_pushed = True
        #if you have pushed an object, pull the object at the same positon as you if it is pull (boundary case)                       
        if have_pushed:
            if curr_obj != None:
                for obj in curr_obj:
                    if obj.get_properties(game).intersection({"PULL"}):
                        list_moves |= {(obj,proposed_position,prev_pos)}
        
        return list_moves
        
        
            
#HELPER FUNCTIONS FOR PARSING RULES           
def find_is(game):
    """
    Given: game: internal game rep, 
    returns set of all locations of is

    """
    height = game['dimensions'][0]
    width = game['dimensions'][1]
    is_locations = set()
    for y in range(height):  #going through the rows
        row = game["board"][y]
        for x in range(width): #going through the columns
            for ele in row[x]:
                if ele.noun == "IS":
                    is_locations.add((y,x))
    return is_locations

def surrounding_locs(dimensions, is_location):
    """
    Given: dimension and a location of is
    returns a dictionary with the keyboard direction as keys and a list of all the coords outward in that direction as the list

    """
    ans = {
        "up": [],
        "down": [],
        "left": [],
        "right": [],
    }
    for key in direction_vector:
        curr_loc = (is_location[0]+direction_vector[key][0],is_location[1]+direction_vector[key][1])
        while in_bounds(dimensions, curr_loc):
            ans[key].append(curr_loc)
            curr_loc = (curr_loc[0]+direction_vector[key][0],curr_loc[1]+direction_vector[key][1])
    return ans 


def valid_words(game, locations, props = True):
    """
    Given: game: internal game rep, a list of locations, and a boolean automaticall set to true 
    True if youre looking for subject, false for predicate
    returns list of valid words for a rule expression, basically the predicate or subject

    """
    ans = []
    nouns_at_loc = []
    and_prev = True
    
    if props:
        poss_words = PROPERTIES | {"AND"} | NOUNS
        valid = PROPERTIES | NOUNS
    else:
        poss_words = NOUNS | {"AND"}
        valid = NOUNS
        
    for ele in locations:
        nouns_at_loc.append(set([obj.noun for obj in get_obj(game, ele)]))
        
    i = 0
    
  
    while i < len(nouns_at_loc) and nouns_at_loc[i].intersection(poss_words):
        for ele in nouns_at_loc[i]:
            if ele in valid and and_prev:
                ans.append(ele)
                and_prev = False
            elif ele == "AND":
                and_prev = True
       
        i+=1
    
    return ans

def valid_words_dict(game, surround_locs):
    """
    Given: game: internal game rep, and the result of calling surrounding locs
    returns dictionary with direction mapping them to valid predicates and subject lists

    """
    ans = {
        "up": [],
        "down": [],
        "left": [],
        "right": [],
    }
    
    for key in ans:
        if key in ["up","left"]:
            ans[key] = valid_words(game, surround_locs[key], False)
        else:
            ans[key] = valid_words(game, surround_locs[key])
    return ans 
            

def get_rule_key(game):
    """
    Given: game
    returns a key (dict) for mapping properties and a noun_key (dict) for mapping properties

    """
    ans = {"YOU": set(), 
           "WIN": set(), 
           "STOP": set(), 
           "PUSH": WORDS, 
           "DEFEAT":set(), 
           "PULL":set()
        }
    noun_ans = {"SNEK": set(), 
                "FLAG": set(), 
                "ROCK": set(), 
                "WALL": set(), 
                "COMPUTER":set(),
                "BUG": set()
        }
    
    is_locations = find_is(game)
    for loc in is_locations:
        surround = surrounding_locs(game["dimensions"], loc)
        val_words = valid_words_dict(game, surround)
        up = set([word.lower() for word in val_words["up"]])
        left = set([word.lower() for word in val_words["left"]])
        
        #mapping up to down
        for ele in set(val_words["down"]).intersection(PROPERTIES):
            ans[ele] = ans[ele] | up
        for ele in set(val_words["down"]).intersection(NOUNS): 
            noun_ans[ele] = noun_ans[ele] | up
            
        #mapping left to right 
        for ele in set(val_words["right"]).intersection(PROPERTIES):
            ans[ele] = ans[ele] | left
        for ele in set(val_words["right"]).intersection(NOUNS):
            noun_ans[ele] = noun_ans[ele] | left
        
    return ans, noun_ans
            
                  
        
        

def new_game(level_description):
    """
    Given a description of a game state, create and return a game
    representation of your choice.

    The given description is a list of lists of lists of strs, where UPPERCASE
    strings represent word objects and lowercase strings represent regular
    objects (as described in the lab writeup).

    For example, a valid level_description is:

    [
        [[], ['snek'], []],
        [['SNEK'], ['IS'], ['YOU']],
    ]

    The exact choice of representation is up to you; but note that what you
    return will be used as input to the other functions.
    """
    #getting the height and width from the list of lists
    height = len(level_description)
    width = len(level_description[0])
    board = [[[] for j in range(width)] for i in range(height)]
    game_obj_list = []    
    dimensions = (height, width)
    
    
    
    #iterating through the lab representation and getting the coordinates for each board element
    #building board
    for y in range(height):  #going through the rows
        row = level_description[y]
        for x in range(width): #going through the columns
            for ele in row[x]:
                if 'wall' in ele:
                    board[y][x].append(Game_Obj("wall",(y,x)))
                if 'computer' in ele:
                    board[y][x].append(Game_Obj("computer", (y,x)))
                if 'snek' in ele:
                    board[y][x].append(Game_Obj("snek",  (y,x)))
                if 'flag' in ele:
                    board[y][x].append(Game_Obj("flag", (y,x)))
                if 'rock' in ele:
                    board[y][x].append(Game_Obj("rock", (y,x)))
                if 'bug' in ele:
                    board[y][x].append(Game_Obj("bug",  (y,x)))
                for word in WORDS:
                    if word in ele:
                        board[y][x].append(Game_Obj(word, (y,x)))
            
            game_obj_list.extend(board[y][x])   
    #game rep is here
    game = {
        "board": board, #board with Game_Obj objects at each place in the board
        "object_list": game_obj_list, #list of objects
        "key": set(),
        "dimensions": dimensions
        }
    
    rule_key, noun_key = get_rule_key(game)
    game["key"] = rule_key
    game["noun_key"] = noun_key
    
    
    return game



        
def victory_check(game):
    """
    Given a game representation (of the form returned from new_game), return
    a Boolean: True if the given game satisfies the victory condition, and
    False otherwise.
    """
    you_coords =set()
    win_coords = set()
    for ele in game["object_list"]:
        if ele.noun in game["key"]["WIN"]:   
            win_coords.add(ele.position)
        if ele.noun in game["key"]["YOU"]:
            you_coords.add(ele.position)
    if you_coords.intersection(win_coords):
        return True
    return False

def defeat(game):
    """
    Given game
    handles the defeat by removing YOU object where there are defeat ones
    """
    you_coords = set()
    defeat_coords = set()
 
    for ele in game["object_list"]:
        if ele.noun in game["key"]["DEFEAT"]:   
            defeat_coords.add(ele.position)
        if ele.noun in game["key"]["YOU"]:
            you_coords.add(ele.position)

    
    for coord in you_coords.intersection(defeat_coords):
        remove_all(game, coord, game["key"]["YOU"])
                
                
def remove_all(game, coord, noun):
    """
    helper
    Given: game, coordinate, and set of nouns that you would like to remove
    removes every object of that type from that position in the board

    """
    objs_at = get_obj(game, coord)
    for ele in objs_at:
        if ele.noun in noun:
            ele.remove_from_board(game,coord)
            game["object_list"].remove(ele)
    for ele in objs_at:
        if ele.noun in noun:
            ele.remove_from_board(game,coord)
            game["object_list"].remove(ele)
            
 

def step_game(game, direction):
    """
    Given a game representation (as returned from new_game), modify that game
    representation in-place according to one step of the game.  The user's
    input is given by direction, which is one of the following:
    {'up', 'down', 'left', 'right'}.

    step_game should return a Boolean: True if the game has been won after
    updating the state, and False otherwise.
    """
    
    direct = direction_vector[direction] 
    all_moves = set()
    for obj in game["object_list"]:
        if obj.get_properties(game).intersection({"YOU"}): #moving every you object
            pos_try = (direct[0]+obj.position[0], direct[1]+obj.position[1])
            if obj.can_move(game,pos_try,direct):
                all_moves |= obj.move(game,pos_try,direct) #adding up all the moves
                
    #executing all of the moves           
    for ele in all_moves:
        curr_obj = ele[0]
        prev_pos = ele[2]
        proposed_position = ele[1]
        curr_obj.remove_from_board(game, prev_pos)
        curr_obj.position = proposed_position 
        curr_obj.add_to_board(game, proposed_position)
    
    
    #change the rules    
    new_key, new_noun = get_rule_key(game)
    game["key"] = new_key
    game["noun_key"] = new_noun
    
    
    #adjusting object types
    for obj in game["object_list"]:
        obj.change_noun(game)
        
    defeat(game)
    
    return victory_check(game)
        


def dump_game(game):
    """
    Given a game representation (as returned from new_game), convert it back
    into a level description that would be a suitable input to new_game.

    This function is used by the GUI and tests to see what your game
    implementation has done, and it can also serve as a rudimentary way to
    print out the current state of your game for testing and debugging on your
    own.
    """
    height, width = game['dimensions'] 
    
    #objects are already in the right place, just getting the nound
    return [[[obj.noun for obj in place] for place in row] for row in game['board']]


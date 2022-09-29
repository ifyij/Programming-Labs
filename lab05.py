#!/usr/bin/env python3
"""6.009 Lab 5 -- Boolean satisfiability solving"""

import sys
import typing
import doctest
sys.setrecursionlimit(10000)
# NO ADDITIONAL IMPORTS


def update_formula(formula,literal):
    """
    Parameters
    ----------
    formula : The formula in CNF format that you wish to update list of lists
    literal : tuple (variable, bool) its the literal you are updating the formula with

    Returns
    -------
    ans : The new formula now that the varibale is chosen
    if there is no solution it returns None

    """
    ans = [] #the new formula
    inter = [] #intermediate list for building clauses
    
    #A base case check in case formula of type None is passed in 
    if formula == None: 
        return None
    
    for ele in formula:
        if literal not in ele: #only want the clauses not satisfied by the literal, so the lists without the literal
            #if there is a unit clause that is the opposite of this literal, returns None
            if len(ele)==1 and ele[0][0]==literal[0]: 
                return None
            #getting every literal in each clause that is possible if the passed in literal is true/false
            for lit in ele:
                if literal[0] != lit[0]:
                    inter.append(lit) #add the literals to the current clause
            ans.append(inter) #add the clause to the formula
            inter = [] #resetting intermediate clause generating list
    return ans



def unit_clause(formula):
    """
    Parameters
    ----------
    formula : a CNF formula passed in (list of lists)

    Returns
    -------
    bool that is True if a unit clause is in the formula and False if there isnt one

    """
    if formula == None: #boundary case because sometimes the formula is None 
        return False
    for ele in formula: #goes through all of the clauses in the formula passed in
        if len(ele) == 1: #looks for unit clause, a list of len 1
            return True
    return False
    

def satisfying_assignment(formula):
    """
    Find a satisfying assignment for a given CNF formula.
    Returns that assignment if one exists, or None otherwise.

    >>> satisfying_assignment([])
    {}
    >>> x = satisfying_assignment([[('a', True), ('b', False), ('c', True)]])
    >>> x.get('a', None) is True or x.get('b', None) is False or x.get('c', None) is True
    True
    >>> satisfying_assignment([[('a', True)], [('a', False)]])
    """
    ans = {} #initializing empty dictionary answer
    remain = []
    
    #unit clause checker
    while unit_clause(formula): #while a unit clause exists
        for ele in formula:
            if len(ele) == 1: #gets that unit clause
                formula = update_formula(formula, ele[0]) #updates formula with unit clause literal
                if formula != None:
                    ans[ele[0][0]] = ele[0][1] #adds the entry to the dictionary
                    break
                else:
                    return None #this is if it doesnt work with the unit clause 
                
    #base case
    if formula == None:
        return None
    if len(formula) == 0: #achieved the solution
        return ans        
    
    #putting all the remaining variables in a list
    for i in formula:
        for j in i:
            remain.append(j[0])
    #there are no variables left to check for so there is no solution
    if len(remain)==0:
        return None
    
    #recursive case
    
    variable = remain.pop(0) #getting a variable to check the condition for 
    new_form = update_formula(formula, (variable,True)) #new formula if this variable is True
    true_assignment = satisfying_assignment(new_form) #solution dictionary for this assignement
    
    if true_assignment != None: #it works
        ans[variable] = True #set this variable to True
        ans.update(true_assignment) #add the solution from the recursive call to the ans dictionary
    else:
        new_form = update_formula(formula,(variable,False)) #try false now
        false_assign = satisfying_assignment(new_form) #false dictionary solution to the new formula
        if false_assign != None: #it works
            ans[variable] = False
            ans.update(false_assign)
        else:
            return None #neither work so theres no solution
    return ans
        
    


def boolify_scheduling_problem(student_preferences, room_capacities):
    """
    Convert a quiz room scheduling problem into a Boolean formula.

    student_preferences: a dictionary mapping a student name (string) to a list
                         of room names (strings) that work for that student

    room_capacities: a dictionary mapping each room name to a positive integer
                     for how many students can fit in that room

    Returns: a CNF formula encoding the scheduling problem, as per the
             lab write-up

    We assume no student or room names contain underscores.
    """
    
    def student_pref(student_preferences):
        """
        Given student preferences dictionary
        returns a formula that makes sure each student gets their desired location
        ans: list of lists, formula with clauses
        

        """
        ans = []
        for ele in student_preferences.items(): #iterating through dictionary items
            inter = [] #clause building intermediate list
            student = ele[0] #gets a student name
            for place in ele[1]: #iterating through the student's preferences
                variable = '_'.join([student,place]) #creates the variable name Student_place
                inter.append((variable,True)) #add the appropriate literals to the clause for that student
            ans.append(inter) #appends that student's clause
        return ans
    
    def only_one(student_preferences, room_capacities):
        """
        Given student preferences dictionary and room capacities dictionary
        returns a list of lists CNF formula that ensures that each student is assigned to at most one room

        """
        rooms = list(room_capacities.keys()) #list if rooms
        students = list(student_preferences.keys()) #list of students
        room_pairs = set() #intializing a set that will have the pairs of students
        for i in rooms:
            for j in rooms:
                if j != i: #making sure pairs are different
                    pair = frozenset((i,j)) #pair is a tuple in a frozen set (i think it turns it into a set)
                    room_pairs.add(pair) #adds the pairs that are frozen sets to the the set
        ans = [] #initializing answer list 
        for student in students: 
            for ele in room_pairs:
                inter = [] #intermediate list for clause buiding
                for place in ele:
                    variable = '_'.join([student,place])
                    inter.append((variable,False)) #makes it false, adds appropriate literal to clause
                ans.append(inter) #adds clauses to formula
        return ans #returns that appropiate formula
    
    #helper function for no_oversubscribed
    def make_groups(group_set,size):
        """
        Given a list or set of elements, an an integer size
        returns a set of unique groups of that size (set of frozensets)

        """
        ans = set() #initializing the answer
        #base case
        if size == 1: 
            for ele in group_set:
                #then is an unfinished group or the groups building block, ele is first element in that group
                then = frozenset({ele}) 
                ans.add(then) #adding those groups to a set and returning it
            return ans
        #recursive case
        else:
            for ele in make_groups(group_set, size-1):
                for pla in group_set: #getting elements in the passed in iterable to add to the group
                    if pla not in ele: #no repeats
                        then = ele | frozenset({pla}) #adding to the the element to the already existing group
                        ans.add(then) #adding the group to the set answer and returning it
        return ans
                
    def no_oversubscribed(student_preferences,room_capacities):
        """
        Given student preferences dictionary and room capacities dictionary
        Returns a CNF formula ensuring that each room is not over subscribed past its limit

        """
        rooms = list(room_capacities.keys())
        students = list(student_preferences.keys())
        ans = []
        
        for room in rooms: #iterating through the rooms
            if room_capacities[room] < len(students): #only looking at the rooms where oversubcription is possible
                student_groups = make_groups(students,room_capacities[room]+1) #making groups of the appropiate size N+1 with no repeats
                for ele in student_groups: #iterating through those groups, each group is a clause
                    inter = [] #clause building list
                    for person in ele: #each person in a group and the room is a variable
                        variable = '_'.join([person,room])
                        inter.append((variable,False))
                    ans.append(inter)
        return ans
    
    #adding them all together to get the total formula
    return student_pref(student_preferences) + only_one(student_preferences, room_capacities) + no_oversubscribed(student_preferences, room_capacities)
    
            


if __name__ == '__main__':
    import doctest
    _doctest_flags = doctest.NORMALIZE_WHITESPACE | doctest.ELLIPSIS
    doctest.testmod(optionflags=_doctest_flags)

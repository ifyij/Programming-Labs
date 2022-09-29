"""6.009 Lab 9: Carlae Interpreter Part 2"""

import sys
sys.setrecursionlimit(10_000)

#!/usr/bin/env python3
"""6.009 Lab 8: Carlae (LISP) Interpreter"""

import doctest

# NO ADDITIONAL IMPORTS!


###########################
# Carlae-related Exceptions #
###########################


class CarlaeError(Exception):
    """
    A type of exception to be raised if there is an error with a Carlae
    program.  Should never be raised directly; rather, subclasses should be
    raised.
    """

    pass


class CarlaeSyntaxError(CarlaeError):
    """
    Exception to be raised when trying to evaluate a malformed expression.
    """

    pass


class CarlaeNameError(CarlaeError):
    """
    Exception to be raised when looking up a name that has not been defined.
    """

    pass


class CarlaeEvaluationError(CarlaeError):
    """
    Exception to be raised if there is an error during evaluation other than a
    CarlaeNameError.
    """

    pass


############################
# Tokenization and Parsing #
############################


def number_or_symbol(x):
    """
    Helper function: given a string, convert it to an integer or a float if
    possible; otherwise, return the string itself

    >>> number_or_symbol('8')
    8
    >>> number_or_symbol('-5.32')
    -5.32
    >>> number_or_symbol('1.2.3.4')
    '1.2.3.4'
    >>> number_or_symbol('x')
    'x'
    """
    try:
        return int(x)
    except ValueError:
        try:
            return float(x)
        except ValueError:
            return x


def tokenize(source):
    """
    Splits an input string into meaningful tokens (left parens, right parens,
    other whitespace-separated values).  Returns a list of strings.

    Arguments:
        source (str): a string containing the source code of a Carlae
                      expression
    """
    #removing comments from source
    source_copy = source #a copy of the source to replace the comments
    curr_comment = "" #variable for building comment
    j = 0
    get_comment = False 
    while j < len(source):
        if source[j] == '#': #beginning of a comment
            get_comment = True 
        while get_comment and j < len(source): #building comment while loop 
            curr_comment += source[j]
            if source[j] == '\n': #comment ends as a new line
                get_comment = False
            j+=1
        source_copy = source_copy.replace(curr_comment, '') #removing comment from the source

        curr_comment = "" #resetting the comment
        j+=1 #getting the next index
                   
        
    #adding spaces after every parentheses and line
    exp_list = []
    for i in range(len(source_copy)):
        exp_list.append(source_copy[i])
        if source_copy[i] in ['\n','(',')']:
            exp_list.append(' ')
    yit = []
    for ele in exp_list:
        if ele == ')' or ele == '\n':
            yit.append(' ')
            yit.append(ele)
        else:
            yit.append(ele)
            
  
    exp = ''.join(yit) #creating string from list with spaces
    ans = list(exp.split(' ')) #splitting the string into a list at all the spaces
    
    #removing unimportant tokens in the list
    hep = []
    for ele in ans:
        if ele != '' and ele !='\n': 
            hep.append(ele)
    return hep


def parse(tokens):
    """
    Parses a list of tokens, constructing a representation where:
        * symbols are represented as Python strings
        * numbers are represented as Python ints or floats
        * S-expressions are represented as Python lists

    Arguments:
        tokens (list): a list of strings representing tokens
        
    """
  
    def parse_expression(index):
        ans = [] 
        if index < len(tokens): #checking to see if the index is in bounds
            token = tokens[index]  #getting specific tokaen
            curr_tok = token 
            curr_ind = index +1
            token = number_or_symbol(token)
            if token == '(': 
                while curr_ind < len(tokens) and tokens[curr_ind] != ')' : #to make sure the next index is not a closed parentheses
                    curr_tok, curr_ind = parse_expression(curr_ind) 
                    ans.append(curr_tok)
                       
                #after calling parse expression on every token in the parentheses the next index should be a parentheses
                if curr_ind < len(tokens):  
                    if tokens[curr_ind]==')': 
                       return ans, curr_ind +1
                    else:
                       raise CarlaeSyntaxError #otherwise it is a syntax error because theres no closed parentheses
                 
                else:
                    raise CarlaeSyntaxError

            elif token == ')':
                raise CarlaeSyntaxError() #too many closed parentheses
            else:
                return token, index +1
            
           
    parsed_expression, next_index = parse_expression(0)

   
    if next_index != len(tokens):
        raise CarlaeSyntaxError
    return parsed_expression


######################
# Built-in Functions #
######################

#mul function
def mul(nums):
    prod = 1
    for ele in nums:
        prod *= ele
    return prod


def div(nums):
    return nums[0] / mul(nums[1:])

#boolean functions
def eq_ques(nums):
    # =?
    for i in range(1,len(nums)):
        if nums[i-1] != nums[i]:
            return False
    return True
def greater(nums):
    # >
    for i in range(1,len(nums)):
        if nums[i-1] <= nums[i]:
            return False
    return True
def less(nums):
    # <
    for i in range(1,len(nums)):
        if nums[i-1] >= nums[i]:
            return False
    return True

def greater_eq(nums):
    # >=
    for i in range(1,len(nums)):
        if nums[i-1] < nums[i]:
            return False
    return True
def less_eq(nums):
    # <=
    for i in range(1,len(nums)):
        if nums[i-1] > nums[i]:
            return False
    return True

def not_fun(exp):
    #not
    if len(exp) > 1:
        raise CarlaeEvaluationError
    if len(exp) == 0:
        raise CarlaeEvaluationError
    return not exp[0]

#pair functions
def head(pair):
    """
    Takes in a pair and returns its head

    """
    if len(pair) == 0:
        raise CarlaeEvaluationError()
    if len(pair) > 1:
        raise CarlaeEvaluationError
    if isinstance(pair[0],Pair):
        return pair[0].get_head()
    else:
        raise CarlaeEvaluationError
def tail(pair):
    """
    Takes in a pair and returns its tail

    """
    if len(pair) == 0:
        raise CarlaeEvaluationError()
    if len(pair) > 1:
        raise CarlaeEvaluationError
    if isinstance(pair[0],Pair):
        return pair[0].get_tail()
    else:
        raise CarlaeEvaluationError

#lab functions
def make_list(elements):
    """
    Takes in a list of values and returns a linked list with those values
    """
    if len(elements) == 0:
        return set() #returning nil
    if len(elements) == 1:
        return Pair(elements[0],set()) # (pair ele nil)
    else:
        return Pair(elements[0], make_list(elements[1:]))
    
def is_list(argument):
    """
    Passes in an argument and checks if it is a linked list
    """
    if isinstance(argument,list):
        if len(argument) != 1: #function called with too many params
            raise CarlaeEvaluationError
        arg = argument[0]
    else:
        arg = argument
    if arg == set(): #set() is nil
        return True #nil is an empty list
    if isinstance(arg,Pair):
        if arg.get_tail() == set():
            return True #ends correctly
        elif isinstance(arg.get_tail(),Pair):
            return is_list(arg.get_tail()) #recursive call
        else:
            return False
    else:
        return False

def length(argument):
    """
    Passes in a linked list and returns the length of the list
    """
    if isinstance(argument,list):
        if len(argument) != 1:
            raise CarlaeEvaluationError #func called with too many arguments
        arg = argument[0]
    else:
        arg = argument
        
    if not is_list(arg):
        raise CarlaeEvaluationError #callled on something other than a list
    ans = 0
    if arg == set():
        return 0 #empty list
    if isinstance(arg,Pair):
        if arg.get_tail() == set():
            return 1 #list of lenght one
        else:
            #recursive piece
            ans = 1 +  length(arg.get_tail())
            return ans
def nth(argument):
    """
    Takes in a list and a nonnegative index,
    returns the element at the given index in the given list.
    """
    
    if len(argument) != 2: #wrong number of arguments 
        raise CarlaeEvaluationError
    if isinstance(argument[0],list): 
        if len(argument[0]) != 1: #wrong number of arguments
           
            raise CarlaeEvaluationError
        arg = argument[0][0]
        index = argument[1]
    else:
        arg = argument[0]
        index = argument[1]
    
    if not is_list(arg):
        if isinstance(arg, Pair) and index == 0:
            return arg.get_head()
        else:
            raise CarlaeEvaluationError #a list or a pair was not called 
    else:
        if index == 0:
            if arg == set():
                
                raise CarlaeEvaluationError
            else:
                return arg.get_head()
        else:
            if arg.get_tail() == set(): 
                raise CarlaeEvaluationError #out of bounds error
            else:
                return nth([arg.get_tail(), index -1]) #recursive case
            
def copy(pair_list):
    """
    Takes in a list and returns a copy of that list, a helper function for concat
    """
    if pair_list == set():
        return set()
    if pair_list.get_tail() == set():
        return Pair(pair_list.get_head(),set()) #base case
    else:
        return Pair(pair_list.get_head(), copy(pair_list.get_tail())) #recursive case
            
def final_pair(pair_list):
    """
    Takes in a list and returns the Pair object associated with the last element of the list, helper for concat
    """
    if pair_list == set():
        return set() #nil boundary case
    else:
        if pair_list.get_tail() == set(): #final pair found, base case
            return pair_list
        else:
            return final_pair(pair_list.get_tail()) #recursive case

def concat(lists):
    """
    Takes in an arbitrary number of lists as arguments, 
    returns a new list representing the concatenation of these lists
    """
    new_param = []
    if len(lists) == 0:
        return set()
    if len(lists) == 1:
        if is_list(lists[0]):
            return copy(lists[0]) #base case when all lists are combined return a copy of them
        else:
            raise CarlaeEvaluationError #parameter is not a list
    else:
        #recursive case, combining first two lists and calling the function again
        if is_list(lists[0]) and is_list(lists[1]): 
            first = copy(lists[0])
            second = copy(lists[1]) #take this out if recursive limit is reached
            last_pair = final_pair(first) #last pair in the first list
            if last_pair == set():
                first = second #the first list is nil so the combination is just the second one
            else:
                last_pair.set_tail(second) #combining first two
            new_param.append(first) #add them to new list
            if len(lists) > 2:
                new_param.extend(lists[2:]) #add the rest of the lists
            return concat(new_param) 
        else:
            raise CarlaeEvaluationError #parameters are not lists 

def map_fun(arguments):
    """
    Takes a function and a list as arguments,
    returns a new list containing the results of applying the given function to each element of the given list.
    """  
    if len(arguments) != 2: #too many params
        raise CarlaeEvaluationError
    function = arguments[0]
    list1 = arguments[1]
    #similar to copy but calling function on the head
    if callable(function) and is_list(list1):
        if list1 == set():
            return set()
        elif list1.get_tail() == set():
            return Pair(function([list1.get_head()]), set()) 
        else:
            
            return Pair(function([list1.get_head()]), map_fun([function,copy(list1.get_tail())]))
    else:
        raise CarlaeEvaluationError


def filt(arguments):
    """
    Takes a function and a list as arguments,
    returns a new list containing only the elements of the given list for which the given function returns true.

    """
    new_lis = []
    key = map_fun(arguments) #linked list of True and False to see which arguments stay
    list1 = arguments[1] 
    lent = length(list1) #length of both they key and list
    for i in range(lent):
        if nth([key,i]): #if key index is True append the corresponding item in the list
            new_lis.append(nth([list1,i]))
    return make_list(new_lis) 

def reduce(arguments):
    """
    Takes a function, a list, and an initial value as inputs
    Returns the result of successively applying the given function to the elements in the list

    """
    if len(arguments) != 3: #wrong # of args
        raise CarlaeEvaluationError
    function = arguments[0]
    list1 = arguments[1]
    initial = arguments[2]
    if callable(function) and is_list(list1):
        if list1 == set(): #empty list set equal to new
            return initial #return original number
        elif list1.get_tail() == set():
            initial = function([initial, list1.get_head()]) #last element in the list evaluate initial final time
            return initial
            
        else:
            initial = function([initial, list1.get_head()]) #keep changing accumulating initial
            return reduce([function, list1.get_tail(),initial])
    
    else:
        raise CarlaeEvaluationError
def begin(arguments):
    """
    Returns the last element of the argument passed in

    """
    return arguments[-1]
    
carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mul, #adding the functions into builtins
    "/": div,
    "@t": True,
    "@f": False,
    "=?": eq_ques,
    '>': greater,
    ">=": greater_eq,
    "<": less,
    "<=": less_eq,
    "not": not_fun,
    "head": head,
    "tail": tail,
    "nil": set(), #nil is an empty set
    "list": make_list,
    "list?": is_list,
    "length": length,
    "nth": nth,
    "concat": concat, 
    "map": map_fun,
    "filter": filt,
    "reduce": reduce,
    "begin": begin,
    
    
}


##############
# Evaluation #
##############
class Environment:
    
    def __init__(self, parent = None):
        self.variables = {} #variables are a dictionary 
        if isinstance(parent, Environment): #whether the environment has a parent environment or not
            self.parent = parent
            self.hasparent = True
        else:
            self.hasparent = False
    
    def add_variables(self, var_dict):
        self.variables.update(var_dict) #add variables to a dictionary
    def add_var(self, var_name, value):
        self.variables[var_name] = value #add a single variable to a dictionary
       
    def del_var(self, var_name):
        #deleting a variable from the environment
        if var_name in self.variables:
            ans= self.variables[var_name]
            del self.variables[var_name]
            return ans
        else:
            raise CarlaeNameError #can't access parent
    def get_val(self, var_name):
        if var_name in self.variables:
            return self.variables[var_name]
        elif var_name not in self.variables and self.hasparent:
            return self.parent.get_val(var_name) #look up to see if the variable is in the dictionary
        else:
            raise CarlaeNameError #can't access parent
        
    def set_val(self, var_name, val):
        #setting variable in the environment
        if var_name in self.variables:
            self.variables[var_name] = val
        elif var_name not in self.variables and self.hasparent:
            self.parent.set_val(var_name,val) #look up to see if the variable is in the dictionary
        else:
            raise CarlaeNameError #can't access parent
        
        
class Function:
    
    def __init__(self, param, body, env):
        self.parameters = param # a list of parameters
        self.body = body # body of a function is a list of tokens
        self.env = env #enclosing environment
        
    def __call__(self,params): #overriding call function to make it callable
        if len(params) != len(self.parameters):
            raise CarlaeEvaluationError #not the correct number of parameters
            
        # map parameters to the parameter names instance variable
        new_dic = {self.parameters[x]: params[x] for x in range(len(params))}
        fun_env = Environment(self.env) #create a new environment for the function call with the enclosing env of the function as the parent
        fun_env.add_variables(new_dic) #add the bounded parameters to the environment
        return evaluate(self.body,fun_env) #evaluate the body
            
class And():
    #for And special form 
    def __init__(self, env):
        self.env = env #enclosing environment
    
    def __call__(self, expressions):
        for ele in expressions:
            if evaluate(ele,self.env) == False:
                return False
        return True
class Or():
    #for Or special form
    def __init__(self, env):
        self.env = env #enclosing environment
        
    def __call__(self,expressions):
        for ele in expressions:
            if evaluate(ele,self.env) == True:
                return True
        return False

class Pair():
    
    def __init__(self, head, tail):
        self.head = head
        self.tail = tail
    
    def get_head(self):
        return self.head
    def get_tail(self):
        return self.tail
    def set_tail(self, new_list):
        self.tail = new_list
    
    def __repr__(self):
        return 'Pair(' + repr(self.head) + ',' + repr(self.tail) + ')'

            
        

glob_env = Environment() #make a global environment
glob_env.add_variables(carlae_builtins) #add the built-ins to the variables bound in that environment

def evaluate(tree, env = None ):
    """
    Evaluate the given syntax tree according to the rules of the Carlae
    language.

    Arguments:
        tree (type varies): a fully parsed expression, as the output from the
                            parse function
    """
    
    if env == None:
        env = Environment(glob_env) #the environment when there is none passed in is one with the global environment as a parent
    arguments = [] #the arguments if a function object is being instantiated 
    if isinstance(tree, list): #evaluating an S expression
        if tree == []:
            raise CarlaeEvaluationError
        if tree[0] == ':=': #assigning a variable
            if isinstance(tree[1],list): #if assignment is followed with an S expression then a function is being instantiated
                fun_creat = ['function', tree[1][1:],tree[2]] #create a function S expression for evaluation
                ans = evaluate(fun_creat,env) 
                env.add_var(tree[1][0], ans) #bind the new function object to the current environment with the given function name
                return ans #return func object
            else:
                #assignment is not followed by S expression so evaluate the next item and bind it to the environment
                ans = evaluate(tree[2],env)
                env.add_var(tree[1], ans)
                return ans
        if tree[0] == 'function':
            new_func = Function(tree[1],tree[2],env) #create a function object with the enclosing env as the parent
            return new_func
        if tree[0] == 'if':
            if evaluate(tree[1],env):
                return evaluate(tree[2],env)
            else:
                return evaluate(tree[3],env)
        #Special forms 
        if tree[0] == 'and':
            and_op = And(env)
            express = tree[1:]
            return and_op(express)
        if tree[0] == 'or':
            or_op = Or(env)
            express = tree[1:]
            return or_op(express)
        if tree[0] == 'pair':
            if len(tree) != 3:
                raise CarlaeEvaluationError
            return Pair(evaluate(tree[1],env),evaluate(tree[2],env))
        if tree[0] == 'del':
            if len(tree) !=2:
                raise CarlaeEvaluationError()
            return env.del_var(tree[1]) #deleting using the Environment class method
        if tree[0] == 'let':
            if len(tree) != 3:
                raise CarlaeEvaluationError()
            newer_env = Environment(env)
            for ele in tree[1]:
                ans = evaluate(ele[1],env)
                newer_env.add_var(ele[0], ans)
            return evaluate(tree[2],newer_env)
        if tree[0] == 'set!':
            if len(tree) != 3:
                raise CarlaeEvaluationError()
            val = evaluate(tree[2], env)
            env.set_val(tree[1], val) #setting using the Envirnoment class method
            return val
                
            
        
        if not isinstance(tree[0], str) and not isinstance(tree[0],list):
            raise CarlaeEvaluationError #the first element in the S expression is a number
        if isinstance(tree[0],list): #the first element in the S expression is another S expression that should evaluate to a function
            function = evaluate(tree[0],env) #build function object
            if not callable(function): #first element does not evaluate to a function
                raise CarlaeEvaluationError()
        else: #first element in the S expression is a string, name of a function object
            try:  
                function = env.get_val(tree[0]) #getting the function object
                if not callable(function): #the object is a var and not callable
                    raise CarlaeEvaluationError
            except: #it is not in the environment 
                    raise CarlaeNameError
        
        #evaluate function at the first index of the S expression for the following parameters
        for i in range(1,len(tree)):
            arguments.append(evaluate(tree[i],env)) #adding parameters to list by evaluating them first
        return function(arguments) #calling function on list of parameters
        
    elif isinstance(tree,str): # evaluating a variable
        ans = env.get_val(tree) #looking it up in the environment
        return ans
    else:
        return tree #it is a number and evaluates to itself
    
def result_and_env(tree, env = None):
    if env == None:
        env = Environment(glob_env) #creating env if none is passed in
    return (evaluate(tree,env),env) #returning the evalated tree and the enclosing environment
    
def evaluate_file(filename, env = None):
    #for getting expression from a file
    if env == None:
        env = Environment(glob_env)
    file = open(filename)
    expression = file.read()
    tree = parse(tokenize(expression))
    return evaluate(tree,env)
def REPL(env1=None):
    if env1 == None:
        env1 = Environment(glob_env)
    x = input('in>')
    while x != 'EXIT':
        try:
            print('\n out>', result_and_env(parse(tokenize(x)),env1)[0]) #printing the output of evaluate 
        except Exception as e:
            print(e.__class__.__name__) #printing exception
            
        x = input('\n in>')


if __name__ == "__main__":
    # code in this block will only be executed if lab.py is the main file being
    # run (not when this module is imported)

    # uncommenting the following line will run doctests from above
    # doctest.testmod()
    
   #print(length(evaluate(parse(tokenize('(list 1 2 3 4)')))))
   
   # crap = evaluate(parse(tokenize('(list 1 3 5 9 10 3)')))
   # trin = evaluate(parse(tokenize('(list 7 7 7 7 7)')))
   # yent = evaluate(parse(tokenize('(list 929 9 0 9 )')))
   # print(concat([crap,trin,yent]))
   
   #print(len(parse(tokenize('(let ((x 5) (y 3)) (+ x y z))'))))
   
   # env = Environment(glob_env)
   # for i in range(1, len(sys.argv)):
   #     evaluate_file(sys.argv[i])
   
   REPL()
    
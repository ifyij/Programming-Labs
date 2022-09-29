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

carlae_builtins = {
    "+": sum,
    "-": lambda args: -args[0] if len(args) == 1 else (args[0] - sum(args[1:])),
    "*": mul, #adding the functions into builtins
    "/": div
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
       
    def get_val(self, var_name):
        if var_name in self.variables:
            return self.variables[var_name]
        elif var_name not in self.variables and self.hasparent:
            return self.parent.get_val(var_name) #look up to see if the variable is in the dictionary
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
    
    
def REPL():
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
    
   
    
    REPL()
    
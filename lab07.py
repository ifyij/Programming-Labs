import doctest

# NO ADDITIONAL IMPORTS ALLOWED!
# You are welcome to modify the classes below, as well as to implement new
# classes and helper functions as necessary.


class Symbol:
    operator = 'none' #a class variable for inheritance purposes
    
    #overiding all of the operations in the super class so it applies to all symbolic expressions
    def __add__(self, other):
        return Add(self, other)
    def __radd__(self, other):
        return Add(other, self) #radd requires switching the parameters in the constructor of the binops
    def __sub__(self,other):
        return Sub(self,other)
    def __rsub__(self,other):
        return Sub(other,self)
    def __mul__(self, other):
        return Mul(self, other)
    def __rmul__(self, other):
        return Mul(other, self)
    def __truediv__(self, other):
        return Div(self, other)
    def __rtruediv__(self, other):
        return Div(other, self)
    def __pow__(self, power):
        return Pow(self, power)
    def __rpow__(self, other):
        return Pow(other, self)





class Var(Symbol):
    precedence = 10 #the precedence must be higher than all the binops to avoid unnecessary parenthesization of variables
    
    
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `name`, containing the
        value passed in to the initializer.
        """
        self.name = n

    def __str__(self):
        return self.name

    def __repr__(self):
        return "Var(" + repr(self.name) + ")"
    
    def deriv(self,respect):
        #respect is the variable you're taking the derivative with respect to
        if respect == self.name:
            return Num(1)
        else:
            return Num(0) #partial derivative with respect to another variable is 0
    def simplify(self):
        return self
    
    def eval(self,mapping):
        if self.name in mapping:
            return mapping[self.name]
        else:
            return self
    
    

class Num(Symbol):
    precedence = 10 #to avoid parentheses
    
    def __init__(self, n):
        """
        Initializer.  Store an instance variable called `n`, containing the
        value passed in to the initializer.
        """
        self.n = n

    def __str__(self):
        return str(self.n)

    def __repr__(self):
        return "Num(" + repr(self.n) + ")"
    def deriv(self,respect):
        return Num(0) 
    def simplify(self):
        return self
    def eval(self,mapping):
        return self.n
    


class BinOp(Symbol):
    def __init__(self, left, right):
        
        def num_or_var(val):
            #returns the appropriate symbolic expression depending what's passed in
            if isinstance(val, str):
                return Var(val)
            elif isinstance(val, (int,float)):
                return Num(val)
            else:
                return val
        self.left = num_or_var(left)
        self.right = num_or_var(right)

    def __str__(self):
        if self.special_case:
            #for Div and Sub wrapping the right side same or lower precedence in parentheses
            if self.right.precedence <= self.precedence:
                right_side = '(' + self.right.__str__() + ')'
            else:
                right_side =  self.right.__str__()
        else:
            if self.right.precedence < self.precedence: #otherwise wrap it if it is of lower precedence
                right_side =  '(' + self.right.__str__() + ')'
            else:
                right_side =  self.right.__str__()
        
        if self.special_case2:
            #for Pow wrapping the left side of same or lower precedence in parentheses
            if self.left.precedence <= self.precedence:
                left_side = '(' + self.left.__str__() + ')'
            else:
                left_side =  self.left.__str__()
        else:
            if self.left.precedence < self.precedence:
                left_side = '(' + self.left.__str__() + ')'
            else:
                left_side =  self.left.__str__()
        
        return left_side + ' '+ self.operator + ' ' + right_side
            
    
class Add(BinOp):
    operator = '+'
    precedence = 1 #addition has lowest precedence
    special_case = False #not Div or Sub
    special_case2 = False #not Pow
    def __repr__(self):
        return 'Add(' + repr(self.left) + ',' + repr(self.right) + ')'
    def deriv(self,respect):
        return self.left.deriv(respect) + self.right.deriv(respect)
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if isinstance(self.left, Num) and isinstance(self.right,Num):
            return Num(self.left.n +self.right.n) #if both are numbers
        #adding 0 simplification  
        elif isinstance(self.left,Num) and self.left.n == 0:
            return self.right 
        elif isinstance(self.right,Num) and self.right.n == 0:
            return self.left
        else:
            return self.left + self.right
    
    def eval(self,mapping):
        return self.left.eval(mapping) + self.right.eval(mapping)
            
        

class Sub(BinOp):
    operator = '-' 
    precedence = 1 #lowest precedence
    special_case = True #special case for parentheses wrapping (Div and Sub)
    special_case2 = False #not Pow
    
    def __repr__(self):
        return 'Sub(' + repr(self.left) + ',' + repr(self.right) + ')'
    def deriv(self,respect):
        return self.left.deriv(respect) - self.right.deriv(respect)
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if isinstance(self.left, Num) and isinstance(self.right,Num):
            return Num(self.left.n - self.right.n)
        elif isinstance(self.right,Num) and self.right.n == 0: #subtracting 0 simplification
            return self.left
        else:
            return self.left - self.right
    
    def eval(self,mapping):
        return self.left.eval(mapping) - self.right.eval(mapping)

class Mul(BinOp):
    operator = '*'
    precedence = 2 #higher precedence than subtraction and addition
    special_case = False
    special_case2 = False

    def __repr__(self):
        return 'Mul(' + repr(self.left) + ',' + repr(self.right) + ')'

    def deriv(self,respect):
        return self.left*self.right.deriv(respect) + self.right*self.left.deriv(respect)
    
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        
        if isinstance(self.left, Num) and isinstance(self.right,Num):
            return Num(self.left.n * self.right.n)
        #multiplying by 0
        elif isinstance(self.left,Num) and self.left.n == 0:
            return Num(0)
        elif isinstance(self.right,Num) and self.right.n == 0:
            return Num(0)
        #multiplying by 1
        elif isinstance(self.left,Num) and self.left.n == 1:
            return self.right
        elif isinstance(self.right,Num) and self.right.n == 1:
            return self.left
        else:
            return self.left * self.right
    
    def eval(self,mapping):
        return self.left.eval(mapping) * self.right.eval(mapping)
        
class Div(BinOp):
    operator = '/'
    precedence = 2 #same precedence as Mul
    special_case = True #wrapping in parentheses special case
    special_case2 = False
    def __repr__(self):
        return 'Div(' + repr(self.left) + ',' + repr(self.right) + ')'

    def deriv(self,respect):
        return (self.right*self.left.deriv(respect) - self.left*self.right.deriv(respect))/(self.right*self.right)
    
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if isinstance(self.left, Num) and isinstance(self.right,Num):
            return Num(self.left.n / self.right.n)
        #dividing by 1
        elif isinstance(self.right,Num) and self.right.n == 1:
            return self.left.simplify()
        #dividing 0 by something
        elif isinstance(self.left,Num) and self.left.n == 0:
            return Num(0)
        else:
            return self.left / self.right
    def eval(self,mapping):
         return self.left.eval(mapping) / self.right.eval(mapping)
     
class Pow(BinOp):
    
    operator = '**'
    precedence = 3 #higher precedence than Mul and Div
    special_case = False
    special_case2 = True #wrapping in parentheses for Pow
    def __repr__(self):
        return 'Pow(' + repr(self.left) + ',' + repr(self.right) + ')'
    def deriv(self,respect):
        if not isinstance(self.right,Num):
            raise TypeError #derivative calculator does not handle this case
        else:
            return self.right*(self.left**(self.right-1))*self.left.deriv(respect)
    def simplify(self):
        self.left = self.left.simplify()
        self.right = self.right.simplify()
        if isinstance(self.left, Num) and isinstance(self.right,Num):
            return Num(self.left.n ** self.right.n)
        #raising to power of 1
        elif isinstance(self.right,Num) and self.right.n == 1:
            return self.left.simplify()
        #raising ti power of 0
        elif isinstance(self.right,Num) and self.right.n == 0:
            return Num(1)
        #base is 0
        elif isinstance(self.left,Num) and self.left.n == 0:
            if isinstance(self.right,Num) and self.right.n > 0:
                return Num(0)
            elif not isinstance(self.right,Num):
                return Num(0)
        else:
            return self.left ** self.right
    def eval(self,mapping):
         return self.left.eval(mapping) ** self.right.eval(mapping)
    
     
def tokenize(expression):
    """
    take a string as described above as input and should output a list of meaningful tokens 
    (parentheses, variable names, numbers, or operands).

    """
    #adding spaces after parentheses
    exp_list = [] 
    for i in range(len(expression)):
        exp_list.append(expression[i])
        if expression[i] in ['(',')']:
            exp_list.append(' ')
    #ensuring that there is a space after every parentheses, this means theres a space between each token
    exp_list2 = []
    for ele in exp_list:
        if ele == ')':
            exp_list2.append(' ')
            exp_list2.append(ele)
        else:
            exp_list2.append(ele)
            
      
    exp = ''.join(exp_list2) #creating a string out of the list with the spaces after parentheses
    ans_list = list(exp.split(' ')) #creating list out of all the tokens using the spaces in the tokens 
    ans = []
    #removing the empty strings in the list
    for ele in ans_list:
        if ele != '':
            ans.append(ele)
    return ans

                

def parse(tokens):
    
    def parse_expression(index):
        binops = {'+':Add, '-':Sub, '*':Mul, '**':Pow, '/':Div} #dictionary for the different binops
        if index < len(tokens):
            token = tokens[index] 
      
            if token.isnumeric() or len(token)>1: 
                return Num(int(token)), index + 1 #parsing numbers
            elif token.isalpha():
                return Var(token), index +1 #parsing variable
            elif token == '(':
                #parsing right and left expression
                exp1, nindex = parse_expression(index+1) 
                operator = tokens[nindex] #getting the operation between the expressions
                exp2, n2index = parse_expression(nindex+1)
                return binops[operator](exp1,exp2), n2index +1 #appropiate output
                
   
           
    parsed_expression, next_index = parse_expression(0)
    return parsed_expression

def expression(exp):
    tokens = tokenize(exp)
    return parse(tokens)
        
        
if __name__ == "__main__":
    doctest.testmod()
    #z = Add(Var('x'), Sub(Var('y'), Mul(Var('z'), Num(2))))
    #print(z.eval({ 'y': 10, 'z':3}))
    
    # print(expression("x"))
    # print(expression("(((x * 2) + 4) / w)"))
    # print(tokenize("(x * (-200 + 300))"))
    fxy1 = expression('((5 * x) * (y ** 2))')
    fxy2 =  expression('((3 * x) + (2 * y))')
    z = fxy1 +fxy2
    print(z)
    print(z.deriv('y').simplify())
    print(z.deriv('x').simplify())
    print(z.eval({'x':3, 'y':2}))
    
    
   
    
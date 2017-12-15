import collections
import re

INTEGER, PLUS, MINUS, MUL, LPAREN, RPAREN, EOF, ID ,ASSIGN,END= (
                                                  'INTEGER', 'PLUS', 'MINUS', 'MUL', '(', ')', 'EOF','ID','ASSIGN','END'
                                                  )

Token_Tuple = collections.namedtuple('Token', ['typ', 'value', 'line', 'column'])
symbol = {}
def tokenize(s):
    keywords = {'IF', 'THEN', 'ENDIF', 'FOR', 'NEXT', 'GOSUB', 'RETURN'}
    token_specification = [
        ('INTEGER',  r'\d+(\.\d*)?'), # Integer or decimal number
        ('ASSIGN',  r'='),          # Assignment operator
        ('END',     r';'),           # Statement terminator
        ('ID',      r'[A-Za-z]+'),   # Identifiers
        ('OP',      r'[+*\/\-]'),    # Arithmetic operators
        ('NEWLINE', r'\n'),          # Line endings
        ('SKIP',    r'[ \t]'),       # Skip over spaces and tabs
    ]
    tok_regex = '|'.join('(?P<%s>%s)' % pair for pair in token_specification)
    get_token = re.compile(tok_regex).match
    line = 1
    pos = line_start = 0
    mo = get_token(s)
    while mo is not None:
        typ = mo.lastgroup
        if typ == 'NEWLINE':
            line_start = pos
            line += 1
        elif typ != 'SKIP':
            val = mo.group(typ)
            if typ == 'ID' and val in keywords:
                typ = val
            yield Token_Tuple(typ, val, line, mo.start()-line_start)
        pos = mo.end()
        mo = get_token(s, pos)
    if pos != len(s):
        raise RuntimeError('Unexpected character %r on line %d' %(s[pos], line))

statements = '''
    IF quantity THEN
        total := total + price * quantity;
        tax := price * 0.05;
    ENDIF;
'''
statements = '''
    x = 3;
    '''
class Token(object):
    def __init__(self, type, value):
        self.type = type
        self.value = value
    
    def __str__(self):
        """String representation of the class instance.
            
            Examples:
            Token(INTEGER, 3)
            Token(PLUS, '+')
            Token(MUL, '*')
            """
        return 'Token({type}, {value})'.format(
                                               type=self.type,
                                               value=repr(self.value)
                                               )
    
    def __repr__(self):
        return self.__str__()
def get_all_token(tuples):
    tokens = []
    for tk in tuples:
        token = Token(tk[0],tk[1])
        tokens.append(token)
    return tokens

class Lexer:
    def __init__(self,text):
        self.tokens = get_all_token(tokenize(text))
        self.tokens.append(Token(EOF,'EOF'))
        self.token_index = 0
    
    def get_next_token(self):
        the_token = self.tokens[self.token_index]
        self.token_index = self.token_index+1
        return the_token

###############################################################################
#                                                                             #
#  PARSER                                                                     #
#                                                                             #
###############################################################################
class AST(object):
    pass
class BinOp(AST):
    def __init__(self, left, op, right):
        self.left = left
        self.token = self.op = op
        self.right = right


class Num(AST):
    def __init__(self, token):
        self.token = token
        self.value = token.value

class Id(AST):
    def __init__(self, token):
        self.token = token
        if token.value in symbol:
            self.value = symbol[token.value]
        else:
            self.value = '0'

class Parser(object):
    def __init__(self, lexer):
        self.lexer = lexer
        # set current token to the first token taken from the input
        self.current_token = self.lexer.get_next_token()
        self.current_id = ''
    
    def error(self):
        raise Exception('Invalid syntax')
    def get_current_id(self):
        return self.current_id
    def eat(self, token_type):
        # compare the current token type with the passed token
        # type and if they match then "eat" the current token
        # and assign the next token to the self.current_token,
        # otherwise raise an exception.
        if self.current_token.type == token_type:
            self.current_token = self.lexer.get_next_token()
        else:
            self.error()

    def factor(self):
        """Fact:
            ( Exp ) | - Fact | + Fact | Literal | Identifier"""
        token = self.current_token
        if token.type == PLUS:
            self.eat(PLUS)
            node = self.factor()
            return node
        elif token.type == MINUS:
            self.eat(MINUS)
            node = self.factor()
            return node
        elif token.type == INTEGER:
            self.eat(INTEGER)
            return Num(token)
        elif token.type == ID:
            self.eat(ID)
            return Id(token)
        elif token.type == LPAREN:
            self.eat(LPAREN)
            node = self.expr()
            self.eat(RPAREN)
            return node

    def term(self):
        """term : factor ((MUL ) factor)*"""
        """Term:
            Term * Fact  | Fact"""
        node = self.factor()
        
        while self.current_token.type in (MUL):
            token = self.current_token
            if token.type == MUL:
                self.eat(MUL)
            
            node = BinOp(left=node, op=token, right=self.factor())
        
        return node
    
    def expr(self):
        """
            Exp:
            Exp + Term | Exp - Term | Term
            
            expr   : term ((PLUS | MINUS) term)*
            term   : factor ((MUL ) factor)*
            factor : INTEGER | LPAREN expr RPAREN
            """
        node = self.term()
        
        while self.current_token.type in (PLUS, MINUS):
            token = self.current_token
            if token.type == PLUS:
                self.eat(PLUS)
            elif token.type == MINUS:
                self.eat(MINUS)
            
            node = BinOp(left=node, op=token, right=self.term())
        
        return node

    def assign(self):
        token = self.current_token
        if token.type == ID:
            self.current_id = token.value
            self.eat(ID)
            token = self.current_token
            if token.type == ASSIGN:
                self.eat(ASSIGN)
                node = self.expr()
                token = self.current_token
                if token.type == END:
                    self.eat(END)
                    return node
        else:
            print ('error')
        pass
    def prog(self):
        #return self.assign()
        #token = self.current_token
        #print (token)
        #while self.current_token!=EOF:
        node = self.assign()
        return node
    

    def parse(self):
        return self.prog()


###############################################################################
#                                                                             #
#  INTERPRETER                                                                #
#                                                                             #
###############################################################################

class NodeVisitor(object):
    def visit(self, node):
        method_name = 'visit_' + type(node).__name__
        visitor = getattr(self, method_name, self.generic_visit)
        return visitor(node)
    
    def generic_visit(self, node):
        raise Exception('No visit_{} method'.format(type(node).__name__))


class Interpreter(NodeVisitor):
    def __init__(self, parser):
        self.parser = parser
    
    def visit_BinOp(self, node):
        if node.op.type == PLUS:
            return self.visit(node.left) + self.visit(node.right)
        elif node.op.type == MINUS:
            return self.visit(node.left) - self.visit(node.right)
        elif node.op.type == MUL:
            return self.visit(node.left) * self.visit(node.right)


    def visit_Num(self, node):
        print (node)
        return node.value
    def visit_Id(self, node):
        print (node)
        return symbol[node.value]
    def interpret(self):
        tree = self.parser.parse()
        return self.visit(tree)


def main():
    
    
    lines = ['x = 1;','y = 3;']
    for line in lines:
        lexer = Lexer(line)
        parser = Parser(lexer)
        interpreter = Interpreter(parser)
        result = interpreter.interpret()
        #print(result)
        symbol[parser.get_current_id()] = result
        for xxx in get_all_token(tokenize(line)):
            
            print(xxx)
        
    for k,v in symbol.items():
        print (k,v)
#print (symbol)



if __name__ == '__main__':
    main()





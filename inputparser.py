
#------------------------------------------------------------------------------
#   Copyright (c) 2008
#       Roger Hale    roger314159@hotmail.com
#
#   This file is part of MiraMath.
#
#   MiraMath is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   MiraMath is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with MiraMath.  If not, see <http://www.gnu.org/licenses/>.
#------------------------------------------------------------------------------

import sys
import os
import re

import ply.lex as lex
import ply.yacc as yacc

from keywords import *

sys.path.insert(0,"../..")


#Simple decorator that will print method doc string when method is called
def show_docstring(original_method):
    def new_method(self, t):
        #print '\nParser method document string:\n', original_method.__doc__
        #print '\nParser method name: ', original_method.__name__
        original_method(self, t)
        #print 'Parser method output: ', t[0]

    #Set doc string of new returned method to be equal to original, undecorated, method doc string
    new_method.__doc__ = original_method.__doc__
    return new_method


class InputParser(object):

    def __init__(self, **kw):
        #Get the namespace dictionary for Keyword class
        keywords = Keyword.__dict__
        self.reset()

        #Define a 'rule maker' lambda
        #Produces e.g. t_KEYWORD=r'KEYWORD' token rule
        rulemaker = lambda x, y : 'InputParser.t_' + x + " = '" + y + "'"

        #For each keyword defined in class Keyword a add token corresponding to the keyword
        #to tokens list and create a t_'keyword' class variable to define a search rule for
        #that keyword. This avoids the need of having to write a bunch of t_KEYWORD='<keyword>'
        #lines to define all the search rules for the lexer
        #
        #Remember that at this point the class attribute 'tokens' has already been partially filled, here we append the keywords
        for k in keywords:
            if k.isupper():
                InputParser.tokens.append(k)  #Add token to existing token list (tokens is a CLASS variable, already filled below)
                s = keywords[k]
                exec(rulemaker(k, keywords[k]))  #Create token rule attribute in this class

        #Figure out file names of various parser files
        try:
            modname = os.path.split(os.path.splitext(__file__)[0])[1] + "_" + self.__class__.__name__
        except:
            modname = "parser"+"_"+self.__class__.__name__
        self.debugfile = modname + ".dbg"
        self.tabmodule = modname + "_" + "parsetab"

        # Build the lexer and parser
        self.lexer = lex.lex(object=self, debug=0)
        self.parser = yacc.yacc(module=self,
                                debug=0,
                                debugfile=self.debugfile,
                                tabmodule=self.tabmodule)

    def run(self, s):
        self.parser.parse(s, self.lexer)

#        print 'parser input string=', s
#        print 'parser: input variables=', self.inputVariables
#        print 'parser: index variables=', self.indexVariables
#        print 'parser: input functions=', self.inputFunctions
#        print 'parser: program=\n', self.program
#        print 'functions=\n', self.functions

    def getParserOutput(self):
        return self.program, self.functions

    def reset(self):
        self.program = ''
        self.functions = ''
        self.inputVariables = set([])
        self.inputFunctions = set([])
        self.functionArgs = set([])
        self.more_than_one_row = False
        self.recordIndexVariables = 0
        self.indexVariables = []
        self.indexVariablesStack = []
        self.functionCounter = 0
        self.nested_variables = []

    ########################################LEXER STUFF FROM HERE###################################
    #Reserved words
    reserved = {'if'       : 'IF',
                'else'     : 'ELSE',
                'elif'     : 'ELIF',
                'for'      : 'FOR',
                'in'       : 'IN',
                'while'    : 'WHILE',
                'continue' : 'CONTINUE',
                'break'    : 'BREAK',
                'return'   : 'RETURN',
    }

    #Addtional tokens
    tokens = [
        'LABEL',
        'FLOAT',
        'INTEGER',
        'HEXADECIMAL',
        'BINARY',
        'COMMA',
        'COMPLEX',
        'STRING',
        'ASSIGNMENT',
        'PERIOD',
        'COLON',
        'SEMICOLON',
        'FACTORIAL',
        'EQUAL',
        'LESSTHAN',
        'GREATERTHAN',
        'LESSTHANEQUAL',
        'GREATERTHANEQUAL',
        'NOTEQUAL',
        'BITWISENOT',
        'BITWISEAND',
        'BITWISEOR',
        'BITWISEXOR',
        'SPACE',
    ]

    tokens += list(reserved.values())

    #This function is intended to catch the programming keywords (if, while, for, etc) and labels
    #Labels must start with a roman/greek letter, followed by 0-n groupings in the
    #following format: "_X", where X is a group of roman/greek/number chars
    #e.g. a_1, a_1_b, abc_abc123
    def t_LABEL(self, t):
        r'( [a-zA-Z] | (__[a-zA-Z]+__) ) ( (_?)( [a-zA-Z0-9] | (__[a-zA-Z]+__) )+ )*'
        t.type = self.reserved.get(t.value, 'LABEL')    # Check dictionary for reserved words, if not in dict return 'LABEL'
        return t

    def t_error(self, t):
        print "*****Lexer illegal character = ", t.value[0]
        t.lexer.skip(1)
        raise SyntaxError("*****Lexer error at '%s'" % t)


    #token search rules
    t_FLOAT             = r'((\d+\.\d*)(E[\+-]?\d+)?) | ([1-9]\d*E[\+-]?\d+)'
    t_INTEGER           = r'\d+'
    t_HEXADECIMAL       = r'0x[0-9A-Fa-f]+'
    t_BINARY            = r'0b[01]+'
    t_COMPLEX           = r'(((\d+\.\d*)(E[\+-]?\d+)?) | ([1-9]\d*E[\+-]?\d+) | (\d+))[ji]'
    t_STRING            = r" \" ( [a-zA-Z] | (__[a-zA-Z]+__) ) ( (_?)( [a-zA-Z0-9] | (__[a-zA-Z]+__) )+ )* \" "
    t_COMMA             = r'\,'
    t_PERIOD            = r'\.'
    t_ASSIGNMENT        = r':='
    t_COLON             = r':'
    t_SEMICOLON         = r';'
    t_FACTORIAL         = r'!'
    t_EQUAL             = r'=='
    t_LESSTHAN          = r'<'
    t_GREATERTHAN       = r'>'
    t_LESSTHANEQUAL     = r'<='
    t_GREATERTHANEQUAL  = r'>='
    t_NOTEQUAL          = r'!='
    t_BITWISENOT        = r'\!\!'
    t_BITWISEAND        = r'\&\&'
    t_BITWISEOR         = r'\|\|'
    t_BITWISEXOR        = r'\^\^'
    t_SPACE             = r'[ ]'

    #Literal tokens
    literals = "+-*"

    #Stuff to ignore
    #t_ignore_SPACE              = r'[ ]{1}'
    t_ignore_LPAREN             = r'\(' #Already have a keyword for this
    t_ignore_RPAREN             = r'\)' #Ditto
    t_ignore_DIVIDE             = '/'   #Divide
    t_ignore_LBRACKET           = r'\['
    t_ignore_RBRACKET           = r'\]'


    #**********************************PARSER STUFF BELOW HERE************************************
    # Parsing rules
    precedence = (
        ('left','+','-'),
        ('left', 'DIVIDESTART', '*', 'LEFTPAREN'),
        ('left', 'FACTORIAL'),
        ('right', 'POWERSTART', 'TRANSPOSESTART', 'CONJUGATESTART', 'HERMITIANSTART'),
        ('right','UMINUS')
        )

    start = 'statement'

    @show_docstring
    def p_statement_expression(self, t):
        '''statement : expression'''

        #If the expression has variables with array indices then wrap expression with for loops
        if self.indexVariables:

            #Must return a call to a function since this piece of python code will be run using an eval
            t[0] = """__result = __loop_thru_index_variables(%s, '%s', globals())""" % (self.indexVariables, t[1])

        else:
            #t[0] = t[1]
            t[0] = "__result = %s" % (t[1])

        #Final result is program
        self.program = t[0]
        print 'program=', t[0]
        print 'functions=', self.functions

    @show_docstring
    def p_assignment_to_variable(self, t):
        '''assignment : LABEL ASSIGNMENT expression'''
        t[0] = "_%s = (%s)" % (t[1], t[3])
        self.index_of_label = ''
        self.index_variables = []
        self.indexed_label = "_%s" % t[1]

    @show_docstring
    def p_assignment_to_indexed_variable(self, t):
        '''assignment : LABEL INDEXSTART seen_INDEXSTART indexlist INDEXEND ASSIGNMENT seen_ASSIGNMENT expression'''
        t[0] = "_%s[%s] = (%s)" % (t[1], t[4], t[8])

        s = t[4]
        index_string = s.split(',')
        new_index_string = []
        for part in index_string:
            temp = part
            parts = part.split(':')
            if len(parts) > 1:
                max_part = parts[1]
                temp = max_part + '-1'
            new_index_string.append(temp)

        self.index_of_label = ','.join(new_index_string)  #s
        print 'in p_assignment_to_indexed_variable, index_of_label=', self.index_of_label
        print 'should not be here'
        self.indexed_label = "_%s" % t[1]

    @show_docstring
    def p_seen_ASSIGNMENT(self, t):
        '''seen_ASSIGNMENT :'''
        self.recordIndexVariables -= 1
        t[0] = ''

        #Remember index variables used on lhs of equal sign
        self.index_variables = self.indexVariables[:]

    @show_docstring
    def p_statement_assignment(self, t):
        '''statement : assignment'''

        #If the expression has variables with array indices then wrap expression with for loops
        if self.indexVariables or self.index_of_label:
            t[0] = """__loop_thru_index_variables2(%s, '%s', '%s', %s, '[%s]', globals())""" % \
                   (self.indexVariables, t[1], self.indexed_label, self.index_variables, self.index_of_label)

        else:
            t[0] = t[1]

        #Final result is program
        self.program = t[0]

    @show_docstring
    def p_statement_assign_program_to_variable(self, t):
        '''statement : LABEL ASSIGNMENT program'''

        f = """\
def __program_function():
    retval = 0
%s
    return retval
""" % (t[3])

        self.functions += f
        t[0] = "_%s = __program_function()" % t[1]

        #Save the final parsed result
        self.program = t[0]

    @show_docstring
    def p_statement_assign_program_to_indexed_variable(self, t):
        '''statement : indexed_label ASSIGNMENT program'''

        f = """\
def __program_function():
    retval = 0
%s
    return retval
""" % (t[3])

        self.functions += f
        t[0] = "%s = __program_function()" % t[1]

        #Save the final parsed result
        self.program = t[0]

    @show_docstring
    def p_statement_program(self, t):
        '''statement : program'''

        f = """\
def __program_function():
    retval = 0
%s
    return retval
""" % (t[1])

        self.functions += f
        t[0] = "__program_function()"

        #Save the final parsed result
        self.program = t[0]

    @show_docstring
    def p_statement_define_function_using_program(self, t):
        '''statement : LABEL LEFTPAREN BODYSTART commalist BODYEND RIGHTPAREN ASSIGNMENT program'''

        s = """\
def %s(%s):
    retval = 0
%s
    return retval
""" % (t[1], t[4], t[8])

        t[0] = '0'
        self.program = t[0]
        self.functions += s

        #Remove function arguements from the set of variables used in current equation
        self.inputVariables = self.inputVariables.difference(self.functionArgs)

    @show_docstring
    def p_statement_create_symbols(self, t):
        '''statement : DEFINESYMBOLSTART SYMBOLLISTSTART commalist SYMBOLLISTEND DEFINESYMBOLEND'''
        s = """\
%s = sympy.symbols('%s', each_char=False)
""" % (t[3], t[3])

        self.program = s

    @show_docstring
    def p_statement_create_real_symbols(self, t):
        '''statement : DEFINEREALSTART SYMBOLLISTSTART commalist SYMBOLLISTEND DEFINEREALEND'''
        s = """\
%s = sympy.symbols('%s', each_char=False, real=True)
""" % (t[3], t[3])

        self.program = s

    @show_docstring
    def p_statement_create_integer_symbols(self, t):
        '''statement : DEFINEINTEGERSTART SYMBOLLISTSTART commalist SYMBOLLISTEND DEFINEINTEGEREND'''
        s = """\
%s = sympy.symbols('%s', each_char=False, integer=True)
""" % (t[3], t[3])

        self.program = s

    @show_docstring
    def p_statement_create_complex_symbols(self, t):
        '''statement : DEFINECOMPLEXSTART SYMBOLLISTSTART commalist SYMBOLLISTEND DEFINECOMPLEXEND'''
        s = """\
%s = sympy.symbols('%s', each_char=False, complex=True)
""" % (t[3], t[3])

        self.program = s

    @show_docstring
    def p_define_function(self, t):
        '''expression : LABEL LEFTPAREN BODYSTART commalist BODYEND RIGHTPAREN ASSIGNMENT expression'''

        s = """\
def %s(%s):
    return %s
""" % (t[1], t[4], t[8])

        t[0] = '0'  #Need 0 for statement:expression above so that __result is set to something
        self.functions += s

        #Remove function arguements from the set of variables used in current equation
        self.inputVariables = self.inputVariables.difference(self.functionArgs)

    @show_docstring
    def p_expression_function(self, t):
        '''expression : function
                      | FLOAT function
                      | INTEGER function
                      | function_power
                      | FLOAT function_power
                      | INTEGER function_power'''
        if len(t) == 2:
            t[0] = t[1]
        else:
            t[0] = "%s * %s" % (t[1], t[2])

    @show_docstring
    def p_function(self, t):
        '''function : LABEL LEFTPAREN BODYSTART commalist BODYEND RIGHTPAREN'''
        t[0] = "%s(%s)" % (t[1], t[4])
        self.inputFunctions.add(t[1])

    @show_docstring
    def p_function_power(self, t):
        '''function_power : LABEL POWERSTART expression POWEREND LEFTPAREN BODYSTART commalist BODYEND RIGHTPAREN'''
        t[0] = "(%s(%s)+0j) ** (%s)" % (t[1], t[7], t[3])
        self.inputFunctions.add(t[1])

    @show_docstring
    def p_commalist(self, t):
        '''commalist : expression COMMA commalist
                     | expression'''

        if len(t) == 2:
            t[0] = "%s" % t[1]
        else:
            t[0] = "%s, %s" % (t[1], t[3])

        self.functionArgs.add("_%s" % t[1])

    @show_docstring
    def p_expression_label(self, t):
        '''expression : label
                      | FLOAT label
                      | INTEGER label
                      | indexed_label
                      | FLOAT indexed_label
                      | INTEGER indexed_label
                      | indexed_label_power
                      | FLOAT indexed_label_power
                      | INTEGER indexed_label_power
                      | label_power
                      | FLOAT label_power
                      | INTEGER label_power'''

        if len(t) == 3:
            t[0] = "%s * %s" % (t[1], t[2])
        else:
            t[0] = t[1]

    @show_docstring
    def p_label(self, t):
        '''label : LABEL'''
        t[0] = "_%s" % t[1]

        #If this label is used as an index then record it if it has not already been recorded
        if self.recordIndexVariables and t[0] not in self.indexVariables:
            self.indexVariables.append(t[0])

        #Add variable name to set of variables used in the equation
        self.inputVariables.add(t[0])

    @show_docstring
    #Handle for e.g. x[i]**2
    def p_indexed_label_raised_to_power(self, t):
        '''indexed_label_power : LABEL SUBSUPSTART INDEXSTART seen_INDEXSTART indexlist INDEXEND POWERSTART expression POWEREND SUBSUPEND'''
        t[0] = "_%s[%s] ** %s" % (t[1], t[5], t[8])
        self.inputVariables.add("_%s" % t[1])
        self.recordIndexVariables -= 1

    @show_docstring
    #Handle for e.g. conjugate of x[i]
    def p_indexed_label_conjugated(self, t):
        '''indexed_label_power : LABEL SUBSUPSTART INDEXSTART seen_INDEXSTART indexlist INDEXEND CONJUGATESTART CONJUGATEEND SUBSUPEND'''
        t[0] = "__conjugate(_%s[%s])" % (t[1], t[5])
        self.inputVariables.add("_%s" % t[1])
        self.recordIndexVariables -= 1

    @show_docstring
    def p_indexed_label(self, t):
        '''indexed_label : LABEL INDEXSTART seen_INDEXSTART indexlist INDEXEND'''
        t[0] = "_%s[%s]" % (t[1], t[4])
        self.inputVariables.add("_%s" % t[1])
        self.recordIndexVariables -= 1

    @show_docstring
    def p_seen_INDEXSTART(self, t):
        '''seen_INDEXSTART :'''
        self.recordIndexVariables += 1
        t[0] = ''

    def p_indexlist(self, t):
        '''indexlist : expression COLON expression COLON expression COMMA indexlist
                     | expression COLON expression COMMA indexlist
                     | expression COLON expression COLON expression
                     | expression COMMA indexlist
                     | expression COLON expression
                     | expression'''
        l = len(t)
        if l == 2:
            t[0] = t[1]

        elif l == 4:
            if t[2] == ',':
                t[0] = "%s, %s" % (t[1], t[3])

            elif t[2] == ':':
                t[0] = "%s: %s+1" % (t[1], t[3])

        elif l == 6:
            if t[4] == ',':
                t[0] = "%s: %s+1, %s" % (t[1], t[3], t[5])

            elif t[4] == ':':
                t[0] = "%s: %s+1: %s" % (t[1], t[3], t[5])

        elif l == 8:
            t[0] = "%s: %s+1: %s, %s" % (t[1], t[3], t[5], t[7])

    @show_docstring
    def p_label_subscript(self, t):
        '''expression : LABEL SUBSCRIPTSTART LABEL SUBSCRIPTEND'''
        t[0] = "_%s__SUBSCRIPT_%s" % (t[1], t[3])

        #Add variable name to set of variables used in the equation
        self.inputVariables.add(t[0])

    @show_docstring
    def p_label_superscript(self, t):
        '''expression : LABEL SUPERSCRIPTSTART LABEL SUPERSCRIPTEND'''
        t[0] = "_%s__SUPERSCRIPT_%s" % (t[1],  t[3])

        #Add variable name to set of variables used in the equation
        self.inputVariables.add(t[0])

    @show_docstring
    def p_label_power(self, t):
        '''label_power : LABEL POWERSTART expression POWEREND'''

        s = "_%s" % t[1]
        t[0] = "(%s) ** (%s)" % (s,  t[3])

        #Add variable name to set of variables used in the equation
        self.inputVariables.add(s)

        #If this label is used as an index then record it if it has not already been recorded
        if self.recordIndexVariables and s not in self.indexVariables:
            self.indexVariables.append(s)

    @show_docstring
    def p_expression_power(self, t):
        '''expression : INTEGER       POWERSTART expression POWEREND
                      | FLOAT         POWERSTART expression POWEREND
                      | absolute      POWERSTART expression POWEREND
                      | determinant   POWERSTART expression POWEREND
                      | norm          POWERSTART expression POWEREND
                      | array         POWERSTART expression POWEREND
                      | parenthesis   POWERSTART expression POWEREND'''
        t[0] = "(%s) ** (%s)" % (t[1],  t[3])

    @show_docstring
    def p_parenthesis(self, t):
        '''parenthesis : LEFTPAREN BODYSTART expression BODYEND RIGHTPAREN'''
        t[0] = "(%s)" % t[3]

    @show_docstring
    def p_expression_parenthesis(self, t):
        '''expression : parenthesis'''
        t[0] = t[1]

    @show_docstring
    def p_expression_uminus(self, t):
        '''expression : '-' expression %prec UMINUS'''
        t[0] = '-' + t[2]

    @show_docstring
    def p_expression_complex(self, t):
        '''expression : COMPLEX'''
        s = re.sub('i', 'j', t[1])
        t[0] = s

    @show_docstring
    def p_expression_float(self, t):
        '''expression : FLOAT'''
        t[0] = t[1]

    @show_docstring
    def p_expression_decimal(self, t):
        '''expression : INTEGER'''
        t[0] = t[1]

    @show_docstring
    def p_expression_binary(self, t):
        '''expression : BINARY'''
        s = t[1]
        num = s[2:]
        t[0] = "int('%s', 2)" % num

    @show_docstring
    def p_expression_hexadecimal(self, t):
        '''expression : HEXADECIMAL'''
        s = t[1]
        num = s[2:]
        t[0] = "int('%s', 16)" % num

    @show_docstring
    def p_expression_string(self, t):
        '''expression : STRING'''
        t[0] = t[1]

    @show_docstring
    def p_expression_binop(self, t):
        '''expression : expression '+' expression
                      | expression '-' expression
                      | expression '*' expression
                      | expression EQUAL expression
                      | expression LESSTHAN expression
                      | expression GREATERTHAN expression
                      | expression LESSTHANEQUAL expression
                      | expression GREATERTHANEQUAL expression
                      | expression NOTEQUAL expression'''

        l = [ t[1], t[2], t[3] ]
        t[0] = ''.join(l)

    def p_assigment_list(self, t):
        '''assignment_list : expression EQUAL expression COMMA assignment_list
                           | expression EQUAL expression'''
        if len(t) == 6:
            t[0] = "%s,'%s':%s" % (t[5], t[1], t[3])
        else:
            t[0] = "'%s':%s" % (t[1], t[3])

    @show_docstring
    def p_expression_bitwise_not(self, t):
        '''expression : BITWISENOT expression'''
        l = [ '~', t[2] ]
        t[0] = ''.join(l)

    @show_docstring
    def p_expression_bitwise_and(self, t):
        '''expression : expression BITWISEAND expression'''
        l = [ t[1], '&', t[3] ]
        t[0] = ''.join(l)

    @show_docstring
    def p_expression_bitwise_or(self, t):
        '''expression : expression BITWISEOR expression'''
        l = [ t[1], '|', t[3] ]
        t[0] = ''.join(l)

    @show_docstring
    def p_expression_bitwise_xor(self, t):
        '''expression : expression BITWISEXOR expression'''
        l = [ t[1], '^', t[3] ]
        t[0] = ''.join(l)

    @show_docstring
    def p_expression_dotproduct(self, t):
        '''expression : expression DOTPRODUCTSTART DOTPRODUCTEND expression'''
        t[0] = "scipy.dot(%s, %s)" % (t[1], t[4])

    @show_docstring
    def p_expression_convolution(self, t):
        '''expression : expression CONVOLVESTART CONVOLVEEND expression'''
        t[0] = "scipy.convolve(%s, %s)" % (t[1], t[4])

    @show_docstring
    def p_expression_ceiling(self, t):
        '''expression : CEILSTART BODYSTART expression BODYEND CEILEND'''
        t[0] = "scipy.ceil(%s)" % (t[3])

    @show_docstring
    def p_expression_floor(self, t):
        '''expression : FLOORSTART BODYSTART expression BODYEND FLOOREND'''
        t[0] = "scipy.floor(%s)" % (t[3])

    @show_docstring
    def p_expression_divide(self, t):
        '''expression : DIVIDESTART NUMSTART expression NUMEND DENOMSTART expression DENOMEND DIVIDEEND'''
        #t[0] = "(%s) / (%s)" % (t[3], t[6])
        t[0] = "__divide((%s),(%s))" % (t[3], t[6])

    @show_docstring
    def p_expression_squareroot(self, t):
        '''expression : SQUAREROOTSTART ROOTBODYSTART expression ROOTBODYEND SQUAREROOTEND'''
        t[0] = "__sqrt(%s)" % t[3]

    @show_docstring
    def p_expression_ordernroot(self, t):
        '''expression : ORDERNROOTSTART ORDERSTART expression ORDEREND ROOTBODYSTART expression ROOTBODYEND ORDERNROOTEND'''
        t[0] = "1 * scipy.real_if_close((%s + 0j) ** (1.0 / %s))" % (t[6],  t[3])

    @show_docstring
    def p_expression_factorial(self, t):
        '''expression : expression FACTORIAL'''
        t[0] = "__factorial(%s)" % t[1]

    @show_docstring
    def p_expression_transpose(self, t):
        '''expression : expression TRANSPOSESTART TRANSPOSEEND'''
        t[0] = "(__transpose(%s))" % t[1]

    @show_docstring
    def p_expression_hermitian(self, t):
        '''expression : expression HERMITIANSTART HERMITIANEND'''
        t[0] = "(__hermitian(%s))" % t[1]

    @show_docstring
    def p_expression_conjugate(self, t):
        '''expression : expression CONJUGATESTART CONJUGATEEND'''
        t[0] = '__conjugate(%s)' % t[1]

    @show_docstring
    def p_absolute(self, t):
        '''absolute : ABSOLUTESTART BODYSTART expression BODYEND ABSOLUTEEND'''
        t[0] = "__absolute(%s)" % t[3]

    @show_docstring
    def p_expression_absolute(self, t):
        '''expression : absolute'''
        t[0] = t[1]

    @show_docstring
    def p_determinant(self, t):
        '''determinant : DETERMINANTSTART BODYSTART expression BODYEND DETERMINANTEND'''
        t[0] = "__determinant(%s)" %t[3]

    @show_docstring
    def p_expression_determinant(self, t):
        '''expression : determinant'''
        t[0] = t[1]

    @show_docstring
    def p_norm(self, t):
        '''norm : NORMSTART BODYSTART expression BODYEND NORMEND'''
        t[0] = "scipy.linalg.norm(%s)" % t[3]

    @show_docstring
    def p_expression_norm(self, t):
        '''expression : norm'''
        t[0] = t[1]

    @show_docstring
    def p_expression_sum(self, t):
#        '''expression : SUMSTART seen_SUMSTART FROMSTART SUMVARSTART LABEL SUMVAREND ASSIGNMENT SUMFROMVALSTART expression SUMFROMVALEND FROMEND SUMTOSTART expression SUMTOEND seen_SUMTOEND SUMBODYSTART expression SUMBODYEND SUMEND'''
        '''expression : SUMSTART seen_SUMSTART SUMVAREND ASSIGNMENT SUMFROMVALSTART expression SUMFROMVALEND FROMEND SUMTOSTART expression SUMTOEND seen_SUMTOEND SUMBODYSTART expression SUMBODYEND SUMEND'''

        #Pop off in reverse order
        list_of_index_vars_before_sum_body = self.indexVariablesStack.pop()
        list_of_index_vars_before_sum = self.indexVariablesStack.pop()

        temp = "_%s" % t[2]

        if temp in self.indexVariables:
            self.inputVariables.discard(temp)

        if temp not in list_of_index_vars_before_sum_body and temp in self.indexVariables:
            self.indexVariables.remove(temp)


        self.nested_variables.pop()
        if self.nested_variables:
            args_str = ("_%s, " * len(self.nested_variables)) % tuple(self.nested_variables)
        else:
            args_str = ''

        s = """
def __run_time_function_%s(%s):
    retval =__summation(lambda _%s: %s, %s, %s, '%s')
    return retval
""" % (self.functionCounter, args_str, t[2], t[14], t[6], t[10], t[2])
        self.functions += s

        t[0] = "__run_time_function_%s(%s)" % (self.functionCounter, args_str)

        #Increment must be done after setting t[0]
        self.functionCounter += 1

    @show_docstring
    def p_seen_SUMTOEND(self, t):
        '''seen_SUMTOEND :'''
        self.indexVariablesStack.append(self.indexVariables[:])
        t[0] = ''

    @show_docstring
    def p_seen_SUMSTART(self, t):
        #'''seen_SUMSTART :'''
        '''seen_SUMSTART : FROMSTART SUMVARSTART LABEL'''
        self.indexVariablesStack.append(self.indexVariables[:])
        #t[0] = ''
        t[0] = t[3]
        self.nested_variables.append(t[0])

    @show_docstring
    def p_expression_matrixsum(self, t):
        '''expression : MATRIXSUMSTART BODYSTART expression BODYEND MATRIXSUMEND'''
        t[0] = "scipy.sum(%s, dtype=float)" % t[3]

    @show_docstring
    def p_expression_rangesum(self, t):
        '''expression : RANGESUMSTART FROMSTART LABEL FROMEND BODYSTART expression BODYEND RANGESUMEND'''

        #Put sum inside a function so that loop variable does not pollute name worksheet space
        s = """
def __rangesum_func_%s():
    __temp = %s[:]
    return scipy.sum([%s for %s in __temp], dtype=float)
""" % (self.functionCounter, t[3], t[6], t[3])

        self.functions += s
        t[0] = "__rangesum_func_%s()" % (self.functionCounter)
        self.functionCounter += 1

        #Remove counter variable from the set of variables used in current equation
        self.inputVariables.discard(t[4])

    @show_docstring
    def p_expression_product(self, t):
        '''expression : PRODUCTSTART seen_SUMSTART FROMSTART SUMVARSTART LABEL SUMVAREND \
                        ASSIGNMENT SUMFROMVALSTART expression SUMFROMVALEND FROMEND \
                        SUMTOSTART expression SUMTOEND seen_SUMTOEND SUMBODYSTART expression SUMBODYEND PRODUCTEND'''

        #Pop off in reverse order
        list_of_index_vars_before_sum_body = self.indexVariablesStack.pop()
        list_of_index_vars_before_sum = self.indexVariablesStack.pop()

        temp = "_%s" % t[5]
        if temp not in list_of_index_vars_before_sum_body and temp in self.indexVariables:
            self.indexVariables.remove(temp)

        s = """
def __run_time_function_%s():
    return __product('%s', '_%s', '%s', '%s', globals())
""" % (self.functionCounter, t[17], t[5], t[9], t[13])
        self.functions += s

        t[0] = "__run_time_function_%s()" % (self.functionCounter)

        #Remove counter variable from the set of variables used in current equation
        self.inputVariables.discard("_%s" % t[5])
        self.functionCounter += 1

    @show_docstring
    def p_expression_range(self, t):
        '''expression : expression SEMICOLON expression
                      | expression SEMICOLON expression COMMA expression'''
        if len(t) == 4:
            t[0] = "scipy.arange(%s, %s+1, 1)" % (t[1], t[3])
        else:
            t[0] = "scipy.arange(%s, %s+%s, %s)" % (t[1], t[3], t[5], t[5])

    @show_docstring
    def p_expression_matrixaverage(self, t):
        '''expression : AVERAGESTART BODYSTART expression BODYEND AVERAGEEND'''
        t[0] = "scipy.mean(%s)" % t[3]

    @show_docstring
    def p_expression_vectorize(self, t):
        '''expression : VECTORIZESTART BODYSTART expression BODYEND VECTORIZEEND'''

        args_string = ','.join(self.inputVariables)
        f = """\
def __vectorize_function(%s):
    return %s
""" % (args_string, t[3])

        self.functions += f
        t[0] = "scipy.vectorize(__vectorize_function)(%s)" % args_string

    @show_docstring
    def p_elements(self, t):
        '''elements : ELEMENTSTART expression ELEMENTEND elements
                    | ELEMENTSTART expression ELEMENTEND'''
        if len(t) == 4:
            t[0] = "scipy.array(%s)" % t[2]
        else:
            t[0] = "scipy.array(%s), %s" % (t[2], t[4])

    @show_docstring
    def p_row(self, t):
        '''row : ROWSTART elements ROWEND'''
        t[0] = "scipy.hstack([%s])" % t[2]

    @show_docstring
    def p_rows(self, t):
        '''rows : row rows
                | row'''
        if len(t) == 2:
            t[0] = t[1]
        else:
            t[0] = "%s, %s" % (t[1], t[2])
            self.more_than_one_row = True

    @show_docstring
    def p_matrix(self, t):
        '''array : MATRIXSTART rows MATRIXEND'''
        if self.more_than_one_row:
            t[0] = "__matrix(scipy.vstack([%s]))" % t[2]
            self.more_than_one_row = False
        else:
            t[0] = "__matrix(%s)" % t[2]

    @show_docstring
    def p_array(self, t):
        '''array : ARRAYSTART rows ARRAYEND'''
        if self.more_than_one_row:
            t[0] = "scipy.array(scipy.vstack([%s]))" % t[2]
            self.more_than_one_row = False
        else:
            t[0] = "scipy.array(%s)" % t[2]

    @show_docstring
    def p_quickarray(self, t):
        '''array : LEFTPAREN BODYSTART commalist BODYEND RIGHTPAREN'''
        t[0] = "scipy.hstack([%s])" % t[3]

    @show_docstring
    def p_expression_array(self, t):
        '''expression : array'''
        t[0] = t[1]

    @show_docstring
    def p_expression_plot3dvalues(self, t):
        '''expression : PLOT3DVALUESSTART expression PLOT3DVALUESEND
                      | PLOT3DVALUESSTART expression COMMA expression COMMA expression PLOT3DVALUESEND'''
        if len(t) == 4:
            t[0] = t[2]
        else:
            t[0] = "(%s, %s, %s)" % (t[2], t[4], t[6])

    @show_docstring
    def p_expression_substitution(self, t):
        '''expression : SUBSTITUTIONSTART BODYSTART expression BODYEND BODYSTART assignment_list BODYEND SUBSTITUTIONEND'''
        d = t[6]
        l1 = d.split(',')
        l2 = [v.split(':')[0].strip("'") for v in l1]
        for k in l2:
            if k in self.inputVariables:
                self.inputVariables.remove(k)

        s = """
def __run_time_function_%s():
    return __substitution('%s', {%s}, globals(), %s)
""" % (self.functionCounter, t[3], t[6], self.inputVariables)
        self.functions += s

        t[0] = "__run_time_function_%s()" % (self.functionCounter)

        self.functionCounter += 1

    @show_docstring
    def p_expression_definite_integral(self, t):
        '''expression : INTEGRALSTART INTFROMSTART expression INTFROMEND INTTOSTART expression INTTOEND INTBODYSTART expression INTBODYEND INTVARSTART LABEL INTVAREND INTEGRALEND'''

        #Remove variable of integration
        #self.inputVariables.discard(t[12])

#        s1 = """
#def __run_time_function_%s(_%s):
#    return %s
#""" % (self.functionCounter, t[12], t[9])
#
#        s1b = """__run_time_function_%s""" % self.functionCounter
#
#        self.functionCounter += 1
#        self.functions += s1
#
#
#        s = """
#def __run_time_function_%s():
#    return __definite_integral(%s, %s, %s, '_%s', globals())
#""" % (self.functionCounter, s1b, t[3], t[6], t[12])


        s = """
def __run_time_function_%s():
    return __definite_integral(lambda _%s: %s, %s, %s, '_%s',   globals())
""" % (self.functionCounter, t[12], t[9], t[3], t[6], t[12])

        self.functions += s

        t[0] = "__run_time_function_%s()" % (self.functionCounter)

        self.functionCounter += 1

    @show_docstring
    def p_expression_indefinite_integral(self, t):
        '''expression : INDEFINTEGRALSTART INTBODYSTART expression INTBODYEND INTVARSTART LABEL INTVAREND INDEFINTEGRALEND'''

        #Remove variable of integration
        #self.inputVariables.discard('_%s' % t[6])

        s = """
def __run_time_function_%s():
    _%s = sympy.Symbol('_%s')
    return __indefinite_integral(lambda _%s: %s, _%s)
""" % (self.functionCounter, t[6], t[6], t[6], t[3], t[6])
        self.functions += s

        t[0] = "__run_time_function_%s()" % (self.functionCounter)

        self.functionCounter += 1

    @show_docstring
    def p_expression_differential(self, t):
        '''expression : DIVIDESTART NUMSTART DEESTART expression DEEEND NUMEND DENOMSTART DEESTART LABEL DEEEND DENOMEND DIVIDEEND'''
        t[0] = "__differentiate(lambda _%s: %s, _%s, globals())" % (t[9], t[4], t[9])

    @show_docstring
    def p_expression_limit(self, t):
        '''expression : LIMITSTART '+' BODYSTART LABEL BODYEND BODYSTART expression BODYEND LIMITEND expression
                      | LIMITSTART '-' BODYSTART LABEL BODYEND BODYSTART expression BODYEND LIMITEND expression'''
        if t[2] == '+':
            t[0] = "__limit(_%s, lambda _%s: %s, lambda _%s: %s, '+')" % (t[4], t[4], t[7], t[4], t[10])
        else:
            t[0] = "__limit(_%s, lambda _%s: %s, lambda _%s: %s, '-')" % (t[4], t[4], t[7], t[4], t[10])

        s = """\
_%s = sympy.Symbol('_%s')
""" % (t[4], t[4])

        self.functions += s

    @show_docstring
    def p_expression_recuring_decimal(self, t):
        '''expression : FLOAT LEFTPAREN BODYSTART INTEGER BODYEND RIGHTPAREN'''
        t[0] = "'%s[%s]'" % (t[1], t[4])

    #*************************Programming***********************
    @show_docstring
    def p_program_spaces(self, t):
        '''spaces : SPACE spaces
                  | SPACE'''
        if len(t) == 3:
            t[0] = ' ' + t[2]
        else:
            t[0] = ' '

    @show_docstring
    def p_program_indentation(self, t):
        '''indentation : LINESTART spaces
                       | LINESTART'''
        if len(t) == 3:
            t[0] = t[2] + '    '
        else:
            t[0] = '    '

    @show_docstring
    def p_programline_expression(self, t):
        '''programline : indentation expression LINEEND
                       | indentation assignment LINEEND'''
        if t[2] == '':
            t[0] = ''
        else:
            t[0] = t[1] + "retval = %s\n" % t[2]

    @show_docstring
    def p_programline_for_statement(self, t):
        '''programline : indentation FOR spaces LABEL spaces IN spaces expression LINEEND'''
        t[0] = t[1] + "for _%s in %s:\n" % (t[4], t[8])

        #Remove counter variable from the set of variables used in current equation
        self.inputVariables.discard("_%s" % t[4])

    @show_docstring
    def p_programline_while_statement(self, t):
        '''programline : indentation WHILE spaces expression LINEEND'''
        t[0] = t[1] + "while %s:\n" % t[4]

    @show_docstring
    def p_programline_return_statement(self, t):
        '''programline : indentation RETURN spaces expression LINEEND'''
        t[0] = t[1] + "return %s\n" % t[4]

    @show_docstring
    def p_programline_break_statement(self, t):
        '''programline : indentation BREAK LINEEND'''
        t[0] = t[1] + "break\n"

    @show_docstring
    def p_programline_continue_statement(self, t):
        '''programline : indentation CONTINUE LINEEND'''
        t[0] = t[1] + "continue\n"

    @show_docstring
    def p_programline_if_statement(self, t):
        '''programline : indentation IF spaces expression LINEEND'''
        t[0] = t[1] + "if %s:\n" % t[4]

    @show_docstring
    def p_programline_elif_statement(self, t):
        '''programline : indentation ELIF spaces expression LINEEND'''
        t[0] = t[1] + "elif %s:\n" % t[4]

    @show_docstring
    def p_programline_else_statement(self, t):
        '''programline : indentation ELSE LINEEND'''
        t[0] = t[1] + "else:\n"

    @show_docstring
    def p_programlines_programline(self, t):
        '''programlines : programline programlines
                        | programline'''
        if len(t) == 3:
            t[0] = t[1] + t[2]
        else:
            t[0] = t[1]

    @show_docstring
    def p_program_programlines(self, t):
        '''program : PROGRAMSTART PROGRAMBODYSTART programlines PROGRAMBODYEND PROGRAMEND'''
        t[0] = t[3]

    #*************************Error handling*********************
    def p_error(self, t):
        print "*****Parser syntax error at '%s'" % t
        raise SyntaxError("*****Parser syntax error at '%s'" % t)




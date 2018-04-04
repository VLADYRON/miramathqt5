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
sys.path.insert(0,"../..")
import os
import re

import ply.lex as lex
import ply.yacc as yacc

from keywords import *
from equationwidgets import *
from symbolscharmap import SymbolsTable


#Simple decorator that will print method doc string when method is called
def show_docstring(original_method):
    def new_method(self, t):
        #print '\nOutput parser method document string:\n', original_method.__doc__
        print '\nOutput parser method name: ', original_method.__name__
        original_method(self, t)

    #Set doc string of new returned method to be equal to original, undecorated, method doc string
    new_method.__doc__ = original_method.__doc__
    return new_method

class OutputParser(object):

    def __init__(self, **kw):

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

        #Create a list of special symbols (ASCII names of symbols)
       # [ascii_value, unicode_value, tooltip] = zip(*SymbolsTable.symbols)
        self.specialSymbols = dict(zip(SymbolsTable.ascii_value, SymbolsTable.unicode_value))

    def run(self, parent, s, font):
        self.font = font
        self.parentEquation = parent
        self.outputEquation = []
        self.showMultiplySigns = False
        self.parser.parse(s, self.lexer)
        return self.outputEquation

    def testLexer(self, s):
        self.lexer.input(s)
        while 1:
            tok = lex.token()
            if not tok: break      # No more input
            print tok

    ########################################LEXER STUFF FROM HERE###################################
    #Reserved words
    reserved = {
        #Reserved labels
        'pi'        : 'PI',
        'oo'        : 'INFINITY',
        'I'         : 'ROOTMINUSONE',
        'exp'       : 'EULER',
        'conjugate' : 'CONJUGATE',
        'abs'       : 'ABSOLUTE',
        'gamma'     : 'GAMMA',
        'DiracDelta': 'DIRACDELTA',
    }

    #Addtional tokens
    tokens = [
        'LABEL',
        'FLOAT',
        'INTEGER',
        'LPAREN',
        'RPAREN',
        'POWER',
        'PI',
        'INFINITY',
        'ROOTMINUSONE',
        'EULER',
        'SQUAREROOT',
        'CONJUGATE',
        'ABSOLUTE',
        'FACTORIAL',
        'GAMMA',
        'DIRACDELTA',
    ]

    def t_LABEL(self, t):
        r' _? ( [a-zA-Z] | (__[a-zA-Z]+__) )  ( (_?) ( [a-zA-Z0-9] | (__[a-zA-Z]+__) )+ )*'
        t.type = self.reserved.get(t.value, 'LABEL')    # Check dictionary for reserved words, if not in dict return 'LABEL'
        return t

    def t_FLOAT(self, t):
        r'((\d+\.\d*)(E[\+-]?\d+)?) | ([1-9]\d*E[\+-]?\d+)'
        t.type = 'FLOAT'
        return t

    def t_INTEGER(self, t):
        r'\d+'
        t.type = 'INTEGER'
        return t

    def t_SQUAREROOT(self, t):
        r'\*\*\(1/2\)'
        t.type = 'SQUAREROOT'
        return t

    special_syms_re = re.compile("__[a-zA-Z]+__|_|[a-zA-Z0-9]*")

    #token search rules
    t_LPAREN            = r'\('
    t_RPAREN            = r'\)'
    t_POWER             = r'\*\*'
    t_FACTORIAL         = r'!'

    #Literal tokens
    literals = "+-*/"

    #ignore wish list
    t_ignore            = ' \t'

    def t_error(self, t):
        print "Lexer illegal character = ", t.value[0]
        t.lexer.skip(1)

    #**********************************PARSER STUFF BELOW HERE************************************
    # Parsing rules
#    precedence = (
#        ('left','+','-'),
#        ('left', '*'),
#        ('left', '/'),
#        ('right', 'POWER'),
#        ('right', 'LPAREN'),
#        ('right', 'UMINUS'),
#        ('right', 'SQUAREROOT')
#        )


    precedence = (
        ('left','+','-'),
        ('left', '*'),
        ('right', 'UMINUS'),
        ('left', '/'),
        ('right', 'POWER'),
        ('right', 'LPAREN'),
        ('right', 'SQUAREROOT')
        )


    #Top level rules
    def p_statement_expression(self, t):
        '''statement : expression'''
        t[0] = t[1]

        #Save the final parsed result
        self.outputEquation = t[0]

    def p_label(self, t):
        '''label : LABEL'''

        parts = self.special_syms_re.findall(t[1])

        l = []
        for i, part in enumerate(parts):
            if (part == '_' and i == 0) or part == '':
                continue

            if self.specialSymbols.has_key(part):
                c = EquationChar(self.parentEquation, self.specialSymbols[part], part, self.font)
                l.append(c)
            else:
                ll = [EquationChar(self.parentEquation, c, c, self.font) for c in part]
                l.extend(ll)
        t[0] = l

    def p_expression_label(self, t):
        '''expression : label'''
        t[0] = t[1]

    def p_expression_pi(self, t):
        '''expression : PI'''
        t[0] = [EquationChar(self.parentEquation, u'\u03c0', '__pi__', self.font)]

    def p_expression_infinity(self, t):
        '''expression : INFINITY'''
        t[0] = [EquationChar(self.parentEquation, u'\u221e', '__infinity__', self.font)]

    def p_expression_complex(self, t):
        '''expression : INTEGER '*' ROOTMINUSONE
                      | FLOAT '*' ROOTMINUSONE
                      | ROOTMINUSONE'''

        c1 = EquationChar(self.parentEquation, 'j', 'j', self.font)
        if len(t) == 4:
            l = [EquationChar(self.parentEquation, v, v, self.font) for v in t[1]]
        else:
            l = [EquationChar(self.parentEquation, '1', '1', self.font)]
        l.append(c1)
        t[0] = l

    def p_expression_number(self, t):
        '''expression : INTEGER
                      | FLOAT'''
        t[0] = [EquationChar(self.parentEquation, v, v, self.font) for v in t[1]]

    def p_expression_uminus(self, t):
        '''expression : '-' expression %prec UMINUS'''
        c = EquationChar(self.parentEquation, ' - ', '-', self.font)
        l = [c]
        l.extend(list(t[2]))
        t[0] = l

    def p_expression_factorial(self, t):
        '''expression : expression FACTORIAL'''
        l = list(t[1])
        l.append(EquationChar(self.parentEquation, '!', '!', self.font))
        t[0] = l

    def p_expression_gamma(self, t):
        '''expression : GAMMA LPAREN expression RPAREN'''
        l = []
        c0 = EquationChar(self.parentEquation, u'\u0393', '__GAMMA__', self.font)
        c1 = Keyword(Keyword.LEFTPAREN, cursorright=2)
        c2 = EquationParenthesis(self.parentEquation, '__leftparenthesis__')
        c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
        c3.selectEntireMathObject = True
        c3.cursorLookRight = True
        c4 = Keyword(Keyword.BODYEND, cursorright=3)
        c4.selectEntireMathObject = True
        c5 = EquationParenthesis(self.parentEquation, '__rightparenthesis__')
        c6 = Keyword(Keyword.RIGHTPAREN, cursorleft=2)

        l = [c0, c1, c2, c3]
        l.extend(list(t[3]))
        l.extend([c4, c5, c6])
        t[0] = l

    def p_expression_diracdelta(self, t):
        '''expression : DIRACDELTA LPAREN expression RPAREN'''
        l = []
        c0 = EquationChar(self.parentEquation, u'\u03b4', '__delta__', self.font)
        c1 = Keyword(Keyword.LEFTPAREN, cursorright=2)
        c2 = EquationParenthesis(self.parentEquation, '__leftparenthesis__')
        c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
        c3.selectEntireMathObject = True
        c3.cursorLookRight = True
        c4 = Keyword(Keyword.BODYEND, cursorright=3)
        c4.selectEntireMathObject = True
        c5 = EquationParenthesis(self.parentEquation, '__rightparenthesis__')
        c6 = Keyword(Keyword.RIGHTPAREN, cursorleft=2)

        l = [c0, c1, c2, c3]
        l.extend(list(t[3]))
        l.extend([c4, c5, c6])
        t[0] = l

    def p_expression_conjugate(self, t):
        '''expression : CONJUGATE LPAREN expression RPAREN'''
        l = list(t[3])
        c1 = Keyword(Keyword.CONJUGATESTART)
        c2 = EquationChar(self.parentEquation, '*', '__star__', self.font)
        c3 = Keyword(Keyword.CONJUGATEEND)
        l.extend([c1, c2, c3])
        t[0] = l

    def p_expression_absolute(self, t):
        '''expression : ABSOLUTE LPAREN expression RPAREN'''
        c1 = Keyword(Keyword.ABSOLUTESTART, cursorright=3)
        c2 = EquationVerticalLine(self.parentEquation)
        c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
        c3.selectEntireMathObject = True
        c3.cursorLookRight = True
        c4 = Keyword(Keyword.BODYEND, cursorright=3)
        c4.selectEntireMathObject = True
        c5 = EquationVerticalLine(self.parentEquation)
        c6 = Keyword(Keyword.ABSOLUTEEND, cursorleft=3)

        l = [c1, c2, c3]
        l.extend(list(t[3]))
        l.extend([c4, c5, c6])
        t[0] = l

    def p_expression_function(self, t):
        '''expression : label LPAREN expression RPAREN
                      | label LPAREN expression RPAREN POWER expression'''
#        '''expression : label LPAREN expression RPAREN'''

        l = []
        c1 = Keyword(Keyword.LEFTPAREN, cursorright=2)
        c2 = EquationParenthesis(self.parentEquation, '__leftparenthesis__')
        c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
        c3.selectEntireMathObject = True
        c3.cursorLookRight = True
        c4 = Keyword(Keyword.BODYEND, cursorright=3)
        c4.selectEntireMathObject = True
        c5 = EquationParenthesis(self.parentEquation, '__rightparenthesis__')
        c6 = Keyword(Keyword.RIGHTPAREN, cursorleft=2)
        c7 = Keyword(Keyword.POWERSTART)
        c8 = Keyword(Keyword.POWEREND)

        if len(t) == 7:
            print 'got function raised to power'
            l = list(t[1])
            l.append(c7)
            l.extend(list(t[6]))
            l.append(c8)
            l.extend([c1, c2, c3])
            l.extend(list(t[3]))
            l.extend([c4, c5, c6])
            t[0] = l

        else:
            l = list(t[1])
            l.extend([c1, c2, c3])
            l.extend(list(t[3]))
            l.extend([c4, c5, c6])
            t[0] = l

    def p_expression_eulerpower(self, t):
        '''expression : EULER LPAREN expression RPAREN'''
        c1 = EquationChar(self.parentEquation, 'e', 'e', self.font)
        c2 = Keyword(Keyword.POWERSTART)
        c3 = Keyword(Keyword.POWEREND)
        l = [c1, c2]
        l.extend(list(t[3]))
        l.append(c3)
        t[0] = l

    def p_expression_divide(self, t):
        '''expression : expression '/' expression
                      | LPAREN expression '/' expression RPAREN
                      | LPAREN expression RPAREN '/' expression
                      | expression '/' LPAREN expression RPAREN
                      | LPAREN expression RPAREN '/' LPAREN expression RPAREN'''
        print 'parser got divide'
        length = len(t)
        if length == 4:
            num = t[1]
            denom = t[3]
        elif length == 6:
            if t[3] == '/':
                num = t[2]
                denom = t[4]
            elif t[4] == '/':
                num = t[2]
                denom = t[5]
            else:
                num = t[1]
                denom = t[4]
        elif length == 8:
            num = t[2]
            denom = t[6]

        c1 = Keyword(Keyword.DIVIDESTART, cursorright=2)
        c2 = Keyword(Keyword.NUMSTART, cursorleft=2)
        c3 = Keyword(Keyword.NUMEND, cursorright=3)
        c4 = EquationDivideLine(self.parentEquation)
        c5 = Keyword(Keyword.DENOMSTART, cursorleft=3)
        c6 = Keyword(Keyword.DENOMEND, cursorright=2)
        c7 = Keyword(Keyword.DIVIDEEND, cursorleft=2)
        l = [c1, c2]
        l.extend(list(num))
        l.extend([c3, c4, c5])
        l.extend(list(denom))
        l.extend([c6, c7])
        t[0] = l

    #Look for s*m^(-e) s=number,m=mantissa,e=exponent, output format is s/(m^e)
    def p_expression_divide_multiply(self, t):
        '''expression : expression '*' expression POWER LPAREN '-' expression RPAREN
                      | expression POWER LPAREN '-' expression RPAREN'''

        c1 = Keyword(Keyword.DIVIDESTART, cursorright=2)
        c2 = Keyword(Keyword.NUMSTART, cursorleft=2)
        c3 = Keyword(Keyword.NUMEND, cursorright=3)
        c4 = EquationDivideLine(self.parentEquation)
        c5 = Keyword(Keyword.DENOMSTART, cursorleft=3)
        c6 = Keyword(Keyword.POWERSTART)
        c7 = Keyword(Keyword.POWEREND)
        c8 = Keyword(Keyword.DENOMEND, cursorright=2)
        c9 = Keyword(Keyword.DIVIDEEND, cursorleft=2)

        if len(t) == 9:
            denom = t[3]
            num = t[1]
            pwr = t[7]

            l = [c1, c2]
            l.extend(list(num))
            l.extend([c3, c4, c5])
            l.extend(list(denom))
            l.extend([c6])
            l.extend(list(pwr))
            l.extend([c7, c8, c9])

        else:
            denom = t[1]
            num = EquationChar(self.parentEquation, '1', '1', self.font)
            pwr = t[5]

            l = [c1, c2, num, c3, c4, c5]
            l.extend(list(denom))
            l.extend([c6])
            l.extend(list(pwr))
            l.extend([c7, c8, c9])
        t[0] = l

    def p_expression_power(self, t):
        '''expression : expression POWER expression
                      | expression POWER LPAREN expression RPAREN'''
        c1 = Keyword(Keyword.POWERSTART)
        c2 = Keyword(Keyword.POWEREND)
        l = list(t[1])
        l.append(c1)

        if len(t) == 4:
            l.extend(list(t[3]))
        else:
            l.extend(list(t[4]))
        l.append(c2)
        t[0] = l

    def p_expression_squareroot(self, t):
        '''expression : expression SQUAREROOT
                      | LPAREN expression RPAREN SQUAREROOT'''
        c1 = Keyword(Keyword.SQUAREROOTSTART, cursorright=3)
        c2 = EquationSquareRootLine(self.parentEquation)
        c3 = Keyword(Keyword.ROOTBODYSTART, cursorleft=3)
        c3.selectEntireMathObject = True
        c3.cursorLookRight = True
        c4 = Keyword(Keyword.ROOTBODYEND, cursorright=2)
        c5 = Keyword(Keyword.SQUAREROOTEND, cursorleft=2)
        l = [c1, c2, c3]

        if len(t) == 3:
            l.extend(list(t[1]))
        else:
            l.extend(list(t[2]))

        l.extend([c4, c5])
        t[0] = l

    def p_expression_parenthesis(self, t):
        '''expression : LPAREN expression RPAREN'''
        c1 = Keyword(Keyword.LEFTPAREN, cursorright=2)
        c2 = EquationParenthesis(self.parentEquation, '__leftparenthesis__')
        c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
        c3.selectEntireMathObject = True
        c3.cursorLookRight = True
        c4 = Keyword(Keyword.BODYEND, cursorright=3)
        c4.selectEntireMathObject = True
        c5 = EquationParenthesis(self.parentEquation, '__rightparenthesis__')
        c6 = Keyword(Keyword.RIGHTPAREN, cursorleft=2)
        l = [c1, c2, c3]
        l.extend(list(t[2]))
        l.extend([c4, c5, c6])
        t[0] = l

#    def p_expression_scaled_label(self, t):
#        '''expression : FLOAT '*' label %prec SCALEDNUM
#                      | INTEGER '*' label %prec SCALEDNUM'''
#        l = [EquationChar(self.parentEquation, v, v, self.font) for v in t[1]]
#        if self.showMultiplySigns:
#            multiplySymbol = u" \u00b7 "
#            c = EquationChar(self.parentEquation, multiplySymbol, '*', self.font)
#            l.append(c)
#        l.extend(list(t[3]))
#        t[0] = l

    def p_expression_binop(self, t):
        '''expression : expression '+' expression
                      | expression '-' expression
                      | expression '*' expression'''
        l = t[1]

        if t[2] == '*':
            multiplySymbol = u" \u00b7 "
            c = EquationChar(self.parentEquation, multiplySymbol, '*', self.font)
            l.append(c)
        else:
            c = EquationChar(self.parentEquation, ' ' + t[2] + ' ', t[2], self.font)
            l.append(c)

        l.extend(list(t[3]))
        t[0] = l

    def p_error(self, t):
        print "Output parser syntax error at '%s'" % t




def main():
    p = OutputParser()
    #print 'made parser'
    #s = '-(1/2)*x**4 + (3/5)*x**5+sin(x)+cos(4/5)+tan(x*1/2)+x*0.05'
    #p.run(s)

    p.testLexer('__alpha__a__beta__')


if __name__=="__main__":
    main()

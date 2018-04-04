
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

'''This file is executed to fill the worksheet namespace before any equations are executed. It is shared by all equations'''

import sympy
import scipy

#*******************************************************************************************************************
#*Constants visible in worksheet
#*******************************************************************************************************************
___pi__         = sympy.pi
___infinity__   = sympy.oo
_e              = sympy.E


#*******************************************************************************************************************
#*Functions visible in worksheet
#*******************************************************************************************************************

#Trig functions
sin             = sympy.sin
cos             = sympy.cos
tan             = sympy.tan
cot             = sympy.cot
asin            = sympy.asin
acos            = sympy.acos
atan            = sympy.atan
acot            = sympy.acot
cosh            = sympy.cosh
sinh            = sympy.sinh
tanh            = sympy.tanh
coth            = sympy.coth
acosh           = sympy.acosh
asinh           = sympy.asinh
atanh           = sympy.atanh
acoth           = sympy.acoth

log             = sympy.log
exp             = sympy.exp
arg             = sympy.arg

#Special functions
__delta__       = sympy.DiracDelta
Ylm             = sympy.Ylm
__GAMMA__       = sympy.gamma
__zeta__        = sympy.zeta
chebyshevt      = sympy.chebyshevt
legendre        = sympy.legendre
assoc_legendre  = sympy.assoc_legendre
hermite         = sympy.hermite

#Combinatorial
falling_factorial = sympy.ff
binomial        = sympy.binomial

def Re(z):
    return sympy.re(z)

def Im(z):
    return sympy.im(z)

def series(expr, var, num=5):
    return sympy.Basic.removeO(sympy.series(expr, var, n=num))


#*********************************************************************************************************************
#*Hidden functions used within equation namespace, but called by parser generated code
#*********************************************************************************************************************
__matrix        = sympy.Matrix
__sqrt          = sympy.sqrt
__conjugate     = sympy.conjugate
__absolute      = sympy.abs

def __zeros(dimensions, dtype=object):
    return scipy.zeros(dimensions, dtype)

def __divide(p, q):
    #Use rational function if we have a ratio of 2 ints
    if isinstance(p, (int, sympy.core.numbers.Integer, sympy.core.numbers.Rational)) and \
       isinstance(q, (int, sympy.core.numbers.Integer, sympy.core.numbers.Rational)):
        return sympy.Rational(p, q)
    else:
        return p/q

def __factorial(x):
    return sympy.factorial(x)

#Perform symbolic substitution
def __substitution(program_string, d, g, inputvars):
    temp_dict = {}
    temp_dict2 = {}

    #Look at each item in dict d, find all variables that are assigned a value, e.g x=3
    for k, v in d.iteritems():
        if g.has_key(k):
            temp_dict[k] = g[k]
            g[k] = v
            temp_dict2[k] = 1
        else:
            g[k] = v
            temp_dict2[k] = 1

    s = "(%s).subs(%s)" % (program_string, d)
    l = {}
    r = eval(s, g, l)

    for k in temp_dict2:
        del g[k]
        if temp_dict.has_key(k):
            g[k] = temp_dict[k]

    return r

#Perform symbolic definite integration
def __definite_integral(integrand_func, from_val, to_val, variable_name, g):
    integration_var = g[variable_name]
    return sympy.integrate(integrand_func(integration_var), (integration_var, from_val, to_val))

#Perform symbolic indefinite integration
def __indefinite_integral(integrand_func, variable):
    return sympy.integrate(integrand_func(variable), variable)

#perform symbolic differentiation
def __differentiate(function_object, variable, g):
    return sympy.diff(function_object(variable), variable)

def __limit(limit_variable, limit_value_func, function_object, direction):
    print 'limit', limit_variable, limit_value_func, function_object
    return sympy.limit(function_object(limit_variable), limit_variable, limit_value_func(limit_variable), dir=direction)
    #return sympy.limit(func, limit_variable, limit_value_func, dir=direction)

def __determinant(m):
    return m.det()

def __transpose(m):
    return m.T

#def __summation(body_str, label_str, from_str, to_str, g):
#    s = """sympy.Sum(%s, (%s, %s, %s)).doit()""" % (body_str, label_str, from_str, to_str)
#    return eval(s, g)


def __summation(func, from_val, to_val, var_name_str):
    #__dummy = sympy.Symbol(var_name_str)
    s = "%s=sympy.Symbol('%s')" % (var_name_str, var_name_str)
    exec(s)
    __dummy = locals()[var_name_str]
    return sympy.Sum(func(__dummy), (__dummy, from_val, to_val)).doit()



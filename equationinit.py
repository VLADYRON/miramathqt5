
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
import time as __time_module

expand          = sympy.expand

def time(n):
    if n <=1:
        return __time_module.time()
    else:
        return scipy.array([__time_module.time() for i in xrange(n)])

#Rational class
#Creates an instance of Rational suitably initialized
class rational(sympy.Rational):
    def __new__(cls, p, q=1):
        r = sympy.Rational
        num = r(str(p))
        denom = r(str(q))
        return num/denom


#Do some voodoo magic to wrap for loops around any expression containing hanging indices
def __loop_thru_index_variables(index_vars, expression, g):
    indent = ''
    program_init = ''
    program = ''
    program_cleanup = ''
    dimensions = []
    indices = []

    #Look at each indexing variable
    for varname in index_vars:
        var = 0
        if varname in g:
            var = g[varname]
        else:
            raise NameError('name ' + varname + ' is not defined')

        #If indexing variable is an array type then create a for loop to iterate over that array
        if isinstance(var, scipy.ndarray):
            #This variable holds the dimensions of the result
            dimensions.append(str(len(var)))

            #Make sure the wrapper loop variables are visible everywhere since expression might contain
            #nested calls to subfunctions that use the index variables and expect to see globals
            temp1 = 'global ' + varname + '\n'
            program_init += temp1

            #Create a line of code that will create a deep copy of the global array variable and assign it
            #to a local variable within this function namespace
            #e.g. temp_i = i[:]
            temp2 = '__temp_' + varname + ' = ' + varname + '[:]\n'
            program_init += temp2

            temp3 = varname + ' = __temp_' + varname + '\n'
            program_cleanup += temp3

            #Create a counter variable used in loop to index into result stored in array m
            #e.g. index_i which is used for e.g. m[index_i, index_j....]
            counter = '__index_' + varname
            indices.append(counter)

            #Create a line of code that contains the for statement for the index variable
            #e.g. for index_i, i in enumerate(temp_i)
            temp4 = indent + 'for ' + counter + ', ' + varname + ' in enumerate(__temp_' + varname + '):\n'
            program += temp4

            #Increment indentation, ready for next for loop
            indent += '    '

    if len(dimensions):
        #Create a line of code to make an empty array to store result. This is the result that will be return by this function.
        #The value displayed by the eval statement in equation.py will be this result.
        #e.g. m=scipy.array([len(i), len(j), len ...])
        create_array = "__m = __zeros([" + ','.join(dimensions) + "])\n"
        program_init += create_array

        #program has the for loops, now create and add the final line containing the original expression, with indents
        #e.g. this final line inside the loop will look like:  m[index_i, index_j...] = expression
        program += indent + '__m[' + ','.join(indices) + '] = ' + expression + '\n'

        #Create the final program
        final_program = program_init + program + program_cleanup

        #Create a locals dict for exec context
        l = {'__m':0}

        exec final_program in g, l

    else:
        #None of the indexing variables were array types so simply execute the original expression
        program = '__m = ' + expression

        #Create a locals dict for exec context
        l = {'__m':0}

        exec program in g, l

    #Return result to eval statement in equation.py.  This is what gets displayed on the screen.
    return l['__m']


#Do even more voodoo magic to wrap for loops around assignment expression containing hanging indices
#This function will wrap for e.g x[i,j] = y[i,j+1] with some for loops that loop through all values of
#i,j.  It will also look at the max values of i,j to determine the dimensions of the result x, creating
#a new array x if x does not exist or its dimensions are less than required for the result.  The newly
#created array x will be initialized with zeros.
#
#The generated python code will look something like this (final_program below):
#
#            global _a
#            _a = __zeros([6, 5])
#            global _i
#            __temp__i = _i[:]
#            global _j
#            __temp__j = _j[:]
#            for _i in __temp__i:
#                for _j in __temp__j:
#                    _a[_i-1, _j] = (4 * _r[_i+1, _j+2])   <-----Original expression fed into function, now wrapped with for loops
#            _i = __temp__i
#            _j = __temp__j
#
#This piece of code is then fed into exec, using the global namespace of the worksheet for context so
#so that variables contained in the original expressiona are accessible.  Note the use of the
#global keyword above so that any functions called within the within expression have access
#to the loop variables (i,j in this case).
#
def __loop_thru_index_variables2(index_vars, expression, indexed_label, index_variables_lhs, index_of_label, variables_dict):
    indent = '    '
    program_init1 = ''
    program_init2a = ''
    program_init2b = ''
    program_init2c = ''
    program = ''
    program_clean = ''
    wrap_expression_flag = False

    #variables_dict = globals()

    #Code inside this if statement will determine if we need to pre-create an array to store the results
    #of looping through all the index variables.  If so, then create an array of zeros of suitable size
    #and same name as the lhs assignment variable

    #Does lhs label have an index?
    if len(index_of_label) > 2:  # 2 because index_of_label is a string that can be "[x,y,z]" = "[]" when x,y,z do not exist

        #Determine dimensions of result array (left hand side of equation)
        max_var_values = {}
        for varname in index_variables_lhs:   # These index variables appear in the index on the left hand side

            if varname in variables_dict:
                var = variables_dict[varname]

            else:
                raise NameError('name ' + varname + ' is not defined')

            #Get maximum value of index variable if it is an array type
            if isinstance(var, scipy.ndarray):
                max_var_values[varname] = var.max()

        #Determine size of new array of zeros by evaluating max value of each dimension
        new_dimensions = eval(index_of_label, variables_dict, max_var_values)
        new_dimensions = [x+1 for x in new_dimensions]

        #Make sure result is placed in globals so other equations in worksheet can see it
        program_init1 += "global %s\n" % indexed_label

        #Check if lhs indexed variable is in global (worksheet) namespace.
        #If not, then create a new array of zeros with correct dimensions calculated above.
        if indexed_label in variables_dict and \
            isinstance(variables_dict[indexed_label], scipy.ndarray) and \
            len(variables_dict[indexed_label].shape) == len(new_dimensions):

            shape = variables_dict[indexed_label].shape
            new_dimensions = [max(x, y) for x, y in zip(shape, new_dimensions)]

            #Are we trying to make the array bigger? If so, then create code to create an array of zeros,
            #copy over values in smaller array to new bigger array.
            if new_dimensions != list(shape):
                program_init1 += "__old_smaller_array = %s[:]\n" % indexed_label
                program_init2a += """\
    if __old_smaller_array.dtype == scipy.dtype(complex):
        %s = __zeros(%s, dtype=complex)
    elif __old_smaller_array.dtype == scipy.dtype('object'):
        %s = __zeros(%s, dtype=object)
    else:
        %s = __zeros(%s)
""" % (indexed_label, new_dimensions, indexed_label, new_dimensions, indexed_label, new_dimensions)

                program_init2b += "    %s = __zeros(%s, dtype=complex)\n" % (indexed_label, new_dimensions)
                program_init2c += "    %s = __zeros(%s, dtype=object)\n" % (indexed_label, new_dimensions)

                temp1 = ( ':%s,' * len(shape) ) % shape
                temp_string = '    %s[' % indexed_label + temp1 + '] = __old_smaller_array[' + temp1 + ']\n'

                program_init2a += temp_string
                program_init2b += temp_string
                program_init2c += temp_string

            #Go here is we are setting an existing element of the array (no need to create a new bigger array)
            else:
                program_init2b += "    %s = %s.astype(complex)\n" % (indexed_label, indexed_label)
                program_init2c += "    %s = %s.astype(object)\n" % (indexed_label, indexed_label)

        else:
            #Assignment result variable has not previously been defined so need to create an an array of zeros of suitable size
            program_init2a += "    %s = __zeros(%s)\n" % (indexed_label, new_dimensions)
            program_init2b += "    %s = __zeros(%s, dtype=complex)\n" % (indexed_label, new_dimensions)
            program_init2c += "    %s = __zeros(%s, dtype=object)\n" % (indexed_label, new_dimensions)

    #Look at each indexing variable
    for varname in index_vars:
        var = 0
        if varname in variables_dict:
            var = variables_dict[varname]
        else:
            raise NameError('name ' + varname + ' is not defined')

        #If indexing variable is an array type then create a for loop to iterate over that array
        if isinstance(var, scipy.ndarray):
            wrap_expression_flag = True

            temp1 = 'global ' + varname + '\n'
            program_init1 += temp1

            #Create a line of code that will assign the global array variable (=an index) to a temp local variable
            temp2 = '__temp_' + varname + ' = ' + varname + '[:]\n'
            program_init1 += temp2

            #Create a line of code that will restore value of array variable
            temp3 = varname + ' = __temp_' + varname + '\n'
            program_clean += temp3

            #Create a line of code that contains the for statement for the index variable
            #e.g. for index, var in enumerate(index_array)
            temp4 = indent + 'for ' + varname + ' in __temp_' + varname + ':\n'
            program += temp4

            #Increment indentation, ready for next for loop
            indent += '    '

    #Creat try and except string parts
    program_try_part = 'try:\n'
    program_except_part1a = 'except TypeError:\n'
    program_except_part1b = 'except ValueError:\n'

    #Only run thru nested loops if we have some array type variables in the lhs indices
    if wrap_expression_flag:
        #program has the for loops, now create and add the final line containing the original expression, with indents
        program += indent + expression + '\n'

        #Create the final program
        final_program = program_init1 + \
                        program_try_part + program_init2a + program + \
                        program_except_part1a + program_init2b + program +  \
                        program_except_part1b + program_init2c + program + program_clean

        print '****************final program=\n', final_program

        #Use an exec statement. This is will execute final_program in the __loop_thru_index_variables function namespace.
        exec final_program in variables_dict

    else:
        #None of the indexing variables were array types so simply execute the original expression

        #Create the final program
        final_program = program_init1 + \
                        program_try_part + program_init2a + '    ' + expression + '\n' + \
                        program_except_part1a + program_init2b + '    ' + expression + '\n' + \
                        program_except_part1b + program_init2c + '    ' + expression + '\n' + program_clean

        print '****************final (non looping vars) program=\n', final_program

        exec final_program in variables_dict


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

import copy

from PyQt4.QtCore import *

import threading
import time
import Queue
import sys
import scipy

class ExecThread(QThread):

    #Define a signal that takes an integer arguement
    show_results_signal = pyqtSignal((int, ), name='show_results_signal')

    def __init__(self, parent):

        #Setup the global name space which is shared between all equations in worksheet
        self.numerics_global_namespace = {}
        self.symbolics_global_namespace = {}
        self.worksheet_variable_namespace = {}

        f = open('numerics_init.py')
        numerics_init_program = f.read()
        f.close()

        f = open('symbolics_init.py')
        symbolics_init_program = f.read()
        f.close()

        f = open('equationinit.py')
        equation_init_program = f.read()
        f.close()

        exec numerics_init_program in self.numerics_global_namespace    # execfile goes away in 3.0
        exec symbolics_init_program in self.symbolics_global_namespace    # execfile goes away in 3.0

        exec equation_init_program in self.numerics_global_namespace    # execfile goes away in 3.0
        exec equation_init_program in self.symbolics_global_namespace    # execfile goes away in 3.0

        #Create Q to hold incomming equation mini-programs
        self.program_q = Queue.Queue()

        #Create Q to hold results
        self.results_q = Queue.Queue()

        #Create an event
        #Equations in worksheet will only get run when this event is set
        self.execution_event = threading.Event()
        self.execution_event.clear()

        #Call super classes init method last when were ready to go
        super(ExecThread, self).__init__(parent)

        #Finally start up thread
        self.start()

    def run(self):

        symbolics_globals = self.symbolics_global_namespace
        numerics_globals = self.numerics_global_namespace

        #Forever loop waits for commands to execute all equations from main thread
        while(1):

            #Wait for requests to appear on input Q. Block if Q is empty.
            #Each item in Q is a list, e.g. [(...), (...), object_id]
            q_item = self.program_q.get()

            #Item off Q is a list. Last element of list is ID of equation/plot
            object_id = q_item.pop()

            results = []

            #Loop through equation(s). Plots have more than one equation.
            for temp in q_item:

                #Updack data
                program = temp[0]
                inputvars = temp[1]
                inputfuncs = temp[2]
                has_result = temp[3]
                force_symbolic = temp[4]

                try:
                    if force_symbolic:
                        self.worksheet_variable_namespace.update(symbolics_globals)
                        exec program in self.worksheet_variable_namespace
                        is_symbolic = True

                    else:
                        #Look for any symbolic variables/functions used by this equation (self)
                        self.worksheet_variable_namespace.update(numerics_globals)
                        is_symbolic = self.check_for_symbolic_vars(inputvars, inputfuncs)

                        if is_symbolic:
                            self.worksheet_variable_namespace.update(symbolics_globals)
                            exec program in self.worksheet_variable_namespace
                        else:
                            self.worksheet_variable_namespace.update(numerics_globals)
                            exec program in self.worksheet_variable_namespace

                    #Remember result
                    if has_result:
                        result = self.worksheet_variable_namespace['__result']
                    else:
                        result = None

                    error = None

                except:
                    result = None
                    error = str(sys.exc_value)

                #Put results on output Q and notify parent thread via a Qt signal
                #We use copy.copy here so that the value of result at this instant is sent in the Q.
                #Since the Q object is sent asynchronously if we used 'result' without the copy the
                #value sent could be random.  Presumably result is a reference (pointer) to some memory location
                #that gets read at the time the Q object is sent which maybe be sometime after the put() call.
                t = (copy.copy(result), error, is_symbolic)
                results.append(t)

            results.append(object_id)

            #Send result back to main thread
            #Format is: [(result,error,is_symbolic), (...), (...), object_id]
            self.results_q.put(results)
            self.show_results_signal.emit(object_id)

    def check_for_symbolic_vars(self, inputvars, inputfuncs):

        numerical_vars = self.numerics_global_namespace
        symbolic_vars = self.symbolics_global_namespace
        worksheet_variables = self.worksheet_variable_namespace

        #Find any symbolic type variables
        for variable_name in inputvars:
            variable = worksheet_variables.get(variable_name) # Get actual value, return None if not in dict
            m = type(variable).mro()

            #Do a string search for sympy.  This seems to be about 10x faster than doing,
            #for example: if '_evalf' in dir(variable)
            if 'sympy' in str(m) or (isinstance(variable, scipy.ndarray) and variable.dtype.name == 'object'):
                return True

        #Find any symbolic type functions
        for function_name in inputfuncs:
            if worksheet_variables.has_key(function_name):
                function = worksheet_variables[function_name]
            elif symbolic_vars.has_key(function_name):
                function = symbolic_vars[function_name]
            else:
                function = None
            #function = worksheet_variables.get(function_name) # Get actual value, return None if not in dict
            m = type(function)

            #Do a string search for sympy.  This seems to be about 10x faster than doing,
            #for example: if '_evalf' in dir(variable)
            if 'sympy' in str(m):
                self.isSymbolic = True
                return True

        return False

    def reset(self):
        self.worksheet_variable_namespace = {}

    def do_computation(self, program):
        self.program_q.put(program)

    def stop_computations(self):
        #Still need to figure out how to stop the thread if it is in the middle of a looong run
        pass


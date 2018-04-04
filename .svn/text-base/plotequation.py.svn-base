
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
import re
import copy
import scipy
import time

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import inputparser
import outputparser
from equationcursor import *
from equationwidgets import *
from keywords import *
from activebox import *
from selectionbox import *
from symbolscharmap import SymbolsTable
from equation import *



class PlotEquation(Equation):
    """This object holds an entire equation"""
    def __init__(self, parent, position, font, plot3d_flag=False):
        Equation.__init__(self, parent, position, font)

        self.finishedInit = False

        self.setFlag(QGraphicsRectItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, False)
        self.setZValue(3)

        #Initialize variables
        self.object_type = 'plotequation'
        self.activeBox = None
        self.shadowBox = None
        self.borderWidth = 3 #Unseen border around equation, used in bounding rectangle

        #Initialize plot equation (insert place holder)
        if plot3d_flag:
            self.insert_place_holder2()
        else:
            self.insert_place_holder1()

        self.cursor.hide()

        self.is_valid = False

        self.finishedInit = True

    def updateBoundingRect(self):
        top = self.top - self.borderWidth
        bottom = self.bottom + self.borderWidth
        left = -self.borderWidth
        right = self.width + self.borderWidth

        #Update bounding rectangle around equation
        w = right - left
        h = bottom - top
        self.setRect(QRectF(left, top, w, bottom-top))

    def mousePressEvent(self, event):
        QGraphicsRectItem.mousePressEvent(self, event)

        #Clear any existing selection box
        self.clearSelectionBox()

        p = event.pos()
        s = event.scenePos()
        item = self.scene().itemAt(s)

        if item.object_type == 'character':
            self.characterClicked = True

            #Position and show equation cursor at clicked character location
            self.getClickedCursorPosition(item, p)
        else:
            self.cursor.hide()
            self.clearFocus()

    def mouseMoveEvent(self, event):
        #Do not pass up move events up to parent when dragging over equation
        #Cursor is being dragged over equation characters?
        if self.characterClicked:
            position = event.scenePos()
            item = self.scene().itemAt(position)
            if item.object_type == 'character':
                self.setSelectionBox(item)

    def mouseReleaseEvent(self, event):
        QGraphicsRectItem.mouseReleaseEvent(self, event)
        self.setCursor(Qt.OpenHandCursor)
        self.resizeStartHandle = 0
        self.characterClicked = False

    def hoverEnterEvent(self, event):
        pass

    def hoverLeaveEvent(self, event):
        pass

    def itemChange(self, change, value):
        return QGraphicsRectItem.itemChange(self, change, value)

    def keyPressEvent(self, event):
        QGraphicsRectItem.keyPressEvent(self, event)

        if self.cursor.isVisible() or self.showSelectionBox:
            self.handleKeyInput(event)

    def handleKeyInput(self, event):
        key = event.key()
        c = str(event.text())

        #Filter key inputs
        if key == Qt.Key_AsciiCircum:
            self.addPower()
        elif key == Qt.Key_ParenLeft:
            self.addLeftParen()
        elif key == Qt.Key_Slash:
            self.addDivide()
        elif key == Qt.Key_Semicolon:
            self.addRange()
        elif key == Qt.Key_Colon:
            self.addColon()
        elif key == Qt.Key_BracketLeft:
            self.addIndex()
        elif key == Qt.Key_Space:
            pass
        elif key == Qt.Key_End:
            self.moveCursorEnd()
        elif key == Qt.Key_Home:
            self.moveCursorStart()
        elif key == Qt.Key_Left:
            self.moveCursorLeft()
        elif key == Qt.Key_Right:
            self.moveCursorRight()
        elif key == Qt.Key_Up:
            self.moveCursorUp()
        elif key == Qt.Key_Down:
            self.moveCursorDown()
        elif key == Qt.Key_Backspace:
            self.delCharacter()
            if self.length == 0:
                self.insert_place_holder1()
                self.setCursorPosition()
                self.equationNeedsParsing = True
        elif c in self.allowedEquationKeys:
            self.addCharacter(c, c)

    def insert_place_holder1(self):
        c = EquationReservedSpace(self)
        self.equationList.insert(0, c)
        self.length = 1
        self.equationListIndex = 1
        self.layoutEquation()
        self.equationNeedsParsing = False

    def insert_place_holder2(self):
        c1 = Keyword(Keyword.PLOT3DVALUESSTART, cursorleft=0)
        c2 = EquationReservedSpace(self)
        c3 = Keyword(Keyword.PLOT3DVALUESEND, cursorright=0)
        self.equationList[:0] = [c1, c2, c3]
        self.length = 3
        self.equationListIndex = 1
        self.layoutEquation()
        self.equationNeedsParsing = False

    #********************************************************************************
    #*Methods below this point handle the entry of various types of characters into
    #*the equation
    #********************************************************************************
    def handleToolbuttonInput(self, button, *args):
        '''handles requests from main window'''

        #Return keyboard focus to this equation
        self.setFocus()

        if button == 'newmatrix':
            rows = args[0]
            cols = args[1]
            self.addMatrix(rows, cols)
        if button == 'newarray':
            rows = args[0]
            cols = args[1]
            self.addMatrix(rows, cols, t='array')
        elif button == 'specialsymbol':
            unicode_value = args[0]
            ascii_value = args[1]
            self.addCharacter(unicode_value, ascii_value)
        elif button == 'summation':
            self.addProductSummation('sum')
        elif button == 'rangesummation':
            self.addRangeProductSummation('sum')
        elif button == 'product':
            self.addProductSummation('product')
        elif button == 'determinant':
            self.addDeterminant()
        elif button == 'transpose':
            self.addTranspose()
        elif button == 'conjugate':
            self.addConjugate()
        elif button == 'power':
            self.addPower()
        elif button == 'hermitian':
            self.addHermitian()
        elif button == 'matrixsum':
            self.addMatrixSum()
        elif button == 'norm':
            self.addNorm()
        elif button == 'squareroot':
            self.addSquareRoot()
        elif button == 'ordernroot':
            self.addOrderNRoot()
        elif button == 'absolute':
            self.addAbsolute()
        elif button == 'defintegral':
            self.addDefiniteIntegral()
        elif button == 'indefintegral':
            self.addIndefiniteIntegral()
        elif button == 'differentiate':
            self.addDifferentiate()
        elif button == 'limitright':
            self.addLimit(1)
        elif button == 'limitleft':
            self.addLimit(0)
        elif button == 'createsymbol':
            self.addCreateSymbol(args[0])
        elif button == 'symbolicevaluate':
            pass
        elif button == 'substitution':
            self.addSubstitution()
        elif button == 'dotproduct':
            self.addDotProduct()
        elif button == 'meanaverage':
            self.addMeanAverage()
        elif button == 'subscript':
            self.addSubSuperScript('subscript')
        elif button == 'superscript':
            self.addSubSuperScript('superscript')
        elif button == 'inputtable':
            pass
            #self.addInputTable()
        elif button == 'vectorize':
            self.addVectorize()
        elif button == 'convolution':
            self.addConvolution()
        elif button == 'floor':
            self.addFloorCeil('floor')
        elif button == 'ceil':
            self.addFloorCeil('ceil')

    #*************************************************************************************
    #*Methods below this point handle parsing and executing equation
    #*************************************************************************************
    def tryToExecuteEquation(self):
        """This method will first check if the equation has been parsed, if not then parse it.
           Then it will execute the equation"""

        ret_val = None
        self.is_valid = False

        #If equation has been edited then it needs to be reparsed and executed
        if self.equationNeedsParsing:
            is_parsable = True
            for c in self.equationList:
                if c.object_type == 'character' and c.ascii_value == "__reserved__":
                    is_parsable = False
                    break

            if is_parsable:
                self.equationNeedsParsing = False
                self.parseEquation()
            else:
                self.equationHasBeenParsed = False
                self.setToolTip('Equation is incomplete')
                self.setColor(QColor('red'))

        if self.equationHasBeenParsed:
            has_result = False
            if not self.isAssignment and not self.hasProgram:
                has_result = True

            #Prepare what's needed for the execution thread
            ret_val = (self.program, self.inputVariables, self.inputFunctions, has_result, self.forceSymbolic)
            self.is_valid = True

        return ret_val

    def parseEquation(self):
        '''This function parses the equation and produces a Python program'''
        s = self.getEquationString()
        self.equationParser.reset()

        #Try running parser
        try:
            self.equationParser.run(s)   # Parse
            self.inputVariables = self.equationParser.inputVariables    # Vars used by eqn
            self.inputFunctions = self.equationParser.inputFunctions
            self.program = ''.join([self.equationParser.functions, self.equationParser.program])
            self.equationHasBeenParsed = True

        except:
            print str(sys.exc_info())
            self.setToolTip('Parser: Syntax error in equation')
            self.setColor(QColor('red'))
            self.equationHasBeenParsed = False

            self.inputVariables = []
            self.inputFunctions = []
            self.program = ''



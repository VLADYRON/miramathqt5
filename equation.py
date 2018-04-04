
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
import time
import copy
import re
import scipy
import sympy

#from PyQt4 import Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *

from equationwidgets import *
from keywords import Keyword
from symbolscharmap import SymbolsTable
from layout import Layout

import inputparser
import outputparser
import equationcursor
import activebox
import shadowbox
import selectionbox


class Equation(QGraphicsRectItem):
    """This object holds an entire equation"""
    dragOffEdgeOfSceneX = False
    dragOffEdgeOfSceneY = False
    layoutengine = Layout()
    equationParser = inputparser.InputParser()
    outputParser = outputparser.OutputParser()
    selectionColor = QColor('yellow')   # Background color of selected chars in equation
    selectionBorderColor = QColor('red')
    highlightedColor = QColor(144, 238, 144,  128)  # Background color of selected equation
    cursorOverEquationColor = QColor(0, 0xfd, 0xf8, 128)

    #Define how certain symbols are displayed on the screen
    multiplySymbol = u" \u00b7 "
    sumChar = u"\u2211"
    productChar = u"\u220f"
    hermitianChar = u"\u2020"
    dotChar = u"\u2022"
    rightArrowChar = u"\u2192"

    #Define various regular expressions used to process equation string
    label_pattern = re.compile( r'([a-zA-Z]|(__[a-zA-Z]+__))[a-zA-Z0-9_]*' )

    operatorSet = set('+-*')

    #Define various constants used by all equations
    borderWidth = 10                    # Width of border around equation
    displayResultAsTableThreshold = 10  # Max size for matrices

    specialSymbols = set(SymbolsTable.ascii_value)
    alphaSymbols = set("abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ'_")
    numSymbols = set('0123456789.')
    operatorSymbols = set('+-*')

    cursorChars = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789._')
    cursorChars = cursorChars.union(set(['__reserved__']))
    cursorChars = cursorChars.union(specialSymbols)

    varSizedSymbols1 = set(['__squareroot__',
                            '__integral_top__',
                            '__integral_bottom__',
                            '__summation__',
                            '__product__',
                            '__overline__',
                            '__arrow__',
                            '__programline__',
                            ])

    varSizedSymbols2 = set(['__leftparenthesis__',
                            '__rightparenthesis__',
                            '__rightsquarebracket__',
                            '__leftsquarebracket__',
                            '__floorleft__',
                            '__floorright__',
                            '__ceilleft__',
                            '__ceilright__',
                            '__verticalline__',
                            '__norm__',
                            '__leftbrace__',
                            '__rightbrace__',
                            ])

    varSizedSymbols3 = set(list(['__divideline__']))

    otherSymbols1 = set(['__reserved__',
                         '__transpose__',
                         '__star__',
                         '__hermitian__',
                         '__dot__',
                         '__calculusdee__',
                         '__symbol__',
                         '__real_symbol__',
                         '__integer_symbol__',
                         '__complex_symbol__',
                         '__limit__',
                         '__limitarrow__',
                         '__equalsign__',
                        ])

    #List containing names of variables in this object that are to be saved to disk
    save_variables = ['fontSize',                   \
                      'isAssignment',                     \
                      'isSymbolic',                        \
                      'hasResult',                          \
                      'equationNeedsParsing',      \
                      'equationHasBeenParsed',    \
                      'program',                \
                      'functions',              \
                      'inputVariables',         \
                      'object_type',                   \
                      'resultString',           \
                      'hasTable',               \
                      'tableIndex',             \
                      'initialTableWidth',      \
                      'initialTableHeight'      \
                      ]

    allowedEquationKeys = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-/*^!,.;_[(~ <>')
    special_delete_keywords1 = set([Keyword.HERMITIANEND,  \
                                    Keyword.CONJUGATEEND,  \
                                    Keyword.TRANSPOSEEND,  \
                                    Keyword.SUBSCRIPTEND])


    def __init__(self, parent, position, font):
        QGraphicsRectItem.__init__(self, parent)
        self.finishedInit = False

        self.setToolTip('Equation')
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.setCursor(Qt.ArrowCursor)
        self.setPos(position)       # Set position of equation using scene coordinates
        self.setAcceptsHoverEvents(True)
        self.setSelected(True)
        self.setZValue(100)  # Z value on worksheet
        self.object_id = id(self)  # Unique ID for instance

        #Create equation cursor
        self.cursor = equationcursor.EquationCursor(self)

        #Create active box (shown when editing eqn), shadow box (shown when
        #mouse over eqn) and selection box (shown when part of eqn is selected)
        self.activeBox = activebox.ActiveBox('table', self)
        self.activeBox.setColor(self.highlightedColor)
        self.shadowBox = shadowbox.ShadowBox(self)
        self.shadowBox.setColor(self.cursorOverEquationColor)
        self.selectionBox = selectionbox.SelectionBox(self)
        self.selectionBox.setColor(self.selectionColor)

        #Initialize variables
        self.object_type = 'equation'
        self.equation_index = 0  # Index of this equation within worksheet list of equations
        self.currentIndex = -1  # Index of this equation in worksheets list
        self.length = 0
        self.width = 0
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.positionChanged = False
        self.font = QFont(font.family(), font.pointSize())
        self.equationList = []
        self.equationListIndex = 0
        self.equationNeedsParsing = True
        self.equationHasBeenParsed = False
        self.hasTable = False
        self.tableIndex = 0
        self.initialTableWidth = 400
        self.initialTableHeight = 400
        self.hasResult = False
        self.isAssignment = False       # Set this flag if this equation contains an assignment
        self.hasProgram = False         # Set this if there is a program block in the equation
        self.isGlobalDefinition = False # Global definitions will be executed before all others
        self.is_symbolic = False
        self.forceSymbolic = False
        self.showSelectionBox = False
        self.characterClicked = False
        self.selectionStartIndex = -1
        self.selectionRightIndex = -1
        self.selectionLeftIndex = -1
        self.inputVariables = set([])   # Records input variable names (labels used by eqn)
        self.outputValue = None         # Records the numerical result of equation (if any)
        self.inputValues = {}
        self.program = ''
        self.resultString = ''
        self.result = None
        self.finishedInit = True
        self.ignoreInput = False
        pen = QPen(Qt.transparent)
        self.setPen(pen)

    def updateBoundingRect(self):
        top = self.top - self.borderWidth
        bottom = self.bottom + self.borderWidth
        left = -self.borderWidth
        right = self.width + self.borderWidth

        #Update bounding rectangle around equation
        w = right - left
        h = bottom - top
        #self.prepareGeometryChange()
        #self.update()
        self.setRect(left, top, w, h)
        self.shadowBox.setRect(left, top, w, h)
        self.activeBox.setSize(w, h)
        self.activeBox.setPos(left, top)

    def setFontSize(self, size):
        self.font.setPointSize(size)
        self.layoutEquation()
        if self.cursor.isVisible():
            self.setCursorPosition()

    def setFont(self, fontname):
        self.font.setFamily(fontname)

        #Set fontname for individual chars, WITHOUT changing pointsizes
        for c in self.equationList:
            if isinstance(c, EquationChar) or isinstance(c, EquationTable):
                c.setFontName(fontname)

        self.layoutEquation()
        if self.cursor.isVisible():
            self.setCursorPosition()

    def setColor(self, color):
        for c in self.equationList:
            if c.object_type == 'character':
                c.setColor(color)
        self.update()

    def mousePressEvent(self, event):
        QGraphicsRectItem.mousePressEvent(self, event)

        #Clear any existing selection box
        self.clearSelectionBox()

        self.setCursor(Qt.ClosedHandCursor)
        p = event.pos()
        s = event.scenePos()

        #Are we clicking on a resize handle?
        self.resizeStartHandle = self.activeBox.mouseInResizeHandle(p)

        item = self.scene().itemAt(s)

        if item.object_type == 'character':
            self.characterClicked = True
            self.getClickedCursorPosition(item, p)
        else:
            self.cursor.hide()
            self.clearFocus()

    def mouseMoveEvent(self, event):
        r = self.resizeStartHandle

        #Equation is being resized (has a table in it)
        if r:
            p = event.pos()
            m = self.borderWidth
            table = self.equationList[self.tableIndex]
            rightbracketwidth = leftbracketwidth = self.equationList[self.tableIndex+3].width
            tablex, tabley = table.getPosition()
            x = p.x()
            y = p.y()

            #Right resize handle dragged
            if r == 1:
                w = x - tablex - m - rightbracketwidth
                h = table.bottom - table.top
                table.setSize(w, h)

            #Bottom right resize handle dragged
            elif r == 2:
                w = x - tablex - m - rightbracketwidth
                h = y - tabley - m
                table.setSize(w, h)

            #Bottom resize handle dragged
            elif r == 3:
                w = table.width
                h = y - tabley - m
                table.setSize(w, h)

            #Bottom resize handle dragged
            elif r == 4:
                w = table.width
                h = tabley + table.bottom - table.top - y - m
                table.setSize(w, h)

            #Top resize handle dragged
            elif r == 5:
                w = x - tablex - m - rightbracketwidth
                h = tabley + table.bottom - table.top - y - m
                table.setSize(w, h)

            #Top left resize handle
            elif r == 6:
                old_width = table.width
                change_width = x + m
                w = table.width - change_width
                h = tabley + table.bottom - table.top - y - m
                table.setSize(w, h)
                deltax = old_width - table.width
                self.moveBy(deltax, 0)

            #Left middle resize handle dragged
            elif r == 7:
                old_width = table.width
                change_width = x + m
                w = table.width - change_width
                h = table.bottom - table.top
                table.setSize(w, h)
                deltax = old_width - table.width
                self.moveBy(deltax, 0)

            #Bottom left resize handle dragged
            elif r == 8:
                old_width = table.width
                change_width = x + m
                w = table.width - change_width
                h = y - tabley - m
                table.setSize(w, h)
                deltax = old_width - table.width
                self.moveBy(deltax, 0)

            l, r, t, b = self.layoutengine.layoutEquationPart(self.equationList, 0, len(self.equationList), self.font.pointSize())
            self.width = r - l
            self.top = t
            self.bottom = b
            self.updateBoundingRect()

            #Remember size of table. This is used if equation is re-computed and a new table is generated.
            self.initialTableWidth = table.width
            self.initialTableHeight = table.bottom - table.top

        #Cursor is being dragged over equation characters?
        elif self.characterClicked:
            position = event.scenePos()
            item = self.scene().itemAt(position)
            if item != self.activeBox:
                self.setSelectionBox(item)
        else:
            QGraphicsRectItem.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        QGraphicsRectItem.mouseReleaseEvent(self, event)
        self.setCursor(Qt.OpenHandCursor)
        self.resizeStartHandle = 0
        self.characterClicked = False

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        if not self.isSelected():
            self.shadowBox.show()

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        self.shadowBox.hide()

    def mouseDoubleClickEvent(self, event):
        s = self.alphaSymbols
        s = s.union(self.numSymbols)
        s = s.union(self.specialSymbols)

        index = self.equationListIndex
        eqnlist = self.equationList
        start = end = -1

        #Was a variable, float, int, function or complex double clicked?
        if index < self.length and eqnlist[index].object_type == 'character' \
            and eqnlist[index].ascii_value in s:

            #Look to the right
            end = self.length
            for i in xrange(index, self.length):
                c = eqnlist[i]
                if c.ascii_value in s:
                    end = i
                else:
                    break

            #Look to the left
            start = 0
            for i in xrange(index, -1, -1):
                c = eqnlist[i]
                if c.ascii_value in s:
                    start = i
                else:
                    break

        if index > 0 and eqnlist[index-1].object_type == 'character' and eqnlist[index-1].ascii_value in s:

            #Look to the right
            end = self.length
            for i in xrange(index-1, self.length):
                c = eqnlist[i]
                if c.ascii_value in s:
                    end = i
                else:
                    break

            #Look to the left
            start = 0
            for i in xrange(index-1, -1, -1):
                c = eqnlist[i]
                if c.ascii_value in s:
                    start = i
                else:
                    break

        if start != -1 and end != -1:
            self.selectionLeftIndex = start
            self.selectionRightIndex = end

            #Create a rectangle around selected text
            self.createSelectionBox()

    def itemChange(self, change, value):
        #Look for select/deselect events
        if change == QGraphicsRectItem.ItemSelectedChange and self.finishedInit:
            if value.toInt()[0]:
                #Equation was selected so show active box and hide shadow box
                self.activeBox.showBox(self.hasTable)
                self.shadowBox.hide()

            else:
                #Equation was deselected, hide cursor, active box and selection box
                self.cursor.hide()
                self.activeBox.hideBox()
                self.clearSelectionBox()
                if self.hasTable:
                    table = self.equationList[self.tableIndex]
                    table.clearSelection()

        #Look for movement
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            self.positionChanged = True

        return QGraphicsRectItem.itemChange(self, change, value)

    def keyPressEvent(self, event):
        #Do not propagate key events up to parent
        if self.cursor.isVisible() or self.showSelectionBox:
            self.handleKeyInput(event)

    def handleKeyInput(self, event):
        '''All keyboard input come through here'''
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
        elif key == Qt.Key_AsciiTilde:
            self.addTilde()
        elif key == Qt.Key_BracketLeft:
            self.addIndex()
        elif key == Qt.Key_Space:
            self.addSpace()
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
        elif key == Qt.Key_Return:
            event.setAccepted(False)
        elif key == Qt.Key_Apostrophe:
            self.addApostrophe()

        #Handle all other keys
        elif c in self.allowedEquationKeys:
            self.addCharacter(c, c)

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
        elif button == 'newline':
            self.addNewLine()
        elif button == 'if':
            self.addIf()
        elif button == 'else':
            self.addElse()
        elif button == 'elif':
            self.addElif()
        elif button == 'for':
            self.addFor()
        elif button == 'while':
            self.addWhile()
        elif button == 'continue':
            self.addContinue()
        elif button == 'break':
            self.addBreak()
        elif button == 'return':
            self.addReturn()
        elif button == 'operator':
            self.addCharacter(args[0], args[1])
        elif button == 'equality':
            self.addEquality()

    #****************************************************************************************
    #Methods below handle basic editing features (copy, cut, paste, delete)
    #****************************************************************************************
    def copyFromEquation(self):
        d = []
        if self.showSelectionBox:
            #Get part of equation highlighted
            eqnlist = self.equationList[self.selectionLeftIndex: self.selectionRightIndex+1]
            for c in eqnlist:
                d.append(c.__dict__.copy())

        return d

    def cutFromEquation(self):
        d = []
        if self.showSelectionBox:

            eqnlist = self.equationList[self.selectionLeftIndex: self.selectionRightIndex+1]
            for c in eqnlist:
                d.append(c.__dict__.copy())

            self.delCharacter()

        return d

    def pasteIntoEquation(self, itemsdict):
        #Only insert if cursor is visible (set visible when new equation made or if we insert
        #into an existing selected equation)
        if self.cursor.isVisible():
            #Remove old result before pasting
            self.deleteResult(True)

            #Delete highlighted items (if any) before pasting
            if self.showSelectionBox:
                deleteSelectionBoxContents()

            #Insert clipboard chars
            self.restoreEquationList(itemsdict)
            self.setSelected(True)

            #Only redraw equation and move cursor if there is something left to draw
            if self.length > 0:
                self.layoutEquation()
                self.setCursorPosition()
                self.equationNeedsParsing = True

    def delCharacter(self):
        eqnlist = self.equationList

        #If selection box visible, delete selection
        if self.showSelectionBox:
            #Delete selection box
            self.deleteSelectionBoxContents()

            i = self.equationListIndex
            if 0 < i < self.length:
                #Delete a program line
                c1 = self.equationList[i-1]
                c2 = self.equationList[i]
                if c1.value == Keyword.LINEEND:
                    self.equationListIndex = i - 1  # Move cursor back to end of above line

                #If there are no more program lines left then delete remaining parts of program
                elif c1.value == Keyword.PROGRAMBODYSTART and c2.value == Keyword.PROGRAMBODYEND:
                    self.equationListIndex = i - 3  #Go to start of program
                    self.length -= 5
                    i = self.equationListIndex
                    d1 = eqnlist.pop(i)  # PROGRAMSTART keyword
                    d2 = eqnlist.pop(i)  # Program vertical line
                    d3 = eqnlist.pop(i)  # PROGRAMBODYSTART keyword
                    d4 = eqnlist.pop(i)  # PROGRAMBODYEND keyword
                    d5 = eqnlist.pop(i)  # PROGRAMEND keyword
                    self.scene().removeItem(d2)
                    del d1
                    del d2
                    del d3
                    del d4
                    del d5
                    self.hasProgram = False

                #Have reached the beginning of the program using delete key, move cursor to beginning of next line
                elif c2.value == Keyword.LINESTART:
                    self.equationListIndex = i + 1

                #If nothing left between matching keywords then insert reserved char
                elif c2.object_type == 'keyword':
                    self.findMatchingKeywords()
                    if c2.match == i-1:
                        c3 = EquationReservedSpace(self)
                        eqnlist.insert(i, c3)
                        self.length += 1

            #Only redraw equation and move cursor if there is something left to draw
            if self.length > 0:
                self.layoutEquation()
                self.setCursorPosition()
                self.equationNeedsParsing = True

        #Do something if cursor is visible
        elif self.cursor.isVisible():
            index = self.equationListIndex

            #Delete result if cursor is at end of eqn and delete key is pressed
            if index == self.length and eqnlist[index-1].ascii_value == Keyword.EQUALSEND:
                self.deleteResult()
                self.equationListIndex = self.length

                #Only redraw equation and move cursor if there is something left to draw
                if self.length > 0:
                    self.layoutEquation()
                    self.setCursorPosition()

            #Delete others if cursor not at start of equation
            elif index >= 1:
                #Remove widget from widgets list
                c = eqnlist[index-1]

                #Select everythang between keyword and matching keyword
                if c.object_type == 'keyword':
                    if c.value == Keyword.LINESTART:
                        #Show a rectangle around program line
                        self.selectionLeftIndex = index - 1
                        self.selectionRightIndex = c.match
                        self.createSelectionBox()

                    if c.match < index-1:
                        #Show a rectangle around text to be deleted
                        self.selectionLeftIndex = c.match
                        self.selectionRightIndex = index - 1
                        self.createSelectionBox()

                #Delete a character
                elif c.object_type == 'character':
                    #Delete old result if it exists
                    self.deleteResult(True)

                    c = eqnlist[index-1]
                    if c.ascii_value == ':=':
                        if self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:
                            k = self.testCursorBetweenKeywords(Keyword.LINESTART)
                            c_k = eqnlist[k]
                            c_k.programLineIsAssignment = False
                        else:
                            self.isAssignment = False
                    c = eqnlist.pop(index-1)
                    self.scene().removeItem(c)
                    self.equationListIndex -= 1
                    self.length -= 1
                    del c

                    #If nothing left between matching keywords then insert reserved char
                    i = self.equationListIndex
                    if 0 < i < self.length:
                        c = eqnlist[i]
                        if c.object_type == 'keyword':
                            self.findMatchingKeywords()
                            if c.match == i-1:
                                if c.value in self.special_delete_keywords1:
                                    c1 = eqnlist.pop(i)
                                    c2 = eqnlist.pop(i-1)
                                    del c1
                                    del c2
                                    self.equationListIndex = i - 1
                                    self.length -= 2
                                else:
                                    c2 = EquationReservedSpace(self)
                                    eqnlist.insert(i, c2)
                                    self.length += 1

                    #Only redraw equation and move cursor if there is something left to draw
                    if self.length > 0:
                        self.layoutEquation()
                        self.setCursorPosition()
                        self.equationNeedsParsing = True

        #Need this check here
        if self.length:
            self.checkForIgnoreInput()

    #Called from worksheet when user drags mouse over equation
    def setSelectionBox(self, item):
        eqnlist = self.equationList

        #Is item in equation?
        if item in eqnlist:
            #Determine range of characters selected
            i = eqnlist.index(item)
            if self.selectionStartIndex == -1:
                self.selectionStartIndex = i
                self.selectionRightIndex = i
                self.selectionLeftIndex = i
            elif i >= self.selectionStartIndex:
                self.selectionLeftIndex = self.selectionStartIndex
                self.selectionRightIndex = i
            elif i < self.selectionStartIndex:
                self.selectionLeftIndex = i
                self.selectionRightIndex = self.selectionStartIndex

            #start and end are indices of start and end of block of selected characters
            start = self.selectionLeftIndex
            end = self.selectionRightIndex

            #Was cursor dragged over a keyword? If so, then include everythang between
            #matching keywords in selected block.
            j = start - 1
            loopend = end
            while j < loopend:
                j += 1
                c = eqnlist[j]

                if c.object_type == 'keyword':
                    if c.selectEntireMathObject == True:
                        #Handle special cases, e.g. select entire divide or summation, etc
                        n1 = start
                        n2 = end
                        if c.value == Keyword.NUMEND or \
                           c.value == Keyword.ORDEREND:
                            n1 = c.match - 1
                            c = eqnlist[n1]
                            n2 = c.match
                        elif c.value == Keyword.DENOMSTART:
                            n2 = c.match + 1
                            c = eqnlist[n2]
                            n1 = c.match
                        elif c.value == Keyword.ROOTBODYSTART:
                            n2 = c.match + 1
                            c = eqnlist[n2]
                            n1 = c.match
                        elif c.value == Keyword.BODYSTART:
                            n1 = j - 2
                            n2 = c.match + 2
                        elif c.value == Keyword.BODYEND:
                            n1 = c.match - 2
                            n2 = j + 2
                        elif c.value == Keyword.SUMVARSTART:
                            n1 = j - 3
                            c = eqnlist[n1]
                            n2 = c.match
                        elif c.value == Keyword.SUMFROMVALSTART:
                            c = eqnlist[c.match + 1]
                            n1 = c.match - 2
                            c = eqnlist[n1]
                            n2 = c.match
                        elif c.value == Keyword.SUMTOSTART:
                            c = eqnlist[j-1]
                            n1 = c.match - 2
                            c = eqnlist[n1]
                            n2 = c.match
                        elif c.value == Keyword.SUMBODYSTART:
                            n2 = c.match + 2
                            c = eqnlist[n2]
                            n1 = c.match
                        elif c.value == Keyword.INTFROMSTART:
                            n1 = j - 2
                            c = eqnlist[n1]
                            n2 = c.match
                        elif c.value == Keyword.INTTOSTART:
                            c = eqnlist[j-1]
                            n1 = c.match - 2
                            c = eqnlist[n1]
                            n2 = c.match
                        elif c.value == Keyword.INTBODYSTART:
                            c = eqnlist[j-1]   # c=Keyword.INTTOEND
                            c = eqnlist[c.match-1]  # c=Keyword.INTFROMEND
                            n1 = c.match - 2
                            c = eqnlist[n1]
                            n2 = c.match
                        elif c.value == Keyword.INTVARSTART:
                            n2 = c.match + 1
                            c = eqnlist[n2]
                            n1 = c.match
                        elif c.value == Keyword.PROGRAMBODYSTART:
                            n1 = j - 2
                            c = eqnlist[n1] # PROGRAMSTART keyword
                            n2 = c.match    # PROGRAMEND keyword

                        #Check range of selected items is growing
                        if n1 < start:
                            start = n1
                        if n2 > end:
                            end = n2
                            j = end
                    else:
                        #Selected everythang between keywords
                        if c.match < start:
                            start = c.match
                        elif c.match > end:
                            end = c.match

            self.selectionLeftIndex = start
            self.selectionRightIndex = end

            #Create a rectangle around selected text from start to end (inclusive)
            self.createSelectionBox()

    def createSelectionBox(self):
        '''Creates a rectangle around selected text'''

        #Hide equation cursor when selection box is visible
        self.cursor.hide()

        start = self.selectionLeftIndex
        end = self.selectionRightIndex
        l, r, t, b = self.layoutengine.getSizeOfEquationPart(self.equationList[start:end+1])
        s = self.font.pointSize() * 0.1     # Add some spacing above and below box
        self.selectionBox.createBox([l, t-s, r, t-s, r, b+s, l, b+s])
        self.selectionBox.show()
        self.showSelectionBox = True

    def clearSelectionBox(self):
        self.selectionStartIndex = -1
        self.selectionRightIndex = -1
        self.selectionLeftIndex = -1
        self.showSelectionBox = False
        self.selectionBox.hide()

    def deleteSelectionBoxContents(self):
        #Remove old result
        self.deleteResult(True)

        #Remove highlighted object
        self.removeObjectsFromList(self.selectionLeftIndex, self.selectionRightIndex + 1)

        #Reset selection box stuff
        self.clearSelectionBox()

    def removeObjectsFromList(self, start, end):
        eqnlist = self.equationList
        self.length -= (end - start)
        self.equationListIndex = start

        for i in range(start, end):
            c = eqnlist.pop(start)

            if c.object_type == 'character':  # Handle chars
                if c.ascii_value == ':=':
                    self.isAssignment = False
                self.scene().removeItem(c)

            else:   #Handle certain keywords
                if c.ascii_value == Keyword.PROGRAMSTART:
                    self.hasProgram = False

            del c


    #********************************************************************************
    #Methods below are for loading and saving equation
    #********************************************************************************
    def getDictionary(self):
        #Create a dictionary containing variables that can be serialized
        d = {}

        #Create list. Each element is a dictionary representing a widget in equation
        saveList = []
        for c in self.equationList:
            saveList.append(c.getDict())
        d['saveList'] = saveList

        #Save various things
        d['savex'] = self.x()
        d['savey'] = self.y()

        #Save additional variables in this equation using magic
        #       l[0]   l[1]       l[2]     l[3]
        l = [   "d['",  '',  "'] = self.",  '']
        for k in self.save_variables:
            l[1] = k
            l[3] = k
            s = ''.join(l)
            exec(s)

        return d

    def setDictionary(self, eqn_dict):
        #Restore various variables in this instance of equation class
        x = eqn_dict['savex']
        y = eqn_dict['savey']
        self.setPos(x, y)

        l = ['self.', '', " = eqn_dict['", '', "']"]
        for k in self.save_variables:
            if eqn_dict.has_key(k):
                l[1] = k
                l[3] = k
                s = ''.join(l)
                exec(s)

        #Restore objects in self.equationList
        list_of_objects = eqn_dict['saveList']
        self.restoreEquationList(list_of_objects)

        #Draw the equation
        self.layoutEquation()

        #Restore other thangs
        self.setSelected(False)
        self.positionChanged = False

    def restoreEquationList(self, d):
        #Restore objects in self.equationList
        self.length += len(d)
        index = self.equationListIndex
        eqnlist = self.equationList

        for object_dict in d:

            #Recreate keyword object
            if object_dict['object_type'] == 'keyword':
                value = object_dict['value']
                c = Keyword(value)

            #Recreate regular character
            else:
                value = object_dict['value']
                ascii_value = object_dict['ascii_value']
                font = self.font

                if ascii_value == '__squareroot__':
                    c = EquationSquareRootLine(self)
                elif ascii_value == '__divideline__':
                    c = EquationDivideLine(self)
                elif ascii_value == '__leftsquarebracket__':
                    c = EquationSquareBracketLine(self, value = '__leftsquarebracket__')
                elif ascii_value == '__rightsquarebracket__':
                    c = EquationSquareBracketLine(self, value = '__rightsquarebracket__')
                elif ascii_value == '__verticalline__':
                    c = EquationVerticalLine(self)
                elif ascii_value == '__leftparenthesis__':
                    c = EquationParenthesis(self, '__leftparenthesis__')
                elif ascii_value == '__rightparenthesis__':
                    c = EquationParenthesis(self, '__rightparenthesis__')
                elif ascii_value == '__leftbrace__':
                    c = EquationBraces(self, '__leftbrace__')
                elif ascii_value == '__rightbrace__':
                    c = EquationBraces(self, '__rightbrace__')
                elif ascii_value == '__norm__':
                    c = EquationNormLines(self)
                elif ascii_value == '__reserved__':
                    c = EquationReservedSpace(self)
                elif ascii_value == '__transpose__':
                    c = EquationChar(self, 'T', '__transpose__', font)
                elif ascii_value == '__star__':
                    c = EquationChar(self, '*', '__star__', font)
                elif ascii_value == '__hermitian__':
                    c = EquationChar(self, self.hermitianChar, '__hermitian__', font)
                elif ascii_value == '__product__':
                    c = EquationChar(self, self.productChar, '__product__', font)
                elif ascii_value == '__summation__':
                    c = EquationChar(self, self.sumChar, '__summation__', font)
                elif ascii_value == '__dot__':
                    c = EquationChar(self, self.dotChar, '__dot__', font)
                elif ascii_value == '__overline__':
                    c = EquationOverLine(self)
                elif ascii_value == '__integral_top__':
                    c = EquationChar(self, u'\u2320', '__integral_top__', font)
                elif ascii_value == '__integral_bottom__':
                    c = EquationChar(self, u'\u2321', '__integral_bottom__', font)
                elif ascii_value == '__table__':
                    c = EquationTable(self, object_dict['data'], object_dict['numrows'], object_dict['numcols'], font)
                elif ascii_value == '__limit__':
                    c = EquationChar(self, 'lim', '__limit__', font)
                elif ascii_value == '__limitarrow__':
                    c = EquationChar(self, u'u\2192', '__limitarrow__', font)
                else:
                    c = EquationChar(self, value, ascii_value, font)

            #Restore object dictionary
            c.__dict__.update(object_dict)
            eqnlist.insert(index, c)
            index += 1

        self.equationListIndex = index

    #********************************************************************************
    #*Methods below this point handle the entry of various types of characters into
    #*the equation
    #********************************************************************************
    def addCharacter(self, value, ascii_value):
        #Add character only if cursor is visible
        if (self.cursor.isVisible() or self.showSelectionBox) and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList
            length = self.length

            #insert '_'
            if ascii_value == '_':
                #Prevent double underscore
                v1 = None
                v2 = None
                if i < length:
                    v1 = eqnlist[i].ascii_value
                if i > 0:
                    v2 = eqnlist[i-1].ascii_value
                if not v1 == '_' and not v2 == '_':
                    c = EquationChar(self, '_', '_', font)
                    eqnlist.insert(i, c)
                    self.equationListIndex += 1
                    self.length += 1

            #insert *
            elif ascii_value == '*':
                if length == 0:
                    self.insertCharPattern1(i, self.multiplySymbol, '*')
                else:
                    if i == 0:
                        if eqnlist[i].ascii_value in self.operatorSet:
                            self.insertCharPattern1(i, self.multiplySymbol, '*')
                        else:
                            self.insertCharPattern2(i, self.multiplySymbol, '*')
                    elif i == length:
                        if eqnlist[i-1].ascii_value in self.operatorSet:
                            self.insertCharPattern1(i, self.multiplySymbol, '*')
                        else:
                            self.insertCharPattern3(i, self.multiplySymbol, '*')
                    else:
                        t1 = eqnlist[i-1].ascii_value in self.operatorSet
                        t2 = eqnlist[i].ascii_value in self.operatorSet
                        if t1 and t2:
                            self.insertCharPattern1(i, self.multiplySymbol, '*')
                        elif t1:
                            self.insertCharPattern2(i, self.multiplySymbol, '*')
                        elif t2:
                            self.insertCharPattern3(i, self.multiplySymbol, '*')
                        else:
                            c = EquationChar(self, self.multiplySymbol, value, font)
                            eqnlist.insert(i, c)
                            self.equationListIndex += 1
                            self.length += 1

            #Insert +
            elif ascii_value == '+':
                if length == 0:
                    self.insertCharPattern1(i, ' + ', '+')
                else:
                    if i == 0:
                        if eqnlist[i].ascii_value in self.operatorSet:
                            self.insertCharPattern1(i, ' + ', '+')
                        else:
                            self.insertCharPattern2(i, ' + ', '+')
                    elif i == length:
                        if eqnlist[i-1].ascii_value in self.operatorSet:
                            self.insertCharPattern1(i, ' + ', '+')
                        else:
                            self.insertCharPattern3(i, ' + ', '+')
                    else:
                        t1 = eqnlist[i-1].ascii_value in self.operatorSet
                        t2 = eqnlist[i].ascii_value in self.operatorSet
                        if t1 and t2:
                            self.insertCharPattern1(i, ' + ', '+')
                        elif t1:
                            self.insertCharPattern2(i, ' + ', '+')
                        elif t2:
                            self.insertCharPattern3(i, ' + ', '+')
                        else:
                            c = EquationChar(self, ' + ', '+', font)
                            eqnlist.insert(i, c)
                            self.equationListIndex += 1
                            self.length += 1

            #Insert -
            elif ascii_value == '-':
                if length == 0:
                    self.insertCharPattern1(i, ' - ', '-')
                else:
                    if i == 0:
                        if eqnlist[i].ascii_value in self.operatorSet:
                            self.insertCharPattern1(i, ' - ', '-')
                        else:
                            self.insertCharPattern2(i, ' - ', '-')
                    elif i == length:
                        if eqnlist[i-1].ascii_value in self.operatorSet:
                            self.insertCharPattern1(i, ' - ', '-')
                        else:
                            self.insertCharPattern3(i, ' - ', '-')
                    else:
                        t1 = eqnlist[i-1].ascii_value in self.operatorSet
                        t2 = eqnlist[i].ascii_value in self.operatorSet
                        if t1 and t2:
                            self.insertCharPattern1(i, ' - ', '-')
                        elif t1:
                            self.insertCharPattern2(i, ' - ', '-')
                        elif t2:
                            self.insertCharPattern3(i, ' - ', '-')
                        else:
                            c = EquationChar(self, ' - ', '-', font)
                            eqnlist.insert(i, c)
                            self.equationListIndex += 1
                            self.length += 1

            elif ascii_value == ',':
                if self.showSelectionBox:
                    #Delete selected chars
                    i = self.selectionLeftIndex
                    self.deleteSelectionBoxContents()

                c = EquationChar(self, ', ', ',', font)

                eqnlist.insert(i, c)
                self.equationListIndex += 1
                self.length += 1

            #Insert a-z, A-Z, 0-9, special symbols (Greeks, etc)
            else:
                if self.showSelectionBox:
                    #Delete selected chars
                    i = self.selectionLeftIndex
                    self.deleteSelectionBoxContents()

                #t1=time.time()
                c = EquationChar(self, value, ascii_value, font)
                #t2=time.time()
                #print (t2-t1)*1000000

                eqnlist.insert(i, c)
                self.equationListIndex += 1
                self.length += 1

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def insertCharPattern1(self, i, v1, v2):
        c1 = EquationReservedSpace(self)
        c2 = EquationChar(self, v1, v2, self.font)
        c3 = EquationReservedSpace(self)
        insert = self.equationList.insert
        self.equationList[i: i] = [c1, c2, c3]

        self.equationListIndex += 1
        self.length += 3

    def insertCharPattern2(self, i, v1, v2):
        c1 = EquationReservedSpace(self)
        c2 = EquationChar(self, v1, v2, self.font)
        insert = self.equationList.insert
        insert(i, c1)
        insert(i+1, c2)
        self.equationListIndex += 1
        self.length += 2

    def insertCharPattern3(self, i, v1, v2):
        c1 = EquationChar(self, v1, v2, self.font)
        c2 = EquationReservedSpace(self)
        insert = self.equationList.insert
        insert(i, c1)
        insert(i+1, c2)
        self.equationListIndex += 2
        self.length += 2

    def deleteReservedCharacter(self):
        """If the current character under the editing cursor is a reserved space character
        (a square block) then remove character from list before inserting new characters"""
        i = self.equationListIndex
        eqnlist = self.equationList

        if i < self.length:
            c1 = eqnlist[i]
            if c1.ascii_value == '__reserved__':
                c1 = eqnlist.pop(i)
                self.scene().removeItem(c1)
                del c1
                self.length -= 1
            elif i > 0:
                c2 = eqnlist[i-1]
                if c2.ascii_value == '__reserved__':
                    c2 = eqnlist.pop(i-1)
                    self.scene().removeItem(c2)
                    del c2
                    self.length -= 1
                    self.equationListIndex -= 1
        elif self.length:
            c2 = eqnlist[i-1]
            if c2.ascii_value == '__reserved__':
                c2 = eqnlist.pop(i-1)
                self.scene().removeItem(c2)
                del c2
                self.length -= 1
                self.equationListIndex -= 1

    def addColon(self):
        #Add character only if cursor is visible
        if self.cursor.isVisible():
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList
            length = self.length

            #Allow colons inside indexes for slicing
            if self.testCursorBetweenKeywords(Keyword.INDEXSTART) != -1:
                #Allow colons in indices for slicing
                c = EquationChar(self, ':', ':', font)
                eqnlist.insert(i, c)
                self.equationListIndex += 1
                self.length += 1

                self.layoutEquation()
                self.setCursorPosition()
                self.equationNeedsParsing = True

            #elif (i == length or i == 0) and not self.isAssignment:
            elif self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:
                k = self.testCursorBetweenKeywords(Keyword.LINESTART)
                c = eqnlist[k]
                if c.programLineIsAssignment == False:
                    c.programLineIsAssignment = True
                    c1 = EquationChar(self, ':=', ':=', font)
                    c2 = EquationReservedSpace(self)
                    eqnlist.insert(i, c1)
                    eqnlist.insert(i+1, c2)

                    self.equationListIndex += 2
                    self.length += 2

                    self.layoutEquation()
                    self.setCursorPosition()
                    self.equationNeedsParsing = True

            elif not self.isAssignment:
                self.isAssignment = True  #Set flag
                c1 = EquationChar(self, ':=', ':=', font)
                c2 = EquationReservedSpace(self)
                eqnlist.insert(i, c1)
                eqnlist.insert(i+1, c2)

                if i == 0:
                    c3 = EquationReservedSpace(self)
                    eqnlist.insert(0, c3)
                    self.equationListIndex = 1
                    self.length += 3
                else:
                    self.equationListIndex += 2
                    self.length += 2

                self.layoutEquation()
                self.setCursorPosition()
                self.equationNeedsParsing = True

    def addTilde(self):
        #Add character only if cursor is visible
        if self.cursor.isVisible():
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList
            length = self.length

            #Can only put '=' sign at end of equation
            if i == length and not self.isAssignment:
                self.isAssignment = True  #Set flag
                self.isGlobalDefinition = True
                c1 = EquationChar(self, u':\u2261', ':=', font)
                c2 = EquationReservedSpace(self)
                eqnlist.insert(i, c1)
                eqnlist.insert(i+1, c2)

                if i == 0:
                    c3 = EquationReservedSpace(self)
                    eqnlist.insert(0, c3)
                    self.equationListIndex = 1
                    self.length += 3
                else:
                    self.equationListIndex += 2
                    self.length += 2

                self.layoutEquation()
                self.setCursorPosition()
                self.equationNeedsParsing = True

    def addEquality(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationChar(self, '=', '==', self.font)
            c1.setBold()
            eqnlist[i: i] = [c1]

            self.equationListIndex = i + 1
            self.length += 1
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addRange(self):
        #Add character only if cursor is visible
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            i = self.equationListIndex
            eqnlist = self.equationList
            length = self.length

            c1 = EquationReservedSpace(self)
            c2 = EquationChar(self, ' ... ', ';', self.font)
            c3 = EquationReservedSpace(self)
            eqnlist[i: i] = [c1, c2, c3]

            self.equationListIndex = i
            self.length += 3

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addSubSuperScript(self, v):
        #Add character only if cursor is visible
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            i = self.equationListIndex
            eqnlist = self.equationList
            length = self.length

            if v == 'superscript':
                c1 = Keyword(Keyword.SUPERSCRIPTSTART)
                c3 = Keyword(Keyword.SUPERSCRIPTEND)
            else:
                c1 = Keyword(Keyword.SUBSCRIPTSTART)
                c3 = Keyword(Keyword.SUBSCRIPTEND)

            c1.cursorLookRight = True
            c2 = EquationReservedSpace(self)
            eqnlist[i: i] = [c1, c2, c3]

            self.equationListIndex = i + 2
            self.length += 3

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addIndex(self):
        #Add character only if cursor is visible
        if self.cursor.isVisible() and not self.ignoreInput:
            got_subsup = False

            #Delete old result if it exists
            self.deleteResult(True)

            i = self.equationListIndex
            eqnlist = self.equationList
            cursor_right = 2

            #Add power after an index (if it exists), then wrap both with SUBSUPSTART,SUBSUPEND keywords
            if i < self.length and eqnlist[i].ascii_value == Keyword.POWERSTART:
                got_subsup = True

                c = eqnlist[i]
                c.cursorLeft = 2
                n = c.match + 2  # This is the index where the SUBSUPEND keyword below will be inserted

                cb = eqnlist[c.match]  #POWEREND keyword
                cb.cursorRight = 2

                c1 = Keyword(Keyword.SUBSUPSTART, cursorright=2)
                c2 = Keyword(Keyword.SUBSUPEND, cursorleft=2)
                eqnlist.insert(i, c1)
                eqnlist.insert(n, c2)
                self.length += 2
                i += 1  # Index where INDEXSTART will be inserted below

            elif i > 0 and eqnlist[i-1].ascii_value == Keyword.POWEREND:
                got_subsup = True

                c = eqnlist[i-1]
                c.cursorRight = 2
                n = c.match  #index of POWERSTART keyword

                cb = eqnlist[n]  #POWERSTART keyword
                cb.cursorLeft = 2

                c1 = Keyword(Keyword.SUBSUPSTART, cursorright=2)
                c2 = Keyword(Keyword.SUBSUPEND, cursorleft=2)
                eqnlist.insert(i, c2)
                eqnlist.insert(n, c1)
                self.length += 2
                i = n + 1  # Index where INDEXSTART will be inserted below

            #Add power after an index (if it exists), then wrap both with SUBSUPSTART,SUBSUPEND keywords
            elif i < self.length and eqnlist[i].ascii_value == Keyword.CONJUGATESTART:
                got_subsup = True
                cursor_right = 5

                c = eqnlist[i]
                n = c.match + 2  # This is the index where the SUBSUPEND keyword below will be inserted

                c1 = Keyword(Keyword.SUBSUPSTART, cursorright=2)
                c2 = Keyword(Keyword.SUBSUPEND, cursorleft=5)
                eqnlist.insert(i, c1)
                eqnlist.insert(n, c2)
                self.length += 2
                i += 1  # Index where INDEXSTART will be inserted below

            elif i > 0 and eqnlist[i-1].ascii_value == Keyword.CONJUGATEEND:
                got_subsup = True
                cursor_right = 5

                c = eqnlist[i-1]
                n = c.match  #index of POWERSTART keyword

                c1 = Keyword(Keyword.SUBSUPSTART, cursorright=2)
                c2 = Keyword(Keyword.SUBSUPEND, cursorleft=5)
                eqnlist.insert(i, c2)
                eqnlist.insert(n, c1)
                self.length += 2
                i = n + 1  # Index where INDEXSTART will be inserted below

            #If cursor is at a reserved space character then remove reserved character first
            #self.deleteReservedCharacter()

            c1 = Keyword(Keyword.INDEXSTART)
            c1.cursorLookRight = True
            c2 = EquationReservedSpace(self)
            c3 = Keyword(Keyword.INDEXEND)
            self.equationListIndex = i + 2
            if got_subsup:
                c1.cursorLeft = 2
                c3.cursorRight = cursor_right
            eqnlist[i: i] = [c1, c2, c3]
            self.length += 3

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addDivide(self):
        #Add character only if cursor is visible
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            i = self.equationListIndex
            eqnlist = self.equationList
            length = self.length

            c1 = Keyword(Keyword.DIVIDESTART, cursorright=2)
            c2 = Keyword(Keyword.NUMSTART, cursorleft=2)
            c2.cursorLookRight = True
            c3 = EquationReservedSpace(self)
            c4 = Keyword(Keyword.NUMEND, cursorright=3)
            c4.selectEntireMathObject = True
            c5 = EquationDivideLine(self)
            c6 = Keyword(Keyword.DENOMSTART, cursorleft=3)
            c6.selectEntireMathObject = True
            c6.cursorLookRight = True
            c7 = EquationReservedSpace(self)
            c8 = Keyword(Keyword.DENOMEND, cursorright=2)
            c9 = Keyword(Keyword.DIVIDEEND, cursorleft=2)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9]
            self.equationListIndex = i + 3
            self.length += 9

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

        elif self.showSelectionBox and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            length = self.length
            eqnlist = self.equationList
            i1 = self.selectionRightIndex + 1
            i2 = self.selectionLeftIndex

            c1 = Keyword(Keyword.DIVIDESTART, cursorright=2)
            c2 = Keyword(Keyword.NUMSTART, cursorleft=2)
            c2.cursorLookRight = True
            c3 = Keyword(Keyword.NUMEND, cursorright=3)
            c3.selectEntireMathObject = True
            c4 = EquationDivideLine(self)
            c5 = Keyword(Keyword.DENOMSTART, cursorleft=3)
            c5.selectEntireMathObject = True
            c5.cursorLookRight = True
            c6 = EquationReservedSpace(self)
            c7 = Keyword(Keyword.DENOMEND, cursorright=2)
            c8 = Keyword(Keyword.DIVIDEEND, cursorleft=2)

            #Insert right keyword first
            eqnlist[i1: i1] = [c3, c4, c5, c6, c7, c8]

            #Insert left keyword and squareroot symbol second
            eqnlist.insert(i2, c1)
            eqnlist.insert(i2+1, c2)

            self.equationListIndex = i1 + 6
            self.length += 8

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addLeftParen(self):
        #Add character only if cursor is visible
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            i = self.equationListIndex
            eqnlist = self.equationList
            length = self.length

            c1 = Keyword(Keyword.LEFTPAREN, cursorright=3)
            c2 = EquationParenthesis(self, '__leftparenthesis__')
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.BODYEND, cursorright=3)
            c5.selectEntireMathObject = True
            c6 = EquationParenthesis(self, '__rightparenthesis__')
            c7 = Keyword(Keyword.RIGHTPAREN, cursorleft=3)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7]

            self.equationListIndex = i + 4
            self.length += 7

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

        elif self.showSelectionBox and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            length = self.length
            eqnlist = self.equationList
            i1 = self.selectionRightIndex + 1
            i2 = self.selectionLeftIndex

            c1 = Keyword(Keyword.LEFTPAREN, cursorright=3)
            c2 = EquationParenthesis(self, '__leftparenthesis__')
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = Keyword(Keyword.BODYEND, cursorright=3)
            c4.selectEntireMathObject = True
            c5 = EquationParenthesis(self, '__rightparenthesis__')
            c6 = Keyword(Keyword.RIGHTPAREN, cursorleft=3)

            #Insert right keyword first
            eqnlist.insert(i1, c4)
            eqnlist.insert(i1+1, c5)
            eqnlist.insert(i1+2, c6)

            #Insert left keyword and squareroot symbol second
            eqnlist.insert(i2, c1)
            eqnlist.insert(i2+1, c2)
            eqnlist.insert(i2+2, c3)
            self.equationListIndex = i1 + 4
            self.length += 6

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addDifferentiate(self, higherorder=False):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = Keyword(Keyword.DIVIDESTART, cursorright=4)
            c2 = Keyword(Keyword.NUMSTART)
            c2.cursorLookRight = True
            c3 = EquationChar(self, 'd', '__calculusdee__', font)
            c3.cursorClickMoveRight = 2
            c3.cursorClickMoveLeft = -2
            c4 = Keyword(Keyword.DEESTART, cursorleft=4)
            c5 = EquationReservedSpace(self)
            c6 = Keyword(Keyword.DEEEND, cursorright=6)
            c7 = Keyword(Keyword.NUMEND)
            c8 = EquationDivideLine(self)
            c9 = Keyword(Keyword.DENOMSTART)
            c9.cursorLookRight = True
            c10 = EquationChar(self, 'd', '__calculusdee__', font)
            c10.cursorClickMoveRight = 2
            c10.cursorClickMoveLeft = -2
            c11 = Keyword(Keyword.DEESTART, cursorleft=6)
            c12 = EquationReservedSpace(self)
            c13 = Keyword(Keyword.DEEEND, cursorright=3)
            c14 = Keyword(Keyword.DENOMEND)
            c15 = Keyword(Keyword.DIVIDEEND, cursorleft=3)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15]

            if higherorder:
                print 'got nth order diff'
                #do stuff here

            self.equationListIndex = i + 5
            self.length += 15
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addLimit(self, lr):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = 0
            eqnlist = self.equationList

            c1 = Keyword(Keyword.LIMITSTART, cursorright=5)
            c2 = EquationChar(self, 'lim', '__limit__', font)
            c3 = EquationChar(self, u'\u2192', '__limitarrow__', font)
            if lr:
                c4 = EquationChar(self, ' + ', '+', font)
            else:
                c4 = EquationChar(self, ' - ', '-', font)
            c5 = Keyword(Keyword.BODYSTART, cursorleft=5)
            c6 = EquationReservedSpace(self)
            c7 = Keyword(Keyword.BODYEND, cursorright=2)
            c8 = Keyword(Keyword.BODYSTART, cursorleft=2)
            c9 = EquationReservedSpace(self)
            c10 = Keyword(Keyword.BODYEND, cursorright=3)
            c11 = EquationSpace(self)
            c12 = Keyword(Keyword.LIMITEND, cursorleft=3)
            c13 = EquationReservedSpace(self)

            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13]

            self.equationListIndex = i + 5
            self.length += 13
            self.forceSymbolic = True
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addCreateSymbol(self, sym_type=None):
        if not self.length:
            if sym_type == 'real':
                c1 = Keyword(Keyword.DEFINEREALSTART)
                c2 = EquationChar(self, "Real symbols:  ", "__real_symbol__", self.font)
                c6 = Keyword(Keyword.DEFINEREALEND)
            elif sym_type == 'integer':
                c1 = Keyword(Keyword.DEFINEINTEGERSTART)
                c2 = EquationChar(self, "Integer symbols:  ", "__integer_symbol__", self.font)
                c6 = Keyword(Keyword.DEFINEINTEGEREND)
            elif sym_type == 'complex':
                c1 = Keyword(Keyword.DEFINECOMPLEXSTART)
                c2 = EquationChar(self, "Complex symbols:  ", "__complex_symbol__", self.font)
                c6 = Keyword(Keyword.DEFINECOMPLEXEND)
            else:
                c1 = Keyword(Keyword.DEFINESYMBOLSTART)
                c2 = EquationChar(self, "Symbols:  ", "__symbol__", self.font)
                c6 = Keyword(Keyword.DEFINESYMBOLEND)

            c2.cursorClickMoveRight = 2
            c2.cursorClickMoveLeft = -2

            c3 = Keyword(Keyword.SYMBOLLISTSTART, cursorleft=0)
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.SYMBOLLISTEND, cursorright=0)
            self.equationList = [c1, c2, c3, c4, c5, c6]

            self.equationListIndex = 3
            self.length = 6
            self.isAssignment = True
            self.forceSymbolic = True

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addApostrophe(self):
        #Add character when equation is highlighted and cursor active. Put '=' sign at end of eqn only
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationChar(self, "'", "'", self.font)
            c2 = EquationReservedSpace(self)
            c3 = EquationChar(self, "'", "'", self.font)
            eqnlist[i: i] = [c1, c2, c3]

            self.equationListIndex += 1
            self.length += 3

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addSquareRoot(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            i = self.equationListIndex
            eqnlist = self.equationList
            c1 = Keyword(Keyword.SQUAREROOTSTART, cursorright=3)
            c2 = EquationSquareRootLine(self)
            c3 = Keyword(Keyword.ROOTBODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.ROOTBODYEND, cursorright=2)
            c6 = Keyword(Keyword.SQUAREROOTEND, cursorleft=2)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6]

            self.equationListIndex = i + 4
            self.length += 6
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

        elif self.showSelectionBox and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            c1 = Keyword(Keyword.SQUAREROOTSTART, cursorright=3)
            c2 = EquationSquareRootLine(self)
            c3 = Keyword(Keyword.ROOTBODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = Keyword(Keyword.ROOTBODYEND, cursorright=2)
            c5 = Keyword(Keyword.SQUAREROOTEND, cursorleft=2)


            eqnlist = self.equationList
            i1 = self.selectionRightIndex + 1
            i2 = self.selectionLeftIndex

            #Insert right keyword first
            eqnlist.insert(i1, c4)
            eqnlist.insert(i1+1, c5)

            #Insert left keyword and squareroot symbol second
            eqnlist.insert(i2, c1)
            eqnlist.insert(i2+1, c2)
            eqnlist.insert(i2+2, c3)

            self.equationListIndex = i1 + 3
            self.length += 5
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addOrderNRoot(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            i = self.equationListIndex
            eqnlist = self.equationList
            c1 = Keyword(Keyword.ORDERNROOTSTART, cursorright=2)
            c2 = Keyword(Keyword.ORDERSTART, cursorleft=2)
            c2.cursorLookRight = True
            c3 = EquationReservedSpace(self)
            c4 = Keyword(Keyword.ORDEREND, cursorright=3)
            c4.selectEntireMathObject = True
            c5 = EquationSquareRootLine(self)
            c6 = Keyword(Keyword.ROOTBODYSTART, cursorleft=3)
            c6.selectEntireMathObject = True
            c6.cursorLookRight = True
            c7 = EquationReservedSpace(self)
            c8 = Keyword(Keyword.ROOTBODYEND, cursorright=2)
            c9 = Keyword(Keyword.ORDERNROOTEND, cursorleft=2)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9]

            self.equationListIndex = i + 3
            self.length += 9
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

        elif self.showSelectionBox and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            c1 = Keyword(Keyword.ORDERNROOTSTART, cursorright=2)
            c2 = Keyword(Keyword.ORDERSTART, cursorleft=2)
            c2.cursorLookRight = True
            c3 = EquationReservedSpace(self)
            c4 = Keyword(Keyword.ORDEREND, cursorright=3)
            c4.selectEntireMathObject = True
            c5 = EquationSquareRootLine(self)
            c6 = Keyword(Keyword.ROOTBODYSTART, cursorleft=3)
            c6.selectEntireMathObject = True
            c6.cursorLookRight = True
            c7 = Keyword(Keyword.ROOTBODYEND, cursorright=2)
            c8 = Keyword(Keyword.ORDERNROOTEND, cursorright=1, cursorleft=1)

            eqnlist = self.equationList
            i1 = self.selectionRightIndex + 1
            i2 = self.selectionLeftIndex

            #Insert right keyword first
            eqnlist.insert(i1, c7)
            eqnlist.insert(i1+1, c8)

            #Insert left keyword and squareroot symbol second
            eqnlist.insert(i2, c1)
            eqnlist.insert(i2+1, c2)
            eqnlist.insert(i2+2, c3)
            eqnlist.insert(i2+3, c4)
            eqnlist.insert(i2+4, c5)
            eqnlist.insert(i2+5, c6)

            self.equationListIndex = i2 + 3
            self.length += 8
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addMatrix(self, rows, cols, t='matrix'):
        if self.cursor.isVisible() and not self.ignoreInput:

            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            j = i = self.equationListIndex
            eqnlist = self.equationList

            if t == 'matrix':
                c1 = Keyword(Keyword.MATRIXSTART, rows, cols, cursorright=4, cursorleft=1)
                c2 = EquationSquareBracketLine(self, value = '__leftsquarebracket__')
                c3 = EquationSquareBracketLine(self, value = '__rightsquarebracket__')
                c3.cursorClickMoveRight = 2
                c3.cursorClickMoveLeft = 2
                c4 = Keyword(Keyword.MATRIXEND, cursorleft=4)
            elif t == 'array':
                c1 = Keyword(Keyword.ARRAYSTART, rows, cols, cursorright=4, cursorleft=1)
                c2 = EquationParenthesis(self, value = '__leftparenthesis__')
                c2.cursorClickMoveRight = 3
                c2.cursorClickMoveLeft = 1
                c3 = EquationParenthesis(self, value = '__rightparenthesis__')
                c3.cursorClickMoveRight = 2
                c3.cursorClickMoveLeft = 2
                c4 = Keyword(Keyword.ARRAYEND, cursorleft=4)

            eqnlist.insert(j, c1)
            eqnlist.insert(j+1, c2)

            j += 2
            key_row_start = Keyword(Keyword.ROWSTART)
            key_row_end = Keyword(Keyword.ROWEND)
            key_element_start = Keyword(Keyword.ELEMENTSTART, cursorleft=2)
            key_element_start.cursorLookRight = True
            key_element_end = Keyword(Keyword.ELEMENTEND, cursorright=2)

            #Loop to create empty matrix
            for r in range(rows):
                key_element_start.row = r
                key_row_start.row = r   # Used to help locate cursor inside matrix
                eqnlist.insert(j, copy.copy(key_row_start))
                j += 1
                for c in range(cols):
                    key_element_start.col = c   # Used to help locate cursor inside matrix
                    c5 = EquationReservedSpace(self)
                    eqnlist.insert(j, copy.copy(key_element_start))
                    eqnlist.insert(j+1, c5)
                    eqnlist.insert(j+2, copy.copy(key_element_end))
                    j += 3
                eqnlist.insert(j, copy.copy(key_row_end))
                j += 1

            eqnlist.insert(j, c3)
            eqnlist.insert(j+1, c4)

            self.equationListIndex = i + 5
            mat_size = rows * cols * 3 + 4 + 2 * rows
            self.length += mat_size
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addProductSummation(self, s):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            if s == 'sum':
                c1 = Keyword(Keyword.SUMSTART, cursorright=4)
                c2 = EquationChar(self, self.sumChar, '__summation__', font)
                c2.cursorClickMoveRight = -1
                c2.cursorClickMoveLeft = 1
                c19 = Keyword(Keyword.SUMEND, cursorleft=3)
            elif s == 'product':
                c1 = Keyword(Keyword.PRODUCTSTART, cursorright=4)
                c2 = EquationChar(self, self.productChar, '__product__', font)
                c2.cursorClickMoveRight = -1
                c2.cursorClickMoveLeft = 1
                c19 = Keyword(Keyword.PRODUCTEND, cursorleft=3)
            c3 = Keyword(Keyword.FROMSTART)
            c4 = Keyword(Keyword.SUMVARSTART, cursorleft=4)
            c4.selectEntireMathObject = True
            c5 = EquationReservedSpace(self)
            c6 = Keyword(Keyword.SUMVAREND, cursorright=3)
            c7 = EquationChar(self, '=', ':=', font)
            c8 = Keyword(Keyword.SUMFROMVALSTART, cursorleft=3)
            c8.selectEntireMathObject = True
            c8.cursorLookRight = True
            c9 = EquationReservedSpace(self)
            c10 = Keyword(Keyword.SUMFROMVALEND, cursorright=3)
            c11 = Keyword(Keyword.FROMEND)
            c12 = Keyword(Keyword.SUMTOSTART, cursorleft=3)
            c12.selectEntireMathObject = True
            c12.cursorLookRight = True
            c13 = EquationReservedSpace(self)
            c14 = Keyword(Keyword.SUMTOEND, cursorright=2)
            c15 = Keyword(Keyword.SUMBODYSTART, cursorleft=2)
            c15.selectEntireMathObject = True
            c15.cursorLookRight = True
            c16 = EquationReservedSpace(self)
            c17 = Keyword(Keyword.SUMBODYEND,  cursorright=3)
            c18 = EquationSpace(self)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17, c18, c19]

            self.equationListIndex = i + 5
            self.length += 19
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addRangeProductSummation(self, s):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            if s == 'sum':
                c1 = Keyword(Keyword.RANGESUMSTART, cursorright=3)
                c2 = EquationChar(self, self.sumChar, '__summation__', font)
                c2.cursorClickMoveRight = -1
                c2.cursorClickMoveLeft = 1
                c9 = Keyword(Keyword.RANGESUMEND, cursorleft=2)
            elif s == 'product':
                c1 = Keyword(Keyword.RANGEPRODUCTSTART, cursorright=3)
                c2 = EquationChar(self, self.productChar, '__product__', font)
                c2.cursorClickMoveRight = -1
                c2.cursorClickMoveLeft = 1
                c9 = Keyword(Keyword.RANGEPRODUCTEND, cursorleft=2)
            c3 = Keyword(Keyword.FROMSTART, cursorleft=3)
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.FROMEND, cursorright=2)
            c6 = Keyword(Keyword.BODYSTART, cursorleft=2)
            c6.cursorLookRight = True
            c7 = EquationReservedSpace(self)
            c8 = Keyword(Keyword.BODYEND, cursorright=2)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9]

            self.equationListIndex = i + 4
            self.length += 9
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addDeterminant(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()
            i = self.equationListIndex
            eqnlist = self.equationList
            c1 = Keyword(Keyword.DETERMINANTSTART, cursorright=3)
            c2 = EquationVerticalLine(self)
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.BODYEND, cursorright=3)
            c5.selectEntireMathObject = True
            c6 = EquationVerticalLine(self)
            c7 = Keyword(Keyword.DETERMINANTEND, cursorleft=3)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7]

            self.equationListIndex = i + 4
            self.length += 7
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

        elif self.showSelectionBox and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            c1 = Keyword(Keyword.DETERMINANTSTART, cursorright=3)
            c2 = EquationVerticalLine(self)
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = Keyword(Keyword.BODYEND, cursorright=3)
            c4.selectEntireMathObject = True
            c5 = EquationVerticalLine(self)
            c6 = Keyword(Keyword.DETERMINANTEND, cursorleft=3)

            eqnlist = self.equationList
            i1 = self.selectionRightIndex + 1
            i2 = self.selectionLeftIndex

            eqnlist.insert(i1, c4)
            eqnlist.insert(i1+1, c5)
            eqnlist.insert(i1+2, c6)
            eqnlist.insert(i2, c1)
            eqnlist.insert(i2+1, c2)
            eqnlist.insert(i1+2, c3)

            self.equationListIndex = i1 + 4
            self.length += 6
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addNorm(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()
            i = self.equationListIndex
            eqnlist = self.equationList
            c1 = Keyword(Keyword.NORMSTART, cursorright=3)
            c2 = EquationNormLines(self)
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.BODYEND, cursorright=3)
            c5.selectEntireMathObject = True
            c6 = EquationNormLines(self)
            c7 = Keyword(Keyword.NORMEND, cursorleft=3)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7]

            self.equationListIndex = i + 4
            self.length += 7
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

        elif self.showSelectionBox and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            c1 = Keyword(Keyword.NORMSTART, cursorright=3)
            c2 = EquationNormLines(self)
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.cursorLookRight = True
            c3.selectEntireMathObject = True
            c4 = Keyword(Keyword.BODYEND, cursorright=3)
            c4.selectEntireMathObject = True
            c5 = EquationNormLines(self)
            c6 = Keyword(Keyword.NORMEND, cursorleft=3)

            eqnlist = self.equationList
            i1 = self.selectionRightIndex + 1
            i2 = self.selectionLeftIndex

            eqnlist.insert(i1, c4)
            eqnlist.insert(i1+1, c5)
            eqnlist.insert(i1+2, c6)
            eqnlist.insert(i2, c1)
            eqnlist.insert(i2+1, c2)
            eqnlist.insert(i1+2, c3)

            self.equationListIndex = i1 + 4
            self.length += 6
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addTranspose(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            if i == 0:
                c1 = EquationReservedSpace(self)
                c2 = Keyword(Keyword.TRANSPOSESTART, cursorright=1)
                c3 = EquationChar(self, 'T', '__transpose__', font)
                c3.cursorClickMoveRight = 2
                c3.cursorClickMoveLeft = 1
                c3.setNormal()
                c4 = Keyword(Keyword.TRANSPOSEEND, cursorleft=1)
                eqnlist[i: i] = [c1, c2, c3, c4]
                self.equationListIndex = i + 1
                self.length += 4
            else:
                c1 = Keyword(Keyword.TRANSPOSESTART, cursorright=1)
                c2 = EquationChar(self, 'T', '__transpose__', font)
                c2.cursorClickMoveRight = 2
                c2.cursorClickMoveLeft = 1
                c2.setNormal()
                c3 = Keyword(Keyword.TRANSPOSEEND, cursorleft=1)
                eqnlist[i: i] = [c1, c2, c3]
                self.equationListIndex = i + 3
                self.length += 3

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addConjugate(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            got_subsup = False

            #Delete old result if it exists
            self.deleteResult(True)

            i = self.equationListIndex
            eqnlist = self.equationList

            #Are we conjugating an indexed variable?
            if i < self.length and eqnlist[i].ascii_value == Keyword.INDEXSTART:
                got_subsup = True
                c = eqnlist[i]
                c.cursorLeft = 2
                n = c.match + 2  # This is the index where the CONJUGATESTART keyword below will be inserted
                cursor_index = n + 4

                cb = eqnlist[c.match]   # INDEXEND end keyword
                cb.cursorRight = 5

                c1 = Keyword(Keyword.SUBSUPSTART, cursorright=2)
                c2 = Keyword(Keyword.SUBSUPEND, cursorleft=5)
                eqnlist.insert(i, c1)
                eqnlist.insert(n, c2)
                self.length += 2
                i = n  # Index where conjugate will be inserted below

            elif i > 0 and eqnlist[i-1].ascii_value == Keyword.INDEXEND:
                got_subsup = True
                c = eqnlist[i-1]
                c.cursorRight = 5
                n = c.match  #index of indexstart keyword
                cursor_index = i + 5

                cb = eqnlist[n]
                cb.cursorLeft = 2

                c1 = Keyword(Keyword.SUBSUPSTART, cursorright=2)
                c2 = Keyword(Keyword.SUBSUPEND, cursorleft=5)
                eqnlist.insert(i, c2)
                eqnlist.insert(n, c1)
                self.length += 2
                i += 1  # Index where conjugate will be inserted below

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font

            if i == 0:
                c1 = EquationReservedSpace(self)
                c2 = Keyword(Keyword.CONJUGATESTART, cursorright=3)
                c3 = EquationChar(self, '*', '__star__', font)
                c3.cursorClickMoveRight = 2
                c3.cursorClickMoveLeft = 1
                c3.setNormal()
                c4 = Keyword(Keyword.CONJUGATEEND, cursorleft=3)
                if got_subsup:
                    c2.cursorLeft = 2
                    c4.cursorRight = 2
                eqnlist[i: i] = [c1, c2, c3, c4]
                self.equationListIndex = 1
                self.length += 4

            else:
                c1 = Keyword(Keyword.CONJUGATESTART, cursorright=3)
                c2 = EquationChar(self, '*', '__star__', font)
                c2.cursorClickMoveRight = 2
                c2.cursorClickMoveLeft = 1
                c2.setNormal()
                c3 = Keyword(Keyword.CONJUGATEEND, cursorleft=3)
                self.equationListIndex = i + 3
                if got_subsup:
                    c1.cursorLeft = 2
                    c3.cursorRight = 2
                    self.equationListIndex = cursor_index
                eqnlist[i: i] = [c1, c2, c3]
                self.length += 3

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addHermitian(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            if i == 0:
                c1 = EquationReservedSpace(self)
                c2 = Keyword(Keyword.HERMITIANSTART, cursorright=3)
                c3 = EquationChar(self, self.hermitianChar, '__hermitian__', font)
                c3.cursorClickMoveRight = 2
                c3.cursorClickMoveLeft = 1
                c3.setNormal()
                c4 = Keyword(Keyword.HERMITIANEND, cursorleft=3)
                eqnlist[i: i] = [c1, c2, c3, c4]
                self.equationListIndex = i + 1
                self.length += 4
            else:
                c1 = Keyword(Keyword.HERMITIANSTART, cursorright=3)
                c2 = EquationChar(self, self.hermitianChar, '__hermitian__', font)
                c2.cursorClickMoveRight = 2
                c2.cursorClickMoveLeft = 1
                c2.setNormal()
                c3 = Keyword(Keyword.HERMITIANEND, cursorleft=3)
                eqnlist[i: i] = [c1, c2, c3]
                self.equationListIndex = i + 3
                self.length += 3

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addDotProduct(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = Keyword(Keyword.DOTPRODUCTSTART, cursorright=3)
            c2 = EquationChar(self, self.dotChar, '__dot__', self.font)
            c2.cursorClickMoveRight = 2
            c2.cursorClickMoveLeft = 1
            c3 = Keyword(Keyword.DOTPRODUCTEND, cursorleft=3)
            eqnlist[i: i] = [c1, c2, c3]

            self.equationListIndex = i + 3
            self.length += 3
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addMatrixSum(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = Keyword(Keyword.MATRIXSUMSTART, cursorright=3)
            c2 = EquationChar(self, self.sumChar, '__summation__', self.font)
            c3 = Keyword(Keyword.BODYSTART, cursorleft=2)
            c3.cursorLookRight = True
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.BODYEND, cursorright=2)
            c6 = Keyword(Keyword.MATRIXSUMEND, cursorleft=2)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6]

            self.equationListIndex = i + 4
            self.length += 6
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addMeanAverage(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = Keyword(Keyword.AVERAGESTART, cursorright=3)
            c2 = EquationOverLine(self)
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.BODYEND, cursorright=2)
            c6 = Keyword(Keyword.AVERAGEEND, cursorleft=2)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6]

            self.equationListIndex = i + 4
            self.length += 6
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addVectorize(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = Keyword(Keyword.VECTORIZESTART, cursorright=3)
            c2 = EquationArrowLine(self)
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.BODYEND, cursorright=2)
            c6 = Keyword(Keyword.VECTORIZEEND, cursorleft=2)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6]

            self.equationListIndex = i + 4
            self.length += 6
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addConvolution(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationReservedSpace(self)
            c2 = Keyword(Keyword.CONVOLVESTART, cursorright=3)
            c3 = EquationChar(self, '*', '__star__', self.font)
            c3.cursorClickMoveRight = 2
            c3.cursorClickMoveLeft = 1
            c4 = Keyword(Keyword.CONVOLVEEND, cursorleft=3)
            c5 = EquationReservedSpace(self)

            eqnlist[i: i] = [c1, c2, c3, c4, c5]

            self.equationListIndex = i
            self.length += 5
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addFloorCeil(self, t):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()
            i = self.equationListIndex
            eqnlist = self.equationList

            if t == 'floor':
                c1 = Keyword(Keyword.FLOORSTART, cursorright=3)
                c2 = EquationSquareBracketLine(self, value='__floorleft__')
                c6 = EquationSquareBracketLine(self, value='__floorright__')
                c7 = Keyword(Keyword.FLOOREND, cursorleft=3)
            else:
                c1 = Keyword(Keyword.CEILSTART, cursorright=3)
                c2 = EquationSquareBracketLine(self, value='__ceilleft__')
                c6 = EquationSquareBracketLine(self, value='__ceilright__')
                c7 = Keyword(Keyword.CEILEND, cursorleft=3)

            c2.cursorClickMoveRight = 1
            c2.cursorClickMoveLeft = 2
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.BODYEND, cursorright=3)
            c6.cursorClickMoveRight = 1
            c6.cursorClickMoveLeft = 2

            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7]

            self.equationListIndex = i + 3
            self.length += 7
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addAbsolute(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()
            i = self.equationListIndex
            eqnlist = self.equationList
            c1 = Keyword(Keyword.ABSOLUTESTART, cursorright=3)
            c2 = EquationVerticalLine(self)
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.BODYEND, cursorright=3)
            c5.selectEntireMathObject = True
            c6 = EquationVerticalLine(self)
            c7 = Keyword(Keyword.ABSOLUTEEND, cursorleft=3)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7]

            self.equationListIndex = i + 4
            self.length += 7
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

        elif self.showSelectionBox and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            length = self.length
            eqnlist = self.equationList
            i1 = self.selectionRightIndex + 1
            i2 = self.selectionLeftIndex

            c1 = Keyword(Keyword.ABSOLUTESTART, cursorright=3)
            c2 = EquationVerticalLine(self)
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = Keyword(Keyword.BODYEND, cursorright=3)
            c4.selectEntireMathObject = True
            c5 = EquationVerticalLine(self)
            c6 = Keyword(Keyword.ABSOLUTEEND, cursorleft=3)

            #Insert right keyword first
            eqnlist.insert(i1, c4)
            eqnlist.insert(i1+1, c5)
            eqnlist.insert(i1+2, c6)

            #Insert left keyword and squareroot symbol second
            eqnlist.insert(i2, c1)
            eqnlist.insert(i2+1, c2)
            eqnlist.insert(i2+2, c3)

            self.equationListIndex = i1 + 4
            self.length += 6
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addPower(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            got_subsup = False

            #Delete old result if it exists
            self.deleteResult(True)

            i = self.equationListIndex
            eqnlist = self.equationList

            #Add power after an index (if it exists), then wrap both with SUBSUPSTART,SUBSUPEND keywords
            if i < self.length and eqnlist[i].ascii_value == Keyword.INDEXSTART:
                got_subsup = True
                c = eqnlist[i]
                c.cursorLeft = 2
                n = c.match + 2  # This is the index where the POWERSTART keyword below will be inserted

                cb = eqnlist[c.match]
                cb.cursorRight = 2

                c1 = Keyword(Keyword.SUBSUPSTART, cursorright=2)
                c2 = Keyword(Keyword.SUBSUPEND, cursorleft=2)
                eqnlist.insert(i, c1)
                eqnlist.insert(n, c2)
                self.length += 2
                i = n  # Index where power will be inserted below

            elif i > 0 and eqnlist[i-1].ascii_value == Keyword.INDEXEND:
                got_subsup = True
                c = eqnlist[i-1]
                c.cursorRight = 2
                n = c.match  #index of indexstart keyword

                cb = eqnlist[n]
                cb.cursorLeft = 2

                c1 = Keyword(Keyword.SUBSUPSTART, cursorright=2)
                c2 = Keyword(Keyword.SUBSUPEND, cursorleft=2)
                eqnlist.insert(i, c2)
                eqnlist.insert(n, c1)
                self.length += 2
                i += 1  # Index where power will be inserted below

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            c1 = Keyword(Keyword.POWERSTART)
            c1.cursorLookRight = True
            c2 = EquationReservedSpace(self)
            c3 = Keyword(Keyword.POWEREND)
            if got_subsup:
                c1.cursorLeft = 2
                c3.cursorRight = 2
            eqnlist.insert(i, c1)
            eqnlist.insert(i+1, c2)
            eqnlist.insert(i+2, c3)
            self.equationListIndex = i + 2
            self.length += 3

            if i == 0:
                c1 = EquationReservedSpace(self)
                eqnlist.insert(0, c1)
                self.equationListIndex = 0
                self.length += 1
            elif i > 0:
                c = eqnlist[i-1]
                s = self.alphaSymbols
                s = s.union(self.numSymbols)
                s = s.union(self.specialSymbols)
                k = set([Keyword.RIGHTPAREN,  Keyword.MATRIXEND, Keyword.INDEXEND])
                s = s.union(k)

                if c.ascii_value not in s:
                    c1 = EquationReservedSpace(self)
                    eqnlist.insert(i, c1)
                    self.equationListIndex = i
                    self.length += 1

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addSubstitution(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = Keyword(Keyword.SUBSTITUTIONSTART, cursorright=3)

            c2 = EquationSquareBracketLine(self)
            c2.cursorClickMoveRight = 2
            c2.cursorClickMoveLeft = 1
            c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c3.selectEntireMathObject = True
            c3.cursorLookRight = True
            c4 = EquationReservedSpace(self)
            c5 = Keyword(Keyword.BODYEND, cursorright=3)
            c5.selectEntireMathObject = True
            c6 = EquationSquareBracketLine(self, value='__rightsquarebracket__')
            c6.cursorClickMoveRight = 2
            c6.cursorClickMoveLeft = 1

            c7 = Keyword(Keyword.BODYSTART, cursorleft=3)
            c7.selectEntireMathObject = True
            c7.cursorLookRight = True
            c8 = EquationReservedSpace(self)
            c9 = Keyword(Keyword.BODYEND, cursorright=2)
            c9.selectEntireMathObject = True

            c10 = Keyword(Keyword.SUBSTITUTIONEND, cursorleft=2)

            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10]

            self.equationListIndex = i + 3
            self.length += 10
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addDefiniteIntegral(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = Keyword(Keyword.INTEGRALSTART, cursorright=4)
            c2 = EquationChar(self, u'\u2320', '__integral_top__', font)
            c2.cursorClickMoveRight = -1
            c2.cursorClickMoveLeft = 1
            c3 = EquationChar(self, u'\u2321', '__integral_bottom__', font)
            c3.cursorClickMoveRight = -2
            c3.cursorClickMoveLeft = 2
            c4 = Keyword(Keyword.INTFROMSTART, cursorleft=4)
            c4.selectEntireMathObject = True
            c5 = EquationReservedSpace(self)
            c6 = Keyword(Keyword.INTFROMEND, cursorright=2)
            c7 = Keyword(Keyword.INTTOSTART, cursorleft=2)
            c7.selectEntireMathObject = True
            c8 = EquationReservedSpace(self)
            c9 = Keyword(Keyword.INTTOEND, cursorright=2)
            c10 = Keyword(Keyword.INTBODYSTART, cursorleft=2)
            c10.selectEntireMathObject = True
            c11 = EquationReservedSpace(self)
            c12 = Keyword(Keyword.INTBODYEND, cursorright=3)
            c13 = EquationChar(self, 'd', '__calculusdee__', font)
            c13.cursorClickMoveRight = 2
            c13.cursorClickMoveLeft = 1
            c13.setFlag(QGraphicsItem.ItemIsSelectable, False)
            c14 = Keyword(Keyword.INTVARSTART, cursorleft=3)
            c14.selectEntireMathObject = True
            c15 = EquationReservedSpace(self)
            c16 = Keyword(Keyword.INTVAREND, cursorright=3)
            c17 = EquationSpace(self)
            c17.cursorClickMoveRight = 2
            c17.cursorClickMoveLeft = 1
            c18 = Keyword(Keyword.INTEGRALEND, cursorleft=3)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12, c13, c14, c15, c16, c17, c18]
            self.equationListIndex = i + 4
            self.length += 18
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addIndefiniteIntegral(self):
        if self.cursor.isVisible() and not self.ignoreInput:
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = Keyword(Keyword.INDEFINTEGRALSTART, cursorright=4)
            c2 = EquationChar(self, u'\u2320', '__integral_top__', font)
            c2.cursorClickMoveRight = 3
            c2.cursorClickMoveLeft = 1
            c3 = EquationChar(self, u'\u2321', '__integral_bottom__', font)
            c3.cursorClickMoveRight = 2
            c3.cursorClickMoveLeft = 2
            c4 = Keyword(Keyword.INTBODYSTART, cursorleft=4)
            c4.selectEntireMathObject = True
            c5 = EquationReservedSpace(self)
            c6 = Keyword(Keyword.INTBODYEND, cursorright=3)
            c7 = EquationChar(self, 'd', '__calculusdee__', font)
            c7.cursorClickMoveRight = 2
            c7.cursorClickMoveLeft = 1
            c7.setFlag(QGraphicsItem.ItemIsSelectable, False)
            c8 = Keyword(Keyword.INTVARSTART, cursorleft=3)
            c8.selectEntireMathObject = True
            c9 = EquationReservedSpace(self)
            c10 = Keyword(Keyword.INTVAREND, cursorright=3)
            c11 = EquationSpace(self)
            c12 = Keyword(Keyword.INDEFINTEGRALEND, cursorleft=3)
            eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11, c12]
            self.equationListIndex = i + 4
            self.length += 12
            self.forceSymbolic = True
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addNewLine(self):
        if self.cursor.isVisible() and not self.ignoreInput:

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            #Are we adding a single new line, or starting a new program block?
            m = self.testCursorBetweenKeywords(Keyword.LINESTART)
            if  m != -1:
                c1 = Keyword(Keyword.LINESTART)
                c1.cursorLookRight = True
                c2 = EquationReservedSpace(self)
                c3 = Keyword(Keyword.LINEEND)

                c = eqnlist[m] #LINESTART Keyword
                n = c.match    #Index of LINEEND keyword

                eqnlist[n+1: n+1] = [c1, c2, c3]

                self.equationListIndex = n + 2
                self.length += 3

                self.layoutEquation()
                self.setCursorPosition()
                self.equationNeedsParsing = True

            #Only allow insertion of a new program at certain locations in program, e.g. at end of line
            #Equations can be either:
            # x:=program
            # f(x):=program
            # or just a stand alone program
            elif (i == 0 and self.length == 0) or \
                 (self.length >= 2 and i == self.length-1 and \
                  eqnlist[i].ascii_value == '__reserved__' and eqnlist[i-1].ascii_value == ':=')  or \
                 (self.length >= 2 and i == self.length and \
                  eqnlist[i-1].ascii_value == '__reserved__' and eqnlist[i-2].ascii_value == ':=')  or \
                 (self.length >= 1 and i == self.length and eqnlist[i-1].ascii_value == ':='):

                #If cursor is at a reserved space character then remove reserved character first
                self.deleteReservedCharacter()

                self.hasProgram = True

                c1 = Keyword(Keyword.PROGRAMSTART, cursorright=4)
                c2 = EquationProgramLine(self)
                c3 = Keyword(Keyword.PROGRAMBODYSTART)
                c3.selectEntireMathObject = True
                c4 = Keyword(Keyword.LINESTART)
                c4.cursorLookRight = True
                c5 = EquationReservedSpace(self)
                c6 = Keyword(Keyword.LINEEND)
                c7 = Keyword(Keyword.LINESTART)
                c7.cursorLookRight = True
                c8 = EquationReservedSpace(self)
                c9 = Keyword(Keyword.LINEEND)
                c10 = Keyword(Keyword.PROGRAMBODYEND)
                c11 = Keyword(Keyword.PROGRAMEND, cursorleft=3)
                eqnlist[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9, c10, c11]
                self.equationListIndex = i + 4
                self.length += 11

                self.layoutEquation()
                self.setCursorPosition()
                self.equationNeedsParsing = True

    def addSpace(self):
        line_start_index = self.testCursorBetweenKeywords(Keyword.LINESTART)
        if line_start_index != -1 and self.cursor.isVisible():  #Only allow inside a program
            i = self.equationListIndex
            eqnlist = self.equationList
            font = self.font

            c = eqnlist[i-1]
            if c.value == Keyword.LINESTART or c.value == '    ':
                c1 = EquationChar(self, '    ', '    ', self.font)
                self.equationList.insert(i, c1)
                self.equationListIndex = i + 1
                self.length += 1
                self.layoutEquation()
                self.setCursorPosition()
                self.equationNeedsParsing = True

    def addIf(self):
        if self.cursor.isVisible() and self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:  # Only allow inside a program
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationChar(self, 'if ', 'if ', self.font)
            c2 = EquationReservedSpace(self)

            eqnlist[i: i] = [c1, c2]

            self.equationListIndex = i + 2
            self.length += 2
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addElse(self):
        if self.cursor.isVisible() and self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:  # Only allow inside a program
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationChar(self, 'else', 'else', self.font)

            eqnlist[i: i] = [c1]

            self.equationListIndex = i + 1
            self.length += 1
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addElif(self):
        if self.cursor.isVisible() and self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:  # Only allow inside a program
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationChar(self, 'elif ', 'elif ', self.font)
            c2 = EquationReservedSpace(self)

            eqnlist[i: i] = [c1, c2]

            self.equationListIndex = i + 2
            self.length += 2
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addFor(self):
        if self.cursor.isVisible() and self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:  # Only allow inside a program
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationChar(self, 'for ', 'for ', self.font)
            c2 = EquationReservedSpace(self)
            c3 = EquationChar(self, ' in ', ' in ', self.font)
            c4 = EquationReservedSpace(self)

            eqnlist[i:i] = [c1, c2, c3, c4]

            self.equationListIndex = i + 1
            self.length += 4
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addWhile(self):
        if self.cursor.isVisible() and self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:  # Only allow inside a program
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationChar(self, 'while ', 'while ', self.font)
            c2 = EquationReservedSpace(self)

            eqnlist[i:i] = [c1, c2]

            self.equationListIndex = i + 2
            self.length += 2
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addContinue(self):
        if self.cursor.isVisible() and self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:  # Only allow inside a program
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationChar(self, 'continue', 'continue', self.font)

            eqnlist[i: i] = [c1]

            self.equationListIndex = i + 1
            self.length += 1
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addBreak(self):
        if self.cursor.isVisible() and self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:  # Only allow inside a program
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationChar(self, 'break', 'break', self.font)

            eqnlist[i:i] = [c1]

            self.equationListIndex = i + 1
            self.length += 1
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addReturn(self):
        if self.cursor.isVisible() and self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:  # Only allow inside a program
            #Delete old result if it exists
            self.deleteResult(True)

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList

            c1 = EquationChar(self, 'return ', 'return ', self.font)
            c2 = EquationReservedSpace(self)

            eqnlist[i:i] = [c1, c2]

            self.equationListIndex = i + 2
            self.length += 2
            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True


    #**********************************************************************************
    #*Methods below this point handle the actual drawing of the equation on the screen
    #**********************************************************************************
    def layoutEquation(self):
        '''This is the top level entry point for drawing an equation'''
        #Look for functions and variables, set variables italic
        #self.adjustFonts()

        #Unselect any equations
        self.clearSelectionBox()

        eqnlist = self.equationList

        #Loop to find all matching pairs of keywords
        self.findMatchingKeywords()

        #This is where the fun starts. Use recursion to draw various parts of equation
        left, right, top, bottom = self.layoutengine.layoutEquationPart(eqnlist, 0, len(eqnlist), self.font.pointSize())

        #Figure out new size of equation
        self.width = w = right - left
        self.top = top
        self.bottom = bottom
        self.height = bottom - top

        #Resize path used to draw bounding rectangle
        self.updateBoundingRect()

    def findMatchingKeywords(self):
        eqnlist = self.equationList
        index = self.equationListIndex
        stack = []

        #Look for keywords
        for i, c in enumerate(eqnlist):
            if c.object_type == 'keyword':

                #Stack has something on it
                if stack:
                    if c.value == stack[-1][0]:
                        j = stack[-1][1]            # Index of left keyword
                        eqnlist[j].match = i        # i=index of right keyword
                        c.match = j                 # Set right keyword to point to left keyword
                        stack.pop(-1)
                    else:
                        #Look in python dict for keyword that matches current keyword
                        matching_keyword = Keyword.matchingKeywords[c.value]

                        #Push matching keyword and index of current keyword on stack
                        stack.append([matching_keyword, i])

                #Else stack is empty
                else:
                    #Look in python dict for keyword that matches current keyword
                    matching_keyword = Keyword.matchingKeywords[c.value]

                    #Push matching keyword and index of current keyword on stack
                    stack.append([matching_keyword, i])

    def adjustFonts(self):
        #Look for keywords and characters
        eqnlist = self.equationList
        length = self.length
        start = end = -1
        previous_character = None
        found_label = False
        found_number = False
        s1 = set('0123456789')
        s2 = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')
        s3 = s1.union(s2)
        s4 = set('abcdefABCDEF')

        for i,c in enumerate(eqnlist):
            if c.object_type == 'character':
                v = c.ascii_value

                if not found_label:
                    if found_number:
                        if v not in s1:
                            found_number = False
                    elif v in s2:
                        c.setItalic()
                        found_label = True
                    elif v in s1:
                        found_number = True
                        start = i
                        first_digit = v
                else:
                    if v in s3:
                        if v in s2:
                            c.setItalic()
                    else:
                        found_label = False

    #***************************************************************************************
    #*Methods below this point handle moving the cursor around the equation
    #***************************************************************************************
    def getClickedCursorPosition(self, clicked_char, click_position):
        """Find which section of the equation was clicked, and where to place cursor"""
        xl = click_position.x()
        p = clicked_char.pos()
        xc = p.x()
        yc = p.y()
        w = clicked_char.width

        #Find index of the clicked widget
        index = self.equationList.index(clicked_char)
        if xl-xc < 0.5*w:
            x = xc
            self.equationListIndex = index - clicked_char.cursorClickMoveLeft
        else:
            x = xc + w
            self.equationListIndex = index + clicked_char.cursorClickMoveRight

        self.checkForIgnoreInput()
        self.cursor.show()
        self.setCursorPosition()

    def moveCursorRight(self):
        eqnlist = self.equationList
        length = self.length
        index = self.equationListIndex
        next = index

        #Move cursor right
        if index < length:
            c = eqnlist[index]  # Look at the current character

            if c.object_type == 'keyword':

                #Figure out where to go after current matrix element
                if c.value == Keyword.ELEMENTEND:
                    c = eqnlist[index+1]
                    if c.value == Keyword.ROWEND:
                        next += 4       # Either jump to element on next row or out of matrix
                    else:
                        next += 2

                #Figure out where to go after current program line
                elif c.value == Keyword.LINEEND:
                    c = eqnlist[index+1]
                    if c.value != Keyword.PROGRAMBODYEND:   # If cursor is at end of last line the next=index and cursor does not move right
                        next += 2

                elif c.value == Keyword.INDEXEND:
                    next += c.cursorRight
                    k = self.testCursorBetweenKeywords(Keyword.SUBSUPSTART)
                    if k != -1:
                        c1 = eqnlist[k]
                        next = c1.match + 1

                else:
                    next += c.cursorRight

            else:
                next += c.cursorRight

        self.equationListIndex = next
        self.checkForIgnoreInput()
        self.setCursorPosition()

    def moveCursorLeft(self):
        eqnlist = self.equationList
        length = self.length
        index = self.equationListIndex
        next = index

        #Move cursor left
        if index > 0:
            c = eqnlist[index-1]    # Look at previous character

            if c.object_type == 'keyword':

                #Figure out where to go after current matrix element
                if c.value == Keyword.ELEMENTSTART:
                    c = eqnlist[index-2]
                    if c.value == Keyword.ROWSTART:
                        next -= 4       # Either jump to element on previous row or out of matrix
                    else:
                        next -= 2       # Jump to end of previous element

                #Figure out where to go after current program line
                elif c.value == Keyword.LINESTART:
                    c = eqnlist[index-2]
                    if c.value == Keyword.PROGRAMBODYSTART:
                        next -= 4
                    else:
                        next -= 2

                elif c.value == Keyword.SUBSUPEND:
                    # get right most edge of power
                    for i in xrange(index-3, -1, -1):
                        c1 = eqnlist[i]
                        if c1.object_type == 'character':
                            rightx1 = c1.pos().x() + c1.width
                            break

                    #Get right most edge of index
                    c2 = eqnlist[index-2]  #END keyword
                    for i in xrange(c2.match-2, -1, -1):
                        c3 = eqnlist[i]
                        if c3.object_type == 'character':
                            rightx2 = c3.pos().x() + c3.width
                            break

                    #Is the width of the index > width of power, if so, move cursor to closest char in index
                    next -= 2
                    if rightx2 > rightx1:
                        next = c2.match - 1

                elif c.value == Keyword.POWERSTART:
                    next -= c.cursorLeft
                    k = self.testCursorBetweenKeywords(Keyword.SUBSUPSTART)
                    if k != -1:
                        next = k

                else:
                    next -= c.cursorLeft

            else:
                next -= c.cursorLeft

        self.equationListIndex = next
        self.checkForIgnoreInput()
        self.setCursorPosition()

    def moveCursorEnd(self):
        eqnlist = self.equationList
        length = self.length
        index = self.equationListIndex

        #Move to end of equation when 'end' key is hit
        next = length
        for i in xrange(index, length):
            c = eqnlist[i]
            if c.object_type == 'keyword' or c.value == ')':
                next = i
                break

        self.equationListIndex = next
        self.checkForIgnoreInput()
        self.setCursorPosition()

    def moveCursorStart(self):
        eqnlist = self.equationList
        length = self.length
        index = self.equationListIndex

        next = 0
        if index:
            for i in xrange(index-1, -1, -1):
                c = eqnlist[i]
                if c.object_type == 'keyword' or c.value == '(':
                    next = i + 1
                    break

        self.equationListIndex = next
        self.checkForIgnoreInput()
        self.setCursorPosition()

    def moveCursorUp(self):
        eqnlist = self.equationList
        length = self.length
        index = self.equationListIndex
        next = index

        if self.testCursorBetweenKeywords(Keyword.DENOMSTART) != -1:
            i = self.testCursorBetweenKeywords(Keyword.DENOMSTART)
            c = eqnlist[i+2]
            if c.object_type == 'keyword' and c.ascii_value == Keyword.DEESTART:
                next = eqnlist[i-3].match + 1
            else:
                next = eqnlist[i-2].match + 1

        elif self.testCursorBetweenKeywords(Keyword.FROMSTART) != -1:
            i = self.testCursorBetweenKeywords(Keyword.FROMSTART)
            c = eqnlist[i]
            next = c.match + 2

        #Is cursor inside a matrix element? If so get position of start of element
        elif self.testCursorBetweenKeywords(Keyword.ELEMENTSTART) != -1:
            i = self.testCursorBetweenKeywords(Keyword.ELEMENTSTART)
            c = eqnlist[i]
            current_row = c.row
            current_col = c.col
            if c.row != 0:
                #Find corresponding element on previous row
                for j in xrange(i-1, -1, -1):
                    c = eqnlist[j]
                    if c.object_type == 'keyword' and c.value == Keyword.ELEMENTSTART:
                        if c.row == current_row-1 and c.col == current_col:
                            next = j + 1
                            break

        elif self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:
            k = self.testCursorBetweenKeywords(Keyword.LINESTART)
            c = eqnlist[k-1]
            if c.value == Keyword.LINEEND:
                next = c.match + 1

        elif self.testCursorBetweenKeywords(Keyword.SUBSUPSTART) != -1:
            if self.testCursorBetweenKeywords(Keyword.INDEXSTART) != -1:
                k = self.testCursorBetweenKeywords(Keyword.INDEXSTART)
                c = eqnlist[k]  # INDEXSTART keyword
                next = c.match + 2

        self.equationListIndex = next
        self.checkForIgnoreInput()
        self.setCursorPosition()

    def moveCursorDown(self):
        eqnlist = self.equationList
        length = self.length
        index = self.equationListIndex
        next = index

        #If in numerator, move down to denom
        if self.testCursorBetweenKeywords(Keyword.NUMSTART) != -1:
            i = self.testCursorBetweenKeywords(Keyword.NUMSTART)
            c = eqnlist[i+2]
            if c.object_type == 'keyword' and c.ascii_value == Keyword.DEESTART:
                next = c.match + 6
            else:
                c = eqnlist[i]
                next = c.match + 3

        elif self.testCursorBetweenKeywords(Keyword.TOSTART) != -1:
            i = self.testCursorBetweenKeywords(Keyword.TOSTART)
            c = eqnlist[i-1]
            next = c.match +1

        #Is cursor inside a matrix element? If so get position of start of element
        elif self.testCursorBetweenKeywords(Keyword.ELEMENTSTART) != -1:
            i = self.testCursorBetweenKeywords(Keyword.ELEMENTSTART)
            c = eqnlist[i]
            current_row = c.row
            current_col = c.col

            #Find corresponding element on next row
            for j in xrange(c.match+1, length):
                c = eqnlist[j]
                if c.object_type == 'keyword' and c.value == Keyword.ELEMENTSTART:
                    if c.row == current_row+1 and c.col == current_col:
                        next = j + 1
                        break

        elif self.testCursorBetweenKeywords(Keyword.LINESTART) != -1:
            k = self.testCursorBetweenKeywords(Keyword.LINESTART)
            c = eqnlist[k]
            k = c.match
            c = eqnlist[k+1]
            if c.value == Keyword.LINESTART:
                next = k + 2

        elif self.testCursorBetweenKeywords(Keyword.SUBSUPSTART) != -1:
            if self.testCursorBetweenKeywords(Keyword.INDEXSTART) == -1:  # <-------Note ==
                #Cursor is not in the index, so it has to be in power
                k = self.testCursorBetweenKeywords(Keyword.SUBSUPSTART)
                next = k + 2

        self.equationListIndex = next
        self.checkForIgnoreInput()
        self.setCursorPosition()

    def testCursorBetweenKeywords(self, k_value):   # k_value is start keyword
        #Is cursor between keywords?
        index = self.equationListIndex
        eqnlist = self.equationList

        ret_val = -1
        for i in xrange(index-1, -1, -1):
            c = eqnlist[i]
            if c.object_type == 'keyword' and c.value == k_value:
                #Found a keyword
                if index <= c.match:
                    #Cursor is between keywords
                    ret_val = i
                    break

        #Returns -1 if cursor not between desired keywords
        return ret_val

    def testCursorBetweenAnyKeywords(self):
        #Is cursor between keywords?
        index = self.equationListIndex
        eqnlist = self.equationList

        ret_val = False
        for i in xrange(index-1, -1, -1):
            c = eqnlist[i]
            if c.object_type == 'keyword':
                #Found a keyword
                if i < index <= c.match:
                    #Cursor is between keywords
                    ret_val = True
                    break

        #Returns -1 if cursor not between desired keywords
        return ret_val

    def setCursorPosition(self):
        #Characters forming labels, numbers
        s3 = self.cursorChars

        #OTher characters
        s4 = set(',+-*<>:')
        s4 = s4.union(set(['    ', ';', ':=', '==', 'for ', 'while ', 'break', 'if ', 'continue', ' in ', 'return ', 'elif ', 'else']))

        #Make sure cursor is visible
        self.cursor.show()

        #Clear selection box if we previously highlighted something
        if self.showSelectionBox:
            self.clearSelectionBox()

        index = self.equationListIndex
        eqnlist = self.equationList
        length = self.length

        #Find out what is the cursor on and what is to the left of cursor
        if 0 < index < length:
            c1 = eqnlist[index]
            c2 = eqnlist[index-1]
            ascii_value1 = c1.ascii_value
            ascii_value2 = c2.ascii_value

        elif index == 0:
            c1 = eqnlist[index]
            c2 = None
            ascii_value1 = c1.ascii_value
            ascii_value2 = None

        else:
            c1 = None
            c2 = eqnlist[index-1]
            ascii_value1 = None
            ascii_value2 = c2.ascii_value

        #Cursor is on a regular character
        if ascii_value1 in s3:
            self.handleCursorOnChar(c1, index)

        #Cursor is to the right of a regular character
        elif ascii_value2 in s3:
            self.handleCursorOnChar(c2, index-1)

        #Handle other visible characters
        elif ascii_value1 in s4:
            x, y = c1.getPosition()
            size = c1.fontSize
            self.cursor.setPosition(x-1, y, 1, 2, size)

        elif ascii_value2 in s4:
            x, y = c2.getPosition()
            size = c2.fontSize
            width = c2.width
            self.cursor.setPosition(x+width-1, y, 1, 2, size)

        #Cursor at beginning of equation and not next to a regular char
        elif c2 is None:
            self.cursor.setPosition(-1, 0, 1, 2, self.font.pointSize())

        #Cursor at end of equation and not next to a regular char
        elif c1 is None:
            self.cursor.setPosition(self.width-1, 0, 1, 2, self.font.pointSize())

        elif c1.object_type == 'keyword' and c2.object_type == 'keyword':
            #Cursor is between keywords. Decide if we use cursor position and
            #size info in left or right keywords
            if c2.cursorLookRight == True:
                x = c1.cursorX
                y = c1.cursorY
                size = c1.cursorSize
                self.cursor.setPosition(x-1, y, 1, 2, size)
            else:
                x = c2.cursorX
                y = c2.cursorY
                size = c2.cursorSize
                self.cursor.setPosition(x-1, y, 1, 2, size)

        #Do this after moving cursor, prevents missing pixels
        self.update()

    def handleCursorOnChar(self, c1, index):
        s = self.cursorChars

        eqnlist = self.equationList
        length = self.length

        #Look to the right
        end = start = index
        endchar = startchar = c1

        for i in xrange(index+1, length):
            c = eqnlist[i]
            if c.ascii_value in s:
                end = i
                endchar = c
            else:
                break

        #Look to the left
        for i in xrange(index-1, -1, -1):
            c = eqnlist[i]
            if c.ascii_value in s:
                start = i
                startchar = c
            else:
                break

        startx, starty = startchar.getPosition()
        endx, endy = endchar.getPosition()
        length = endx + endchar.width - startx
        x1, y1 = c1.getPosition()
        xposition = x1 - startx

        if end == self.equationListIndex-1:
            xposition += endchar.width

        size = c1.fontSize
        baseline_vert_offset = size * 0.1

        #Set cursor size and position
        #self.cursor.setPosition(startx, starty+baseline_vert_offset, xposition, length, -c1.top + baseline_vert_offset)
        self.cursor.setPosition(startx, starty+baseline_vert_offset, xposition, length, size + baseline_vert_offset)

    def checkForIgnoreInput(self):
        #Sometimes must ignore inputs. Look at cursor position and set flag.
        eqnlist = self.equationList
        index = self.equationListIndex

        if index == 0:
            c1 = eqnlist[0]

        elif index == self.length:
            c1 = None
            c2 = eqnlist[index-1]

        else:
            c1 = eqnlist[index]
            c2 = eqnlist[index-1]

    #*************************************************************************************
    #*Methods below this point handle parsing and executing equation
    #*************************************************************************************
    def tryToExecuteEquation(self):
        """This method will first check if the equation has been parsed, if not then parse it.
           Then it will execute the equation"""

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
            t = [(self.program, self.inputVariables, self.inputFunctions, has_result, self.forceSymbolic), self.object_id]
            return t

        return None

    def parseEquation(self):
        '''This function parses the equation and produces a Python program'''
        s = self.getEquationString()
        self.equationParser.reset()

        #Try running parser
        try:
            self.equationParser.run(s)   # Parse
            self.equationHasBeenParsed = True
        except:
            print str(sys.exc_info())
            self.setToolTip('Parser: Syntax error in equation')
            self.setColor(QColor('red'))
            self.equationHasBeenParsed = False

        self.inputVariables = self.equationParser.inputVariables    # Vars used by eqn
        self.inputFunctions = self.equationParser.inputFunctions
        self.program = ''.join([self.equationParser.functions, self.equationParser.program])

    def show_result(self, q_item):
        #For an equation q_item list holds only ONE tuple
        t = q_item[0]

        result = t[0]
        error = t[1]
        self.is_symbolic = t[2]

        self.setToolTip('Equation')
        self.setColor(QColor('black'))

        #Handle errors
        if error != None:
            self.resultString = None
            self.deleteResult(True)
            self.layoutEquation()
            self.setToolTip(error)
            self.setColor(QColor('red'))

        #Are we expecting a result to display?
        elif not self.isAssignment and not self.hasProgram:
            result_string = `result`

            #Only redraw the result if we have to
            if result_string != self.resultString:
                #Save string for next time
                self.resultString = result_string

                if self.is_symbolic or self.forceSymbolic:
                    self.drawSymbolicResult(result, result_string)
                else:
                    self.drawNumericalResult(result, result_string)

    def getEquationString(self):
        #Create a string the Pythonic way
        s = self.varSizedSymbols1
        s = s.union(self.varSizedSymbols2)
        s = s.union(self.varSizedSymbols3)
        s = s.union(self.otherSymbols1)
        eqnlist = self.equationList

        chars = [c.ascii_value for c in eqnlist if c.ascii_value not in s]
        return ''.join(chars)

    def drawNumericalResult(self, result, result_string):
        eqnlist = self.equationList
        append = eqnlist.append
        extend = eqnlist.extend
        make_copy = copy.copy
        font = self.font

        #Is result a matrix/array?
        if isinstance(result, (scipy.ndarray, scipy.matrix)):

            #Get size of matrix
            shape = result.shape
            if len(shape) == 1:
                rows = 1
                cols = shape[0]
            else:
                rows = shape[0]
                cols = shape[1]

            if self.hasTable and rows == eqnlist[self.tableIndex].numtablerows and \
                cols == eqnlist[self.tableIndex].numtablecols:
                eqnlist[self.tableIndex].changeTableData(scipy.asarray(result))
            else:
                #Remove old result if it exists
                t1 = time.time()
                self.deleteResult()
                t2 = time.time()
                #print 'Time to delete result=', int((t2-t1)*1000000)

                c1 = Keyword(Keyword.EQUALS, cursorright=2)
                c2 = EquationChar(self, '=', '=', font)
                c2.cursorLeft = 2
                extend([c1, c2])
                self.length += 2

                #Only 1 element?
                if rows == 1 and cols == 1:
                    nice_result = self.roundResult(result[0])
                    extend(nice_result)
                    self.length += len(nice_result)

                #Is the matrix/array big?
                elif rows > self.displayResultAsTableThreshold or cols > self.displayResultAsTableThreshold:
                    self.insertBigMatrixResult(rows, cols, result)

                else:
                    #Draw regular matrix
                    t1 = time.time()
                    self.insertMatrixResult(rows, cols, result)
                    t2 = time.time()
                    #print 'Time to create numerical matrix result=', int((t2-t1)*1000000)

                #Add end keyword and re-draw equation
                c4 = Keyword(Keyword.EQUALSEND)
                append(c4)
                self.length += 1
                self.hasResult = True      # Set to true once we have added new result to equation
                t1 = time.time()
                self.layoutEquation()
                t2 = time.time()
                #print 'Time to layout numerical result=', int((t2-t1)*1000000)

        #Result is inifinity
        elif result_string == 'inf':
            #Remove old result if it exists
            self.deleteResult()
            c1 = Keyword(Keyword.EQUALS, cursorright=2)
            c2 = EquationChar(self, ' = ', '=', font)
            c2.cursorLeft = 2
            c3 = EquationChar(self, u'\u221e', '__infinity__', font)
            extend([c1, c2, c3])

            #Add end keyword and re-draw equation
            c4 = Keyword(Keyword.EQUALSEND)
            append(c4)
            self.length += 1
            self.hasResult = True      # Set to true once we have added new result to equation
            self.layoutEquation()

        #Result is a number (int, float, complex)
        elif isinstance(result, (float, int, complex)):
            #Remove old result if it exists
            self.deleteResult()
            c1 = Keyword(Keyword.EQUALS, cursorright=2)
            c2 = EquationChar(self, ' = ', '=', font)
            c2.cursorLeft = 2
            nice_result = self.roundResult(result)
            extend([c1, c2])
            extend(nice_result)
            self.length += (2 + len(nice_result))

            #Add end keyword and re-draw equation
            c4 = Keyword(Keyword.EQUALSEND)
            append(c4)
            self.length += 1
            self.hasResult = True      # Set to true once we have added new result to equation
            self.layoutEquation()

    def drawSymbolicResult(self, result, result_string):
        eqnlist = self.equationList
        append = eqnlist.append
        extend = eqnlist.extend
        make_copy = copy.copy
        font = self.font

        #Remove old result if it exists
        self.deleteResult()

        c1 = Keyword(Keyword.EQUALS, cursorright=2)
        c2 = EquationChar(self, u' \u27f6 ', '__limitarrow__', font)
        c2.cursorLeft = 2
        extend([c1, c2])
        self.length += 2

        if isinstance(result, (scipy.ndarray, sympy.Matrix, list)):
            self.insertSymbolicMatrixResult(result)
        else:
            #Feed the symbolic output into a parser to generate GUI widgets
            symbolic_result_widgets = self.outputParser.run(self, result_string, self.font)
            extend(symbolic_result_widgets)
            self.length += len(symbolic_result_widgets)

        #Add end keyword and re-draw equation
        c4 = Keyword(Keyword.EQUALSEND)
        append(c4)
        self.length += 1
        self.hasResult = True      # Set to true once we have added new result to equation
        self.layoutEquation()

    def insertBigMatrixResult(self, rows, cols, result):
        #Draw a table for large matrices and array
        if isinstance(result, scipy.matrix):
            c2 = EquationSquareBracketLine(self, value = '__leftsquarebracket__')
            c8 = EquationSquareBracketLine(self, value = '__rightsquarebracket__')
            c5 = EquationTable(self, scipy.asarray(result), rows, cols, self.font)
        else:
            c2 = EquationParenthesis(self, '__leftparenthesis__')
            c8 = EquationParenthesis(self, '__rightparenthesis__')
            c5 = EquationTable(self, scipy.asarray(result), rows, cols, self.font)

        c5.setFontSize(self.font.pointSize())
        c5.setSize(self.initialTableWidth, self.initialTableHeight)

        self.hasTable = True
        self.tableIndex = self.length + 4
        c1 = Keyword(Keyword.LEFTPAREN, cursorright=3)
        c3 = Keyword(Keyword.BODYSTART, cursorleft=3)
        c3.selectEntireMathObject = True
        c3.cursorLookRight = True
        c4 = Keyword(Keyword.TABLESTART, cursorright = 3)
        c6 = Keyword(Keyword.TABLEEND, cursorleft = 3)
        c7 = Keyword(Keyword.BODYEND, cursorright=3)
        c7.selectEntireMathObject = True
        c9 = Keyword(Keyword.RIGHTPAREN, cursorleft=3)
        i = self.length
        self.equationList[i: i] = [c1, c2, c3, c4, c5, c6, c7, c8, c9]
        self.length += 9

    def insertMatrixResult(self, rows, cols, result):
        eqnlist = self.equationList
        append = eqnlist.append
        extend = eqnlist.extend
        make_copy = copy.copy

        if isinstance(result, scipy.matrix):
            c1 = Keyword(Keyword.MATRIXSTART, rows, cols, cursorright=4, cursorleft=1)
            c2 = EquationSquareBracketLine(self, value = '__leftsquarebracket__')
            c3 = EquationSquareBracketLine(self, value = '__rightsquarebracket__')
            c4 = Keyword(Keyword.MATRIXEND, cursorleft=4)
        else:
            c1 = Keyword(Keyword.ARRAYSTART, rows, cols, cursorright=4, cursorleft=1)
            c2 = EquationParenthesis(self, value = '__leftparenthesis__')
            c3 = EquationParenthesis(self, value = '__rightparenthesis__')
            c4 = Keyword(Keyword.ARRAYEND, cursorleft=4)

        #Add matrix/array start keyword and left bracket/parenthesis
        append(c1)
        append(c2)

        #Create some locals variables so that for loops below are faster
        c_row_start = Keyword(Keyword.ROWSTART)
        c_row_end = Keyword(Keyword.ROWEND)
        c_element_start = Keyword(Keyword.ELEMENTSTART, cursorleft=2)
        c_element_start.cursorLookRight = True
        c_element_end = Keyword(Keyword.ELEMENTEND, cursorright=2)

        #Flatten matrix to a 1-D array
        result = scipy.asarray(result)
        flat_result = result.flatten()

        #Use map function to process each element of array.  Return value is a list.  Each element
        #of the list is a list of GUI characters
        rounded_result = map(self.roundResult, flat_result)

        j = 0
        num = 0
        for r in xrange(rows):
            append(make_copy(c_row_start))
            for c in xrange(cols):
                append(make_copy(c_element_start))
                nice_result = rounded_result[j]
                j += 1
                extend(nice_result)
                num += len(nice_result)
                append(make_copy(c_element_end))
            append(make_copy(c_row_end))

        #Add right bracket/parenthesis at end of matrix/array keyword
        append(c3)
        append(c4)

        mat_size = rows * cols * 2 + 4 + 2 * rows + num
        self.length += mat_size

    def insertSymbolicMatrixResult(self, result):
        eqnlist = self.equationList
        append = eqnlist.append
        extend = eqnlist.extend
        make_copy = copy.copy
        font = self.font

        #Get size of matrix
        shape = result.shape
        if len(shape) == 1:
            rows = 1
            cols = shape[0]
        else:
            rows = shape[0]
            cols = shape[1]
            if rows == 1:
                result = result[0]

        if isinstance(result, sympy.Matrix):
            c1 = Keyword(Keyword.MATRIXSTART, rows, cols, cursorright=4, cursorleft=1)
            c2 = EquationSquareBracketLine(self, value = '__leftsquarebracket__')
            c3 = EquationSquareBracketLine(self, value = '__rightsquarebracket__')
            c4 = Keyword(Keyword.MATRIXEND, cursorleft=4)
        else:
            c1 = Keyword(Keyword.ARRAYSTART, rows, cols, cursorright=4, cursorleft=1)
            c2 = EquationParenthesis(self, value = '__leftparenthesis__')
            c3 = EquationParenthesis(self, value = '__rightparenthesis__')
            c4 = Keyword(Keyword.ARRAYEND, cursorleft=4)

        #Add matrix/array start keyword and left bracket/parenthesis
        append(c1)
        append(c2)

        #Create some locals variables so that for loops below are faster
        c_row_start = Keyword(Keyword.ROWSTART)
        c_row_end = Keyword(Keyword.ROWEND)
        c_element_start = Keyword(Keyword.ELEMENTSTART, cursorleft=2)
        c_element_start.cursorLookRight = True
        c_element_end = Keyword(Keyword.ELEMENTEND, cursorright=2)

        num = 0
        if rows == 1:
            append(make_copy(c_row_start))
            for c in xrange(cols):
                append(make_copy(c_element_start))
                x = (result[c] * sympy.I)/sympy.I
                nice_result = self.outputParser.run(self, str(x), font)
                extend(nice_result)
                num += len(nice_result)
                append(make_copy(c_element_end))
            append(make_copy(c_row_end))

        else:
            for r in xrange(rows):
                append(make_copy(c_row_start))
                for c in xrange(cols):
                    append(make_copy(c_element_start))
                    x = (result[r, c] * sympy.I)/sympy.I
                    nice_result = self.outputParser.run(self, str(x), font)
                    extend(nice_result)
                    num += len(nice_result)
                    append(make_copy(c_element_end))
                append(make_copy(c_row_end))

        #Add right bracket/parenthesis at end of matrix/array keyword
        append(c3)
        append(c4)

        mat_size = rows * cols * 2 + 4 + 2 * rows + num
        self.length += mat_size

    def deleteResult(self, char_entered = False):
        '''Delete the result of an expression'''
        if char_entered:
            self.resultString = None

        if self.hasResult:
            self.hasResult = False
            start = self.equationList[-1].match
            end = self.length
            self.length = start
            pop = self.equationList.pop

            if self.hasTable:
                self.hasTable = False
                self.activeBox.hideResizeHandles()

            remove = self.scene().removeItem
            for i in xrange(start, end):
                c = pop()
                if c.object_type == 'character':
                    remove(c)

            if self.equationListIndex > len(self.equationList):
                self.equationListIndex = len(self.equationList)

    def roundResult(self, val):
        '''Attempt to clean up numerical result. Return a string'''
        val = scipy.real_if_close(val)
        font = self.font

        if scipy.isreal(val):
            retval = self.formatFloatResult(val)

        #Check for rounding/number representation errors
        elif not scipy.iscomplex(scipy.real_if_close(1j * val)):
            #Treat number as pure imaginary
            y = scipy.imag(val) * 1
            #print 'equation: creating float result chars'
            retval = self.formatFloatResult(y)
            c = EquationChar(self, 'j', 'j', font)
            retval.append(c)

        else:
            #Treat number as complex
            x = scipy.real(val) * 1
            y = scipy.imag(val) * 1
            a = self.formatFloatResult(x)
            b = self.formatFloatResult(abs(y))

            if y < 0:
                sign = '-'
            else:
                sign = '+'

            retval = a
            c1 = EquationChar(self, sign, sign, font)
            retval.append(c1)
            retval.extend(b)
            c2 = EquationChar(self, 'j', 'j', font)
            retval.append(c2)

        return retval

    def formatFloatResult(self, num):
        numberfilter = '%.4g'  #'%.3f'

        font = self.font

        #Create formated string
        s = numberfilter % num

        #Attempt to split string into exponent and mantissa
        l = s.split('e')

        #Is float in engineering format?
        if len(l) > 1:
            c1 = Keyword(Keyword.POWERSTART)
            c1.cursorLookRight = True
            c2 = Keyword(Keyword.POWEREND)
            c3 = EquationChar(self, self.multiplySymbol, '*', font)
            c4 = EquationChar(self, '1', '1', font)
            c5 = EquationChar(self, '0', '0', font)

            #Insert mantissa into result
            s1 = l[0]
            retval = [EquationChar(self, val, val, font) for val in s1]

            #Insert *10 ^ exponent
            retval.extend([c3, c4, c5, c1])

            s2 = l[1]
            sign = s2[0]
            s2 = s2[1:]             # Strip sign
            s2 = s2.strip('0')      # Strip any leading zeros

            if sign == '-':
                retval.append(EquationChar(self, '-', '-', font))

            retval.extend( [EquationChar(self, val, val, font) for val in s2] )
            retval.append(c2)
        else:
            #Handle other floats, ints
            s1 = l[0]
            retval = [EquationChar(self, val, val, font) for val in s1]
            #****************Use this line to treat entire number as one object, comment out above line
            #retval = [EquationChar(self, s1, s1, font)]

        return retval

    def checkForSymbolicVars(self, worksheet_variables, numerical_vars, symbolic_vars):
        self.is_symbolic = False

        for variable_name in self.inputVariables:
            variable = worksheet_variables.get(variable_name) # Get actual value, return None if not in dict
            m = type(variable).mro()

            #Do a string search for sympy.  This seems to be about 10x faster than doing,
            #for example: if '_evalf' in dir(variable)
            if 'sympy' in str(m) or (isinstance(variable, scipy.ndarray) and variable.dtype.name == 'object'):
                self.is_symbolic = True
                return

        for function_name in self.inputFunctions:
            if worksheet_variables.has_key(function_name):
                function = worksheet_variables[function_name]
            elif numerical_vars.has_key(function_name):
                function = numerical_vars[function_name]
            elif symbolic_vars.has_key(function_name):
                function = symbolic_vars[function_name]
            else:
                function = None
            #function = worksheet_variables.get(function_name) # Get actual value, return None if not in dict
            m = type(function)

            #Do a string search for sympy.  This seems to be about 10x faster than doing,
            #for example: if '_evalf' in dir(variable)
            if 'sympy' in str(m):
                self.is_symbolic = True
                return

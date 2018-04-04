
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
import os.path
import time
import copy
import re
import scipy

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


class Image(QGraphicsRectItem):
    """This object holds an entire image"""
    layoutengine = Layout()
    selectionColor = QColor('yellow')   #Background color of selected chars in equation
    selectionBorderColor = QColor('red')
    highlightedColor = QColor(144, 238, 144,  128)  #Background color of selected equation
    cursorOverEquationColor = QColor(0, 0xfd, 0xf8, 128)

    #Define various constants used by all equations
    borderWidth = 10                    #Width of border around equation

    #List containing names of variables in this object that are to be saved to disk
    save_variables = ['fontSize',                   \
                      'isAssignment',                     \
                      'isSymbolic',                        \
                      'hasResult',                          \
                      'equationNeedsParsing',      \
                      'equationHasBeenParsed',    \
                      'program',                \
                      'functions',              \
                      'outputVariables',        \
                      'inputVariables',         \
                      'type',                   \
                      'resultString',           \
                      'hasTable',               \
                      'tableIndex',             \
                      'initialTableWidth',      \
                      'initialTableHeight'      \
                      ]

    allowedImageKeys = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789/._~')

    def __init__(self, parent, position, font):
        QGraphicsRectItem.__init__(self, parent)
        self.finishedInit = False

        self.setToolTip('Image')
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.setCursor(Qt.ArrowCursor)
        self.setPos(position)       # Set position of equation using scene coordinates
        self.setAcceptsHoverEvents(True)
        self.setSelected(True)
        self.setZValue(100)  #Z value on worksheet

        #Create equation cursor
        self.cursor = equationcursor.EquationCursor(self)

        #Create active box (shown when editing eqn), shadow box (shown when
        #mouse over eqn) and selection box (shown when part of eqn is selected)
        self.activeBox = activebox.ActiveBox('image', self)
        self.activeBox.setColor(self.highlightedColor)
        self.activeBox.showBox(True)
        self.shadowBox = shadowbox.ShadowBox(self)
        self.shadowBox.setColor(self.cursorOverEquationColor)
        self.selectionBox = selectionbox.SelectionBox(self)
        self.selectionBox.setColor(self.selectionColor)

        #Initialize variables
        self.object_type = 'image'
        self.currentDirectory = os.path.expanduser('~')
        self.currentFile = None
        self.currentIndex = -1  #Index of this equation in worksheets list
        self.finishedInit = True
        self.length = 0
        self.width = 0
        self.top = 0
        self.bottom = 0
        self.positionChanged = False
        self.font = QFont(font.family(), font.pointSize())
        self.equationList = []
        self.equationListIndex = 0
        self.showSelectionBox = False
        self.characterClicked = False
        self.selectionStartIndex = -1
        self.selectionRightIndex = -1
        self.selectionLeftIndex = -1

        #Initialize list
        c1 = Keyword(Keyword.FILESTART)
        c2 = EquationImage(self, self.font.pointSize())
        c3 = Keyword(Keyword.FILENAMESTART, cursorleft = 0)
        c4 = EquationReservedSpace(self)
        c5 = Keyword(Keyword.FILENAMEEND, cursorright = 0)
        c6 = Keyword(Keyword.FILEEND)
        self.equationList = [c1, c2, c3, c4, c5, c6]
        self.equationListIndex = 3
        self.length = 6

        self.layoutEquation()
        self.setCursorPosition()

        self.finishedInit = True

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
            if c.type == 'character':
                c.setColor(color)
        self.update()

    def mousePressEvent(self, event):
        QGraphicsRectItem.mousePressEvent(self, event)

        #Clear any existing selection box
        self.clearSelectionBox()

        self.setCursor(Qt.ClosedHandCursor)
        p = event.pos()
        s = event.scenePos()

        item = self.scene().itemAt(s)

        if item.object_type == 'character':
            if item.ascii_value == '__image__':
                self.cursor.hide()
                self.clearFocus()

                #Open file dialog
                file_name = QFileDialog.getOpenFileName(None, 'Open Image File', self.currentDirectory,  \
                                "Image Files (*.png *.jpg *.bmp *.jpeg *.gif *.pbm *.pgm *.ppm)")

                if file_name:
                    #Insert file name characters into list of widgets
                    self.addCharacters(str(file_name))

                    #Display image
                    self.doLoad()

            else:
                self.characterClicked = True
                self.getClickedCursorPosition(item, p)

        else:
            self.cursor.hide()
            self.clearFocus()

        #Are we clicking on a resize handle?
        self.resizeStartHandle = self.activeBox.mouseInResizeHandle(p)

    def mouseMoveEvent(self, event):
        r = self.resizeStartHandle

        #Image is being resized
        if r:
            p = event.pos()
            m = self.borderWidth
            image = self.equationList[1]
            imagex, imagey = image.getPosition()

            #Right resize handle dragged
            min_height = self.font.pointSize() * 3
            if r == 1:
                image_height = image.bottom - image.top
                deltah = p.y() - m - self.bottom
                h = image_height + deltah

                if h < min_height:
                    h = min_height

            #Bottom right resize handle dragged
            elif r == 2:
                image_height = image.bottom - image.top
                deltah = self.top - p.y()
                h = image_height + deltah

                if h < min_height:
                    h = min_height
                    deltah = h - image_height
                self.moveBy(0, -deltah)

            image.setSize(h)

            l, r, t, b = self.layoutengine.layoutEquationPart(self.equationList, 0, len(self.equationList), self.font.pointSize())
            self.width = r - l
            self.top = t
            self.bottom = b
            self.updateBoundingRect()

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
        if index < self.length and eqnlist[index].type == 'character' \
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

        if index > 0 and eqnlist[index-1].type == 'character' and eqnlist[index-1].ascii_value in s:

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
                self.activeBox.showBox(True)
                self.shadowBox.hide()

            else:
                #Equation was deselected, hide cursor, active box and selection box
                self.cursor.hide()
                self.activeBox.hideBox()
                self.clearSelectionBox()
                self.doLoad()

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
        if key == Qt.Key_End:
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

            #Attempt to display image when return is hit
            self.doLoad()

        #Handle all other keys
        elif c in self.allowedImageKeys:
            self.addCharacter(c, c)

    def handleToolbuttonInput(self, button, *args):
        '''handles requests from main window'''
        pass

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

                #If nothing left between matching keywords then insert reserved char
                if c2.type == 'keyword':
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

            #Delete others if cursor not at start of equation
            if index >= 1:
                #Remove widget from widgets list
                c = eqnlist[index-1]

                #Select everythang between keyword and matching keyword
                if c.type == 'keyword':

                    if c.match < index-1:
                        #Show a rectangle around text to be deleted
                        self.selectionLeftIndex = c.match
                        self.selectionRightIndex = index - 1
                        self.createSelectionBox()

                #Delete a character
                elif c.type == 'character':
                    c = eqnlist.pop(index-1)
                    self.scene().removeItem(c)
                    self.equationListIndex -= 1
                    self.length -= 1
                    del c

                    #If nothing left between matching keywords then insert reserved char
                    i = self.equationListIndex
                    if 0 < i < self.length:
                        c = eqnlist[i]
                        if c.type == 'keyword':
                            self.findMatchingKeywords()
                            if c.match == i-1:
                                c2 = EquationReservedSpace(self)
                                eqnlist.insert(i, c2)
                                self.length += 1

                    #Only redraw equation and move cursor if there is something left to draw
                    if self.length > 0:
                        self.layoutEquation()
                        self.setCursorPosition()
                        self.equationNeedsParsing = True

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

                if c.type == 'keyword':
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
        s = self.font.pointSize() * 0.1  #Add some spacing above and below box
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

            if c.type == 'character':  #Handle chars
                if c.ascii_value == ':=':
                    self.isAssignment = False
                self.scene().removeItem(c)

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
            if object_dict['type'] == 'keyword':
                value = object_dict['value']
                c = Keyword(value)

            #Recreate regular character
            else:
                value = object_dict['value']
                ascii_value = object_dict['ascii_value']
                font = self.font

                if ascii_value == '__reserved__':
                    c = EquationReservedSpace(self)
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
        if (self.cursor.isVisible() or self.showSelectionBox):

            #If cursor is at a reserved space character then remove reserved character first
            self.deleteReservedCharacter()

            font = self.font
            i = self.equationListIndex
            eqnlist = self.equationList
            length = self.length

            if self.showSelectionBox:
                i = self.selectionLeftIndex
                self.deleteSelectionBoxContents()

            c = EquationChar(self, value, ascii_value, font)

            eqnlist.insert(i, c)
            self.equationListIndex += 1
            self.length += 1

            self.layoutEquation()
            self.setCursorPosition()
            self.equationNeedsParsing = True

    def addCharacters(self, string_of_chars):
        #Takes a ascii string and produces a sequence of widgets
        pop = self.equationList.pop
        for i in range(3, self.length-2):
            c = pop(3)  #Pop from index 3
            self.scene().removeItem(c)
            del c

        new_name = [EquationChar(self, ascii_value, ascii_value, self.font) for ascii_value in string_of_chars]
        self.equationList[3:3] = new_name
        self.length = len(self.equationList)
        self.equationListIndex = self.length - 2

        self.layoutEquation()
        self.setCursorPosition()

    def deleteReservedCharacter(self):
        """If the current character under the editing cursor is a reserved space character
        (a square block) then remove character from list before inserting new characters"""
        i = self.equationListIndex
        eqnlist = self.equationList

        c1 = eqnlist[i]
        c2 = eqnlist[i-1]
        if c1.ascii_value == '__reserved__':
            c1 = eqnlist.pop(i)
            self.scene().removeItem(c1)
            del c1
            self.length -= 1
        elif c2.ascii_value == '__reserved__':
            c2 = eqnlist.pop(i-1)
            self.scene().removeItem(c2)
            del c2
            self.length -= 1
            self.equationListIndex -= 1

    #**********************************************************************************
    #*Methods below this point handle the actual drawing of the equation on the screen
    #**********************************************************************************
    def layoutEquation(self):
        '''This is the top level entry point for drawing an equation'''
        #Unselect any equations
        self.clearSelectionBox()

        #Is eqn parsable?
        self.equationIsParsable = True
        eqnlist = self.equationList
        for c in eqnlist:
            if c.object_type == 'character':
                if c.ascii_value == "__reserved__":
                    self.equationIsParsable = False

        #Loop to find all matching pairs of keywords
        self.findMatchingKeywords()

        #This is where the fun starts. Use recursion to draw various parts of equation
        left, right, top, bottom = self.layoutengine.layoutEquationPart(eqnlist, 0, len(eqnlist), self.font.pointSize())

        #Figure out new size of equation
        self.width = w = right - left
        self.top = top
        self.bottom = bottom

        #Resize path used to draw bounding rectangle
        self.updateBoundingRect()

    def findMatchingKeywords(self):
        eqnlist = self.equationList
        index = self.equationListIndex

        c1 = eqnlist[0]
        c1.match = self.length - 1
        c2 = eqnlist[self.length-1]
        c2.match = 0

        c1 = eqnlist[2]
        c1.match = self.length - 2
        c2 = eqnlist[self.length-2]
        c2.match = 2

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
            self.equationListIndex = index
        else:
            x = xc + w
            self.equationListIndex = index + 1

        self.cursor.show()
        self.setCursorPosition()

    def moveCursorRight(self):
        next = self.equationListIndex

        #Move cursor right
        c = self.equationList[self.equationListIndex]  #Look at the current character

        if c.type != 'keyword':
            next += c.cursorRight

        self.equationListIndex = next
        self.setCursorPosition()

    def moveCursorLeft(self):
        next = self.equationListIndex

        #Move cursor left
        c = self.equationList[self.equationListIndex-1] #Look at previous character

        if c.type != 'keyword':
            next -= c.cursorLeft

        self.equationListIndex = next
        self.setCursorPosition()

    def moveCursorEnd(self):
        self.equationListIndex = self.length - 2
        self.setCursorPosition()

    def moveCursorStart(self):
        self.equationListIndex = 3
        self.setCursorPosition()

    def setCursorPosition(self):
        #Make sure cursor is visible
        self.cursor.show()

        #Clear selection box if we previously highlighted something
        if self.showSelectionBox:
            self.clearSelectionBox()

        index = self.equationListIndex
        eqnlist = self.equationList
        length = self.length

        c1 = eqnlist[index]
        c2 = eqnlist[index-1]

        if index < self.length-2:
            x, y = c1.getPosition()
            size = c1.fontSize
            baseline_vert_offset = size * 0.1
            self.cursor.setPosition(x-1, y+baseline_vert_offset, 1, 2, size)

        else:
            x, y = c2.getPosition()
            size = c2.fontSize
            width = c2.width
            baseline_vert_offset = size * 0.1
            self.cursor.setPosition(x+width-1, y+baseline_vert_offset, 1, 2, size)

        #Do this to prevent lost pixels when moving cursor around
        self.update()

    #*************************************************************************************
    #*Methods below are for loading image from file
    #*************************************************************************************
    def doLoad(self):

        #Create a string the Pythonic way
        chars = []
        pixels = None
        append = chars.append
        image_list = self.equationList[3: self.length-2]

        #Extract ascii values, create string
        chars = [c.ascii_value for c in image_list]
        entered_file_name = ''.join(chars)

        if entered_file_name != '__reserved__':
            expanded_file_name = os.path.expanduser(entered_file_name)
            directory, file_name = os.path.split(expanded_file_name)

            #Check if at least the directory is good
            if os.path.exists(expanded_file_name):
                self.currentDirectory = directory
                self.currentFile = file_name

                pixmap = QPixmap(expanded_file_name)
                if not pixmap.isNull():
                    self.equationList[1].setImage(pixmap)
                else:
                    self.equationList[1].resetImage()
                    self.setToolTip('Invalid file format')

                self.layoutEquation()

            else:
                self.currentDirectory = os.path.expanduser('~')
                self.currentFile = None
                self.equationList[1].resetImage()
                self.layoutEquation()
                self.setToolTip('Cannot access file')


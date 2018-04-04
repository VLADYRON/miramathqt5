
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
#from PyQt4 import Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from equationcursor import *
from equationwidgets import *
from activebox import *
from shadowbox import *
from selectionbox import *
from symbolscharmap import SymbolsTable
from keywords import *

class Comment(QGraphicsRectItem):
    """This object holds an entire comment"""
    selectionColor = QColor('yellow')   #Background color of selected chars in equation
    selectionBorderColor = QColor('red')
    highlightedColor = QColor(144, 238, 144,  128)  #Background color of selected equation
    cursorOverEquationColor = QColor(0, 0xfd, 0xf8, 128)

    #Define various constants used by all equations
    borderWidth = 10                    #Width of border around equation

    specialSymbols = set(SymbolsTable.ascii_value)
    alphaSymbols = set('0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ_.')
    allowedEquationKeys = set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789+-/*^!,.;_[(~ <>')

    def __init__(self, parent, position, font, window):
        QGraphicsRectItem.__init__(self, parent)
        self.finishedInit = False

        self.setToolTip('Comment')
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.setCursor(Qt.ArrowCursor)
        self.setPos(position)       #Set position of equation using scene coordinates
        self.setAcceptsHoverEvents(True)
        self.setSelected(True)
        self.setZValue(100)  #Z value on worksheet
        self.parentWindow = window

        #Bacground color
        self.setBackgroundColor(QColor(144, 238, 144,  128))

        #Create equation cursor
        self.cursor = EquationCursor(self)
        s = font.pointSize()
        self.cursor.setPosition(0, 0, 1, 2, s)

        #Create active box (shown when editing eqn), shadow box (shown when
        #mouse over eqn) and selection box (shown when part of eqn is selected)
        self.activeBox = ActiveBox('comment', self)
        self.activeBox.showResizeHandles()

        self.activeBox.setColor(self.highlightedColor)
        self.shadowBox = ShadowBox(self)
        self.shadowBox.setColor(self.cursorOverEquationColor)
        self.selectionBox = SelectionBox(self)
        self.selectionBox.setColor(self.selectionColor)

        #Initialize variables
        self.object_type = 'comment'
        self.maxWidth = 1000
        self.minWidth = 10
        self.lineSpacing = 15
        self.length = 0
        self.lineCount = 0
        self.positionChanged = False
        self.font = QFont(font.family(), font.pointSize())            #Initial font to use
        self.commentList = []
        self.commentListIndex = 0
        self.showSelectionBox = False
        self.characterClicked = False
        self.selectionStartIndex = -1
        self.selectionRightIndex = -1
        self.selectionLeftIndex = -1
        self.finishedInit = True

        pen = QPen(Qt.transparent)
        self.setPen(pen)

        self.width = s * 3
        self.top = -s
        self.bottom = 0
        self.updateBoundingRect()

    def updateBoundingRect(self):
        top = self.top - self.borderWidth
        bottom = self.bottom + self.borderWidth
        left = -self.borderWidth
        right = self.width + self.borderWidth

        #Update bounding rectangle around equation
        w = right - left
        h = bottom - top
        self.setRect(left, top, w, h)
        self.shadowBox.setRect(left, top, w, h)
        self.activeBox.setSize(w, h)
        self.activeBox.setPos(left, top)

    def setFontSize(self, size):
        #Input is size of desired font
        self.font.setPointSize(size)

        if self.showSelectionBox:

            for c in self.commentList[self.selectionLeftIndex: self.selectionRightIndex+1]:
                if isinstance(c, EquationChar):
                    c.setSize(size)

            self.layoutComment()

        elif not self.cursor.isVisible():
            for c in self.commentList:
                if isinstance(c, EquationChar):
                    c.setSize(size)
            self.layoutComment()

    def setFont(self, fontname):
        #Input is name of font family, e.g. New Times Roman, Ariel...
        self.font.setFamily(fontname)

        if self.showSelectionBox:
            for c in self.commentList[self.selectionLeftIndex: self.selectionRightIndex+1]:
                if isinstance(c, EquationChar):
                    c.setFontName(fontname)
            self.layoutComment()

        elif not self.cursor.isVisible():
            for c in self.commentList:
                if isinstance(c, EquationChar):
                    c.setFontName(fontname)
            self.layoutComment()

    def setForegroundColor(self, color):
        for c in self.commentList:
            if c.object_type == 'character':
                c.setColor(color)
        self.update()

    def setBold(self, state):
        self.font.setBold(state)

        if self.showSelectionBox:
            for c in self.commentList[self.selectionLeftIndex: self.selectionRightIndex+1]:
                if isinstance(c, EquationChar):
                    c.setToBold(state)
            self.layoutComment()

        elif not self.cursor.isVisible():
            for c in self.commentList:
                if isinstance(c, EquationChar):
                    c.setToBold(state)
            self.layoutComment()

    def setUnderline(self, state):
        self.font.setUnderline(state)

        if self.showSelectionBox:
            for c in self.commentList[self.selectionLeftIndex: self.selectionRightIndex+1]:
                if isinstance(c, EquationChar):
                    c.setToUnderline(state)
            self.layoutComment()

        elif not self.cursor.isVisible():
            for c in self.commentList:
                if isinstance(c, EquationChar):
                    c.setToUnderline(state)
            self.layoutComment()

    def setItalic(self, state):
        self.font.setItalic(state)

        if self.showSelectionBox:
            for c in self.commentList[self.selectionLeftIndex: self.selectionRightIndex+1]:
                if isinstance(c, EquationChar):
                    c.setToItalic(state)
            self.layoutComment()

        elif not self.cursor.isVisible():
            for c in self.commentList:
                if isinstance(c, EquationChar):
                    c.setToItalic(state)
            self.layoutComment()

    def setBackgroundColor(self, color):
        brush = QBrush(color)
        self.setBrush(brush)

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

        #Comment is being resized
        if r:
            p1 = event.pos()
            b = self.borderWidth
            x1 = p1.x()
            y1 = p1.y()

            #Right resize handle
            if r == 1:
                self.maxWidth = x1 - b

                if self.maxWidth < self.minWidth:
                    self.maxWidth = self.minWidth

                self.layoutComment()

            #Left resize handle
            elif r == 2:
                self.maxWidth = self.width - x1 - b

                if self.maxWidth < self.minWidth:
                    self.maxWidth = self.minWidth

                old_width = self.width
                self.layoutComment()
                self.moveBy(old_width-self.width, 0)


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
        s = s.union(self.specialSymbols)

        index = self.commentListIndex
        eqnlist = self.commentList
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
                self.activeBox.showBox(True)
                self.shadowBox.hide()

            else:
                #Equation was deselected, hide cursor, active box and selection box
                self.cursor.hide()
                self.activeBox.hideBox()
                self.clearSelectionBox()

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
            self.addReturn()

        #Handle all other keys
        elif c in self.allowedEquationKeys:
            self.addCharacter(c, c)

    #****************************************************************************************
    #Methods below handle basic editing features (copy, cut, paste, delete)
    #****************************************************************************************
    def copyFromEquation(self):
        d = []
        if self.showSelectionBox:
            #Get part of equation highlighted
            comment = self.commentList[self.selectionLeftIndex: self.selectionRightIndex+1]
            for c in comment:
                d.append(c.__dict__.copy())

        return d

    def cutFromEquation(self):
        d = []
        if self.showSelectionBox:

            eqnlist = self.commentList[self.selectionLeftIndex: self.selectionRightIndex+1]
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
            self.restorecommentList(itemsdict)
            self.setSelected(True)

            #Only redraw equation and move cursor if there is something left to draw
            if self.length > 0:
                self.layoutComment()
                self.setCursorPosition()

    def delCharacter(self):
        eqnlist = self.commentList
        index = self.commentListIndex

        #If selection box visible, delete selection
        if self.showSelectionBox:
            #Delete selection box
            self.deleteSelectionBoxContents()


            #Only redraw equation and move cursor if there is something left to draw
            if self.length > 0:
                self.layoutComment()
                self.setCursorPosition()

        #Do something if cursor is visible
        elif self.cursor.isVisible() and index >= 1:

                #Remove widget from widgets list
                c = eqnlist[index-1]

                #Delete a character
                if c.object_type == 'character':
                    c = eqnlist.pop(index-1)
                    self.scene().removeItem(c)
                    self.commentListIndex -= 1
                    self.length -= 1
                    del c

                    #Only redraw comment and move cursor if there is something left to draw
                    if self.length > 0:
                        self.layoutComment()
                        self.setCursorPosition()

    #Called from worksheet when user drags mouse over comment
    def setSelectionBox(self, item):
        comment = self.commentList

        #Is item in comment?
        if item in comment:
            #Determine range of characters selected
            i = comment.index(item)
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

            #Create a rectangle around selected text from start to end (inclusive)
            self.createSelectionBox()

    def createSelectionBox(self):
        '''Creates a rectangle around selected text'''
        comment = self.commentList

        #Hide equation cursor when selection box is visible
        self.cursor.hide()

        c1 = comment[self.selectionLeftIndex]
        c2 = comment[self.selectionRightIndex]

        first_line = c1.lineNumber
        last_line = c2.lineNumber
        info = self.lineInfo

        if last_line-first_line:
            left_coords = []
            right_coords = []

            for line in range(first_line, last_line+1):
                left_index, right_index, top, bottom = info[line]
                c_left = comment[left_index]
                c_right = comment[right_index]
                left = c_left.pos().x()
                right = c_right.pos().x() + c_right.width

                if line == first_line:
                    left = c1.pos().x()
                elif line == last_line:
                    right = c2.pos().x() + c2.width

                left_coords.extend([left, top, left, bottom])
                right_coords.extend([top, right, bottom, right])

            right_coords.reverse()
            coords = left_coords + right_coords
        else:
            left_index, right_index, top, bottom = info[first_line]
            left = c1.pos().x()
            right = c2.pos().x() + c2.width
            coords = [left, top, left, bottom, right, bottom, right, top]

        s = self.font.pointSize() * 0.2  #Add some spacing above and below box
        self.selectionBox.createBox(coords)
        self.selectionBox.show()
        self.showSelectionBox = True

    def clearSelectionBox(self):
        self.selectionStartIndex = -1
        self.selectionRightIndex = -1
        self.selectionLeftIndex = -1
        self.showSelectionBox = False
        self.selectionBox.hide()

    def deleteSelectionBoxContents(self):
        start = self.selectionLeftIndex
        end = self.selectionRightIndex + 1
        eqnlist = self.commentList
        self.length -= (end - start)
        self.commentListIndex = start

        for i in range(start, end):
            c = eqnlist.pop(start)

            if c.object_type == 'character':  #Handle chars
                self.scene().removeItem(c)

            del c

        #Reset selection box stuff
        self.clearSelectionBox()


    #********************************************************************************
    #Methods below are for loading and saving equation
    #********************************************************************************
    def getDictionary(self):
        #Create a dictionary containing variables that can be serialized
        d = {}

        #Create list. Each element is a dictionary representing a widget in equation
        saveList = []
        for c in self.commentList:
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

        #Restore objects in self.commentList
        list_of_objects = eqn_dict['saveList']
        self.restorecommentList(list_of_objects)

        #Draw the equation
        self.layoutComment()

        #Restore other thangs
        self.setSelected(False)
        self.positionChanged = False

    def restorecommentList(self, d):
        #Restore objects in self.commentList
        self.length += len(d)
        index = self.commentListIndex
        eqnlist = self.commentList

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

                c = EquationChar(self, value, ascii_value, font)

            #Restore object dictionary
            c.__dict__.update(object_dict)
            eqnlist.insert(index, c)
            index += 1

        self.commentListIndex = index

    #********************************************************************************
    #*Methods below this point handle the entry of various types of characters into
    #*the equation
    #********************************************************************************
    def handleToolbuttonInput(self, button, *args):
        '''handles requests from main window'''

        #Return keyboard focus to this equation
        self.setFocus()

        if button == 'specialsymbol':
            unicode_value = args[0]
            ascii_value = args[1]
            self.addCharacter(unicode_value, ascii_value)

    def addCharacter(self, value, ascii_value):
        #Add character only if cursor is visible
        if self.cursor.isVisible() or self.showSelectionBox:

            if self.showSelectionBox:
                #Delete selected chars
                i = self.selectionLeftIndex
                self.deleteSelectionBoxContents()
            else:
                i = self.commentListIndex

            c = EquationChar(self, value, ascii_value, self.font)  #Create a character using current font

            self.commentList.insert(i, c)
            self.commentListIndex = i + 1
            self.length += 1

            self.layoutComment()
            self.setCursorPosition()

    def addReturn(self):
        pass
#        #Add character only if cursor is visible
#        if self.cursor.isVisible() or self.showSelectionBox:
#
#            if self.showSelectionBox:
#                #Delete selected chars
#                i = self.selectionLeftIndex
#                self.deleteSelectionBoxContents()
#            else:
#                i = self.commentListIndex
#
##            if index < self.length:
##                c = self.commentList[index]
##                x, y = c.getPosition()
##            else:
##                c = self.commentList[index - 1]
##                x, y = c.getPosition()
##                x += c.width
##
##            self.maxWidth = x
#
#            c = Keyword(Keyword.RETURN)
#
#            self.commentList.insert(i, c)
#            self.commentListIndex = i + 2
#            self.length += 1
#
#            self.layoutComment()
#            self.setCursorPosition()


    #**********************************************************************************
    #*Methods below this point handle the actual drawing of the equation on the screen
    #**********************************************************************************
    def layoutComment(self):
        '''This is the top level entry point for drawing a comment'''

        px = 0
        top = 10000
        bottom = -10000
        widest_word = 0
        word_start_index = -1
        comment = self.commentList
        words = []

        #Create a list of words and space chars. Find widest word and find dimensions of each word.
        for i, c in enumerate(comment):

            if c.object_type == 'character':
                if c.ascii_value != ' ':
                    if word_start_index == -1:
                        word_start_index = i   #Remember where word started

                    w = c.width
                    t = c.top
                    b = c.bottom
                    px += w

                    #Highest and lowest point of word
                    if t < top:
                        top = t
                    if b > bottom:
                        bottom = b

                else:
                    #Append word and its' dimensions to list of words
                    if word_start_index > -1:
                        words.append(('word', px, top, bottom, word_start_index, i-1))  #Add new word to list (start, end, width, top, bot)
                        word_start_index = -1
                        top = 10000
                        bottom = -10000
                        if px > widest_word:  #Is this the widest word?
                            widest_word = px
                        px = 0

                    #Handle space character
                    words.append(('space', c.width, c.top, c.bottom, i, i))

            else:
                pass

        #Handle last word
        if word_start_index > -1:
            words.append(('word', px, top, bottom, word_start_index, i))  #Add new word to list (start, end, width, top, bot)
            if px > widest_word:  #Is this the widest word?
                widest_word = px

        #Set minimum width for text block
        self.minWidth = widest_word
        if self.minWidth > self.maxWidth:
            self.maxWidth = self.minWidth

        #Now layout words and spaces
        px = 0
        py = 0
        line_start_index = 0
        bottom_of_previous_line = 0
        top = 10000
        bottom = -10000
        line_count = 0
        max_width = self.maxWidth
        line_spacing = self.lineSpacing
        half_line_space = line_spacing/2
        line_width = 0
        biggest_line_width = 0
        total_char_width = 0
        self.lineInfo = []

        for index, word in enumerate(words):
            wordtype, width, t, b, start, end = word    #word is a tuple, break it down to components
            if line_width + width <= max_width:
                line_width += width

                if wordtype == 'word':
                    total_char_width += width

                if t < top:
                    top = t
                if b > bottom:
                    bottom = b

                line_end_index = end

            #Reached end of a line, layout words and spaces in the line
            else:
                if line_count == 0:
                    self.top = top  #The highest point of the first line in text block
                elif line_count > 0:
                    py += (bottom_of_previous_line - top + line_spacing)

                #Find widest line
                if line_width > biggest_line_width:
                    biggest_line_width = line_width

                #Remember line info
                self.lineInfo.append((line_start_index, line_end_index, top+py-half_line_space, bottom+py+half_line_space+1))

                #Move characters around for current line
                px = 0
                for i in xrange(line_start_index, line_end_index+1):  #line_end_index=start of next line, but xrange goes to line_end_index-1
                    c = comment[i]
                    c.setPosition(px, py)
                    c.lineNumber = line_count
                    px += c.width

                #Set stuff for next line
                line_count += 1
                bottom_of_previous_line = bottom
                line_width = width
                if wordtype == 'word':
                    total_char_width = line_width
                else:
                    total_char_width = 0
                top = t
                bottom = b
                line_start_index = start
                line_end_index = end

        #Handle last line of words
        if line_count == 0:
            self.top = top
            self.bottom = bottom
        elif line_count > 0:
            py += (bottom_of_previous_line - top + line_spacing)
            self.bottom = py + bottom

        #Remember line info
        self.lineInfo.append((line_start_index, line_end_index, top+py-half_line_space, bottom+py+half_line_space))

        #Move characters around for last line
        px = 0
        for i in xrange(line_start_index, line_end_index+1):  #line_end_index=start of next line, but xrange goes to line_end_index-1
            c = comment[i]
            c.setPosition(px, py)
            c.lineNumber = line_count
            px += c.width

        self.lineCount = line_count

        #Find widest line and set width of text block to this value
        if line_width > biggest_line_width:
            biggest_line_width = line_width
        self.width = biggest_line_width

        #Resize path used to draw bounding rectangle
        self.updateBoundingRect()

        #Resize selection box if visible
        if self.showSelectionBox:
            self.createSelectionBox()

    def getSizeOfCommentPart(self, eqnlist):
        #Now get size of equation part and return the size
        left = 10000
        right = -10000
        top = 10000
        bottom = -10000

        for c in eqnlist:
            if c.object_type == 'character':
                x, y = c.getPosition()
                w = c.width
                t = c.top
                b = c.bottom
                if x < left:
                    left = x
                if x+w > right:
                    right = x + w
                if y+t < top:
                    top = y + t
                if y+b > bottom:
                    bottom = y + b
        return left, right, top, bottom

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
        index = self.commentList.index(clicked_char)
        if xl-xc < 0.5*w:
            x = xc
            self.commentListIndex = index
        else:
            x = xc + w
            self.commentListIndex = index + 1

        self.cursor.show()
        self.setCursorPosition()

    def moveCursorRight(self):
        eqnlist = self.commentList
        length = self.length
        index = self.commentListIndex
        next = index

        #Move cursor right
        if index < length:
            c = eqnlist[index]  #Look at the current character

            next += c.cursorRight

        self.commentListIndex = next
        self.setCursorPosition()

    def moveCursorLeft(self):
        eqnlist = self.commentList
        length = self.length
        index = self.commentListIndex
        next = index

        #Move cursor left
        if index > 0:
            c = eqnlist[index-1] #Look at previous character
            next -= c.cursorLeft

        self.commentListIndex = next
        self.setCursorPosition()

    def moveCursorEnd(self):
        eqnlist = self.commentList
        length = self.length
        index = self.commentListIndex

        #Move to end of equation when 'end' key is hit
        next = length
        for i in xrange(index, length):
            c = eqnlist[i]
            if c.object_type == 'keyword' or c.value == ')':
                next = i
                break

        self.commentListIndex = next
        self.setCursorPosition()

    def moveCursorStart(self):
        eqnlist = self.commentList
        length = self.length
        index = self.commentListIndex

        next = 0
        if index:
            for i in xrange(index-1, -1, -1):
                c = eqnlist[i]
                if c.object_type == 'keyword' or c.value == '(':
                    next = i + 1
                    break

        self.commentListIndex = next
        self.setCursorPosition()

    def moveCursorUp(self):
        comment = self.commentList
        length = self.length
        index = self.commentListIndex
        threshold = 100000

        if index < self.length:
            cx1 = comment[index].pos().x()
            line_number = comment[index].lineNumber
        else:
            cx1 = comment[self.length-1].pos().x() + comment[self.length-1].width
            line_number = comment[index-1].lineNumber

        if line_number > 0:
            start, end, t, b = self.lineInfo[line_number-1]

            #Look for a character on line above with x-coordinate approx equal to x-coord on current line
            for i in xrange(start, end+1):
                cx2 = comment[i].pos().x()
                diff = abs(cx2 - cx1)
                if diff < threshold:
                    threshold = diff
                    nearest = i

            self.commentListIndex = nearest
            self.setCursorPosition()

    def moveCursorDown(self):
        comment = self.commentList
        length = self.length
        index = self.commentListIndex
        threshold = 100000

        if index < self.length:
            cx1 = comment[index].pos().x()
            line_number = comment[index].lineNumber
        else:
            cx1 = comment[self.length-1].pos().x() + comment[self.length-1].width
            line_number = comment[index-1].lineNumber

        if line_number < self.lineCount:
            start, end, t, b = self.lineInfo[line_number+1]

            #Look for a character on line above with x-coordinate approx equal to x-coord on current line
            for i in xrange(start, end+1):
                cx2 = comment[i].pos().x()
                diff = abs(cx2 - cx1)
                if diff < threshold:
                    threshold = diff
                    nearest = i

            self.commentListIndex = nearest
            self.setCursorPosition()

    def setCursorPosition(self):
        #Make sure cursor is visible
        self.cursor.show()

        #Clear selection box if we previously highlighted something
        if self.showSelectionBox:
            self.clearSelectionBox()

        index = self.commentListIndex

        if 0 < index <= self.length:
            c1 = self.commentList[index - 1]
            x1, y1 = c1.getPosition()
            x1 += c1.width

        else:
            c1 = self.commentList[0]
            x1, y1 = c1.getPosition()

        self.font = c1.font()   #Get font of character immediately to left of cursor

        size = c1.fontSize
        baseline_vert_offset = size * 0.1

        if -c1.top < size/2:
            h = size/2 + baseline_vert_offset
        else:
            h = -c1.top + baseline_vert_offset

        #Set cursor size and position
        self.cursor.setPosition(x1, y1+baseline_vert_offset, 1, 2, h)

        #Do this to prevent missing pixels as cursor is moved
        self.update()

        #Show current font in main window
        self.parentWindow.displayCurrentFont(self.font)


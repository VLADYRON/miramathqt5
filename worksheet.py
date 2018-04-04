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

#from PyQt4 import Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import *
import time
import copy
import execthread
import cPickle as pickle

from worksheetcursor import *
import equation
import image
import equationwidgets as EquationWidgets
import plot2d
import plot3d
import contourplot
import polarplot
import slider
import comment
import activebox


class WorkSheet(QGraphicsView):
    #Class variable definitions
    backgroundColor = QColor(205, 254, 255)
    clipboard = []

    def __init__(self, parent, runtime_status_message, num_equations_status_message, current_equation_status_message):
        QGraphicsView.__init__(self, parent)
        self.rubberband_start_x = 0
        self.rubberband_start_y = 0
        self.rubberband_start = False
        self.rubberband_move = False
        self.rubberband_move_trigger_threshold = 5
        self.rubberband = QRubberBand(QRubberBand.Rectangle, self)  #Create rubberband
        self.rubberband.hide()
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)

        #Switch to using OpenGL for view
#        glformat = QGLFormat(QGL.SampleBuffers)
#        glformat.setSamples(64)
#        glviewport = QGLWidget(glformat)
#        self.setViewport(glviewport)
#        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)

        self.is_current_tab = True

        #Create scene to hold all worksheet widgets
        self.grid_spacing = 10
        self.left_margin = 10
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        self.setSceneRect(0, 0, 4000, 4000)
        self.setRenderHint(QPainter.Antialiasing, False)
        self.centerOn(QPointF(0,0))     #Scroll viewport to top left corner of scene

        #Create cursor for this worksheet
        self.cursor = WorksheetCursor(5)
        self.scene.addItem(self.cursor)

        #Create empty equations object to hold all equationsdial
        self.equation_list = []
        self.comment_list = []
        self.image_list = []
        self.num_equations = 0
        self.currentEquationIndex = -1
        self.currentCommentIndex = -1
        self.currentImageIndex = -1
        self.mouseSelection = False
        self.selectedChars = set([])

        #Create a seperate thread in which equations will be evaluated and connect signal indicating a result is available
        self.execution_thread = execthread.ExecThread(self)
        self.execution_thread.show_results_signal.connect(self.update_results_handler, type=Qt.QueuedConnection)

        #Pointers to status messages in parent main window
        self.runtime_status_message = runtime_status_message
        self.num_equations_status_message = num_equations_status_message
        self.current_equation_status_message = current_equation_status_message

        self.runtime = 'Run Time: 0 s  '

        self.fileNameDir = None
        self.hasChanged = False
        self.parentWindow = parent

        self.font = QFont('Bitstream Vera Serif', 14)

        #Show page font in main window font toolbar
        self.parentWindow.displayCurrentFont(self.font)

        self.setPreferences()

        #Temporary
        self.testing()

    def testing(self):

#        #Draw some lines
#        c1=QGraphicsLineItem(20,100,600,100,None)
#        c2=QGraphicsLineItem(100,10,100,600,None)
#        self.scene.addItem(c1)
#        self.scene.addItem(c2)

#        pen=QPen(Qt.NoPen)
#        brush=QBrush(QColor('black'))
#        p1 = QPainterPath()
#        p1.addText(QPointF(0,0), self.font, str('.'))
#        d={'.': p1}
#        for i in xrange(10):
#            p = QPainterPath()
#            p.addText(QPointF(0,0), self.font, str(i))
#            d[str(i)]=p
#
#        t1=time.time()
#        x=100
#        y=100
#        for i in xrange(100):
#            for j in xrange(100):
#                v=str((i*100+j)/0.7363467)
#                for k, s in enumerate(v):
#                    path = d[s]
#                    c=QGraphicsPathItem(path)
#                    c.setPen(pen)
#                    c.setBrush(brush)
#                    c.show()
#                    self.scene.addItem(c)
#                    c.setPos(x+k*12, y)
#                x+=180
#            x = 100
#            y+=15
#        t2=time.time()
#        print 'time=', (t2-t1)/1000

        pass

    def setPreferences(self):
        brush = QBrush(self.backgroundColor)
        self.scene.setBackgroundBrush(brush)

    #*****************************************************************************************************
    #* Event handling methods
    #*****************************************************************************************************
    def mousePressEvent(self, event):
        QGraphicsView.mousePressEvent(self, event)

        button = event.button()
        position = event.pos()
        scene_position = self.mapToScene(position)
        x = position.x()
        y = position.y()

        #If no items were clicked then put worksheet cursor at clicked position
        item = self.itemAt(position)

        if (item == None or item == self.cursor) and button == 1:
            self.cursor.setPos(scene_position)
            self.cursor.show()
            self.rubberband_start = True
            self.rubberband_start_x = x
            self.rubberband_start_y = y

            #Empty space clicked, display worksheet font
            self.parentWindow.displayCurrentFont(self.font)

        #At least one equation was clicked when mouse pressed so hide worksheet cursor
        else:
            #Hide worksheet cursor and look for clicked char, if found make equation cursor visible
            self.cursor.hide()

            #Set this flag in case we are doing a selection
            self.currentEquationIndex = -1
            self.currentImageIndex = -1

            if item.object_type == 'character':
                self.mouseSelection = True
                parent_item = item.parentItem()  #Is the clicked char in an equation or a plot equation?
                parent_item_type = parent_item.object_type

                #A character in an equation was clicked on, deselect all other eqns/plots except this one
                if parent_item_type == 'equation':
                    #Unselect everything except this equation
                    self.unselectItems(parent_item)

                    self.currentEquationIndex = self.equation_list.index(parent_item)

                    #Indicate current font in main window
                    self.parentWindow.displayCurrentFont(parent_item.font)

                elif parent_item_type == 'plotequation':
                    #Get the parent plot
                    parent_item = parent_item.parentItem()

                    #Unselect everything except the plot associated with this equation
                    self.unselectItems(parent_item)

                    self.currentEquationIndex = self.equation_list.index(parent_item)

                    #Indicate current font in main window
                    self.parentWindow.displayCurrentFont(parent_item.font)

                elif parent_item_type == 'comment':
                    #Unselect everything except this comment
                    self.unselectItems(parent_item)

                    self.currentCommentIndex = self.comment_list.index(parent_item)

                    #Indicate current font in main window
                    self.parentWindow.displayCurrentFont(item.font())

                elif parent_item_type == 'image':
                    #Unselect everything except this image
                    self.unselectItems(parent_item)

                    self.currentImageIndex = self.image_list.index(parent_item)

                    #Indicate current font in main window
                    self.parentWindow.displayCurrentFont(parent_item.font)

            #If we are clicking on resize handles then deselect all equations except the highlighted eqn
            elif item.object_type == 'resizehandle':
                eqn = item.parentItem().parentItem()
                self.scene.clearSelection()
                eqn.setSelected(True)

            elif isinstance(item, activebox.ActiveBox):
                #Indicate current font in main window
                self.parentWindow.displayCurrentFont(item.parentItem().font)

            #Update status
            self.updateEquationStatusMessage()

    def mouseReleaseEvent(self, event):
        QGraphicsView.mouseReleaseEvent(self, event)
        position = event.pos()   #View coordinates
        scene_position = self.mapToScene(position)
        button = event.button()

        #Hide rubberband
        self.rubberband_start = False
        self.rubberband_move = False
        self.rubberband.hide()

        self.mouseSelection = False

        #Hide worksheet cursor when items are selected
        if len(self.scene.selectedItems()) > 0:
            self.cursor.hide()

            #If there are selected items, check if they were dragged
            changeflag = False
            for eqn in self.equation_list:
                if eqn.positionChanged:
                    eqn.positionChanged = False
                    changeflag = True
            if changeflag:
                self.showChangeOccured()

        #Empty part of scene was clicked so show cursor at position and execute all equations
        else:
            self.cursor.show()
            self.executeEquations()

    def mouseMoveEvent(self, event):
        QGraphicsView.mouseMoveEvent(self, event)

        button = event.button()
        position = event.pos()
        b = button & Qt.LeftButton

        if not self.mouseSelection:
            #Draw rubberband only if button was pressed and moved some distance
            if self.rubberband_start:
                x = position.x()
                y = position.y()
                if abs(x - self.rubberband_start_x) > self.rubberband_move_trigger_threshold or \
                   abs(y - self.rubberband_start_y) > self.rubberband_move_trigger_threshold:
                    self.rubberband_move = True
                    x, y, w, h = self.getRubberbandSize(x, y)
                    self.rubberband.setGeometry(x, y, w, h)
                    self.rubberband.show()

                    self.currentEquationIndex = -1
                    path = QPainterPath()
                    path.addRect(x, y, w, h)
                    self.scene.setSelectionArea(self.mapToScene(path))

    def getRubberbandSize(self, x2, y2):
        """Find top left corner of rubberband, and width and height.
        All coordinates are scene coordinates"""
        x1 = self.rubberband_start_x
        y1 = self.rubberband_start_y
        if x2 > x1:
            x = x1
            w = x2 - x1
        else:
            x = x2
            w = x1 - x2
        if y2 > y1:
            y = y1
            h = y2 - y1
        else:
            y = y2
            h = y1 - y2
        return (x, y, w, h)

    def keyPressEvent(self, event):
        QGraphicsView.keyPressEvent(self, event)
        key = event.key()

        #Worksheet is interested in only a few keys, the rest are forwarded to a new equation
        if key == Qt.Key_Left:
            self.keyLeft()
        elif key == Qt.Key_Right:
            self.keyRight()
        elif key == Qt.Key_Up:
            self.keyUp()
        elif key == Qt.Key_Down:
            self.keyDown()
        elif key == Qt.Key_Return:
            if not event.isAccepted():
                self.keyReturn()
        elif key == Qt.Key_Equal:
            self.keyEquals()
        elif key == Qt.Key_Backspace:
            self.keyBackspace()
        elif key == Qt.Key_Shift:
            pass
        elif key == Qt.Key_QuoteDbl:
            self.addNewComment()
        elif str(event.text()) in equation.Equation.allowedEquationKeys:
            #If worksheet cursor is visible then create new equation
            if self.cursor.isVisible():
                self.addNewEquation()

                #Now we know which equation we are adding character to
                self.equation_list[self.currentEquationIndex].handleKeyInput(event)
                self.equation_list[self.currentEquationIndex].setFocus()

                #Indicate a changed has occured in worksheet
                self.showChangeOccured()

    def processToolbuttonInput(self, button, *args):
        '''Handles input from all buttons in main window interface'''
        programming_buttons = set(['if', 'elif', 'else', 'for', 'while', 'break', 'continue', 'return'])

        #Return keyboard focus to worksheet
        self.setFocus()

        if button == 'plot2d':
            if self.cursor.isVisible():
                self.addNew2dPlot()

        elif button == 'contourplot':
            if self.cursor.isVisible():
                self.addNewContourPlot()

        elif button == 'plot3d':
            if self.cursor.isVisible():
                self.addNew3dPlot()

        elif button == 'polarplot':
            if self.cursor.isVisible():
                self.addNewPolarPlot()

        elif button == 'slider':
            if self.cursor.isVisible():
                self.addNewSlider()

        else:
            if self.cursor.isVisible() and \
                button not in programming_buttons:  #Don't allow programming buttons to create a new equation

                self.addNewEquation()

            if self.currentEquationIndex > -1:
                #Forward command to appropriate equation
                self.equation_list[self.currentEquationIndex].handleToolbuttonInput(button, *args)

                #Indicate a changed has occured in worksheet
                self.showChangeOccured()

            elif self.currentCommentIndex > -1:
                #Forward command to appropriate equation
                self.comment_list[self.currentCommentIndex].handleToolbuttonInput(button, *args)

                #Indicate a changed has occured in worksheet
                self.showChangeOccured()

    def keyBackspace(self):
        if self.cursor.isVisible() == False:
            equation_deleted_flag = self.processDelCharacter()
            if equation_deleted_flag:
                self.cursor.show()
        else:
            x = self.cursor.x()
            if x - self.grid_spacing < 0:
                delta_x = -x
            else:
                delta_x = -self.grid_spacing
            self.cursor.moveBy(delta_x, 0)
            self.ensureVisible(self.cursor, 0, 0)

    def keyLeft(self):
        if self.cursor.isVisible():
            x = self.cursor.x()
            if x - self.grid_spacing < 0:
                delta_x = -x
            else:
                delta_x = -self.grid_spacing
            self.cursor.moveBy(delta_x, 0)
            self.ensureVisible(self.cursor, 0, 0)

    def keyRight(self):
        if self.cursor.isVisible():
            x = self.cursor.x()
            if x + self.grid_spacing > 800:
                delta_x = 800 - x
            else:
                delta_x = self.grid_spacing
            self.cursor.moveBy(delta_x, 0)
            self.ensureVisible(self.cursor, 0, 0)

    def keyUp(self):
        if self.cursor.isVisible():
            y = self.cursor.y()
            if y - self.grid_spacing < 0:
                delta_y = -y
            else:
                delta_y = -self.grid_spacing
            self.cursor.moveBy(0, delta_y)
            self.ensureVisible(self.cursor, 0, 0)

    def keyDown(self):
        if self.cursor.isVisible():
            y = self.cursor.y()
            if y + self.grid_spacing > 1000:
                delta_y = 1000 - y
            else:
                delta_y = self.grid_spacing
            self.cursor.moveBy(0, delta_y)
            self.ensureVisible(self.cursor, 0, 0)

    def keyEquals(self):
        if self.currentEquationIndex > -1:
            eqn = self.equation_list[self.currentEquationIndex]
            p = eqn.scenePos()
            x = p.x()
            y = p.y() + eqn.bottom + eqn.font.pointSize() * 2
            self.cursor.setPos(x, y)
            self.cursor.show()
            self.executeEquations()

    def keyReturn(self):
        if self.currentEquationIndex > -1:
            eqn = self.equation_list[self.currentEquationIndex]
            self.executeEquations()
            p = eqn.scenePos()
            x = p.x()
            y = p.y() + eqn.bottom + eqn.font.pointSize() * 2
            self.cursor.setPos(x, y)
            self.cursor.show()
            self.ensureVisible(self.cursor, 0, 0)

        elif self.currentImageIndex > -1:
            img = self.image_list[self.currentImageIndex]
            self.executeEquations()
            p = img.scenePos()
            x = p.x()
            y = p.y() + img.bottom + img.font.pointSize() * 2
            self.cursor.setPos(x, y)
            self.cursor.show()
            self.ensureVisible(self.cursor, 0, 0)

        else:
            #Shift all equations below cursor down
            self.moveEquationsDown(self.cursor.pos(), self.grid_spacing)

            y = self.cursor.y() + self.grid_spacing
            x = self.cursor.x()
            if y > 900:
                y = 900
            self.cursor.setPos(x, y)
            self.ensureVisible(self.cursor, 0, 0)

    def processDelCharacter(self):
        #Returns True if equation or comment deleted
        ret_val = False
        if self.currentEquationIndex != -1:
            eqn = self.equation_list[self.currentEquationIndex]

            #Delete equation if it's length is zero
            if eqn.object_type == 'equation' and eqn.length == 0:

                #Indicate a changed has occured in worksheet
                self.showChangeOccured()

                eqn = self.equation_list.pop(self.currentEquationIndex)
                self.currentEquationIndex = -1
                self.num_equations -= 1
                self.scene.removeItem(eqn)
                self.cursor.setPos(eqn.pos())
                del eqn

                #Re-execute equations after equation removed
                self.executeEquations()
                ret_val = True

        elif self.currentCommentIndex != -1:
            comment = self.comment_list[self.currentCommentIndex]

            #Delete equation if it's length is zero
            if comment.length == 0:

                #Indicate a changed has occured in worksheet
                self.showChangeOccured()

                comment = self.comment_list.pop(self.currentCommentIndex)
                self.currentCommentIndex = -1
                self.scene.removeItem(comment)
                self.cursor.setPos(comment.pos())
                del comment

                ret_val = True  #Equation was deleted

        else:
            #Do we have a bunch of equations selected?
            if self.num_equations > 0:
                i = self.num_equations-1
                equations_deleted = False
                while i > -1:
                    eqn = self.equation_list[i]
                    if eqn.isSelected():
                        equations_deleted = True
                        eqn = self.equation_list.pop(i)

                        #Remove item (including children objects) from scene and obliterate remains of equation
                        self.scene.removeItem(eqn)
                        self.num_equations -= 1
                        last_position_position = eqn.pos()
                        del eqn
                        ret_val = True
                    i -= 1

                if equations_deleted:
                    #Put worksheet cursor at the coordinates of first deleted eqn
                    self.cursor.setPos(last_position_position)

                    #Re-execute remaining equations after all selected equation(s) have been removed
                    self.executeEquations()

                    #Indicate a changed has occured in worksheet
                    self.showChangeOccured()

        #Update indicated number of equations in status message
        self.updateEquationStatusMessage()
        return ret_val

    def addNewEquation(self):
        self.cursor.hide()
        position = self.cursor.pos() #Location for new equation if one is created
        new_equation = equation.Equation(None, position, self.font)
        self.equation_list.append(new_equation)
        self.scene.addItem(new_equation)  #Add new equation to worksheet
        self.num_equations += 1
        self.currentEquationIndex = self.equation_list.index(new_equation)

        #Let the new equation know where it is in the list of equations
        new_equation.equationIndex = self.currentEquationIndex

        #Sort equations
        self.sortEquationPositions()

        #Update status message to reflect new number of equations
        self.updateEquationStatusMessage()

    def addNew2dPlot(self):
        self.cursor.hide()
        position = self.cursor.pos() #Location for new equation if one is created
        new_plot = plot2d.Plot2d(None, position, self.font)
        self.equation_list.append(new_plot)
        self.scene.addItem(new_plot)  #Add new equation to worksheet
        self.num_equations += 1
        self.currentEquationIndex = self.equation_list.index(new_plot)

        #Let the new equation know where it is in the list of equations
        new_plot.equationIndex = self.currentEquationIndex

        #Sort equations
        self.sortEquationPositions()

        #Update status message to reflect new number of equations
        self.updateEquationStatusMessage()

    def addNewContourPlot(self):
        self.cursor.hide()
        position = self.cursor.pos() #Location for new equation if one is created
        new_plot = contourplot.Plot2dContour(None, position, self.font)
        self.equation_list.append(new_plot)
        self.scene.addItem(new_plot)  #Add new equation to worksheet
        self.num_equations += 1
        self.currentEquationIndex = self.equation_list.index(new_plot)

        #Let the new equation know where it is in the list of equations
        new_plot.equationIndex = self.currentEquationIndex

        #Sort equations
        self.sortEquationPositions()

        #Update status message to reflect new number of equations
        self.updateEquationStatusMessage()

    def addNewPolarPlot(self):
        self.cursor.hide()
        position = self.cursor.pos() #Location for new equation if one is created
        new_plot = polarplot.PolarPlot(None, position, self.font)
        self.equation_list.append(new_plot)
        self.scene.addItem(new_plot)  #Add new equation to worksheet
        self.num_equations += 1
        self.currentEquationIndex = self.equation_list.index(new_plot)

        #Let the new equation know where it is in the list of equations
        new_plot.equationIndex = self.currentEquationIndex

        #Sort equations
        self.sortEquationPositions()

        #Update status message to reflect new number of equations
        self.updateEquationStatusMessage()

    def addNew3dPlot(self):
        self.cursor.hide()
        position = self.cursor.pos() #Location for new equation if one is created
        new_plot = plot3d.Plot3d(None, position, self.font)
        self.equation_list.append(new_plot)
        self.scene.addItem(new_plot)  #Add new equation to worksheet
        self.num_equations += 1
        self.currentEquationIndex = self.equation_list.index(new_plot)

        #Let the new equation know where it is in the list of equations
        new_plot.equationIndex = self.currentEquationIndex

        #Sort equations
        self.sortEquationPositions()

        #Update status message to reflect new number of equations
        self.updateEquationStatusMessage()

    def addNewSlider(self):
        self.cursor.hide()
        position = self.cursor.pos() #Location for new equation if one is created
        new_slider = slider.Slider(None, position, self.font, self)
        self.equation_list.append(new_slider)
        self.scene.addItem(new_slider)  #Add new equation to worksheet
        self.num_equations += 1
        self.currentEquationIndex = self.equation_list.index(new_slider)

        #Let the new equation know where it is in the list of equations
        new_slider.equationIndex = self.currentEquationIndex

        #Sort equations
        self.sortEquationPositions()

        #Update status message to reflect new number of equations
        self.updateEquationStatusMessage()

    def addNewComment(self):
        self.cursor.hide()
        position = self.cursor.pos() #Location for new equation if one is created

        #Create comment object
        new_comment = comment.Comment(None, position, self.font, self.parentWindow)

                #Indicate a changed has occured in worksheet
  #              self.showChangeOccured()

        #Add to canvas
        self.comment_list.append(new_comment)
        self.scene.addItem(new_comment)  #Add new new_comment to worksheet
        self.currentCommentIndex = self.comment_list.index(new_comment)
        self.comment_list[self.currentCommentIndex].setFocus()

    def addNewImage(self):
        self.cursor.hide()
        position = self.cursor.pos() #Location for new equation if one is created

        #Create comment object
        new_image = image.Image(None, position, self.font)

        #Indicate a changed has occured in worksheet
        self.showChangeOccured()

        #Add to canvas
        self.image_list.append(new_image)
        self.scene.addItem(new_image)  #Add new new_comment to worksheet
        self.currentImageIndex = self.image_list.index(new_image)
        self.image_list[self.currentImageIndex].setFocus()

    def unselectItems(self, keep_selected_item):
        #Unselect everything except keep_selected_item
        for item in self.equation_list:
            if item != keep_selected_item:
                item.setSelected(False)

        for item in self.comment_list:
            if item != keep_selected_item:
                item.setSelected(False)

        for item in self.image_list:
            if item != keep_selected_item:
                item.setSelected(False)

    #*************************************************************************************************
    #* Methods below handle cut, paste, insert
    #*************************************************************************************************
    def selectAll(self):
        #Hide worksheet/equation cursor
        if self.currentEquationIndex > -1:
            self.currentEquationIndex = -1
            eqn = self.equation_list[self.currentEquationIndex]
            eqn.hideCursor()
        self.cursor.hide()

        #Select all the equations
        for eqn in self.equation_list:
            eqn.setSelected(True)

    def copy(self):
        copyitems = self.scene.selectedItems()
        num = len(copyitems)

        #More than one worksheet (equation, plot) object selected
        if num > 1:
            l = []
            for item in copyitems:
                d = item.getDictionary()
                l.append(d)
            WorkSheet.clipboard = l

        #One object selected
        elif num == 1:
            item = copyitems[0]
            if item.object_type == 'equation':

                #Copy only selected part of equation
                if item.showSelectionBox:
                    WorkSheet.clipboard = item.copyFromEquation()

                #Copy entire equation
                else:
                    d = item.getDictionary()
                    WorkSheet.clipboard = [d]

    def cut(self):
        copyitems = self.scene.selectedItems()
        num = len(copyitems)

        #More than one equation selected
        if num > 1:
            l = []
            for item in copyitems:
                #Save dictionary of each item so that it can be re-created in paste
                d = item.getDictionary()
                l.append(d)

                #Call this to push character items back onto their stack
                item.removeObjectsFromList(0, item.length)

                #Remove item from scene and list
                self.scene.removeItem(item)
                self.equation_list.remove(item)

            self.num_equations -= num
            self.currentEquationIndex = -1
            WorkSheet.clipboard = l

            #Re-execute worksheet minus deleted equations
            self.cursor.show()
            self.executeEquations()

        #One equation selected
        elif num == 1:
            item = copyitems[0]

            #Figure out if we are cutting an entire equation or just part of it
            if item.object_type == 'equation':

                #Cut only selected part of equation
                if item.showSelectionBox:
                    WorkSheet.clipboard = item.cutFromEquation()

                    #If all visible objects in equation have been cut then delete remains of equation
                    if item.length == 0:
                        self.scene.removeItem(item)
                        self.equation_list.remove(item)
                        self.num_equations -= 1
                        self.currentEquationIndex = -1

                        #Re-execute worksheet minus deleted equations
                        self.cursor.show()
                        self.executeEquations()

                #Cut entire equation
                else:
                    #Save equations dictionary
                    d = item.getDictionary()
                    WorkSheet.clipboard = [d]

                    #Call this to push character items back onto their stack
                    item.removeObjectsFromList(0, item.length)

                    #Remove item from scene and list
                    self.scene.removeItem(item)
                    self.equation_list.remove(item)
                    self.num_equations -= 1
                    self.currentEquationIndex = -1

                    #Re-execute worksheet minus deleted equations
                    self.cursor.show()
                    self.executeEquations()

    def paste(self):
        #Make sure something is in clipboard
        clipboard = WorkSheet.clipboard

        if len(clipboard):

            #Paste to worksheet at cursor position
            if self.cursor.isVisible():
                self.cursor.hide()
                cursor_position = self.cursor.pos()
                d0 = clipboard[0]

                #Does clipboard hold a list of equations?
                if d0['object_type'] == 'equation':
                    #First item on clipboard is an equation so must be pasting 1 or more equations
                    deltax = cursor_position.x() - d0['savex']
                    deltay = cursor_position.y() - d0['savey']

                    for d in clipboard:
                        #Create new object and load its' dictionary
                        eqn = equation.Equation(QPointF(0,0))
                        eqn.setDictionary(d)
                        eqn.moveBy(deltax, deltay)
                        self.equation_list.append(eqn)
                        self.scene.addItem(eqn)
                        eqn.equationIndex = self.equation_list.index(eqn)

                    self.num_equations += len(clipboard)
                    self.currentEquationIndex = -1

                #Clipboard holds individual characters (part of an equation previously copied/cut)
                elif d0['object_type'] == 'character' or d0['object_type'] == 'keyword':
                    #Create new equation
                    eqn = equation.Equation(None, cursor_position,  self.font)

                    #Plug clipboard data into new equation and update
                    eqn.pasteIntoEquation(clipboard)
                    self.equation_list.append(eqn)
                    self.scene.addItem(eqn)
                    i = self.equation_list.index(eqn)
                    eqn.equationIndex = i
                    self.num_equations += 1
                    self.currentEquationIndex = i

                #Sort equations
                self.sortEquationPositions()

                #Indicate a changed has occured in worksheet
                self.showChangeOccured()

                #Update status message to reflect new number of equations
                self.updateEquationStatusMessage()

                #New Equations have been created so re-execute worksheet
                self.cursor.show()
                self.executeEquations()

            #Worksheet cursor not visible, so try to paste into an equation
            else:
                if self.currentEquationIndex != -1:
                    eqn = self.equation_list[self.currentEquationIndex]
                    d0 = clipboard[0]

                    #Only paste if clipboard holds part of an equation
                    if d0['object_type'] == 'character' or d0['object_type'] == 'keyword':
                        #Paste into equation at cursor position
                        eqn.pasteIntoEquation(clipboard)

                    #Indicate a changed has occured in worksheet
                    self.showChangeOccured()

    #**********************************************************************************************
    #* Methods below handle allignment of equations
    #**********************************************************************************************
    def allignLeft(self):
        items = self.scene.selectedItems()

        maxleft = 10000
        if len(items) > 1:
            for item in items:
                left = item.pos().x()
                if left < maxleft:
                    maxleft = left

            for item in items:
                x = item.pos().x()
                item.moveBy(maxleft-x, 0)

            #Indicate a changed has occured in worksheet
            self.showChangeOccured()

    def allignRight(self):
        items = self.scene.selectedItems()

        maxright = -10000
        if len(items) > 1:
            for item in items:
                right = item.pos().x() + item.width
                if right > maxright:
                    maxright = right

            for item in items:
                r = item.pos().x() + item.width
                item.moveBy(maxright-r, 0)

            #Indicate a changed has occured in worksheet
            self.showChangeOccured()

    def allignTop(self):
        items = self.scene.selectedItems()

        maxtop = 10000
        if len(items) > 1:
            for item in items:
                top = item.top + item.pos().y()
                if top < maxtop:
                    maxtop = top

            for item in items:
                t = item.top + item.pos().y()
                item.moveBy(0, maxtop-t)

            #Indicate a changed has occured in worksheet
            self.showChangeOccured()

    def allignBottom(self):
        items = self.scene.selectedItems()

        maxbottom = -10000
        if len(items) > 1:
            for item in items:
                bottom = item.bottom + item.pos().y()
                if bottom > maxbottom:
                    maxbottom = bottom

            for item in items:
                b = item.bottom + item.pos().y()
                item.moveBy(0, maxbottom-b)

            #Indicate a changed has occured in worksheet
            self.showChangeOccured()

    def isEmpty(self):
        retval = False

        #If we only have cursor on page then consider it to be empty
        if len(self.scene.items()) <= 1:
            retval = True
        return retval

    #**************************************************************************************************
    #* Methods below handle load/save
    #**************************************************************************************************
    def saveWorksheet(self, name=None):
        l = []
        for eqn in self.equation_list:
            d = eqn.getDictionary()
            l.append(d)

        #Are we using 'Save' or 'SaveAs' ?
        if name == None:
            name = self.fileNameDir
        else:
            self.fileNameDir = name

        f = open(name, 'wb')
        pickle.dump(l, f)
        f.close()

        #Reset some flags
        self.hasChanged = False

    def loadWorksheet(self, name):
        #Open file, load data and un-serialize it
        self.fileNameDir = name
        f = open(name, 'rb')
        l = pickle.load(f)
        f.close()

        #Create and initialize each equation using loaded data
        position = QPointF(0, 0)
        self.num_equations = len(l)
        for d in l:
            new_equation = equation.Equation(None, position,  self.font)
            self.equation_list.append(new_equation)
            self.scene.addItem(new_equation)
            new_equation.setDictionary(d)
            new_equation.equationIndex = self.equation_list.index(new_equation)

        self.currentEquationIndex = -1

        #Update status message to reflect new number of equations
        self.updateEquationStatusMessage()

    #***************************************************************************************************
    # Methods for executing everythang on worksheet
    #***************************************************************************************************
    def executeEquations(self):
        self.scene.clearSelection()
        self.currentEquationIndex = -1   #Make sure no equations are active

        #Update status
        self.runtime = 'Run Time: ---  '
        self.updateEquationStatusMessage()

        #Wait for previous execution to complete. User will have to click mouse again!
        if self.execution_thread.program_q.qsize() == 0 and self.equation_list:

            #Reset working dictionary in thread to {}
            self.execution_thread.reset()

            #Execute equations in the order they appear on screen
            self.sortEquationPositions()

            self.start_time = time.time()

            #Perform two passes. First run through all global definitions then run all equations
            for eqn in self.equation_list:
                if eqn.isGlobalDefinition:
                    t = eqn.tryToExecuteEquation()

                    #Ship data over to execution thread if valid
                    if t:
                        self.execution_thread.do_computation(t)

            for eqn in self.equation_list:
                t = eqn.tryToExecuteEquation()

                #Ship data over to execution thread if valid
                if t:
                    self.execution_thread.do_computation(t)

            #Remember ID of last equation sent to thread
            self.last_object_id = self.equation_list[-1].object_id

        else:
            print 'No equations or work Q full, wait!'

    def quickExecuteEquations(self):
        #Wait for previous execution to complete. User will have to click mouse again!
        if self.execution_thread.program_q.qsize() == 0 and self.equation_list:

            #Reset working dictionary in thread to {}
            self.execution_thread.reset()

            self.start_time = time.time()

            #Perform two passes. First run through all global definitions then run all equations
            for eqn in self.equation_list:
                if eqn.isGlobalDefinition:
                    t = eqn.tryToExecuteEquation()

                    #Ship data over to execution thread if valid
                    if t:
                        self.execution_thread.do_computation(t)

            for eqn in self.equation_list:
                t = eqn.tryToExecuteEquation()

                #Ship data over to execution thread if valid
                if t:
                    self.execution_thread.do_computation(t)

            #Remember ID of last equation sent to thread
            self.last_object_id = self.equation_list[-1].object_id

        else:
            print 'No equations or work Q full, wait!'

    #This handles asynchronous Qt signals from equation execution thread.
    #Thread fire out signals when it has a result to show
    def update_results_handler(self, n):
        #Get equation results off Q. q_item should hold a list of tuples, except the last element=object_id
        q_item = self.execution_thread.results_q.get()

        #Get hash ID of equation associated with the results. Calculate index of equation based on hash value.
        object_id = q_item.pop()
        m = map(id, self.equation_list)

        #Go and draw equation results on screen. Pass a list of tuples to equation/plot
        if object_id in m:
            i = m.index(object_id)
            self.equation_list[i].show_result(q_item)

        if object_id == self.last_object_id:
            end_time = time.time()
            diff = end_time - self.start_time
            seconds = int(diff)
            milliseconds = int((diff - seconds) * 1000)
            if seconds:
                runtime = 'Run Time: %.1f s  ' % diff
            else:
                runtime = 'Run Time: %s ms  ' % milliseconds

            if self.is_current_tab:
                self.runtime_status_message.setText(runtime)

            self.runtime = runtime

    def sortEquationPositions(self):
        eqnlist = self.equation_list

        #Do the sort; index of each equation in list corresponds to its location on the screen
        eqnlist.sort(self.compareEquationPositions)

        #Update equations own record of its' index
        temp = self.currentEquationIndex
        for i, eqn in enumerate(eqnlist):
            #Look at old index of equation; if old index=currentEquationIndex then set
            #currentEquationIndex to new index
            if eqn.equationIndex == temp:
                self.currentEquationIndex = i

            #Let the current equation know where it is at in the list of equations
            eqn.equation_index = i

    def compareEquationPositions(self, eqn1, eqn2):
        """Compares the positions of two equations on the graphics scene
        returns -1 is eqn1 is above eqn2 or if eqn1 and eqn2 are on the same line and eqn1 is to the left of eqn2
        returns 0 if eqn1 and eqn2 are at the same spot
        returns 1 for all other cases"""
        x1 = eqn1.pos().x()
        x2 = eqn2.pos().x()
        y1 = eqn1.pos().y()
        y2 = eqn2.pos().y()
        if y1 < y2:
            #Point is above
            return -1
        elif y1 > y2:
            #Point is below
            return 1
        else:
            #Points on same line
            if x1 < x2:
                return -1
            elif x1 > x2:
                return 1
            else:
                return 0

    def moveEquationsDown(self, cursor_position, delta_y):  #Scene coordinates
        """Move all equations below current worksheet cursor position down by one grid spacing"""
        y1 = cursor_position.y()
        moved = False
        for eqn in self.equation_list:
            y2 = eqn.pos().y()
            if y2 > y1:
                eqn.moveBy(0, delta_y)
                moved = True

        if moved:
            #Indicate a changed has occured in worksheet
            self.showChangeOccured()

    def updateEquationStatusMessage(self):
        num = self.num_equations
        if num < 10:
            num_string = ' ' + str(num)
        else:
            num_string = str(num)
        num = str(self.num_equations)
        text = 'Equation Count: ' + num_string
        self.num_equations_status_message.setText(text)

        num = self.currentEquationIndex + 1
        if num == 0:
            num_string = 'None'
        elif num < 10:
            num_string = ' ' + str(num)
        else:
            num_string = str(num)
        num = str(self.num_equations)
        text = 'Current Equation: ' + num_string
        self.current_equation_status_message.setText(text)
        self.runtime_status_message.setText(self.runtime)

    def showChangeOccured(self):
        '''This method is called anytime a change happens, e.g. something gets moved, a key is pressed'''
        #Set flag to indicate a changed has been made to worksheet
        self.hasChanged = True
        self.parentWindow.setWindowModified(True)

    def fontSelected(self, fontname):
        self.setFocus()
        items = self.scene.selectedItems()

        if items:
            for item in items:
                if item.object_type == 'equation' or item.object_type == 'comment' or item.object_type == 'plot' or \
                   item.object_type == 'image' or item.object_type == 'slider':
                    item.setFont(fontname)

        else:
            #If no equations are selected then change default font for page
            #Any new equations, plots, etc will use this font
            self.font.setFamily(fontname)

    def fontSize(self, size):
        self.setFocus()
        items = self.scene.selectedItems()

        if items:
            for item in items:
                if item.object_type == 'equation' or item.object_type == 'comment' or item.object_type == 'plot' or \
                   item.object_type == 'image' or item.object_type == 'slider':
                    item.setFontSize(size)

        else:
            #If no equations selected then change default page font size
            #Any new equations, plots, etc will use this size
            self.font.setPointSize(size)

    def bold(self, state):
        self.setFocus()
        items = self.scene.selectedItems()

        if items:
            for item in items:
                if item.object_type == 'comment':
                    item.setBold(state)

    def underline(self, state):
        self.setFocus()
        items = self.scene.selectedItems()

        if items:
            for item in items:
                if item.object_type == 'comment':
                    item.setUnderline(state)

    def italic(self, state):
        self.setFocus()
        items = self.scene.selectedItems()

        if items:
            for item in items:
                if item.object_type == 'comment':
                    item.setItalic(state)



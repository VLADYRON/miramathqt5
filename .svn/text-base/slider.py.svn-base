
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.Qwt5 as Qwt

from activebox import *
from shadowbox import *
from plotequation import *
from equation import *
from colorbutton import ColorButton
from equationwidgets import EquationChar


class Slider(QGraphicsRectItem):
    highlighted_color = QColor(144, 238, 144,  128) #Background color of selected equation
    cursor_over_equation_color = QColor(0, 0xfd, 0xf8, 128)
    new_slider_value = pyqtSignal()
    border_width = 20
    min_limit_eqn_horiz_spacing = 2
    limit_eqn_vert_spacing = 0.5
    slider_thumb_height = 1.5
    slider_thumb_length = 1
    slider_length = 15


    def __init__(self, parent, position, font, worksheet):
        QGraphicsRectItem.__init__(self, parent)
        self.finishedInit = False

        self.setToolTip('Slider')
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.setCursor(Qt.ArrowCursor)
        self.setAcceptsHoverEvents(True)
        self.setZValue(90)  #Z value on worksheet
        self.setPos(position)
        self.object_type = 'slider'
        self.worksheet = worksheet
        self.slider_value = 0
        self.currentIndex = -1  #Index of this equation in worksheets list
        self.positionChanged = False
        self.isGlobalDefinition = False #Global definitions will be executed before all others
        self.font = QFont(font.family(), font.pointSize())
        self.initial_width = Slider.slider_length * font.pointSize()
        self.width = 0
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.character_clicked = False
        self.currentEquation = None
        self.object_id = id(self)  # Unique ID for instance
        self.shadowBox = ShadowBox(self)
        self.shadowBox.setColor(Slider.cursor_over_equation_color)
        self.activeBox = ActiveBox('slider', self)
        self.activeBox.setColor(Slider.highlighted_color)
        self.border_color = QColor('black')
        self.border_width = 1
        self.background_color = QColor(QColor(0, 0, 0, 0))
        self.setPen(QPen(Qt.NoPen))

        #Create Qt slider widget
        slider_widget = SliderWidget(self, font)
        slider_widget.connect(slider_widget, SIGNAL('valueChanged(double)'), self.slider_moved)
        self.slider_widget = slider_widget

        #Insert widget into proxy graphics item
        self.slider = QGraphicsProxyWidget(self, Qt.Widget)  #Pass self as parent, window flags
        self.slider.setWidget(slider_widget)
        self.slider.setZValue(2)
        self.slider.setWindowFrameMargins(0, 0, 0, 0)

        self.slider.object_type = 'slider'

        #Create equal sign
        self.equal_sign = EquationChar(self, ' := ', ' := ', font)

        #Create variable equation object
        self.variable_equation = PlotEquation(self, QPointF(0, 0), font)
        self.variable_equation.isAssignment = True
        self.variable_equation.setToolTip('Variable')

        #Create x and y axis limit equations
        self.min_value_eqn = PlotEquation(self, QPointF(0, 0), self.font)
        self.min_value_eqn.setToolTip('Minimum value')
        self.max_value_eqn = PlotEquation(self, QPointF(0, 0), self.font)
        self.max_value_eqn.setToolTip('Maximum value')

        #Set initial size and do the initial layout of all the various bits and pieces
        self.layout_slider(self.initial_width)

        self.finishedInit = True
        self.setSelected(True)

    def mousePressEvent(self, event):
        QGraphicsRectItem.mousePressEvent(self, event)

        #Set cursor to closed hand
        self.setCursor(Qt.ClosedHandCursor)

        #Mouse click position
        p = event.pos()
        s = event.scenePos()

        #Are we clicking on a resize handle?
        self.resizeStartHandle = self.activeBox.mouseInResizeHandle(p)

        #Hide all equation cursors, then show equation cursor for clicked equation
        self.variable_equation.cursor.hide()
        self.variable_equation.clearSelectionBox()
        self.min_value_eqn.cursor.hide()
        self.min_value_eqn.clearSelectionBox()
        self.max_value_eqn.cursor.hide()
        self.max_value_eqn.clearSelectionBox()

        item = self.scene().itemAt(s)
        if item.object_type == 'character':
            #Which equation was clicked?  Remember which equation is accepting mainwindow toolbutton clicks
            self.currentEquation = item.parentItem()
            self.currentEquation.cursor.show()

            #Set this flag to true if we are clicking on a char, used below in mouse move event handler
            self.character_clicked = True
        else:
            self.currentEquation = None

    def mouseMoveEvent(self, event):
        r = self.resizeStartHandle

        #Equation is being resized (has a table in it)
        if r:
            p = event.pos()
            b = Slider.border_width
            plot = self.slider_widget
            x = p.x()
            y = p.y()

            #Right middle resize handle dragged
            if r == 1:
                self.layout_slider(x-b)

            #Left middle resize handle dragged
            elif r == 2:
                old_width = self.width
                self.layout_slider(self.width-x-b)
                deltax = old_width - self.width
                self.moveBy(deltax, 0)

        #Is mouse being dragged over an equation
        elif self.character_clicked:
            s = event.scenePos()
            item = self.scene().itemAt(s)

            #Make sure mouse is dragged over char in same equation that was initially clicked
            if item.object_type == 'character' and item.parentItem() == self.currentEquation:
                #Which equation was clicked?  Remember which equation is accepting mainwindow toolbutton clicks
                self.currentEquation.setSelectionBox(item)

        elif 1:
            QGraphicsRectItem.mouseMoveEvent(self, event)

    def mouseReleaseEvent(self, event):
        QGraphicsRectItem.mouseReleaseEvent(self, event)
        self.setCursor(Qt.OpenHandCursor)
        self.resizeStartHandle = 0
        self.character_clicked = False

    def mouseDoubleClickEvent(self, event):
        QGraphicsRectItem.mouseDoubleClickEvent(self, event)

    def keyPressEvent(self, event):
        #Do not allow key event to pass up the chain

        #Update size of plot after key press
        self.layout_slider(self.width)

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)
        if not self.isSelected():
            self.shadowBox.show()

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.ArrowCursor)
        if not self.isSelected():
            self.shadowBox.hide()

    def itemChange(self, change, value):
        #Look for select/deselect events
        if change == QGraphicsRectItem.ItemSelectedChange:# and self.finishedInit:

            if value.toInt()[0] and self.finishedInit:
                #Plot was selected so show active box and hide shadow box
                self.activeBox.showBox(True)
                self.shadowBox.hide()

                #Show limit equations
                self.min_value_eqn.show()
                self.max_value_eqn.show()

            else:
                #Plot was deselected, hide cursors, active box and selection box
                self.variable_equation.cursor.hide()
                self.min_value_eqn.cursor.hide()
                self.max_value_eqn.cursor.hide()
                self.activeBox.hideBox()

                #Hide limit equations
                self.min_value_eqn.hide()
                self.max_value_eqn.hide()

        #Look for movement of plot (has it been dragged?)
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            self.positionChanged = True

        return QGraphicsRectItem.itemChange(self, change, value)

    def slider_moved(self, value):
        self.slider_value = value
        self.worksheet.quickExecuteEquations()

        #self.new_slider_value.emit()
        #self.slider_widget.emit(SIGNAL("new_slider_value()"))

    def handleToolbuttonInput(self, button, *args):
        #Handle inputs from mainwindow tool buttons
        if self.currentEquation:
            self.currentEquation.handleToolbuttonInput(button, *args)

            #Update layout after equation is edited
            self.layout_slider(self.width)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def setFontSize(self, size):
        self.font.setPointSize(size)
        self.slider_widget.setFont(self.font)
        self.variable_equation.setFontSize(size)
        self.equal_sign.setSize(size)
        self.min_value_eqn.setFontSize(size)
        self.max_value_eqn.setFontSize(size)

        slider_widget = self.slider_widget
        slider_widget.setThumbLength(Slider.slider_thumb_length*size)
        slider_widget.setThumbWidth(Slider.slider_thumb_height*size)
        slider_widget.setBorderWidth(0.2*size)

        self.layout_slider(self.width)

    def setFont(self, fontname):
        self.font.setFamily(fontname)
        self.slider_widget.setFont(self.font)
        self.variable_equation.setFont(fontname)
        self.equal_sign.setFontName(fontname)
        self.min_value_eqn.setFont(fontname)
        self.max_value_eqn.setFont(fontname)

        self.layout_slider(self.width)

    def layout_slider(self, new_width):
        font_size = self.font.pointSize()
        slider_widget = self.slider_widget
        min_recommended_slider_width = slider_widget.minimumSizeHint().width()
        min_recommended_slider_height = slider_widget.minimumSizeHint().height() + 0.1 * font_size

        hmin = self.min_value_eqn.height
        hmax = self.max_value_eqn.height

        #Set label position
        self.variable_equation.setPos(0, 0)
        x = self.variable_equation.width

        #Position equal sign
        self.equal_sign.setPosition(x, 0)
        x += self.equal_sign.width

        #Get width of min and max labels + spacing between the two
        total_limit_width = self.min_value_eqn.width + self.max_value_eqn.width + font_size * Slider.min_limit_eqn_horiz_spacing

        #Compute minimum total width = width of variable + width of equal sign + width of min,max,spacing
        min_total_width = x + total_limit_width

        #Limit smallest size
        if new_width < min_total_width:
            new_width = min_total_width

        slider_length = new_width - x

        if slider_length < min_recommended_slider_width:
            slider_length = min_recommended_slider_width

        #Finally set size of slider widget
        slider_widget.setGeometry(0, 0, slider_length, min_recommended_slider_height)

        #Get y coord for slider widget and find bottom
        y=-Slider.slider_thumb_height * font_size
        self.bottom = min_recommended_slider_height + y

        #Position slider
        self.slider.setPos(x, y)

        #Get y for limit equations
        y -= Slider.limit_eqn_vert_spacing * font_size

        #Find top
        t1 = y - hmin
        t2 = y - hmax
        if t1 < t2:
            self.top = t1
            h_limit = hmin
        else:
            self.top = t2
            h_limit = hmax

        #Position lower limit equation
        self.min_value_eqn.setPos(x, y-self.min_value_eqn.bottom)
        x += slider_length

        #Position upper limit equation
        self.max_value_eqn.setPos(x-self.max_value_eqn.width, y-self.max_value_eqn.bottom)

        #Figure out position and size of active box
        b = Slider.border_width
        h = min_recommended_slider_height + Slider.limit_eqn_vert_spacing * font_size + h_limit
        w = x
        self.shadowBox.setRect(-b, self.top-b, w+2*b, h+2*b)
        self.activeBox.setSize(w+2*b, h+2*b)
        self.activeBox.setPos(-b, self.top-b)
        self.setRect(-b, self.top-b, w+2*b, h+2*b)

        self.width = w
        self.height = h

    def getDict(self):
        d = self.__dict__.copy()
        return d

    #*************************************************************************************
    #*Methods below this point handle executing plot
    #*************************************************************************************
    def tryToExecuteEquation(self):

        all_equations = [self.variable_equation, self.min_value_eqn, self.max_value_eqn]
        self.all_plot_equations = all_equations

        programs = []

        t1 = self.variable_equation.tryToExecuteEquation()
        t2 = self.min_value_eqn.tryToExecuteEquation()
        t3 = self.max_value_eqn.tryToExecuteEquation()

        if t1 != None:
            variable_program = t1[0] + ' = %s' % self.slider_value
            new_t1 = (variable_program, t1[1], t1[2], t1[3], t1[4])
            programs.append(new_t1)
        else:
            self.variable_equation.setColor(QColor('red'))
            self.variable_equation.setToolTip('Could not parse equation')

        if t2 != None:
            programs.append(t2)
        else:
            self.min_value_eqn.setColor(QColor('red'))
            self.min_value_eqn.setToolTip('Could not parse equation')

        if t3 != None:
            programs.append(t3)
        else:
            self.max_value_eqn.setColor(QColor('red'))
            self.max_value_eqn.setToolTip('Could not parse equation')

        if len(programs) > 0:
            programs.append(self.object_id)
            return programs

        #No valid equations found so do nothing
        else:
            return None

    def show_result(self, q_item):
        all_equations = self.all_plot_equations

        j = 0
        for i, eqn in enumerate(all_equations):
            if eqn.is_valid:
                results = q_item[j]
                j += 1
                result = results[0]
                error = results[1]

                if error != None:
                    eqn.result = None
                    eqn.setColor(QColor('red'))
                    eqn.setToolTip(error)

                else:
                    eqn.result = result
                    eqn.setColor(QColor('black'))
                    eqn.setToolTip('Plot Equation')

            else:
                eqn.result = None

        min = self.min_value_eqn.result
        max = self.max_value_eqn.result

        if min != None and max != None:
            if isinstance(min, int) and isinstance(max, int):
                self.slider_widget.setRange(min, max, 1)
            else:
                self.slider_widget.setRange(min, max)
            self.slider.update()



class SliderWidget(Qwt.QwtSlider):
    def __init__(self, parent, font):
        Qwt.QwtSlider.__init__(self, None, Qt.Horizontal, Qwt.QwtSlider.BottomScale, Qwt.QwtSlider.BgSlot)
        s = font.pointSize()
        self.setThumbLength(Slider.slider_thumb_length*s)
        self.setThumbWidth(Slider.slider_thumb_height*s)
        self.setBorderWidth(0.2*s)
        palette1 = self.palette()
        palette1.setColor(QPalette.Window, QColor(0, 0, 0, 0))
        self.setPalette(palette1)
        self.setTracking(True)
        self.setRange(0.0, 1.0)
        self.setFont(font)
        self.parent_graphics_item = parent

    def mousePressEvent444(self, event):
        print 'slider pressed'
        #event.ignore()
        Qwt.QwtSlider.mousePressEvent(self, event)
        #self.parent_graphics_item.setSelected(True)
        QGraphicsView.mousePressEvent(self.parent_graphics_item.worksheet, event)



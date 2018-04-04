
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

from activebox import *
from shadowbox import *
from plotequation import *
from contourplotwidget import ContourPlot
from equation import *
from colorbutton import ColorButton


class Plot2dContour(QGraphicsRectItem):
    highlighted_color = QColor(144, 238, 144,  128) #Background color of selected equation
    cursor_over_equation_color = QColor(0, 0xfd, 0xf8, 128)
    border_width = 20
    label_distance_from_xaxes = 0.5
    label_distance_from_yaxes = 0.5
    yaxis_equation_vertical_spacing = 2
    xaxis_equation_vertical_spacing = 1.5

    minlinewidth = 1
    maxlinewidth = 10
    minborderwidth = 0
    maxborderwidth = 10

    def __init__(self, parent, position, font):
        QGraphicsRectItem.__init__(self, parent)
        self.finished_init = False

        self.setToolTip('Plot')
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.setCursor(Qt.ArrowCursor)
        self.setAcceptsHoverEvents(True)
        self.setZValue(90)  #Z value on worksheet
        self.setPos(position)
        self.object_type = 'plot'
        self.currentIndex = -1  #Index of this equation in worksheets list
        self.positionChanged = False
        self.isGlobalDefinition = False #Global definitions will be executed before all others
        self.font = QFont(font.family(), font.pointSize())
        self.initialGraphWidth = 300
        self.initialHeightHeight = 300
        self.width = 0
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.characterClicked = False
        self.currentEquation = None
        self.plot_id = id(self)  # Unique ID for instance
        self.shadowBox = ShadowBox(self)
        self.shadowBox.setColor(Plot2dContour.cursor_over_equation_color)
        self.activeBox = ActiveBox('plot', self)
        self.activeBox.setColor(Plot2dContour.highlighted_color)
        self.border_color = QColor('black')
        self.border_width = 1
        self.background_color = QColor(QColor(0, 0, 0, 0))

        #Create Qwt plot widget, with parent=None (as required by QGraphicsProxyWidget.setWidget method)
        self.plot_widget = ContourPlot(self, self.font, self.background_color)
        self.plot = QGraphicsProxyWidget(self, Qt.Widget)  #Pass self as parent, window flags
        self.plot.setWidget(self.plot_widget)
        self.plot.setZValue(2)
        self.plot.setWindowFrameMargins(0, 0, 0, 0)
        self.plot.object_type = '2dplot'

        #Create plot dialog
        self.create_plot_dialog()

        #Setup plot border
        self.set_border_options(False)

        #Create initial x equation
        self.x_axis_equation = PlotEquation(self, QPointF(0, 0), font)
        self.x_axis_equation.setToolTip('X-Axis Equation')

        #Create x and y axis limit equations
        y_max_eqn = PlotEquation(self, QPointF(0, 0), self.font)
        y_max_eqn.setToolTip('Y-Axis maximum value')
        y_max_eqn.hide()
        y_min_eqn = PlotEquation(self, QPointF(0, 0), self.font)
        y_min_eqn.setToolTip('Y-Axis minimum value')
        y_min_eqn.hide()
        x_max_eqn = PlotEquation(self, QPointF(0, 0), self.font)
        x_max_eqn.setToolTip('X-Axis maximum value')
        x_max_eqn.hide()
        x_min_eqn = PlotEquation(self, QPointF(0, 0), self.font)
        x_min_eqn.setToolTip('X-Axis minimum value')
        x_min_eqn.hide()
        self.axes_limit_equations = [y_max_eqn, y_min_eqn, x_max_eqn, x_min_eqn]

        #Set initial size and do the initial layout of all the various bits and pieces
        self.layout_plot(self.initialGraphWidth, self.initialHeightHeight)

        self.finished_init = True
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
        self.x_axis_equation.cursor.hide()
        self.x_axis_equation.clearSelectionBox()

        for eqn in self.axes_limit_equations:
            eqn.cursor.hide()
            eqn.clearSelectionBox()

        item = self.scene().itemAt(s)
        if item.object_type == 'character':
            #Which equation was clicked?  Remember which equation is accepting mainwindow toolbutton clicks
            self.currentEquation = item.parentItem()
            self.currentEquation.cursor.show()

            #Set this flag to true if we are clicking on a char, used below in mouse move event handler
            self.characterClicked = True
        else:
            self.currentEquation = None

    def mouseMoveEvent(self, event):
        r = self.resizeStartHandle

        #Equation is being resized (has a table in it)
        if r:
            p = event.pos()
            b = Plot2dContour.border_width
            plot = self.plot_widget
            x = p.x()
            y = p.y()

            #Right middle resize handle dragged
            if r == 1:
                self.layout_plot(x-b, self.height)

            #Bottom right resize handle dragged
            elif r == 2:
                old_height = self.height
                self.layout_plot(x-b, self.height+y-b)
                deltay = self.height - old_height
                self.moveBy(0, deltay)

            #Bottom middle resize handle dragged
            elif r == 3:
                old_height = self.height
                self.layout_plot(self.width, self.height+y-b)
                deltay = self.height - old_height
                self.moveBy(0, deltay)

            #Top middle resize handle dragged
            elif r == 4:
                self.layout_plot(self.width, -y-b)

            #Top right resize handle dragged
            elif r == 5:
                self.layout_plot(x-b, -y-b)

            #Top left resize handle
            elif r == 6:
                old_width = self.width
                self.layout_plot(self.width-x-b, -y-b)
                deltax = old_width - self.width
                self.moveBy(deltax, 0)

            #Left middle resize handle dragged
            elif r == 7:
                old_width = self.width
                self.layout_plot(self.width-x-b, self.height)
                deltax = old_width - self.width
                self.moveBy(deltax, 0)

            #Bottom left resize handle dragged
            elif r == 8:
                old_height = self.height
                old_width = self.width
                self.layout_plot(self.width-x-b, self.height+y-b)
                deltay = self.height - old_height
                deltax = old_width - self.width
                self.moveBy(deltax, deltay)

        #Is mouse being dragged over an equation
        elif self.characterClicked:
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
        self.characterClicked = False

    def mouseDoubleClickEvent(self, event):
        QGraphicsRectItem.mouseDoubleClickEvent(self, event)
        self.preferences_dialog.show()

    def keyPressEvent(self, event):
        #Do not allow key event to pass up the chain

        #Update size of plot after key press
        self.layout_plot(self.width, self.height)

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
        if change == QGraphicsRectItem.ItemSelectedChange:# and self.finished_init:

            if value.toInt()[0] and self.finished_init:
                #Plot was selected so show active box and hide shadow box
                self.activeBox.showBox(True)
                self.shadowBox.hide()
                for limit_eqn in self.axes_limit_equations:
                    limit_eqn.show()

            else:
                #Plot was deselected, hide cursors, active box and selection box
                self.x_axis_equation.cursor.hide()

                self.activeBox.hideBox()

                for limit_eqn in self.axes_limit_equations:
                    limit_eqn.hide()

        #Look for movement of plot (has it been dragged?)
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            self.positionChanged = True

        return QGraphicsRectItem.itemChange(self, change, value)

    def handleToolbuttonInput(self, button, *args):
        #Handle inputs from mainwindow tool buttons
        if self.currentEquation:
            self.currentEquation.handleToolbuttonInput(button, *args)

            #Update layout after equation is edited
            self.layout_plot(self.width, self.height)

    def create_plot_dialog(self):
        prefs = QDialog()  #No parent=dialog will be a stand-alone window
        prefs.setModal(True)
        prefs.setWindowTitle('Plot preferences')
        prefs.setGeometry(300, 300, 400, 250)
        prefs.setVisible(False)
        prefs.hide()
        self.preferences_dialog = prefs

        #**********Apply,ok, and cancel buttons**********
        applybutton = QPushButton('Apply')
        applybutton.connect(applybutton, SIGNAL('clicked()'), self.preferences_dialog_apply)

        okbutton = QPushButton('OK')
        okbutton.connect(okbutton, SIGNAL('clicked()'), prefs.close)
        okbutton.connect(okbutton, SIGNAL('clicked()'), self.preferences_dialog_apply)

        cancelbutton = QPushButton('Cancel')
        cancelbutton.connect(cancelbutton, SIGNAL('clicked()'), prefs.close)

        prefsbuttons_layout = QHBoxLayout()
        prefsbuttons_layout.addWidget(cancelbutton)
        prefsbuttons_layout.addWidget(applybutton)
        prefsbuttons_layout.addWidget(okbutton)

        #**********Plot background and border properties**********
        self.background_color_button = ColorButton(self.background_color, 'Select plot background color', alpha=True)
        self.border_props = BorderOptions(self.border_color, self.border_width)

        plot_props_layout = QVBoxLayout()
        plot_props_layout.addWidget(QLabel('Plot background color'))
        plot_props_layout.addWidget(self.background_color_button)
        plot_props_layout.addWidget(self.border_props)

        properties_frame = QFrame()
        properties_frame.setToolTip('Set general plot options')
        properties_frame.setFrameShape(QFrame.Box)
        properties_frame.setLayout(plot_props_layout)

        #**********Contour properties**********
        self.show_contours = QCheckBox('Show contours')

        #**********Layout everythang created above in preferences dialog**********
        preflayout = QVBoxLayout(self.preferences_dialog)
        preflayout.addWidget(properties_frame)
        preflayout.addWidget(self.show_contours)
        preflayout.addLayout(prefsbuttons_layout)

    def preferences_dialog_apply(self):
        #This method grabs all the properties from the dialog

        #Plot background color
        self.plot_widget.set_plot_background_color(self.background_color_button.color)

        #Plot border
        flag = self.border_props.show_plot_border.isChecked()
        color = self.border_props.border_color_button.color
        width = self.border_props.plot_border_width.value()
        self.set_border_options(flag, color, width)

        #Show contours
        self.plot_widget.show_contour(self.show_contours.isChecked())

        #Re-layout plot with new/deleted equations
        self.layout_plot(self.width, self.height)

    def set_border_options(self, flag, color=QColor('black'), width=0):
        if flag:
            pen = QPen(color)
            pen.setWidth(width)
            pen.setCapStyle(Qt.SquareCap)
            pen.setJoinStyle(Qt.MiterJoin)
            self.setPen(pen)
        else:
            pen = QPen(Qt.NoPen)
            self.setPen(pen)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def setFontSize(self, size):
        self.font.setPointSize(size)
        self.plot_widget.set_all_fonts(self.font)
        self.x_axis_equation.setFontSize(size)

        for limit in self.axes_limit_equations:
            limit.setFontSize(size)

        self.layout_plot(self.width, self.height)

    def setFont(self, fontname):
        self.font.setFamily(fontname)
        self.plot_widget.set_all_fonts(self.font)
        self.x_axis_equation.setFont(fontname)

        for limit in self.axes_limit_equations:
            limit.setFont(fontname)

        self.layout_plot(self.width, self.height)

    def layout_plot(self, w, h):
        font_size = self.font.pointSize()
        plot_widget = self.plot_widget
        y_axis_label_distance = Plot2dContour.label_distance_from_yaxes * font_size
        x_axis_label_distance = Plot2dContour.label_distance_from_xaxes * font_size
        y_axis_equation_spacing = Plot2dContour.yaxis_equation_vertical_spacing * font_size
        x_axis_equation_spacing = Plot2dContour.xaxis_equation_vertical_spacing * font_size

        y_max_limit = self.axes_limit_equations[0]
        y_min_limit = self.axes_limit_equations[1]
        x_max_limit = self.axes_limit_equations[2]
        x_min_limit = self.axes_limit_equations[3]

        #Get dimensions of x-axis label and max height of all x-axis equations
        w1 = self.x_axis_equation.width
        t1 = self.x_axis_equation.top
        b1 = self.x_axis_equation.bottom
        x_axis_equations_max_height = b1 - t1

        if x_max_limit.height > x_axis_equations_max_height:
            x_axis_equations_max_height = x_max_limit.height
        if x_min_limit.height > x_axis_equations_max_height:
            x_axis_equations_max_height = x_min_limit.height

        #Get max width of x-axis equations including spacing
        all_x_axis_equations_width = w1 + x_min_limit.width + x_max_limit.width + 2 * x_axis_equation_spacing

        #Find widest y-axis equation and height of all y-axis equations including spacing
        y_axis_equations_max_width = 0

        if y_max_limit.width > y_axis_equations_max_width:
            y_axis_equations_max_width = y_max_limit.width
        if y_min_limit.width > y_axis_equations_max_width:
            y_axis_equations_max_width = y_min_limit.width

        #Get height of all y-axis equations, including spacing and limit equations
        all_y_axis_equations_height =  y_max_limit.height + y_min_limit.height + y_axis_equation_spacing

        #Figure desired out dimensions of embedded plot widget
        width_of_plot = w - y_axis_equations_max_width - y_axis_label_distance
        height_of_plot = h - x_axis_equations_max_height - x_axis_label_distance

        #Limit minimum size of plot based on min size of plot widget
        min_width = plot_widget.minimum_plot_width
        min_height = plot_widget.minimum_plot_height
        if width_of_plot < min_width:
            width_of_plot = min_width
            w = width_of_plot + y_axis_equations_max_width + y_axis_label_distance

        if height_of_plot < min_height:
            height_of_plot = min_height
            h = height_of_plot + x_axis_equations_max_height + x_axis_label_distance

        #Limit minimum size of overall plot (widget + all equations)
        temp = all_x_axis_equations_width + y_axis_equation_spacing + y_axis_equations_max_width
        if w < temp:
            w = temp
            width_of_plot = all_x_axis_equations_width

        temp = all_y_axis_equations_height + x_axis_equations_max_height + x_axis_label_distance
        if h < temp:
            h = temp
            height_of_plot = all_y_axis_equations_height

        #Resize and position plot widget
        self.plot_widget.resize(width_of_plot, height_of_plot)
        self.plot.setPos(y_axis_equations_max_width+y_axis_label_distance, -h)

        #Position the x-axis equation
        x = x_min_limit.width + (width_of_plot - x_max_limit.width - x_min_limit.width) * 0.5 - w1 * 0.5
        self.x_axis_equation.setPos(y_axis_equations_max_width+y_axis_label_distance+x, -b1)

        #Position limit equations
        y_max_limit.setPos(0, -h-y_max_limit.top)
        y_min_limit.setPos(0, -x_axis_equations_max_height - x_axis_label_distance - y_min_limit.bottom)
        x_max_limit.setPos(w-x_max_limit.width, -x_max_limit.bottom)
        x_min_limit.setPos(y_axis_equations_max_width+y_axis_label_distance, -x_min_limit.bottom)

        #Figure out position and size of active box
        b = Plot2dContour.border_width
        self.shadowBox.setRect(-b, -h-b, w+2*b, h+2*b)
        self.activeBox.setSize(w+2*b, h+2*b)
        self.activeBox.setPos(-b, -h-b)
        self.setRect(-b, -h-b, w+2*b, h+2*b)

        self.width = w
        self.height = h
        self.top = -h

    def getDict(self):
        d = self.__dict__.copy()
        return d

    #*************************************************************************************
    #*Methods below this point handle executing plot
    #*************************************************************************************
    def tryToExecuteEquation(self):

        all_equations = [self.x_axis_equation]
        all_equations.extend(self.axes_limit_equations)

        self.all_plot_equations = all_equations

        programs = []
        for eqn in all_equations:
            t = eqn.tryToExecuteEquation()
            if t != None:
                programs.append(t)
            else:
                eqn.setColor(QColor('red'))
                eqn.setToolTip('Could not parse equation')

        if len(programs) > 0:
            programs.append(self.plot_id)
            return programs

        #No valid y-equations found so do nothing
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



        #Get x-axis values, kill entire plot if this is erroneous
        x = all_equations[0].result
        if x == None:
            #self.plot_widget.hide_plots()
            return
            #***********************Set plot to display this result here************************
            #*************************************************************


        n = len(all_equations) - 1
        y_max = all_equations[n-3].result
        y_min = all_equations[n-2].result
        x_max = all_equations[n-1].result
        x_min = all_equations[n].result

        #Check y axis scale limit
        if y_min != None and y_max != None:
            if y_max > y_min:
                self.plot_widget.set_y_axis_scale(y_min, y_max)
            else:
                all_equations[n-3].setColor(QColor('red'))
                all_equations[n-3].setToolTip('Ymax is smaller than Ymin')
                all_equations[n-2].setColor(QColor('red'))
                all_equations[n-2].setToolTip('Ymax is smaller than Ymin')
                self.plot_widget.set_y_axis_autoscale()

        else:
            self.plot_widget.set_y_axis_autoscale()

        #Check x-axis scale limits
        if x_min != None and x_max != None:
            if x_max > x_min:
                self.plot_widget.set_x_axis_scale(x_min, x_max)
            else:
                all_equations[n-1].setColor(QColor('red'))
                all_equations[n-1].setToolTip('Xmax is smaller than Xmin')
                all_equations[n].setColor(QColor('red'))
                all_equations[n].setToolTip('Xmax is smaller than Xmin')
                self.plot_widget.set_x_axis_autoscale()

        else:
            self.plot_widget.set_x_axis_autoscale()

        self.plot_widget.replot()


class BorderOptions(QWidget):
    def __init__(self, border_color, border_width):
        QWidget.__init__(self)
        self.show_plot_border = QCheckBox('Show plot border')
        self.show_plot_border.setChecked(False)
        self.border_color_button = ColorButton(border_color, 'Select plot border color', alpha=True)
        self.border_color_button.setEnabled(False)
        self.plot_border_width = QSpinBox()
        self.plot_border_width.setEnabled(False)
        self.plot_border_width.setValue(border_width)
        self.plot_border_width.setRange(Plot2dContour.minborderwidth, Plot2dContour.maxborderwidth)

        layout = QVBoxLayout()
        layout.addWidget(self.show_plot_border)
        layout.addWidget(QLabel('Plot border color'))
        layout.addWidget(self.border_color_button)
        layout.addWidget(QLabel('Plot border width'))
        layout.addWidget(self.plot_border_width)

        self.setLayout(layout)

        self.connect(self.show_plot_border, SIGNAL('stateChanged(int)'), self.show_border)

    def show_border(self, s):
        if s:
            self.border_color_button.setEnabled(True)
            self.plot_border_width.setEnabled(True)
        else:
            self.border_color_button.setEnabled(False)
            self.plot_border_width.setEnabled(False)



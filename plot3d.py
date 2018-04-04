
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

import scipy

from PyQt4.QtCore import *
from PyQt4.QtGui import *

from activebox import *
from shadowbox import *
from plotequation import *
from equation import *
from colorbutton import ColorButton

import plot3dwidget


class Plot3d(QGraphicsRectItem):
    highlightedColor = QColor(144, 238, 144,  128) #Background color of selected equation
    cursorOverEquationColor = QColor(0, 0xfd, 0xf8, 128)
    borderWidth = 20
    labelDistFromAxes = 10

    minlinewidth = 1
    maxlinewidth = 10
    minmarksize = 5
    maxmarksize = 20
    mingridwidth = 0
    maxgridwidth = 10
    maxnumcurves = 10
    minborderwidth = 0
    maxborderwidth = 10

    def __init__(self, parent, position, font):
        QGraphicsRectItem.__init__(self, parent)
        self.finishedInit = False

        self.setToolTip('Plot')
        self.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsRectItem.ItemIsMovable, True)
        self.setFlag(QGraphicsRectItem.ItemIsFocusable, True)
        self.setCursor(Qt.ArrowCursor)
        self.setAcceptsHoverEvents(True)
        self.setZValue(100)  #Z value on worksheet
        self.setPos(position)
        self.object_type = 'plot'
        self.currentIndex = -1  #Index of this equation in worksheets list
        self.object_id = id(self)  # Unique ID for instance
        self.positionChanged = False
        self.isGlobalDefinition = False #Global definitions will be executed before all others
        self.font = QFont(font.family(), font.pointSize())
        self.initial_plot_width = 300
        self.initial_plot_height = 300
        self.width = 0
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.characterClicked = False
        self.pixmapClicked = False
        self.currentEquation = None
        self.shadowBox = ShadowBox(self)
        self.shadowBox.setColor(self.cursorOverEquationColor)
        self.activeBox = ActiveBox('plot', self)
        self.activeBox.setColor(self.highlightedColor)
        self.background_color = QColor(0, 0, 0, 0)
        self.border_color = QColor('black')
        self.border_width = 1

        #Create a pixmap that will display 3D plot
        p = QGraphicsPixmapItem(self)
        p.object_type = 'pixmap'
        p.setZValue(100)
        self.plot_pixmap = p

        #Create Qwt3d plot widget
        self.plot_widget = plot3dwidget.Plot(p, font, self.background_color)

        #Create 3d plot equation
        self.plot_equation = PlotEquation(self, QPointF(0, 0), font, plot3d_flag=True)
        self.plot_equation.setToolTip('Quickplot Equation')

        #Create plot configuration dialog
        self.create_plot_dialog()

        #Setup plot border
        self.set_border_options(False)

        #Set initial size
        self.setSize(self.initial_plot_width, self.initial_plot_height)
        self.finishedInit = True
        self.setSelected(True)

    def mousePressEvent(self, event):
        QGraphicsRectItem.mousePressEvent(self, event)

        #Set cursor to closed hand
        self.setCursor(Qt.ClosedHandCursor)

        #Get mouse click position
        s = event.scenePos()
        p = event.pos()

        #Are we clicking on a resize handle?
        self.resizeStartHandle = self.activeBox.mouseInResizeHandle(p)

        #Hide all equation cursors, then show equation cursor for clicked equation
        self.plot_equation.cursor.hide()
        self.plot_equation.clearSelectionBox()

        item = self.scene().itemAt(s)
        if item.object_type == 'character':
            #Which equation was clicked?  Remember which equation is accepting mainwindow toolbutton clicks
            self.currentEquation = item.parentItem()
            self.currentEquation.cursor.show()

            #Set this flag to true if we are clicking on a char, used below in mouse move event handler
            self.characterClicked = True

        elif item.object_type == 'pixmap':
            self.pixmapClicked = True
            self.currentEquation = None
            p = event.pos()
            e = QMouseEvent(QEvent.MouseButtonPress, QPoint(p.x(), p.y()), event.button(), event.buttons(), event.modifiers())
            self.plot_widget.mousePressEvent(e)

        else:
            self.currentEquation = None

    def mouseMoveEvent(self, event):
        r = self.resizeStartHandle

        if self.pixmapClicked:
            p = event.pos()
            e = QMouseEvent(QEvent.MouseMove, QPoint(p.x(), p.y()), event.button(), event.buttons(), event.modifiers())
            self.plot_widget.mouseMoveEvent(e)

        #Equation is being resized (has a table in it)
        elif r:
            p = event.pos()
            b = self.borderWidth
            plot = self.plot_widget
            x = p.x()
            y = p.y()

            #Right middle resize handle dragged
            if r == 1:
                self.setSize(x-b, self.height)

            #Bottom right resize handle dragged
            elif r == 2:
                old_height = self.height
                self.setSize(x-b, self.height+y-b)
                deltay = self.height - old_height
                self.moveBy(0, deltay)

            #Bottom middle resize handle dragged
            elif r == 3:
                old_height = self.height
                self.setSize(self.width, self.height+y-b)
                deltay = self.height - old_height
                self.moveBy(0, deltay)

            #Top middle resize handle dragged
            elif r == 4:
                self.setSize(self.width, -y-b)

            #Top right resize handle dragged
            elif r == 5:
                self.setSize(x-b, -y-b)

            #Top left resize handle
            elif r == 6:
                old_width = self.width
                self.setSize(self.width-x-b, -y-b)
                deltax = old_width - self.width
                self.moveBy(deltax, 0)

            #Left middle resize handle dragged
            elif r == 7:
                old_width = self.width
                self.setSize(self.width-x-b, self.height)
                deltax = old_width - self.width
                self.moveBy(deltax, 0)

            #Bottom left resize handle dragged
            elif r == 8:
                old_height = self.height
                old_width = self.width
                self.setSize(self.width-x-b, self.height+y-b)
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
        self.pixmapClicked = False

        pos = event.pos()
        e = QMouseEvent(QEvent.MouseButtonRelease, QPoint(pos.x(), pos.y()), event.button(), event.buttons(), event.modifiers())
        self.plot_widget.mouseReleaseEvent(e)

    def mouseDoubleClickEvent(self, event):
        QGraphicsRectItem.mouseDoubleClickEvent(self, event)
        self.preferences_dialog.show()

    def wheelEvent(self, event):
        pos = event.pos()
        e = QWheelEvent(QPoint(pos.x(), pos.y()), event.delta(), event.buttons(), event.modifiers())
        self.plot_widget.wheelEvent(e)

    def keyPressEvent(self, event):
        #Do not allow key event to pass up the chain

        #Update size of plot after key press
        self.setSize(self.plot_width, self.plot_height)

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
                #Equation was selected so show active box and hide shadow box
                self.activeBox.showBox(True)
                self.shadowBox.hide()

            else:
                #Plot was deselected, hide cursors, active box and selection box
                self.plot_equation.cursor.hide()
                self.activeBox.hideBox()

        #Look for movement of plot (has it been dragged?)
        if change == QGraphicsRectItem.ItemPositionHasChanged:
            self.positionChanged = True

        return QGraphicsRectItem.itemChange(self, change, value)

    def handleToolbuttonInput(self, button, *args):
        #Handle inputs from mainwindow tool buttons
        if self.currentEquation:
            self.currentEquation.handleToolbuttonInput(button, *args)

            #Update layout after equation is edited
            self.setSize(self.plot_width, self.plot_height)

    def setFontSize(self, size):
        self.font.setPointSize(size)
        self.plot_widget.set_all_fonts(self.font)
        self.plot_equation.setFontSize(size)
        self.setSize(self.width, self.height)

    def setFont(self, fontname):
        self.font.setFamily(fontname)
        self.plot_widget.set_all_fonts(self.font)
        self.plot_equation.setFont(fontname)
        self.setSize(self.width, self.height)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def setSize(self, desired_total_width, desired_total_height):
        #Get dimensions of equations
        w1 = self.plot_equation.width
        t1 = self.plot_equation.top
        b1 = self.plot_equation.bottom
        h1 = b1 - t1

        #Determine absolute minimum size of plot
        plot_min_width = self.plot_widget.min_width
        plot_min_height = self.plot_widget.min_height
        if plot_min_width < w1:
            plot_min_width = w1

        if desired_total_width < plot_min_width:
            actual_plot_width = plot_min_width
        else:
            actual_plot_width = desired_total_width
        w = actual_plot_width

        desired_plot_height = desired_total_height - h1
        if desired_plot_height < plot_min_height:
            actual_plot_height = plot_min_height
        else:
            actual_plot_height = desired_plot_height
        h = actual_plot_height + h1

        #Remember the actual dimensions of a rectangle containing plot + equations
        self.plot_width = w
        self.plot_height = h

        self.plot_widget.resizeGL(actual_plot_width, actual_plot_height)
        self.plot_pixmap.setPos(0, -h)

        #Position the axis labels
        equation_spacing = self.font.pointSize() * 0.5
        self.plot_equation.setPos(0, -h+actual_plot_height-t1+equation_spacing)

        #Figure out position and size of active box
        b = self.borderWidth
        self.shadowBox.setRect(-b, -h-b, w+2*b, h+2*b)
        self.activeBox.setSize(w+2*b, h+2*b)
        self.activeBox.setPos(-b, -h-b)
        self.setRect(-b, -h-b, w+2*b, h+2*b)

        self.width = w
        self.height = h
        self.top = -h

    def setColor(self, color):
        pass

    def getDict(self):
        d = self.__dict__.copy()
        return d

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

        #**********Plot background color**********
        self.background_color_button = ColorButton(self.background_color, 'Select plot background color', alpha=True)
        background_color_layout = QVBoxLayout()
        background_color_layout.addWidget(QLabel('Plot background color'))
        background_color_layout.addWidget(self.background_color_button)

        #**********Axes properties**********
        self.axes_colorbutton = ColorButton(plot3dwidget.Plot.initial_axes_color, 'Select axes color', alpha=True)
        self.axes_style_combo = QComboBox()
        self.axes_style_combo.insertItems(0, ['None', 'Box', 'Frame'])
        self.axes_style_combo.setCurrentIndex(1)
        self.axes_thickness_spinbox = QSpinBox()
        self.axes_thickness_spinbox.setRange(plot3dwidget.Plot.axesminwidth, plot3dwidget.Plot.axesmaxwidth)
        self.axes_thickness_spinbox.setValue(plot3dwidget.Plot.initial_axes_width)
        axes_layout = QVBoxLayout()
        axes_layout.addWidget(QLabel('Plot axes color'))
        axes_layout.addWidget(self.axes_colorbutton)
        axes_layout.addWidget(QLabel('Plot axes thickness'))
        axes_layout.addWidget(self.axes_thickness_spinbox)
        axes_layout.addWidget(QLabel('Plot axes style'))
        axes_layout.addWidget(self.axes_style_combo)

        axes_frame = QFrame()
        axes_frame.setToolTip('Set axes options')
        axes_frame.setFrameShape(QFrame.Box)
        axes_frame.setLayout(axes_layout)

        #**********Plot mesh lines**********
        self.mesh_colorbutton = ColorButton(plot3dwidget.Plot.initial_mesh_color, 'Select mesh color', alpha=True)
        self.mesh_style_combo = QComboBox()
        self.mesh_style_combo.insertItems(0, ['Wireframe', 'Filled wireframe', 'Filled', 'Points'])
        self.mesh_style_combo.setCurrentIndex(0)
        self.mesh_thickness_spinbox = QSpinBox()
        self.mesh_thickness_spinbox.setRange(plot3dwidget.Plot.minmeshwidth, plot3dwidget.Plot.maxmeshwidth)
        self.mesh_thickness_spinbox.setValue(0)
        plot_mesh_layout = QVBoxLayout()
        plot_mesh_layout.addWidget(QLabel('Plot mesh color'))
        plot_mesh_layout.addWidget(self.mesh_colorbutton)
        plot_mesh_layout.addWidget(QLabel('Plot mesh style'))
        plot_mesh_layout.addWidget(self.mesh_style_combo)
        plot_mesh_layout.addWidget(QLabel('Plot mesh thickness'))
        plot_mesh_layout.addWidget(self.mesh_thickness_spinbox)

        plot_mesh_frame = QFrame()
        plot_mesh_frame.setToolTip('Set mesh options')
        plot_mesh_frame.setFrameShape(QFrame.Box)
        plot_mesh_frame.setLayout(plot_mesh_layout)

        #**********Plot border color, thickness, enable**********
        self.border_props = BorderOptions(self.border_color, self.border_width)

        layout1 = QVBoxLayout()
        layout1.addLayout(background_color_layout)
        layout1.addWidget(axes_frame)
        layout1.addWidget(plot_mesh_frame)
        layout1.addWidget(self.border_props)

        #**********Layout everythang created above in preferences dialog**********
        preflayout = QVBoxLayout(self.preferences_dialog)
        preflayout.addLayout(layout1)
        preflayout.addLayout(prefsbuttons_layout)

    def preferences_dialog_apply(self):

        #Plot background color
        self.plot_widget.set_plot_background_color(self.background_color_button.color)

        #Plot border
        flag = self.border_props.show_plot_border.isChecked()
        color = self.border_props.border_color_button.color
        width = self.border_props.plot_border_width.value()
        self.set_border_options(flag, color, width)

        #Plot mesh
        color = self.mesh_colorbutton.color
        i = self.mesh_style_combo.currentIndex()
        w = self.mesh_thickness_spinbox.value()
        self.plot_widget.set_mesh(color, i, w)

        #Plot axes
        color = self.axes_colorbutton.color
        i = self.axes_style_combo.currentIndex()
        w = self.axes_thickness_spinbox.value()
        self.plot_widget.set_axes(color, i, w)

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


    #*************************************************************************************
    #*Methods below this point handle executing plot
    #*************************************************************************************
    def tryToExecuteEquation(self):

        all_equations = [self.plot_equation]
#        all_equations.extend(self.y_axis_equations)
#        all_equations.extend(self.axes_limit_equations)

        self.all_plot_equations = all_equations

        programs = []
        for eqn in all_equations:
            t = eqn.tryToExecuteEquation()
            if t != None:
                programs.append(t)

            else:
                eqn.setColor(QColor('red'))
                eqn.setToolTip('Could not parse equation')
                self.plot_widget.show_plot(False)

        if len(programs) > 0:
            programs.append(self.object_id)
            return programs

        #No valid input equations found so do nothing
        else:
            print 'hiding plot, no parse input'
            self.plot_widget.show_plot(False)
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

        #Get results
        plot_values = all_equations[0].result
        if plot_values == None:
            self.plot_widget.show_plot(False)

        else:
            if isinstance(plot_values, scipy.ndarray):
                rows, cols = plot_values.shape
                self.plot_widget.do_update_plot(cols, rows, plot_values)

            elif isinstance(plot_values, tuple):
                #x, y, z = plot_values
                m = scipy.dstack(plot_values)
                self.plot_widget.do_update_plot3(m)



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
        self.plot_border_width.setRange(Plot3d.minborderwidth, Plot3d.maxborderwidth)

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

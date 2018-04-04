
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

from PyQt4.QtCore import *
from PyQt4.QtGui import *

import PyQt4.Qwt5 as Qwt

from activebox import *
from shadowbox import *
from plotequation import *
from polarplotwidget import PolarPlotWidget
from equation import *
from colorbutton import ColorButton

import plotlegend


class PolarPlot(QGraphicsRectItem):
    highlighted_color = QColor(144, 238, 144,  128) #Background color of selected equation
    cursor_over_equation_color = QColor(0, 0xfd, 0xf8, 128)
    border_width = 20
    label_distance_from_plot = 0.5
    equation_vertical_spacing = 2
    equation_horizontal_spacing = 1.5
    legend_vertical_spacing = 0.1

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
        self.finished_init = False

        self.setToolTip('Polar Plot')
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
        self.initial_plot_width = 300
        self.initial_plot_height = 300
        self.width = 0
        self.height = 0
        self.top = 0
        self.bottom = 0
        self.character_clicked = False
        self.currentEquation = None
        self.object_id = id(self)  # Unique ID for instance
        self.shadowBox = ShadowBox(self)
        self.shadowBox.setColor(PolarPlot.cursor_over_equation_color)
        self.activeBox = ActiveBox('plot', self)
        self.activeBox.setColor(PolarPlot.highlighted_color)
        self.border_color = QColor('black')
        self.border_width = 1
        self.background_color = QColor(QColor(0, 0, 0, 0))
        self.num_curves = 1
        self.curve_properties = [CurveProperties()]

        #Create Qwt plot widget, with parent=None (as required by QGraphicsProxyWidget.setWidget method)
        self.plot_widget = PolarPlotWidget(None, self, self.font, self.background_color, self.curve_properties[0])
        self.plot = QGraphicsProxyWidget(self, Qt.Widget)  #Pass self as parent, window flags
        self.plot.setWidget(self.plot_widget)
        self.plot.setZValue(2)
        self.plot.setWindowFrameMargins(0, 0, 0, 0)
        self.plot.object_type = 'polarplot'

        #Create plot dialog
        self.create_plot_dialog()

        #Setup plot border
        self.set_border_options(True, QColor('black'), 2)
        #self.set_border_options(False)

        #Create initial azimuth equation
        self.azimuth_axis_equation = PlotEquation(self, QPointF(0, 0), font)
        self.azimuth_axis_equation.setToolTip('Azimuth Equation')

        #Create initial radial-axis equation
        eqn = PlotEquation(self, QPointF(0, 0), self.font)
        eqn.setToolTip('Radial Equation')
        self.radial_axis_equations = [eqn]

        #Create various limit equations
        radial_max_eqn = PlotEquation(self, QPointF(0, 0), self.font)
        radial_max_eqn.setToolTip('Radius maximum value')
        radial_max_eqn.hide()
        azimuth_offset_eqn = PlotEquation(self, QPointF(0, 0), self.font)
        azimuth_offset_eqn.setToolTip('Azimuth offset value')
        azimuth_offset_eqn.hide()
        azimuth_max_eqn = PlotEquation(self, QPointF(0, 0), self.font)
        azimuth_max_eqn.setToolTip('Azimuth maximum value')
        azimuth_max_eqn.hide()
        azimuth_min_eqn = PlotEquation(self, QPointF(0, 0), self.font)
        azimuth_min_eqn.setToolTip('Azimuth minimum value')
        azimuth_min_eqn.hide()
        self.limit_equations = [radial_max_eqn, azimuth_offset_eqn, azimuth_max_eqn, azimuth_min_eqn]

        #Create initial y-axis legends
        legend = plotlegend.Legend(self)
        legend.set_properties(self.curve_properties[0], font.pointSize())
        self.radial_axis_legends = [legend]

        #Set initial size and do the initial layout of all the various bits and pieces
        self.layout_plot(self.initial_plot_width, self.initial_plot_height)

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
        self.azimuth_axis_equation.cursor.hide()
        self.azimuth_axis_equation.clearSelectionBox()

        for yeqn in self.radial_axis_equations:
            yeqn.cursor.hide()
            yeqn.clearSelectionBox()

        for eqn in self.limit_equations:
            eqn.cursor.hide()
            eqn.clearSelectionBox()

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
            b = PolarPlot.border_width
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
                for limit_eqn in self.limit_equations:
                    limit_eqn.show()

            else:
                #Plot was deselected, hide cursors, active box and selection box
                self.azimuth_axis_equation.cursor.hide()
                for radialeqn in self.radial_axis_equations:
                    radialeqn.cursor.hide()
                self.activeBox.hideBox()

                for limit_eqn in self.limit_equations:
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

        #**********Add plot button**********
        addplot = QPushButton('Add curve')
        addplot.setToolTip('Add another curve to plot')
        addplot.connect(addplot, SIGNAL('clicked()'), self.add_plot)

        #**********Plot grid options**********
        major_grid_pen = self.plot_widget.plot_grid.majorGridPen(Qwt.QwtPolar.Radius)
        minor_grid_pen = self.plot_widget.plot_grid.minorGridPen(Qwt.QwtPolar.Radius)

        #Grid checkbox options
        self.radial_grid_options = GridOptions('radial')
        self.azimuth_grid_options = GridOptions('azimuth')

        #Major gridline button and label
        vlayout2a = QVBoxLayout()
        vlayout2a.addWidget(QLabel('Major gridline color'))
        self.major_grid_color_button = ColorButton(major_grid_pen.color(), 'Select major grid color', alpha=True)
        vlayout2a.addWidget(self.major_grid_color_button)

        #Minor gridline button and label
        vlayout2b = QVBoxLayout()
        vlayout2b.addWidget(QLabel('Minor gridline color'))
        self.minor_grid_color_button = ColorButton(minor_grid_pen.color(), 'Select minor grid color', alpha=True)
        vlayout2b.addWidget(self.minor_grid_color_button)

        #Major gridline spinbox and label
        vlayout2c = QVBoxLayout()
        vlayout2c.addWidget(QLabel('Major gridline thickness'))
        self.major_line_width = QSpinBox()
        self.major_line_width.setRange(PolarPlot.mingridwidth, PolarPlot.maxgridwidth)
        vlayout2c.addWidget(self.major_line_width)

        #Minor gridline spinbox and label
        vlayout2d = QVBoxLayout()
        vlayout2d.addWidget(QLabel('Minor gridline thickness'))
        self.minor_line_width = QSpinBox()
        self.minor_line_width.setRange(PolarPlot.mingridwidth, PolarPlot.maxgridwidth)
        vlayout2d.addWidget(self.minor_line_width)

        gridlayout = QGridLayout()
        gridlayout.setRowStretch(2,90)
        gridlayout.addWidget(self.radial_grid_options, 0, 0)
        gridlayout.addLayout(vlayout2a, 0, 1)
        gridlayout.addLayout(vlayout2c, 0, 2)
        gridlayout.addWidget(self.azimuth_grid_options, 1, 0)
        gridlayout.addLayout(vlayout2b, 1, 1)
        gridlayout.addLayout(vlayout2d, 1, 2)

        grid_properties_frame = QFrame()
        grid_properties_frame.setToolTip('Set plot grid options')
        grid_properties_frame.setFrameShape(QFrame.Box)
        grid_properties_frame.setLayout(gridlayout)

        #**********x,y axis logarithmic scale options**********
        self.log_radial_axis_flag = QCheckBox('Use logarithmic scale on radial-axis')
        self.log_radial_axis_flag.setChecked(False)
        self.log_azimuth_axis_flag = QCheckBox('Use logarithmic scale on azimuth-axis')
        self.log_azimuth_axis_flag.setChecked(False)

        log_axis_layout = QVBoxLayout()
        log_axis_layout.addWidget(self.log_azimuth_axis_flag)
        log_axis_layout.addWidget(self.log_radial_axis_flag)

        #**********Plot background color**********
        background_color_layout = QVBoxLayout()
        self.background_color_button = ColorButton(self.background_color, 'Select plot background color', alpha=True)
        background_color_layout.addWidget(QLabel('Plot background color'))
        background_color_layout.addWidget(self.background_color_button)

        #**********Plot border color, thickness, enable**********
        self.border_props = BorderOptions(self.border_color, self.border_width)

        layout1 = QHBoxLayout()
        layout1.addLayout(log_axis_layout)
        layout1.addLayout(background_color_layout)
        layout1.addWidget(self.border_props)

        axes_properties_frame = QFrame()
        axes_properties_frame.setToolTip('Set general plot options')
        axes_properties_frame.setFrameShape(QFrame.Box)
        axes_properties_frame.setLayout(layout1)

        #**********Curve properties**********
        #Title labels
        curvelabel = QLabel('Curve')
        visibilitylabel = QLabel('Visible')
        deletelabel = QLabel('Delete')
        colorlabel = QLabel('Line color')
        aliaslabel = QLabel('Antialiased')
        interpolatedlabel = QLabel('Interpolated')
        widthlabel = QLabel('Line width')
        stylelabel = QLabel('Line style')
        markerlabel = QLabel('Marker style')
        markersizelabel = QLabel('Marker Size')
        markerbrush = QLabel('Marker brush color')
        markerline = QLabel('Marker border color')

        layout = QGridLayout()
        layout.setRowStretch(9,90)
        layout.addWidget(curvelabel, 0, 0)
        layout.addWidget(visibilitylabel, 0, 1)
        layout.addWidget(deletelabel, 0, 2)
        layout.addWidget(colorlabel, 0, 3)
        layout.addWidget(aliaslabel, 0, 4)
        layout.addWidget(interpolatedlabel, 0, 5)
        layout.addWidget(stylelabel, 0, 6)
        layout.addWidget(widthlabel, 0, 7)
        layout.addWidget(markerlabel, 0, 8)
        layout.addWidget(markersizelabel, 0, 9)
        layout.addWidget(markerbrush, 0, 10)
        layout.addWidget(markerline, 0, 11)
        self.properties_grid_layout = layout

        for i, property in enumerate(self.curve_properties):
            self.create_single_curve_options(i+1, property)

        curve_properties_frame = QFrame()
        curve_properties_frame.setToolTip('Set curves options')
        curve_properties_frame.setFrameShape(QFrame.Box)
        curve_properties_frame.setLayout(self.properties_grid_layout)

        #**********Layout everythang created above in preferences dialog**********
        preflayout = QVBoxLayout(self.preferences_dialog)
        preflayout.addWidget(addplot)
        preflayout.addWidget(axes_properties_frame)
        preflayout.addWidget(grid_properties_frame)
        preflayout.addWidget(curve_properties_frame)
        preflayout.addLayout(prefsbuttons_layout)

    def create_single_curve_options(self, row, curve_properties):
        #Set up the curve properties part of the plot dialog window

        layout = self.properties_grid_layout

        #Curve number
        curvenumber = QLabel('%s' % row)

        #Visibility checkbox
        visibility = QCheckBox()
        visibility.setChecked(curve_properties.visibility)

        #Delete checkbox
        delete = QCheckBox()
        delete.setChecked(False)

        #Curve color button
        colorbutton = ColorButton(curve_properties.line_color, 'Select curve line color', alpha=True)

        #Antialiased checkbox
        alias = QCheckBox()
        alias.setChecked(curve_properties.antialias_flag)

        #Interpolated checkbox
        interpolated = QCheckBox()
        interpolated.setChecked(curve_properties.interpolated_flag)

        #Line style combobox
        linestyle = QComboBox()
        linestyle.insertItems(0, ['None', 'Solid', 'Dashed', 'Dots', 'Dashdots', 'Dashdotdots'])
        linestyle.setCurrentIndex(curve_properties.line_style_index)

        #Line width spinbox
        linewidth = QSpinBox()
        linewidth.setRange(PolarPlot.minlinewidth, PolarPlot.maxlinewidth)
        linewidth.setValue(curve_properties.line_width)

        #Marker style combobox
        markerstyle = QComboBox()
        markerstyle.insertItems(0, PolarPlotWidget.marker_style_strings)
        markerstyle.insertSeparator(1)
        markerstyle.setCurrentIndex(curve_properties.marker_style_index)

        #Marker size
        markersize = QSpinBox()
        markersize.setRange(PolarPlot.minmarksize, PolarPlot.maxmarksize)
        markersize.setValue(curve_properties.marker_size)

        #Marker brush color button
        marker_brush_button = ColorButton(curve_properties.marker_color, 'Select marker color', alpha=True)

        #Marker border color button
        marker_line_button = ColorButton(curve_properties.marker_border_color, 'Select marker border color', alpha=True)

        layout.addWidget(curvenumber, row, 0)
        layout.addWidget(visibility, row, 1)
        layout.addWidget(delete, row, 2)
        layout.addWidget(colorbutton, row, 3)
        layout.addWidget(alias, row, 4)
        layout.addWidget(interpolated, row, 5)
        layout.addWidget(linestyle, row, 6)
        layout.addWidget(linewidth, row, 7)
        layout.addWidget(markerstyle, row, 8)
        layout.addWidget(markersize, row, 9)
        layout.addWidget(marker_brush_button, row, 10)
        layout.addWidget(marker_line_button, row, 11)

    def add_plot(self):
        if self.num_curves < PolarPlot.maxnumcurves:
            self.num_curves += 1
            new_curve_properties = CurveProperties()
            self.curve_properties.append(new_curve_properties)

            #Update dialog GUI
            self.create_single_curve_options(self.num_curves, new_curve_properties)

            #Add another curve to plot widget
            self.plot_widget.add_curve(new_curve_properties)

            #Add a new equation and legend to y-axis
            new_eqn = PlotEquation(self, QPointF(0, 0), self.font)
            new_eqn.setToolTip('Radius Equation')
            self.radial_axis_equations.append(new_eqn)
            self.radial_axis_legends.append(plotlegend.Legend(self))

            #Re-layout plot with new/deleted equations
            self.layout_plot(self.width, self.height)

    def preferences_dialog_apply(self):
        #This method grabs all the properties from the dialog and stores them in the
        #self.curve_properties list, as well as changing certain other features of the plot.

        grid_item = self.properties_grid_layout.itemAtPosition
        old_num_curves = self.num_curves

        #Change major/minor grid line colors and thickness, and visibility
        self.plot_widget.set_grid_line_properties(self.radial_grid_options.major_checkbox.isChecked(), \
                                                  self.radial_grid_options.minor_checkbox.isChecked(), \
                                                  self.azimuth_grid_options.major_checkbox.isChecked(), \
                                                  self.azimuth_grid_options.minor_checkbox.isChecked(), \
                                                  self.major_grid_color_button.color, \
                                                  self.minor_grid_color_button.color, \
                                                  self.major_line_width.value(), \
                                                  self.minor_line_width.value())

        #Axes log scales
        self.plot_widget.set_radius_axis_logscale(self.log_radial_axis_flag.isChecked())
        self.plot_widget.set_azimuth_axis_logscale(self.log_azimuth_axis_flag.isChecked())

        #Plot background color
        self.plot_widget.set_plot_background_color(self.background_color_button.color)

        #Plot border
        flag = self.border_props.show_plot_border.isChecked()
        color = self.border_props.border_color_button.color
        width = self.border_props.plot_border_width.value()
        self.set_border_options(flag, color, width)

        #Loop grab properties for each curve from GUI
        self.curve_properties = []
        deleted_curve_indices = []
        for i in xrange(1, self.num_curves+1):

            #Ignore row if delete checkbox checked
            delete_checkbox = grid_item(i, 2).widget()

            if delete_checkbox.isChecked() and self.num_curves > 1:
                self.num_curves -= 1

                #Remember which curve was deleted
                deleted_curve_indices.append(i-1)

                #Delete actual plot curve
                self.plot_widget.remove_curve(i-1)

            else:
                #Grab properties from dialog GUI
                visibility = grid_item(i, 1).widget().isChecked()
                color = grid_item(i, 3).widget().color
                alias = grid_item(i, 4).widget().isChecked()
                interpolated = grid_item(i, 5).widget().isChecked()
                linestyle = grid_item(i, 6).widget().currentIndex()
                linewidth = grid_item(i, 7).widget().value()
                markerstyle = grid_item(i, 8).widget().currentIndex()  # Index in combobox
                markersize = grid_item(i, 9).widget().value()  # Index in combobox
                marker_brush_color = grid_item(i, 10).widget().color
                marker_border_color = grid_item(i, 11).widget().color

                properties = CurveProperties(visibility, color, alias, interpolated, linestyle, linewidth, \
                                             markerstyle, markersize, marker_brush_color, marker_border_color)
                self.curve_properties.append(properties)

        #Clear items in grid layout widget
        for i in xrange(1, old_num_curves+1):
            for j in xrange(12):
                widget = grid_item(i, j).widget()
                widget.setParent(None)
                del widget

        #Remove selected radial-axis equations and associated legends, start with high index first
        deleted_curve_indices.reverse()

        for eqn_num in deleted_curve_indices:
            radialeqn = self.radial_axis_equations.pop(eqn_num)
            self.scene().removeItem(radialeqn)
            del radialeqn

            legend = self.radial_axis_legends.pop(eqn_num)
            self.scene().removeItem(legend)
            del legend

        #Update dialog GUI widget, legend, plot widget curve properties
        for i, property in enumerate(self.curve_properties):
            self.create_single_curve_options(i+1, property)  # property is a list of properties for a single curve

            legend = self.radial_axis_legends[i]
            legend.set_properties(self.curve_properties[i], self.font.pointSize())

            self.plot_widget.set_curve_properties(i, property)

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
        self.plot_widget.setAllFonts(self.font)
        self.azimuth_axis_equation.setFontSize(size)

        for i, yeqn in enumerate(self.radial_axis_equations):
            yeqn.setFontSize(size)
            self.radial_axis_legends[i].set_length(size)

        for limit in self.limit_equations:
            limit.setFontSize(size)

        self.layout_plot(self.width, self.height)

    def setFont(self, fontname):
        self.font.setFamily(fontname)
        self.plot_widget.setAllFonts(self.font)
        self.azimuth_axis_equation.setFont(fontname)

        for yeqn in self.radial_axis_equations:
            yeqn.setFont(fontname)

        for limit in self.limit_equations:
            limit.setFont(fontname)

        self.layout_plot(self.width, self.height)

    def layout_plot(self, w, h):
        font_size = self.font.pointSize()
        plot_widget = self.plot_widget
        label_distance = PolarPlot.label_distance_from_plot * font_size
        equation_vert_spacing = PolarPlot.equation_vertical_spacing * font_size
        equation_horiz_spacing = PolarPlot.equation_horizontal_spacing * font_size
        radial_axis_equations = self.radial_axis_equations
        legend_spacing = PolarPlot.legend_vertical_spacing * font_size

        radial_max_eqn = self.limit_equations[0]
        azimuth_offset_eqn = self.limit_equations[1]
        azimuth_max_eqn = self.limit_equations[2]
        azimuth_min_eqn = self.limit_equations[3]

        #Get dimensions of azimuth-axis label and max height of all azimuth-axis equations
        w1 = self.azimuth_axis_equation.width
        t1 = self.azimuth_axis_equation.top
        b1 = self.azimuth_axis_equation.bottom
        azimuth_equations_max_height = b1 - t1

        if azimuth_max_eqn.height > azimuth_equations_max_height:
            azimuth_equations_max_height = azimuth_max_eqn.height
        if azimuth_min_eqn.height > azimuth_equations_max_height:
            azimuth_equations_max_height = azimuth_min_eqn.height

        #Get max width of x-axis equations including spacing
        all_x_axis_equations_width = w1 + azimuth_min_eqn.width + azimuth_max_eqn.width + 2 * equation_horiz_spacing

        #Find widest y-axis equation and height of all y-axis equations including spacing
        y_axis_equations_max_width = 0
        total_yequations_height = 0
        for i, yeqn in enumerate(radial_axis_equations):
            total_yequations_height += yeqn.height
            total_yequations_height += self.radial_axis_legends[i].height

            if yeqn.width > y_axis_equations_max_width:
                y_axis_equations_max_width = yeqn.width

        if radial_max_eqn.width > y_axis_equations_max_width:
            y_axis_equations_max_width = radial_max_eqn.width
        if azimuth_offset_eqn.width > y_axis_equations_max_width:
            y_axis_equations_max_width = azimuth_offset_eqn.width

        total_yequations_height += (len(radial_axis_equations) * (equation_vert_spacing + legend_spacing))
        total_yequations_height -= equation_vert_spacing

        #Get height of all y-axis equations, including spacing and limit equations
        all_y_axis_equations_height = total_yequations_height + radial_max_eqn.height + azimuth_offset_eqn.height + 2 * equation_vert_spacing

        #Figure desired out dimensions of embedded plot widget
        width_of_plot = w - y_axis_equations_max_width - label_distance
        height_of_plot = h - azimuth_equations_max_height - label_distance

        #Limit minimum size of plot based on min size of plot widget
        min_width = plot_widget.minimum_plot_width
        min_height = plot_widget.minimum_plot_height
        if width_of_plot < min_width:
            width_of_plot = min_width
            w = width_of_plot + y_axis_equations_max_width + label_distance

        if height_of_plot < min_height:
            height_of_plot = min_height
            h = height_of_plot + azimuth_equations_max_height + label_distance

        #Limit minimum size of overall plot (widget + all equations)
        temp = all_x_axis_equations_width + equation_vert_spacing + y_axis_equations_max_width
        if w < temp:
            w = temp
            width_of_plot = all_x_axis_equations_width

        temp = all_y_axis_equations_height + azimuth_equations_max_height + label_distance
        if h < temp:
            h = temp
            height_of_plot = all_y_axis_equations_height

        #Resize and position plot widget
        self.plot_widget.resize(width_of_plot, height_of_plot)
        self.plot.setPos(y_axis_equations_max_width+label_distance, -h)

        #Position the x-axis equation
        x = azimuth_min_eqn.width + (width_of_plot - azimuth_max_eqn.width - azimuth_min_eqn.width) * 0.5 - w1 * 0.5
        self.azimuth_axis_equation.setPos(y_axis_equations_max_width+label_distance+x, -b1)

        #Position the y-axis equations
        y = -h + radial_max_eqn.height + \
            (height_of_plot - radial_max_eqn.height - azimuth_offset_eqn.height) * 0.5 - \
            total_yequations_height * 0.5

        for i, yeqn in enumerate(radial_axis_equations):
            y -= yeqn.top
            yeqn.setPos(0, y)
            legend = self.radial_axis_legends[i]
            y += (yeqn.bottom + legend_spacing - legend.top)
            legend.setPos(0, y+yeqn.bottom+legend_spacing-legend.top)
            y += (legend.bottom + equation_vert_spacing)

        #Position limit equations
        radial_max_eqn.setPos(0, -h-radial_max_eqn.top)
        azimuth_offset_eqn.setPos(0, -azimuth_equations_max_height - label_distance - azimuth_offset_eqn.bottom)
        azimuth_max_eqn.setPos(w-azimuth_max_eqn.width, -azimuth_max_eqn.bottom)
        azimuth_min_eqn.setPos(y_axis_equations_max_width+label_distance, -azimuth_min_eqn.bottom)

        #Figure out position and size of active box
        b = PolarPlot.border_width
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

        all_equations = [self.azimuth_axis_equation]
        all_equations.extend(self.radial_axis_equations)
        all_equations.extend(self.limit_equations)

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
            programs.append(self.object_id)
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
        angle = all_equations[0].result
        if angle == None:
            self.plot_widget.hide_plots()
            return

        #Update actual plot curves
        for i in xrange(len(self.radial_axis_equations)):
            r = all_equations[i+1].result
            if r != None and isinstance(angle, scipy.ndarray) and isinstance(r, scipy.ndarray) and len(angle) > 1 and len(angle) == len(r):
                self.plot_widget.set_plot_data(i, scipy.real(angle), scipy.real(r))
            else:
                self.plot_widget.hide_plot(i)

        n = len(all_equations) - 1
        radial_max = all_equations[n-3].result
        azimuth_offset = all_equations[n-2].result
        azimuth_max = all_equations[n-1].result
        azimuth_min = all_equations[n].result

        #Check radial axis scale limit
        if radial_max != None:
            if radial_max > 0:
                self.plot_widget.set_radius_axis_scale(radial_max)
            else:
                all_equations[n-3].setColor(QColor('red'))
                all_equations[n-3].setToolTip('Incorrect radius limit value')
                all_equations[n-2].setColor(QColor('red'))
                all_equations[n-2].setToolTip('Incorrect radius limit value')
                self.plot_widget.set_axis_autoscale()

        else:
            self.plot_widget.set_axis_autoscale()

        #Check azimuth offset limit
        if azimuth_offset != None:
            self.plot_widget.set_azimuth_offset(azimuth_offset)
        else:
            self.plot_widget.set_azimuth_offset(0)

        #Check azimuth-axis scale limits
        if azimuth_min != None and azimuth_max != None:
            if azimuth_max > azimuth_min:
                self.plot_widget.set_azimuth_axis_scale(azimuth_min, azimuth_max)
            else:
                all_equations[n-1].setColor(QColor('red'))
                all_equations[n-1].setToolTip('Max azimuth is smaller than min azimuth')
                all_equations[n].setColor(QColor('red'))
                all_equations[n].setToolTip('Max azimuth is smaller than min azimuth')
                self.plot_widget.set_axis_autoscale()

        else:
            self.plot_widget.set_axis_autoscale()

        self.plot_widget.replot()


class GridOptions(QWidget):
    def __init__(self, alignment):
        QWidget.__init__(self)
        #Major and minor checkboxes
        self.major_checkbox = QCheckBox('Show major %s gridlines' % alignment)
        self.major_checkbox.setChecked(True)
        self.minor_checkbox = QCheckBox('Show minor %s gridlines' % alignment)
        self.minor_checkbox.setChecked(False)
        self.minor_checkbox.setEnabled(True)

        layout = QVBoxLayout()
        layout.addWidget(self.major_checkbox)
        layout.addWidget(self.minor_checkbox)
        self.setLayout(layout)

        self.connect(self.major_checkbox, SIGNAL('stateChanged(int)'), self.major_change)

    def major_change(self, s):
        if s:
            self.minor_checkbox.setEnabled(True)
        else:
            self.minor_checkbox.setEnabled(False)


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
        self.plot_border_width.setRange(PolarPlot.minborderwidth, PolarPlot.maxborderwidth)

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


class CurveProperties:
    def __init__(self,
                 visibility=1,
                 line_color=QColor(0, 0, 0, 255),
                 antialias_flag=0,
                 interpolated_flag=0,
                 line_style_index=1,
                 line_width=1,
                 marker_style_index=0,
                 marker_size=10,
                 marker_color=QColor(0, 0, 0, 255),
                 marker_border_color=QColor(0, 0, 0, 255)):

        self.visibility = visibility
        self.line_color = line_color
        self.antialias_flag = antialias_flag
        self.interpolated_flag = interpolated_flag
        self.line_style_index = line_style_index
        self.line_width = line_width
        self.marker_style_index = marker_style_index
        self.marker_size = marker_size
        self.marker_color = marker_color
        self.marker_border_color = marker_border_color

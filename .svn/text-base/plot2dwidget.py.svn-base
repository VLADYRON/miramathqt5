
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
from PyQt4.Qwt5.anynumpy import *


class CartesianPlot(Qwt.QwtPlot):
    """Creates a coordinate system"""
    marker_style_strings = ['None',
                            u'\u25cf',
                            u'\u25a0',
                            u'\u25c6',
                            u'\u25b2',
                            u'\u25bc',
                            u'\u25c0',
                            u'\u25b6',
                            '+',
                            u'\u2715',
                            u'\u2500',
                            u'\u2502',
                            u'\u2055',
                            u'\u2217',
                            u'\u2b22']

    marker_styles = [Qwt.QwtSymbol.NoSymbol,
                     Qwt.QwtSymbol.Ellipse,
                     Qwt.QwtSymbol.Rect,
                     Qwt.QwtSymbol.Diamond,
                     Qwt.QwtSymbol.Triangle,
                     Qwt.QwtSymbol.DTriangle,
                     Qwt.QwtSymbol.LTriangle,
                     Qwt.QwtSymbol.RTriangle,
                     Qwt.QwtSymbol.Cross,
                     Qwt.QwtSymbol.XCross,
                     Qwt.QwtSymbol.HLine,
                     Qwt.QwtSymbol.VLine,
                     Qwt.QwtSymbol.Star1,
                     Qwt.QwtSymbol.Star2,
                     Qwt.QwtSymbol.Hexagon]

    curve_styles = [Qt.NoPen,
                    Qt.SolidLine,
                    Qt.DashLine,
                    Qt.DotLine,
                    Qt.DashDotLine,
                    Qt.DashDotDotLine,
                    Qt.CustomDashLine]

    def __init__(self, parent, parent_graphics_item, font, background_color, curve_properties):
        Qwt.QwtPlot.__init__(self, parent)

        self.parent_graphics_item = parent_graphics_item
        self.curves = []

        #Show widget before setting window flags
        self.show()
        self.setWindowFlags(Qt.Widget)
        self.setToolTip('2D Plot')

        self.setFont(font)

        #Plot canvas is a subclass of QFrame. Set some frame attributes
        self.canvas().setFrameStyle(QFrame.Box | QFrame.Plain)
        self.canvas().setLineWidth(0)

        #Set plot background and canvas background
        self.set_plot_background_color(background_color)

        # set plot layout
        self.plotLayout().setMargin(0)
        #self.plotLayout().setCanvasMargin(30)
        self.plotLayout().setAlignCanvasToScales(True)  #Overrides above line

        #Attach a grid.  Set default grid color and style.
        self.plot_grid = Qwt.QwtPlotGrid()
        self.plot_grid.attach(self)
        self.plot_grid.setPen(QPen(QColor('black'), 0, Qt.DotLine))

        #Enable x,y axes
        self.enableAxis(Qwt.QwtPlot.xBottom, True)
        self.enableAxis(Qwt.QwtPlot.yLeft, True)

        #Set axis fonts
        self.setAxisFont(Qwt.QwtPlot.xBottom, font)
        self.setAxisFont(Qwt.QwtPlot.yLeft, font)

        #Initialize with only one curve
        self.add_curve(curve_properties)

        #Find minimum size of plot widget
        min_size = self.minimumSizeHint()
        self.minimum_plot_width = min_size.width()
        self.minimum_plot_height = min_size.height()

        #Create plot zoomers
        self.create_zoomers()

        self.replot()

    def mousePressEvent(self, event):
        QWidget.mousePressEvent(self, event)
        event.accept()
        self.parent_graphics_item.setSelected(True)

    def mouseDoubleClickEvent(self, event):
        QWidget.mouseDoubleClickEvent(self, event)
        self.parent_graphics_item.preferences_dialog.show()

    def set_plot_background_color(self, color):
        self.background_color = color
        palette1 = self.palette()
        palette1.setColor(QPalette.Window, QColor(0, 0, 0, 0))
        self.setPalette(palette1)  # Set Plot+axes background color
        self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintCached,  False)
        self.setCanvasBackground(color)

    def setAllFonts(self, font):
        size = font.pointSize()
        #font.setPointSize(size*0.75)
        self.setFont(font)
        self.setAxisFont(Qwt.QwtPlot.xBottom, font)
        self.setAxisFont(Qwt.QwtPlot.yLeft, font)

        #Find minimum size of plot widget after changing font
        min_size = self.minimumSizeHint()
        self.minimum_plot_width = min_size.width()
        self.minimum_plot_height = min_size.height()
        self.replot()

    def add_curve(self, curve_properties):
        curve = Qwt.QwtPlotCurve()
        curve.attach(self)
        self.curves.append(curve)
        self.set_curve_properties(len(self.curves)-1, curve_properties)

    def remove_curve(self, i):
        deleted_curve = self.curves.pop(i-1)
        deleted_curve.detach()
        del deleted_curve

    def set_curve_properties(self, i, properties):
        #Set line visibility
        c = self.curves[i]
        c.setVisible(properties.visibility)

        #Set line color and width and style
        pen = QPen(properties.line_color)
        pen.setWidth(properties.line_width)
        style = CartesianPlot.curve_styles[properties.line_style_index]
        pen.setStyle(style)
        c.setPen(pen)

        #Set alias
        c.setRenderHint(Qwt.QwtPlotItem.RenderAntialiased, properties.antialias_flag)

        #Set interpolated flag
        c.setCurveAttribute(Qwt.QwtPlotCurve.Fitted, properties.interpolated_flag)

        #Set marker style and size and color
        marker_style_combobox_index = properties.marker_style_index
        if marker_style_combobox_index > 0:
            marker_style_combobox_index -= 1  #Fix index due to spacer in style combobox

        style = CartesianPlot.marker_styles[marker_style_combobox_index]
        marker = Qwt.QwtSymbol()
        marker.setStyle(style)
        marker.setSize(properties.marker_size)
        marker.setPen(QPen(properties.marker_border_color))
        marker.setBrush(QBrush(properties.marker_color))
        c.setSymbol(marker)

        self.replot()

    def set_plot_data(self, i, x, y):
        curve = self.curves[i]
        curve.show()
        curve.setData(x, y)

    def hide_plot(self, i):
        curve = self.curves[i]
        curve.hide()
        self.replot()

    def set_y_axis_scale(self, min, max):
        self.setAxisScale(Qwt.QwtPlot.yLeft, min, max)
        self.replot()

    def set_x_axis_scale(self, min, max):
        self.setAxisScale(Qwt.QwtPlot.xBottom, min, max)
        self.replot()

    def set_y_axis_autoscale(self):
        self.setAxisAutoScale(Qwt.QwtPlot.yLeft)
        self.replot()

    def set_x_axis_autoscale(self):
        self.setAxisAutoScale(Qwt.QwtPlot.xBottom)
        self.replot()

    def set_x_axis_logscale(self, flag):
        if flag:
            self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLog10ScaleEngine())
        else:
            self.setAxisScaleEngine(Qwt.QwtPlot.xBottom, Qwt.QwtLinearScaleEngine())

    def set_y_axis_logscale(self, flag):
        if flag:
            self.setAxisScaleEngine(Qwt.QwtPlot.yLeft, Qwt.QwtLog10ScaleEngine())
        else:
            self.setAxisScaleEngine(Qwt.QwtPlot.yLeft, Qwt.QwtLinearScaleEngine())

    def hide_plots(self):
        for curve in self.curves:
            curve.hide()
        self.replot()

    def y_axis_midpoint(self):
        backbone_length = self.axisWidget(Qwt.QwtPlot.yLeft).scaleDraw().length()
        backbone_y = self.axisWidget(Qwt.QwtPlot.yLeft).scaleDraw().pos().y()
        return backbone_y + backbone_length/2

    def x_axis_midpoint(self):
        backbone_length = self.axisWidget(Qwt.QwtPlot.xBottom).scaleDraw().length()
        backbone_x = self.axisWidget(Qwt.QwtPlot.xBottom).scaleDraw().pos().x()
        axis_widget_x = self.axisWidget(Qwt.QwtPlot.xBottom).pos().x()
        return axis_widget_x + backbone_x + backbone_length/2

    def create_zoomers(self):
        self.zoomers = []
        zoomer = Qwt.QwtPlotZoomer(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yLeft,
            Qwt.QwtPicker.DragSelection,
            Qwt.QwtPicker.AlwaysOff,
            self.canvas())
        zoomer.setRubberBandPen(QPen(Qt.black))
        self.zoomers.append(zoomer)

        zoomer = Qwt.QwtPlotZoomer(
            Qwt.QwtPlot.xTop,
            Qwt.QwtPlot.yRight,
            Qwt.QwtPicker.PointSelection | Qwt.QwtPicker.DragSelection,
            Qwt.QwtPicker.AlwaysOff,
            self.canvas())
        zoomer.setRubberBand(Qwt.QwtPicker.NoRubberBand)
        self.zoomers.append(zoomer)

        self.picker = Qwt.QwtPlotPicker(
            Qwt.QwtPlot.xBottom,
            Qwt.QwtPlot.yLeft,
            Qwt.QwtPicker.PointSelection | Qwt.QwtPicker.DragSelection,
            Qwt.QwtPlotPicker.CrossRubberBand,
            Qwt.QwtPicker.AlwaysOn,
            self.canvas())
        self.picker.setRubberBandPen(QPen(Qt.black))
        self.picker.setTrackerPen(QPen(Qt.black))



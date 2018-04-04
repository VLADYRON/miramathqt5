
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
from PyQt4.Qwt5.anynumpy import *


class PolarPlotWidget(Qwt.QwtPolarPlot):
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
        Qwt.QwtPolarPlot.__init__(self, parent)

        self.parent_graphics_item = parent_graphics_item
        self.curves = []

        #Show widget before setting window flags
        self.show()
        self.setWindowFlags(Qt.Widget)
        self.setToolTip('2D Polar Plot')

        #Set font for entire plot widget
        self.setFont(font)

        #Plot canvas is a subclass of QFrame. Set some frame attributes
        self.canvas().setFrameStyle(QFrame.Box | QFrame.Plain)
        self.canvas().setLineWidth(0)

        #Set plot background and canvas background
        self.set_plot_background_color(background_color)

        #Attach a grid.  Set default grid color and style.
        self.plot_grid = Qwt.QwtPolarGrid()
        self.plot_grid.attach(self)
        self.plot_grid.setPen(QPen(QColor('black'), 0, Qt.DotLine))
        self.plot_grid.setFont(font)

        #Initialize with only one curve
        self.add_curve(curve_properties)

        #Find minimum size of plot widget
        min_size = self.minimumSizeHint()
        self.minimum_plot_width = min_size.width()
        self.minimum_plot_height = min_size.height()

        #Create plot zoomers
        #self.create_zoomers()

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
        self.canvas().setPaintAttribute(Qwt.QwtPolarCanvas.PaintCached,  False)
        self.setPlotBackground(QBrush(QColor(color)))

    def setAllFonts(self, font):
        size = font.pointSize()
        self.setFont(font)
        self.plot_grid.setFont(font)

        #Find minimum size of plot widget after changing font
        min_size = self.minimumSizeHint()
        self.minimum_plot_width = min_size.width()
        self.minimum_plot_height = min_size.height()
        self.replot()

    def add_curve(self, curve_properties):
        curve = Qwt.QwtPolarCurve()
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
        style = PolarPlotWidget.curve_styles[properties.line_style_index]
        pen.setStyle(style)
        c.setPen(pen)

        #Set alias
        c.setRenderHint(Qwt.QwtPolarItem.RenderAntialiased, properties.antialias_flag)

        #Set interpolated flag
        if properties.interpolated_flag:
            c.setCurveFitter(Qwt.QwtPolarFitter())
        else:
            c.setCurveFitter(None)

        #Set marker style and size and color
        marker_style_combobox_index = properties.marker_style_index
        if marker_style_combobox_index > 0:
            marker_style_combobox_index -= 1  #Fix index due to spacer in style combobox

        style = PolarPlotWidget.marker_styles[marker_style_combobox_index]
        marker = Qwt.QwtSymbol()
        marker.setStyle(style)
        marker.setSize(properties.marker_size)
        marker.setPen(QPen(properties.marker_border_color))
        marker.setBrush(QBrush(properties.marker_color))
        c.setSymbol(marker)

        self.replot()

    def set_grid_line_properties(self, show_major_radials_flag, show_minor_radials_flag, \
                                 show_major_circles_flag, show_minor_circles_flag, \
                                 major_grid_color, minor_grid_color, \
                                 major_width, minor_width):
        grid = self.plot_grid
        grid.setMajorGridPen(QPen(QColor(major_grid_color), major_width, Qt.DotLine))
        grid.setMinorGridPen(QPen(QColor(minor_grid_color), minor_width, Qt.DotLine))
        grid.showGrid(Qwt.QwtPolar.Azimuth, show_major_circles_flag)
        grid.showGrid(Qwt.QwtPolar.Radius, show_major_radials_flag)
        grid.showMinorGrid(Qwt.QwtPolar.Azimuth, show_minor_circles_flag)
        grid.showMinorGrid(Qwt.QwtPolar.Radius, show_minor_radials_flag)

    def set_plot_data(self, i, x, y):
        curve = self.curves[i]
        curve.show()
        curve.setData(x, y)

    def hide_plot(self, i):
        curve = self.curves[i]
        curve.hide()
        self.replot()

    def set_azimuth_axis_scale(self, min, max):
        print 'min,max azimuth=', min, max
        self.setScale(Qwt.QwtPolar.Azimuth, min, min, 10)
        #self.setScaleMaxMinor(Qwt.QwtPolar.Azimuth, 2)
        self.replot()

    def set_azimuth_offset(self, offset):
        self.setAzimuthOrigin((offset * 2 * pi)/360)

    def set_radius_axis_scale(self, max):
        print 'max radius=', max
        self.setScale(Qwt.QwtPolar.Radius, 0, max)
        self.replot()

    def set_axis_autoscale(self):
        self.setAutoScale(True)
        self.replot()

    def set_radius_axis_logscale(self, flag):
        if flag:
            self.engione=Qwt.QwtLog10ScaleEngine()
            self.setScaleEngine(Qwt.QwtPolar.Radius, self.engione)
        else:
            self.setScaleEngine(Qwt.QwtPolar.Radius, Qwt.QwtLinearScaleEngine())

    def set_azimuth_axis_logscale(self, flag):
        if flag:
            self.setScaleEngine(Qwt.QwtPolar.Azimuth, Qwt.QwtLog10ScaleEngine())
        else:
            self.setScaleEngine(Qwt.QwtPolar.Azimuth, Qwt.QwtLinearScaleEngine())

    def hide_plots(self):
        for curve in self.curves:
            curve.hide()
        self.replot()

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




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
import scipy

from PyQt4.QtCore import *
from PyQt4.QtGui import *
import PyQt4.Qwt5 as Qwt


class ContourPlot(Qwt.QwtPlot):

    contour_styles = [Qt.NoPen,
                      Qt.SolidLine,
                      Qt.DashLine,
                      Qt.DotLine,
                      Qt.DashDotLine,
                      Qt.DashDotDotLine,
                      Qt.CustomDashLine]

    mincontourwidth = 0
    maxcontourwidth = 5

    def __init__(self, parent_graphics_item, font, background_color):
        Qwt.QwtPlot.__init__(self, None)

        self.parent_graphics_item = parent_graphics_item

        #Show widget before setting window flags
        self.show()

        #Plot canvas is a subclass of QFrame. Set some frame attributes
        self.canvas().setFrameStyle(QFrame.Box | QFrame.Plain)
        self.canvas().setLineWidth(1)

        colorMap = Qwt.QwtLinearColorMap(Qt.darkCyan, Qt.red)
        colorMap.addColorStop(0.1, Qt.cyan)
        colorMap.addColorStop(0.6, Qt.green)
        colorMap.addColorStop(0.95, Qt.yellow)

        #Create spectrogram widget and attach to self
        self.spectrogram = Qwt.QwtPlotSpectrogram()
        self.spectrogram.setColorMap(colorMap)
        self.spectrogram.setData(SpectrogramData())
        self.spectrogram.attach(self)
        self.spectrogram.setContourLevels(scipy.arange(0, 1, 0.1).tolist())
        self.spectrogram.setDisplayMode(Qwt.QwtPlotSpectrogram.ContourMode, True)

        #Allow canvas caching for initial plot
        self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintCached, True)

        #Set up colormap and side bar color-value mapping
        rightAxis = self.axisWidget(Qwt.QwtPlot.yRight)
        rightAxis.setTitle("Intensity")
        rightAxis.setColorBarEnabled(True)
        rightAxis.setColorMap(self.spectrogram.data().range(), self.spectrogram.colorMap())

        self.setAxisScale(Qwt.QwtPlot.yRight,
                          self.spectrogram.data().range().minValue(),
                          self.spectrogram.data().range().maxValue())
        self.enableAxis(Qwt.QwtPlot.yRight)

        self.plotLayout().setAlignCanvasToScales(True)

        # LeftButton for the zooming
        # MidButton for the panning
        # RightButton: zoom out by 1
        # Ctrl+RighButton: zoom out to full size
        zoomer = Qwt.QwtPlotZoomer(self.canvas())
        zoomer.setMousePattern(Qwt.QwtEventPattern.MouseSelect2, Qt.RightButton, Qt.ControlModifier)
        zoomer.setMousePattern(Qwt.QwtEventPattern.MouseSelect3, Qt.RightButton)
        zoomer.setRubberBandPen(Qt.darkBlue)
        zoomer.setTrackerPen(Qt.darkBlue)

        panner = Qwt.QwtPlotPanner(self.canvas())
        panner.setAxisEnabled(Qwt.QwtPlot.yRight, False)
        panner.setMouseButton(Qt.MidButton)

        # Avoid jumping when labels with more/less digits
        # appear/disappear when scrolling vertically
        fm = QFontMetrics(self.axisWidget(Qwt.QwtPlot.yLeft).font())
        self.axisScaleDraw(Qwt.QwtPlot.yLeft).setMinimumExtent(fm.width("100.00"))

        #Set plot background and canvas background
        self.set_plot_background_color(background_color)

        #Set plot default font
        self.set_all_fonts(font)

        #Find minimum size of plot widget
        min_size = self.minimumSizeHint()
        self.minimum_plot_width = min_size.width()
        self.minimum_plot_height = min_size.height()

        #self.set_y_axis_scale(0, 0.5)


        #self.show_spectrogram(False)



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
        self.setCanvasBackground(color)

    def set_all_fonts(self, font):
        size = font.pointSize()
        self.setFont(font)

        self.setAxisFont(Qwt.QwtPlot.xBottom, font)
        self.setAxisFont(Qwt.QwtPlot.yLeft, font)
        self.setAxisFont(Qwt.QwtPlot.yRight, font)

        right_axis = self.axisWidget(Qwt.QwtPlot.yRight)
        right_title = right_axis.title()
        right_title.setFont(font)
        right_axis.setTitle(right_title)

        #Find minimum size of plot widget after changing font
        min_size = self.minimumSizeHint()
        self.minimum_plot_width = min_size.width()
        self.minimum_plot_height = min_size.height()
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

    def show_contour(self, on):
        self.spectrogram.setDisplayMode(Qwt.QwtPlotSpectrogram.ContourMode, on)
        self.replot()

    def show_spectrogram(self, on):
        self.spectrogram.setDisplayMode(Qwt.QwtPlotSpectrogram.ImageMode, on)
        if on:
            pen = QPen()
            self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintCached, True)
        else:
            pen = QPen(Qt.NoPen)
            self.canvas().setPaintAttribute(Qwt.QwtPlotCanvas.PaintCached, False)

        self.spectrogram.setDefaultContourPen(pen)
        self.replot();



class SpectrogramData(Qwt.QwtRasterData):
    def __init__(self):
        Qwt.QwtRasterData.__init__(self, QRectF(0, 0, 1.0, 1.0))

    def copy(self):
        return self

    def initRaster(self, rect, size):
        print rect, size
        Qwt.QwtRasterData.initRaster(self, rect, size)


    def range(self):
        return Qwt.QwtDoubleInterval(0.0, 1.0)

    def value(self, x, y):
#        c = 0.842
#        v1 = x * x + (y-c) * (y+c)
#        v2 = x * (y+c) + x * (y+c)
#        return 1.0 / (v1 * v1 + v2 * v2)
        return 0.75 * scipy.e**-(((9 * x - 2)**2 + (9 * y - 2)**2)/4) + x




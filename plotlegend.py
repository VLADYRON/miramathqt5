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


class Legend(QGraphicsLineItem):
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

    curve_styles = [Qt.NoPen,
                    Qt.SolidLine,
                    Qt.DashLine,
                    Qt.DotLine,
                    Qt.DashDotLine,
                    Qt.DashDotDotLine,
                    Qt.CustomDashLine]

    def __init__(self, parent):
        QGraphicsLineItem.__init__(self, parent)
        self.marker = QGraphicsSimpleTextItem(self)
        self.marker.setFont(QFont('Arial', 12))
        self.setZValue(300)
        self.height = 12
        self.top = 0
        self.bottom = 0
        self.hide()

    def set_length(self, s):
        length = 3 * s
        old_length = self.line().length()
        self.setLine(0, 0, length, 0)
        x = (-old_length + length) * 0.5
        self.marker.moveBy(x, 0)

    def set_properties(self, properties, fontsize):
        self.show()

        #Set legend line width, style, color
        pen = self.pen()
        pen.setWidth(properties.line_width)
        pen.setColor(properties.line_color)
        style = Legend.curve_styles[properties.line_style_index]
        pen.setStyle(style)
        self.setPen(pen)

        #Set legend line length
        length = 3 * fontsize
        self.setLine(0, 0, length, 0)

        mark_style_index = properties.marker_style_index

        if mark_style_index > 0:
            mark_style_index -= 1
            s = Legend.marker_style_strings[mark_style_index]
            self.marker.setText(s)

            #Set marker size
            marker_height = properties.marker_size
            f = self.marker.font()
            f.setPointSize(marker_height)
            self.marker.setFont(f)

            #Set marker brush and pen
            self.marker.setBrush(QBrush(properties.marker_color))
            self.marker.setPen(QPen(properties.marker_border_color))

            #Position marker
            metric = QFontMetrics(f)
            rect = metric.tightBoundingRect(s)
            baseline = metric.ascent()
            top = rect.top()
            bottom = rect.bottom()
            diff = abs(top) - abs(bottom)
            width = metric.width(s)
            self.height = diff
            self.top = -diff/2
            self.bottom = diff/2
            self.marker.setPos((length-width)/2, -baseline-self.top)
            self.marker.show()

        else:
            #No marker selected so hide it
            self.marker.hide()


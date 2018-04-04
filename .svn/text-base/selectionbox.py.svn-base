
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

class SelectionBox(QGraphicsPathItem):
    '''For equations draw rectangle around selected text.
       For text boxes draw a polygon around selected text.'''
    def __init__(self, parent=None):
        QGraphicsPathItem.__init__(self, parent)
        self.hide()

        pen = QPen(Qt.DashLine)
        pen.setCapStyle(Qt.SquareCap)
        pen.setJoinStyle(Qt.MiterJoin)
        pen.setColor(QColor('red'))
        pen.setWidthF(0.01)
        self.setPen(pen)
        self.setZValue(2)
        self.object_type = 'selectionbox'

    def paint(self, painter, option, widget):
        painter.setRenderHint(QPainter.Antialiasing, False)
        QGraphicsPathItem.paint(self, painter, option, widget)

    def setColor(self, color):
        brush = QBrush(color)
        self.setBrush(brush)

    def createBox(self, points):  #Expects a list of x,y pairs
        x0 = points[0]
        y0 = points[1]
        path = QPainterPath(QPointF(x0, y0))
        for i in range(2, len(points), 2):
            path.lineTo(points[i], points[i+1])
        path.closeSubpath()

        self.setPath(path)



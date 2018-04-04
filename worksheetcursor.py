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


class WorksheetCursor(QGraphicsItem):
    def __init__(self, h = 4):
        QGraphicsItem.__init__(self)
        self.visible = True
        self.size = h
        self.setEnabled(False)
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setPos(10,10)
        self.rectangle = QRectF(-h, -h, 2*h, 2*h)
        pen = QPen(Qt.SolidLine)
        pen.setColor(QColor('black'))
        pen.setWidth(0)
        self.pen = pen
        self.point1 = QPoint(-h,0)
        self.point2 = QPoint(h,0)
        self.point3 = QPoint(0,-h)
        self.point4 = QPoint(0,h)

    def boundingRect(self):
        return self.rectangle

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setRenderHint(QPainter.Antialiasing, 0)
        painter.drawLines(self.point1, self.point2, self.point3, self.point4)


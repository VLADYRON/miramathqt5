

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


class EquationCursor(QGraphicsItem):
    def __init__(self, parent):
        QGraphicsItem.__init__(self, parent)
        self.setEnabled(True)
        self.setAcceptedMouseButtons(Qt.NoButton)
        self.setFlag(QGraphicsItem.ItemIsSelectable, False)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
        self.setFlag(QGraphicsItem.ItemIsFocusable, False)
        self.setZValue(3)

        self.object_type = None

        self.point1 = QPoint(0, 0)
        self.point2 = QPoint(0, 0)
        self.point3 = QPoint(0, 0)
        self.point4 = QPoint(0, 0)
        self.visible = True
        self.height = 0              #Cursor height
        self.baselength = 0         #Cursor base line end position
        self.position = 0           #Vertical bar position
        self.rectangle = QRectF(0, 0, 0, 0)
        pen = QPen(Qt.SolidLine)
        pen.setColor(QColor('blue'))
        pen.setWidthF(1)
        self.pen = pen
        self.show()

        #Setup and start timer to blink cursor
        self.timer_interval = 400
        self.timer = QTimer()
        self.timer.setInterval(self.timer_interval)
        self.timer.connect(self.timer, SIGNAL('timeout()'), self.blinkCursor)
        self.timer.start()

    def boundingRect(self):
        return self.rectangle

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)
        painter.setRenderHint(QPainter.Antialiasing, 0)
        if self.baselength > 0.0:
            p1 = self.point1
            p2 = self.point2
            painter.drawLine(p1, p2)

        if self.visible:
            p3 = self.point3
            p4 = self.point4
            painter.drawLine(p3, p4)

    def blinkCursor(self):
        if self.visible == True:
            self.visible = False
            self.update(self.rectangle)
        else:
            self.visible = True
            self.update(self.rectangle)

    def setPosition(self, startx, starty, position, length, height):
        """set position of cursor. x,y are the coordinates of the left end of the baseline.
        position is the x coordinate of the vertical bar.
        length is the length of the baseline"""
        self.prepareGeometryChange()
        self.setPos(startx, starty)
        self.height = height
        self.point1 = QPoint(0, 0)
        self.point2 = QPoint(length, 0)
        self.point3 = QPoint(position, 0)
        self.point4 = QPoint(position, -height)
        self.baselength = length
        self.position = position   #Position of vertical cursor bar relative to start
        self.rectangle = QRectF(0, -height-10, length+1, height+20)
        self.update(self.rectangle)

    def setSize(self, size):
        self.height = size

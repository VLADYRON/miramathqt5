
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


#from PyQt4 import Qt
from PyQt4.QtCore import *
from PyQt4.QtGui import *


class ActiveBox(QGraphicsRectItem):
    def __init__(self, type, parent=None):
        QGraphicsRectItem.__init__(self, parent)
        self.hide()
        self.setZValue(0)
        pen = QPen(Qt.NoPen)
        self.setPen(pen)
        self.resizeHandles = []
        self.resizeHandleSize = 8
        self.resizeHandlesAreVisible = False
        self.activeBoxType = type
        self.object_type = 'activebox'
        self.numhandles = 0

        if type == 'plot' or type == 'table':
            self.numhandles = 8
            cursors = [Qt.SizeHorCursor,\
                       Qt.SizeFDiagCursor,\
                       Qt.SizeVerCursor,\
                       Qt.SizeVerCursor,\
                       Qt.SizeBDiagCursor,\
                       Qt.SizeFDiagCursor,
                       Qt.SizeHorCursor,\
                       Qt.SizeBDiagCursor]

        elif type == 'comment' or type == 'slider':
            self.numhandles = 2
            cursors = [Qt.SizeHorCursor,\
                       Qt.SizeHorCursor]

        elif type == 'image':
            self.numhandles = 2
            cursors = [Qt.SizeVerCursor,\
                       Qt.SizeVerCursor]

        #numhandles should be either 5 or 8 for a table or plot respectively
        for i in xrange(self.numhandles):
            h = ResizeHandle(self, self.resizeHandleSize, cursors[i])
            self.resizeHandles.append(h)

        #self.hide()
        self.showBox(False)

    def setColor(self, color):
        brush = QBrush(color)
        self.setBrush(brush)

    def setSize(self, w, h):
        self.setRect(0, 0, w, h)
        d = self.resizeHandleSize
        d2 = d/2
        w2 = w/2
        h2 = h/2

        if self.activeBoxType == 'plot' or self.activeBoxType == 'table':
            self.resizeHandles[0].setPos(w-d, h2-d2)
            self.resizeHandles[1].setPos(w-d, h-d)
            self.resizeHandles[2].setPos(w2-d2, h-d)
            self.resizeHandles[3].setPos(w2-d2, 0)
            self.resizeHandles[4].setPos(w-d, 0)
            self.resizeHandles[5].setPos(0, 0)
            self.resizeHandles[6].setPos(0, h2-d2)
            self.resizeHandles[7].setPos(0, h-d)

        elif self.activeBoxType == 'comment' or self.activeBoxType == 'slider':
            self.resizeHandles[0].setPos(w-d, h2-d2)
            self.resizeHandles[1].setPos(0, h2-d2)

        elif self.activeBoxType == 'image':
            self.resizeHandles[0].setPos(w2-d2, h-d)
            self.resizeHandles[1].setPos(w2-d2, 0)

    def mouseInResizeHandle(self, p):
        #Returns index of clicked resize handle or zero if non clicked
        retval = 0
        if self.resizeHandlesAreVisible:
            p = self.mapFromParent(p)   #Parent is QGraphicsProxyWidget
            for i, h in enumerate(self.resizeHandles):
                localp = self.mapToItem(h, p)
                if h.contains(localp):
                    retval = i + 1
                    break

        return retval

    def showResizeHandles(self):
        self.resizeHandlesAreVisible = True
        num = self.numhandles
        [self.resizeHandles[i].show() for i in xrange(num)]

    def hideResizeHandles(self):
        self.resizeHandlesAreVisible = False
        num = self.numhandles
        [self.resizeHandles[i].hide() for i in xrange(num)]

    def showBox(self, flag):
        self.show()
        if flag:
            self.showResizeHandles()
        else:
            self.hideResizeHandles()

    def hideBox(self):
        self.hide()
        self.hideResizeHandles()


class ResizeHandle(QGraphicsRectItem):
    def __init__(self, parent, size, cursor):
        QGraphicsRectItem.__init__(self, parent)
        self.object_type = 'resizehandle'
        self.setPen(QPen(Qt.NoPen))
        brush = QBrush(QColor('Blue'))
        self.setBrush(brush)
        self.setCursor(cursor)
        self.setRect(0, 0, size, size)
        self.hide()


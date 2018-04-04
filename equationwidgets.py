
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

import scipy
import time

_LINE_SCALE_FACTOR   = 0.1


class EquationChar(QGraphicsSimpleTextItem):
    """Holds an equation widjet"""

    def __init__(self, parent, value, ascii_value, font):
        QGraphicsSimpleTextItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setText(value)
        self.setAcceptsHoverEvents(True)

        self.value = value
        self.ascii_value = ascii_value
        self.setZValue(100)
        #self.setCursor(Qt.IBeamCursor)  #This really slows down things
        self.object_type = 'character'
        self.setFont(font)
        self.computeCharDimensions()
        self.fontSize = font.pointSize()

        #Used when arrow keys pressed
        self.cursorRight = 1
        self.cursorLeft = 1

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 1
        self.cursorClickMoveLeft = 0

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.IBeamCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

    def setSize(self, fontsize):
        if fontsize != self.fontSize:
            self.fontSize = fontsize
            font = self.font()
            font.setPointSize(fontsize)
            self.setFont(font)
            self.computeCharDimensions()

    def setFontName(self, fontname):
        font = self.font()
        font.setFamily(fontname)
        self.setFont(font)
        self.computeCharDimensions()

    def setToItalic(self, state):
        font = self.font()
        font.setItalic(state)
        self.setFont(font)
        self.update()
        self.computeCharDimensions()

    def setToBold(self, state):
        font = self.font()
        font.setBold(state)
        self.setFont(font)
        self.update()
        self.computeCharDimensions()

    def setToUnderline(self, state):
        font = self.font()
        font.setUnderline(state)
        self.setFont(font)
        self.update()
        self.computeCharDimensions()

    def computeCharDimensions(self):
        metric = QFontMetrics(self.font())
        self.baseline = metric.ascent()         #Get baseline of character
        self.width = metric.width(self.value)
        rect = metric.tightBoundingRect(self.value)
        self.top = rect.top()
        self.bottom = rect.bottom()

#        p = QPainterPath()
#        p.addText(QPointF(0,0), self.font(), self.value)
#        r = p.boundingRect()
#        self.top = r.top()
#        self.bottom = r.bottom() + 1
#        self.width = r.width()*1.3

    def setPosition(self, x, y):
        y = y - self.baseline
        self.setPos(x, y)

    def getPosition(self):
        p = self.pos()
        x = p.x()
        y = p.y()
        y = y + self.baseline
        return x, y

    def setColor(self, color):
        brush = QBrush(color)
        self.setBrush(brush)

    def setItalic(self):
        font = self.font()
        font.setItalic(True)
        self.setFont(font)

    def setNormal(self):
        font = self.font()
        font.setItalic(False)
        self.setFont(font)

    def setBold(self):
        font = self.font()
        font.setBold(True)
        self.setFont(font)

    def getDict(self):
        return self.__dict__


class EquationSpace(QGraphicsRectItem):
    """Holds an equation widjet"""
    def __init__(self, parent):
        QGraphicsSimpleTextItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.setVisible(False)
        self.ascii_value = ''
        self.object_type = 'character'
        self.fontSize = 0

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 1
        self.cursorClickMoveLeft = 0

    def setSize(self, fontsize):
        self.fontSize = fontsize
        self.width = fontsize
        self.top = -fontsize
        self.bottom = 0
        self.setRect(0, 0, self.width, self.top)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        p = self.pos()
        x = p.x()
        y = p.y()
        return x, y

    def setColor(self, color):
        return

    def getDict(self):
        return self.__dict__



class EquationDivideLine(QGraphicsLineItem):
    '''Scalable divide line'''
    def __init__(self, parent):
        QGraphicsLineItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.object_type = 'character'
        self.value = '__divideline__'
        self.ascii_value = '__divideline__'
        self.setZValue(100)
        self.setCursor(Qt.IBeamCursor)
        pen = QPen()
        pen.setWidthF(1)
        pen.setCapStyle(Qt.SquareCap)
        self.setPen(pen)
        self.setEnabled(True)

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 2
        self.cursorClickMoveLeft = 1

    def setSize(self, fontsize, length):
        pen = self.pen()
        pen.setWidth(fontsize * _LINE_SCALE_FACTOR)
        self.setPen(pen)
        self.fontSize = fontsize
        self.top = -fontsize * 0.3
        self.bottom = fontsize * 0.3
        self.spacing = fontsize * 0.3
        self.length = length + fontsize * 0.2  #Add some extra length on ends of divide line
        self.width = self.length + 2 * self.spacing  #Put some spacing around ends of divide line
        self.prepareGeometryChange()
        self.setLine(self.spacing, 0, self.spacing+self.length, 0)

    def setColor(self, color):
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        return self.__dict__


class EquationSquareRootLine(QGraphicsItem):
    '''Scalable square root symbol'''
    def __init__(self, parent):
        QGraphicsItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.bounding_rect = QRectF(0, 0, 0, 0)
        pen = QPen(QColor('black'))
        pen.setWidthF(1)
        pen.setCapStyle(Qt.SquareCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.pen = pen
        self.setZValue(99)
        self.object_type = 'character'
        self.value = '__squareroot__'
        self.ascii_value = '__squareroot__'

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 2
        self.cursorClickMoveLeft = -1

    def boundingRect(self):
        return self.bounding_rect

    def paint(self, painter, option, widget):
        painter.setPen(self.pen)

        #Paint left sloping parts of square root sign
        painter.pen().setJoinStyle(Qt.RoundJoin)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawPath(self.path1)

        #Paint top horiz bar of square root sign
        painter.pen().setJoinStyle(Qt.MiterJoin)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.drawPath(self.path2)

    def setColor(self, color):
        self.pen.setColor(color)

    def setSize(self, width, height, fontsize):
        self.pen.setWidth(fontsize * _LINE_SCALE_FACTOR)
        self.fontSize = fontsize
        vspacing_inside = fontsize * 0.4
        hspacing_inside = fontsize * 0.2
        vspacing_outside = fontsize * 0.1
        lspacing_outside = fontsize * 0.3
        rspacing_outside = fontsize * 0.3

        h = height + vspacing_inside
        w = width
        x = lspacing_outside
        x1 = x
        x2 = x + 0.1 * h
        x3 = x + 0.3 * h
        x4 = x + 0.4 * h
        x5 = x4 + w + hspacing_inside * 2
        self.top = -(h + vspacing_outside)
        self.bottom = 0
        self.contentsOffset = x4 + hspacing_inside  #Used by drawing code to position root contents inside root symbol
        self.orderBottomRHCx = x2  #Used by drawing code for positioning the order of an n-th order root
        self.orderBottomRHCy = -0.7 * h  #Used by drawing code for positioning the order of an n-th order root
        self.width = x5 + rspacing_outside
        self.prepareGeometryChange()  #Call this before changing size of bounding rect
        self.bounding_rect = QRectF(0-5, self.top-5, self.width+10, -self.top+10)

        #path1 is antialiased part of squareroot symbol
        path1 = QPainterPath()
        path1.moveTo(x1, -0.4*h)
        path1.lineTo(x2, -0.55*h)
        path1.lineTo(x3, 0)
        path1.lineTo(x4, -h+1)  #Since anti-aliasing is turned on for this path we add 0.5 to -h here to prevent overshoot
        thickness = fontsize * 0.04
        path1.moveTo(x3, 0)
        path1.lineTo(x3-thickness, 0)
        path1.lineTo(x2-thickness, -0.55*h)
        path1.lineTo(x2, -0.55*h)
        path1.lineTo(x2-thickness, -0.55*h)
        path1.lineTo(x1, -0.4*h)
        self.path1 = path1

        #path2 is aliased
        path2 = QPainterPath()
        path2.moveTo(x4, -h)
        path2.lineTo(x5, -h)
        path2.lineTo(x5, -0.9*h)
        self.path2 = path2

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        d = self.__dict__.copy()
        del d['pen']
        del d['path1']
        del d['path2']
        return d


class EquationSquareBracketLine(QGraphicsPathItem):
    '''Scalable square brackets'''
    def __init__(self, parent, value = '__leftsquarebracket__'):
        QGraphicsPathItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        pen = QPen(QColor('black'))
        pen.setCapStyle(Qt.SquareCap)
        pen.setJoinStyle(Qt.MiterJoin)
        pen.setWidth(1)
        self.setPen(pen)
        self.setZValue(100)
        self.setCursor(Qt.IBeamCursor)
        self.object_type = 'character'
        self.value = value
        self.ascii_value = value

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 3
        self.cursorClickMoveLeft = 1

    def setColor(self, color):
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def setSize(self, height, fontsize):
        pen = self.pen()
        pen.setWidth(fontsize * _LINE_SCALE_FACTOR)
        self.setPen(pen)
        self.fontSize = fontsize
        h = height
        w = self.fontSize * 0.3
        leftspacing = self.fontSize * 0.2
        rightspacing = self.fontSize * 0.2
        self.top = -h
        self.bottom = 0
        self.width = leftspacing + w + rightspacing

        if self.value == '__leftsquarebracket__':
            path = QPainterPath()
            path.moveTo(leftspacing + w, 0)
            path.lineTo(leftspacing + 0, 0)
            path.lineTo(leftspacing + 0, -h)
            path.lineTo(leftspacing + w, -h)
        elif self.value == '__rightsquarebracket__':
            path = QPainterPath()
            path.moveTo(leftspacing + 0, 0)
            path.lineTo(leftspacing + w, 0)
            path.lineTo(leftspacing + w, -h)
            path.lineTo(leftspacing + 0, -h)
        elif self.value == '__floorleft__':
            path = QPainterPath()
            path.moveTo(leftspacing + w, 0)
            path.lineTo(leftspacing + 0, 0)
            path.lineTo(leftspacing + 0, -h)
        elif self.value == '__floorright__':
            path = QPainterPath()
            path.moveTo(leftspacing + 0, 0)
            path.lineTo(leftspacing + w, 0)
            path.lineTo(leftspacing + w, -h)
        elif self.value == '__ceilleft__':
            path = QPainterPath()
            path.moveTo(leftspacing + 0, 0)
            path.lineTo(leftspacing + 0, -h)
            path.lineTo(leftspacing + w, -h)
        elif self.value == '__ceilright__':
            path = QPainterPath()
            path.moveTo(leftspacing + w, 0)
            path.lineTo(leftspacing + w, -h)
            path.lineTo(leftspacing + 0, -h)
        self.prepareGeometryChange()
        self.setPath(path)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        return self.__dict__


class EquationVerticalLine(QGraphicsLineItem):
    '''Scalable determinant line'''
    def __init__(self, parent):
        QGraphicsLineItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        pen = QPen(QColor('black'))
        pen.setWidthF(1)
        pen.setCapStyle(Qt.SquareCap)
        self.setPen(pen)
        self.setZValue(100)
        self.setCursor(Qt.IBeamCursor)
        self.object_type = 'character'
        self.value = '__verticalline__'
        self.ascii_value = '__verticalline__'

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 2
        self.cursorClickMoveLeft = 1

    def setColor(self, color):
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def setSize(self, height, fontsize):
        pen = self.pen()
        pen.setWidth(fontsize * _LINE_SCALE_FACTOR)
        self.setPen(pen)

        self.fontSize = fontsize
        lspacing = fontsize * 0.2
        rspacing = fontsize * 0.2
        self.top = -height
        self.bottom = 0
        self.width = lspacing + 1 + rspacing
        self.setLine(lspacing, 0, lspacing, self.top)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        return self.__dict__


class EquationProgramLine(QGraphicsLineItem):
    '''Scalable vertical line'''
    def __init__(self, parent):
        QGraphicsLineItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        pen = QPen(QColor('black'))
        pen.setWidthF(1)
        pen.setCapStyle(Qt.SquareCap)
        self.setPen(pen)
        self.setZValue(100)
        self.setCursor(Qt.IBeamCursor)
        self.object_type = 'character'
        self.value = '__programline__'
        self.ascii_value = '__programline__'

        #Used when arrow keys pressed
        self.cursorRight = 2
        self.cursorLeft = 1

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 1
        self.cursorClickMoveLeft = 1

    def setColor(self, color):
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def setSize(self, height, fontsize):
        pen = self.pen()
        pen.setWidth(fontsize * _LINE_SCALE_FACTOR)
        self.setPen(pen)

        self.fontSize = fontsize
        lspacing = fontsize * 0.4
        rspacing = fontsize * 0.2
        self.top = -height
        self.bottom = 0
        self.width = lspacing + 1 + rspacing
        self.setLine(lspacing, 0, lspacing, self.top)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        return self.__dict__


class EquationOverLine(QGraphicsLineItem):
    '''Scalable determinant line'''
    def __init__(self, parent):
        QGraphicsLineItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        pen = QPen(QColor('black'))
        pen.setWidthF(1)
        pen.setCapStyle(Qt.SquareCap)
        self.setPen(pen)
        self.setZValue(100)
        self.setCursor(Qt.IBeamCursor)
        self.object_type = 'character'
        self.value = '__overline__'
        self.ascii_value = '__overline__'

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 1
        self.cursorClickMoveLeft = 0

    def setColor(self, color):
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def setSize(self, length, fontsize):
        pen = self.pen()
        pen.setWidth(fontsize * _LINE_SCALE_FACTOR)
        self.setPen(pen)

        self.fontSize = fontsize
        vspacing = fontsize * 0.3
        hspacing = fontsize * 0.3
        self.top = -2 * vspacing - 1
        self.bottom = 0
        self.width = length + 2 * hspacing
        self.setLine(0, -vspacing, length+2*hspacing, -vspacing)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        return self.__dict__


class EquationNormLines(QGraphicsPathItem):
    '''Scalable norm lines'''
    def __init__(self, parent):
        QGraphicsPathItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        pen = QPen(QColor('black'))
        pen.setWidthF(1)
        pen.setCapStyle(Qt.SquareCap)
        self.setPen(pen)
        self.setZValue(100)
        self.setCursor(Qt.IBeamCursor)
        self.object_type = 'character'
        self.value = '__norm__'
        self.ascii_value = '__norm__'

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 2
        self.cursorClickMoveLeft = 1

    def setColor(self, color):
        self.color = color

    def setSize(self, height, fontsize):
        pen = self.pen()
        pen.setWidth(fontsize * _LINE_SCALE_FACTOR)
        self.setPen(pen)

        self.fontSize = fontsize
        lspacing = fontsize * 0.2
        rspacing = fontsize * 0.2
        gap = fontsize * 0.2
        self.top = -height
        self.bottom = 0
        self.width = lspacing + gap + rspacing + 2

        path = QPainterPath()
        path.moveTo(lspacing, 0)
        path.lineTo(lspacing, -height)
        path.moveTo(lspacing+1+gap, 0)
        path.lineTo(lspacing+1+gap, -height)
        self.setPath(path)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        return self.__dict__


class EquationBraces(QGraphicsPathItem):
    '''Scalable braces widget'''
    def __init__(self, parent, value = '__leftbrace__'):
        QGraphicsPathItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        pen = QPen(QColor('black'))
        pen.setCapStyle(Qt.SquareCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)
        self.setZValue(100)
        self.setCursor(Qt.IBeamCursor)
        self.object_type = 'character'
        self.value = value
        self.ascii_value = value

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 2
        self.cursorClickMoveLeft = 1

    def createLines(self, height):
        f = self.fontSize
        h = height
        w = f * 0.5
        self.top = -height
        self.bottom = 0
        path = QPainterPath()
        h = height/2.0
        f = self.fontSize/2.0

        if self.value == '__leftbrace__':
            l = f * 0.5
            r = f * 0.3
            path.moveTo(l+w, 0)
            path.lineTo(l+0.914*w, -0.004*f)
            path.lineTo(l+0.809*w, -0.007*f)
            path.lineTo(l+0.723*w, -0.013*f)
            path.lineTo(l+0.655*w, -0.0233*f)
            path.lineTo(l+0.606*w, -0.038*f)
            path.lineTo(l+0.572*w, -0.058*f)
            path.lineTo(l+0.544*w, -0.0842*f)
            path.lineTo(l+0.524*w, -0.117*f)
            path.lineTo(l+0.51*w, -0.156*f)
            path.lineTo(l+0.506*w, -0.191*f)
            path.lineTo(l+0.5*w, -0.251*f)
            path.lineTo(l+0.5*w, -h+0.5*f)
            path.lineTo(l+0.493*w, -h+0.432*f)
            path.lineTo(l+0.471*w, -h+0.327*f)
            path.lineTo(l+0.433*w, -h+0.24*f)
            path.lineTo(l+0.381*w, -h+0.172*f)
            path.lineTo(l+0.313*w, -h+0.117*f)
            path.lineTo(l+0.227*w, -h+0.07*f)
            path.lineTo(l+0.122*w, -h+0.03*f)
            path.lineTo(l+0, -h)
            path.lineTo(l+0.122*w, -h-0.03*f)
            path.lineTo(l+0.227*w, -h-0.07*f)
            path.lineTo(l+0.313*w, -h-0.117*f)
            path.lineTo(l+0.381*w, -h-0.172*f)
            path.lineTo(l+0.433*w, -h-0.24*f)
            path.lineTo(l+0.471*w, -h-0.327*f)
            path.lineTo(l+0.493*w, -h-0.432*f)
            path.lineTo(l+0.5*w, -h-0.5*f)
            path.lineTo(l+0.5*w, -2*h+0.251*f)
            path.lineTo(l+0.506*w, -2*h+0.191*f)
            path.lineTo(l+0.51*w, -2*h+0.156*f)
            path.lineTo(l+0.524*w, -2*h+0.117*f)
            path.lineTo(l+0.544*w, -2*h+0.0842*f)
            path.lineTo(l+0.572*w, -2*h+0.058*f)
            path.lineTo(l+0.606*w, -2*h+0.038*f)
            path.lineTo(l+0.655*w, -2*h+0.0233*f)
            path.lineTo(l+0.723*w, -2*h+0.013*f)
            path.lineTo(l+0.809*w, -2*h+0.007*f)
            path.lineTo(l+0.914*w, -2*h+0.004*f)
            path.lineTo(l+w, -2*h)
            self.width = l + w + r
        elif self.value == '__rightbrace__':
            l = f * 0.3
            r = f * 0.5
            path.moveTo(l, 0)
            path.lineTo(l+0.086*w, -0.004*f)
            path.lineTo(l+0.191*w, -0.007*f)
            path.lineTo(l+0.277*w, -0.013*f)
            path.lineTo(l+0.345*w, -0.0233*f)
            path.lineTo(l+0.394*w, -0.038*f)
            path.lineTo(l+0.428*w, -0.058*f)
            path.lineTo(l+0.446*w, -0.0842*f)
            path.lineTo(l+0.476*w, -0.117*f)
            path.lineTo(l+0.490*w, -0.156*f)
            path.lineTo(l+0.494*w, -0.191*f)
            path.lineTo(l+0.5*w, -0.251*f)
            path.lineTo(l+0.5*w, -h+0.5*f)
            path.lineTo(l+0.507*w, -h+0.432*f)
            path.lineTo(l+0.529*w, -h+0.327*f)
            path.lineTo(l+0.567*w, -h+0.24*f)
            path.lineTo(l+0.619*w, -h+0.172*f)
            path.lineTo(l+0.687*w, -h+0.117*f)
            path.lineTo(l+0.723*w, -h+0.07*f)
            path.lineTo(l+0.878*w, -h+0.03*f)
            path.lineTo(l+w, -h)
            path.lineTo(l+0.878*w, -h-0.03*f)
            path.lineTo(l+0.723*w, -h-0.07*f)
            path.lineTo(l+0.687*w, -h-0.117*f)
            path.lineTo(l+0.619*w, -h-0.172*f)
            path.lineTo(l+0.567*w, -h-0.24*f)
            path.lineTo(l+0.529*w, -h-0.327*f)
            path.lineTo(l+0.507*w, -h-0.432*f)
            path.lineTo(l+0.5*w, -h-0.5*f)
            path.lineTo(l+0.5*w, -2*h+0.251*f)
            path.lineTo(l+0.494*w, -2*h+0.191*f)
            path.lineTo(l+0.490*w, -2*h+0.156*f)
            path.lineTo(l+0.476*w, -2*h+0.117*f)
            path.lineTo(l+0.446*w, -2*h+0.0842*f)
            path.lineTo(l+0.428*w, -2*h+0.058*f)
            path.lineTo(l+0.394*w, -2*h+0.038*f)
            path.lineTo(l+0.345*w, -2*h+0.0233*f)
            path.lineTo(l+0.277*w, -2*h+0.013*f)
            path.lineTo(l+0.191*w, -2*h+0.007*f)
            path.lineTo(l+0.086*w, -2*h+0.004*f)
            path.lineTo(l, -2*h)
            self.width = l + w + r

        self.setPath(path)

    def setColor(self, color):
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def setSize(self, fontsize, height):
        pen = self.pen()
        pen.setWidth(fontsize * _LINE_SCALE_FACTOR)
        self.setPen(pen)

        self.fontSize = fontsize
        self.createLines(height)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        return self.__dict__


class EquationParenthesis(QGraphicsPathItem):
    '''Scalable parenthesis'''
    def __init__(self, parent, value = '__leftparenthesis__'):
        QGraphicsPathItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        pen = QPen(QColor('black'))
        pen.setCapStyle(Qt.SquareCap)
        pen.setJoinStyle(Qt.RoundJoin)
        self.setPen(pen)
        self.setZValue(100)
        self.setCursor(Qt.IBeamCursor)
        self.object_type = 'character'
        self.value = value
        self.ascii_value = value

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 2
        self.cursorClickMoveLeft = 1

    def paint (self, painter, option, widget = None):
        painter.setRenderHint(QPainter.Antialiasing, True)
        QGraphicsPathItem.paint(self, painter, option, widget)

    def createLines(self, height):
        f = self.fontSize
        h = height
        self.top = -h
        self.bottom = 0
        path = QPainterPath()
        if self.value == '__leftparenthesis__':
            leftspacing = f * 0.3
            rightspacing = f * 0.3
            path.moveTo(leftspacing + f*0.271, 0)
            path.lineTo(leftspacing + f*0.236, -f*0.021)
            path.lineTo(leftspacing + f*0.203, -f*0.044)
            path.lineTo(leftspacing + f*0.174, -f*0.069)
            path.lineTo(leftspacing + f*0.148, -f*0.096)
            path.lineTo(leftspacing + f*0.115, -f*0.136)
            path.lineTo(leftspacing + f*0.086, -f*0.180)
            path.lineTo(leftspacing + f*0.061, -f*0.228)
            path.lineTo(leftspacing + f*0.040, -f*0.279)
            path.lineTo(leftspacing + f*0.023, -f*0.332)
            path.lineTo(leftspacing + f*0.011, -f*0.387)
            path.lineTo(leftspacing + f*0.004, -f*0.442)
            path.lineTo(leftspacing, -f*0.5)
            path.lineTo(leftspacing + f*0.004, -h+f*0.442)
            path.lineTo(leftspacing + f*0.011, -h+f*0.387)
            path.lineTo(leftspacing + f*0.023, -h+f*0.332)
            path.lineTo(leftspacing + f*0.040, -h+f*0.279)
            path.lineTo(leftspacing + f*0.061, -h+f*0.228)
            path.lineTo(leftspacing + f*0.086, -h+f*0.180)
            path.lineTo(leftspacing + f*0.115, -h+f*0.136)
            path.lineTo(leftspacing + f*0.148, -h+f*0.096)
            path.lineTo(leftspacing + f*0.174, -h+f*0.069)
            path.lineTo(leftspacing + f*0.203, -h+f*0.044)
            path.lineTo(leftspacing + f*0.236, -h+f*0.021)
            path.lineTo(leftspacing + f*0.271, -h)
            self.width = leftspacing + f*0.271 + rightspacing
        elif self.value == '__rightparenthesis__':
            leftspacing = f * 0.3
            rightspacing = f * 0.3
            path.moveTo(leftspacing, 0)
            path.lineTo(leftspacing + f*0.035, -f*0.021)
            path.lineTo(leftspacing + f*0.068, -f*0.044)
            path.lineTo(leftspacing + f*0.097, -f*0.069)
            path.lineTo(leftspacing + f*0.123, -f*0.096)
            path.lineTo(leftspacing + f*0.156, -f*0.136)
            path.lineTo(leftspacing + f*0.185, -f*0.180)
            path.lineTo(leftspacing + f*0.210, -f*0.228)
            path.lineTo(leftspacing + f*0.231, -f*0.279)
            path.lineTo(leftspacing + f*0.248, -f*0.332)
            path.lineTo(leftspacing + f*0.260, -f*0.387)
            path.lineTo(leftspacing + f*0.267, -f*0.442)
            path.lineTo(leftspacing + f*0.271, -f*0.5)
            path.lineTo(leftspacing + f*0.267, -h+f*0.442)
            path.lineTo(leftspacing + f*0.260, -h+f*0.387)
            path.lineTo(leftspacing + f*0.248, -h+f*0.332)
            path.lineTo(leftspacing + f*0.231, -h+f*0.279)
            path.lineTo(leftspacing + f*0.210, -h+f*0.228)
            path.lineTo(leftspacing + f*0.185, -h+f*0.180)
            path.lineTo(leftspacing + f*0.156, -h+f*0.136)
            path.lineTo(leftspacing + f*0.123, -h+f*0.096)
            path.lineTo(leftspacing + f*0.097, -h+f*0.069)
            path.lineTo(leftspacing + f*0.068, -h+f*0.044)
            path.lineTo(leftspacing + f*0.035, -h+f*0.021)
            path.lineTo(leftspacing, -h)
            self.width = leftspacing + f*0.271 + rightspacing
        self.setPath(path)

    def setColor(self, color):
        pen = self.pen()
        pen.setColor(color)
        self.setPen(pen)

    def setSize(self, height, fontsize):
        pen = self.pen()
        pen.setWidth(fontsize * _LINE_SCALE_FACTOR)
        self.setPen(pen)

        self.fontSize = fontsize
        self.createLines(height)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        return self.__dict__


class EquationReservedSpace(QGraphicsRectItem):
    def __init__(self, parent):
        QGraphicsRectItem.__init__(self, parent)
        self.setCacheMode(QGraphicsRectItem.DeviceCoordinateCache)
        brush = QBrush(QColor('black'))
        self.setBrush(brush)
        self.setZValue(100)
        self.setCursor(Qt.IBeamCursor)
        self.object_type = 'character'
        self.value = '__reserved__'
        self.ascii_value = self.value

        #Used when arrow keys pressed
        self.cursorRight = 1
        self.cursorLeft = 1

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 1
        self.cursorClickMoveLeft = 0

    def setColor(self, color):
        pen = self.pen()
        brush = self.brush()
        pen.setColor(color)
        brush.setColor(color)
        self.setPen(pen)
        self.setBrush(color)

    def setSize(self, fontSize):
        self.fontSize = fontSize
        x = fontSize * 0.3
        y = -fontSize * 0.7
        w = h = fontSize * 0.4
        self.setRect(x, y, w, h)
        self.top = -fontSize
        self.bottom = 0
        self.width = fontSize

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        return self.__dict__



class EquationTable(QGraphicsProxyWidget):
    def __init__(self, parent, data, numrows, numcols, font):
        QGraphicsProxyWidget.__init__(self, parent)
        self.data = data
        self.numtablerows = numrows
        self.numtablecols = numcols

        self.style = "QTableWidget {background: rgba(0,0,0,0);} \
                QHeaderView {background: %s;} \
                QHeaderView::section { background-color: rgba(0,0,0,0); \
                    margin: 0px; padding:1px; border-color: black; border-style: solid; \
                    border-right-width:1px; border-bottom-width:1px} \
                QTableWidget QTableCornerButton::section {background-color: %s; \
                    margin: 0px; padding:1px; border-color: black; border-style: solid; \
                    border-right-width:1px; border-bottom-width:1px}" % ('rgba(0,0,0,20)', 'rgba(0,0,0,20)')

        #Create and fill table with data
        t = QTableWidget(numrows, numcols)
        setItem = t.setItem
        if numrows > 1 and numcols > 1:
            [setItem(row, col, QTableWidgetItem(str(data[row][col]))) \
                for row in xrange(numrows) for col in xrange(numcols)]

        elif numrows > 1:
            [setItem(row, 0, QTableWidgetItem(str(data[row]))) for row in xrange(numrows)]

        elif numcols > 1:
            [setItem(0, col, QTableWidgetItem(str(data[col]))) for col in xrange(numcols)]

        t.setWindowFlags(Qt.Widget)
        t.setCursor(Qt.IBeamCursor)
        t.verticalScrollBar().setCursor(Qt.ArrowCursor)
        t.horizontalScrollBar().setCursor(Qt.ArrowCursor)
        t.setCornerButtonEnabled(True)
        t.setMinimumSize(100, 20)
        t.setFrameShape(QFrame.Box)
        t.setFrameShadow(QFrame.Plain)
        t.setLineWidth(1)
        t.setToolTip('Table')
        t.setFont(font)
        t.setStyleSheet(self.style)
        self.fontSize = 0

        self.setWidget(t)
        self.setToolTip("Table")
        self.setFlag(QGraphicsItem.ItemIsSelectable, True)
        self.setFlag(QGraphicsItem.ItemIsMovable, True)
        self.setFlag(QGraphicsItem.ItemIsFocusable, True)
        self.setZValue(100)
        self.setHandlesChildEvents(True)
        self.object_type = 'character'
        self.value = '__table__'
        self.ascii_value = self.value

        #Used when arrow keys pressed
        self.cursorRight = 1
        self.cursorLeft = 1

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 0
        self.cursorClickMoveLeft = 0

    def changeTableData(self, data):
        numrows = self.numtablerows
        numcols = self.numtablecols
        item = self.widget().item

        if numrows > 1 and numcols > 1:
            [item(row, col).setText('%.4g' % data[row][col]) \
                for row in xrange(numrows) for col in xrange(numcols)]
        elif numrows > 1:
            [item(row, 0).setText('%.4g' % data[row]) for row in xrange(numrows)]
        elif numcols > 1:
            [item(0, col).setText('%.4g' % data[col]) for col in xrange(numcols)]

        self.widget().resizeColumnsToContents()
        self.widget().resizeRowsToContents()

    def clearSelection(self):
        self.widget().clearSelection()

    def setPosition(self, x, y):
        self.setPos(x+self.hspacing, y)

    def getPosition(self):
        return self.x()-self.hspacing, self.y()

    def moveBy(self, deltax, deltay):
        x = self.x()
        y = self.y()
        self.setPos(x+deltax, y+deltay)

    def setFontSize(self, fontsize):
        #Adjust font size used in the table, including headers.
        #Only change size if it is different from current size.
        #This gives a significant speed boost when resizing table.
        if fontsize != self.fontSize:
            self.fontSize = fontsize
            self.hspacing = fontsize * 0.4   #Horizontal spacing between table widget and other widgets
            t = self.widget()
            font = t.font()
            font.setPointSize(fontsize)
            t.setFont(font)
            t.horizontalHeader().setFont(font)
            t.verticalHeader().setFont(font)
            t.resizeColumnsToContents()
            t.resizeRowsToContents()

            self.widget().setStyleSheet(self.style)

            #Update table size
            self.setSize(t.width(), t.height())


    def setFontName(self, fontname):
        t = self.widget()   #Table widget
        font = t.font()
        font.setFamily(fontname)
        t.setFont(font)
        t.horizontalHeader().setFont(font)
        t.verticalHeader().setFont(font)
        t.resizeColumnsToContents()
        t.resizeRowsToContents()

        #Update table size
        self.setSize(t.width(), t.height())

    def setSize(self, w, h):
        #Add in spacing fudge
        w = w - self.hspacing * 2

        t = self.widget()
        t.horizontalHeader().setMaximumHeight(t.rowHeight(0))

        #Size of entire table if visible on screen
        self.tableActualHeight = t.horizontalHeader().height() + self.numtablerows * t.rowHeight(0) + t.frameWidth() * 2
        self.tableActualWidth = t.verticalHeader().width() + self.numtablecols * t.columnWidth(0) + t.frameWidth() * 2

        actual_width = self.tableActualWidth
        actual_height= self.tableActualHeight

        if w > actual_width:
            hscroll = False
        else:
            hscroll = True
        if h > actual_height:
            vscroll = False
        else:
            vscroll = True

        actual_height_with_horizscroll = actual_height + t.horizontalScrollBar().height()
        actual_width_with_vertscroll = actual_width + t.verticalScrollBar().width()
        if hscroll:
            if h > actual_height_with_horizscroll:
                h = actual_height_with_horizscroll
        else:
            if h > actual_height:
                h = actual_height

        if vscroll:
            if w > actual_width_with_vertscroll:
                w = actual_width_with_vertscroll
        else:
            if w > actual_width:
                w = actual_width

        hmin = t.minimumHeight()
        wmin = t.minimumWidth()
        if h < hmin:
            h = hmin
        if w < wmin:
            w = wmin

        self.resize(w, h)
        self.width = w + self.hspacing * 2
        self.top = 0
        self.bottom = h

    def setColor(self, color):
        pass

    def getDict(self):
        return self.__dict__

    def roundTableResult(self, num):
        '''Attempt to clean up numerical result. Return a string'''
        numberfilter = '%.4g'  #'%.3f'

        x1 = scipy.real(num)
        x2 = scipy.imag(num)
        a = numberfilter%x1
        b = numberfilter%abs(x2)
        if x2 < 0:
            s = ''.join([a, '-', b, 'j'])
        elif x2 > 0:
            s = ''.join([a, '+', b, 'j'])
        else:
            s = a
        return s


class EquationArrowLine(QGraphicsItem):
    '''Scalable arrow symbol'''
    def __init__(self, parent):
        QGraphicsItem.__init__(self, parent)
        self.setCacheMode(QGraphicsItem.DeviceCoordinateCache)
        self.bounding_rect = QRectF(0, 0, 0, 0)
        pen = QPen(QColor('black'))
        pen.setWidthF(1)
        pen.setCapStyle(Qt.SquareCap)
        pen.setJoinStyle(Qt.MiterJoin)
        self.pen = pen
        self.line1 = QLineF(0, 0, 0, 0)
        self.line2 = QLineF(0, 0, 0, 0)
        self.line3 = QLineF(0, 0, 0, 0)
        self.setZValue(100)
        self.object_type = 'character'
        self.value = '__arrow__'
        self.ascii_value = '__arrow__'

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 0
        self.cursorClickMoveLeft = 0

    def boundingRect(self):
        return self.bounding_rect

    def paint(self, painter, option, widget):
        pen = self.pen
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.setRenderHint(QPainter.Antialiasing, False)
        painter.drawLine(self.line1)
        painter.setRenderHint(QPainter.Antialiasing, True)
        painter.drawLine(self.line2)
        painter.drawLine(self.line3)

    def setColor(self, color):
        self.pen.setColor(color)

    def setSize(self, width, fontsize):
        self.pen.setWidth(fontsize * _LINE_SCALE_FACTOR)
        self.fontSize = fontsize
        vspacing = fontsize * 0.2             #Spacing between arrow and characters below it
        additional_length = fontsize * 0.3
        total_length = width + 2 * additional_length
        arrow_height = fontsize * 0.5         #Height of arrow head
        arrow_head_width = fontsize * 0.5
        h = vspacing + arrow_height
        h2 = vspacing + arrow_height/2

        #Create arrow lines
        self.prepareGeometryChange()
        self.line1 = QLineF(0,  -h2,  total_length,  -h2)
        self.line2 = QLineF(total_length,  -h2,  total_length-arrow_head_width,  -h)
        self.line3 = QLineF(total_length,  -h2,  total_length-arrow_head_width,  -vspacing)

        self.top = -h - vspacing
        self.bottom = 0
        self.width = total_length

        self.bounding_rect = QRectF(0, self.top, total_length, -self.top)

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        d = self.__dict__.copy()
        del d['pen']
        return d


class EquationImage(QGraphicsPixmapItem):
    '''Scalable image'''
    SCALE_FACTOR = 3
    def __init__(self, parent, fontsize):
        QGraphicsPixmapItem.__init__(self, parent)
        self.setZValue(100)
        self.object_type = 'character'
        self.value = '__image__'
        self.ascii_value = '__image__'

        self.setAcceptsHoverEvents(True)
        #self.setFlag(QGraphicsPixmapItem.ItemIsSelectable, True)

        #Initialize image
        self.original = QPixmap("icons/helicopter.svg")
        self.setPixmap(self.original)
        self.setSize(fontsize*EquationImage.SCALE_FACTOR)

        #Used when char is clicked using mouse
        self.cursorClickMoveRight = 0
        self.cursorClickMoveLeft = 0

    def hoverEnterEvent(self, event):
        self.setCursor(Qt.ArrowCursor)

    def hoverLeaveEvent(self, event):
        self.setCursor(Qt.OpenHandCursor)

    def resetImage(self):
        self.original = QPixmap("icons/helicopter.svg")
        self.setPixmap(self.original)
        self.setSize(self.bottom-self.top)

    def setImage(self, pixmap):
        self.original = pixmap
        self.setPixmap(pixmap)
        self.setSize(self.bottom-self.top)

    def setColor(self, color):
        self.pen.setColor(color)

    def setSize(self, height):
        pix = self.original
        pix = pix.scaledToHeight(height)
        self.setPixmap(pix)
        self.top = 0
        self.bottom = height
        self.width = pix.width()

    def setPosition(self, x, y):
        self.setPos(x, y)

    def getPosition(self):
        return self.x(), self.y()

    def getDict(self):
        d = self.__dict__.copy()
        del d['pen']
        return d

    def setFileNameCallback(self):
        pass



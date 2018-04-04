
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


class SymbolsTable(QWidget):
    symbols = [ \
        ('__GAMMA__',       u'\u0393',          'Uppercase Gamma'),     \
        ('__DELTA__',       u'\u0394',          'Uppercase Delta'),     \
        ('__THETA__',       u'\u0398',          'Uppercase Theta'),     \
        ('__LAMBDA__',      u'\u039b',          'Uppercase Lambda'),    \
        ('__XI__',          u'\u039e',          'Uppercase Xi'),        \
        ('__SIGMA__',       u'\u03a3',          'Uppercase Sigma'),     \
        ('__PHI__',         u'\u03a6',          'Uppercase Phi'),       \
        ('__PSI__',         u'\u03a8',          'Uppercase Psi'),       \
        ('__OMEGA__',       u'\u03a9',          'Uppercase Omega'),     \
        ('__alpha__',       u'\u03b1',          'Alpha'),               \
        ('__beta__',        u'\u03b2',          'Beta'),                \
        ('__gamma__',       u'\u03b3',          'Gamma'),               \
        ('__delta__',       u'\u03b4',          'Delta'),               \
        ('__epsilon__',     u'\u03b5',          'Epsilon'),             \
        ('__zeta__',        u'\u03b6',          'Zeta'),                \
        ('__eta__',         u'\u03b7',          'Eta'),                 \
        ('__theta__',       u'\u03b8',          'Theta'),               \
        ('__kapa__',        u'\u03ba',          'Kapa'),                \
        ('__lamba__',       u'\u03bb',          'Lambda'),              \
        ('__mu__',          u'\u03bc',          'Mu'),                  \
        ('__nu__',          u'\u03bd',          'Nu'),                  \
        ('__xi__',          u'\u03be',          'Xi'),                  \
        ('__pi__',          u'\u03c0',          'Pi'),                  \
        ('__rho__',         u'\u03c1',          'Rho'),                 \
        ('__stigma__',      u'\u03c2',          'Stigma'),              \
        ('__sigma__',       u'\u03c3',          'Sigma'),               \
        ('__tau__',         u'\u03c4',          'Tau'),                 \
        ('__upsilon__',     u'\u03c5',          'Upsilon'),             \
        ('__phi__',         u'\u03c6',          'Phi'),                 \
        ('__chi__',         u'\u03c7',          'Chi'),                 \
        ('__psi__',         u'\u03c8',          'Psi'),                 \
        ('__omega__',       u'\u03c9',          'Omega'),               \
        ('__infinity__',    u'\u221e',          'Infinity')]

    [ascii_value, unicode_value, tooltip] = zip(*symbols)

    def __init__(self, parent = None):
        QWidget.__init__(self, parent)
        self.fontSize = 14   #The size of displayed greek letters in table
        self.displayFont = QFont('Georgia', self.fontSize)
        self.lastKey = -1
        self.setMouseTracking(True)
        self.boxSize = self.fontSize * 2
        self.numEntries = len(self.symbols)
        self.numGridColumns = 5
        self.numGridRows = self.numEntries / self.numGridColumns
        if self.numEntries % self.numGridColumns != 0:
            self.numGridRows += 1

        self.width = self.numGridColumns * self.boxSize
        self.height = self.numGridRows * self.boxSize
        self.fontMetrics = QFontMetrics(self.displayFont)
        self.setToolTip('Click to enter character')

        self.cursorBox = -1

    def sizeHint(self):
        return QSize(self.width, self.height)

    def mouseMoveEvent(self, event):
        if event.x() < self.width and event.y() < self.height:
            size = self.boxSize
            row = event.y() / size
            col = event.x() / size
            index = row * self.numGridColumns + col
            if index < len(self.symbols):
                tip = self.symbols[index][2]
                self.setToolTip(tip)
            self.cursorBox = row * self.numGridColumns + col
        else:
            self.cursorBox  = -1
        self.update()

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton:
            if event.x() < self.width and event.y() < self.height:
                size = self.boxSize
                row = event.y() / size
                col = event.x() / size
                self.lastKey = row * self.numGridColumns + col
                self.emit(SIGNAL("characterSelected(const QString &, const QString &)"), \
                    self.symbols[self.lastKey][0], self.symbols[self.lastKey][1])
                self.update()
        else:
            QWidget.mousePressEvent(self, event)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        #painter.fillRect(event.rect(), Qt.green)
        painter.setFont(self.displayFont)

        #Draw grid lines
        painter.setPen(Qt.gray)
        painter.pen().setWidthF(1.0)
        size = self.boxSize
        numCols = self.numGridColumns

        #Draw text
        fontMetrics = self.fontMetrics
        i = 0
        row = 0
        col = 0
        while i < self.numEntries:
            #painter.setClipRect(col*size, row*size, size, size)
            painter.setPen(Qt.gray)
            painter.drawRect(col*size, row*size, size, size)

            if i == self.lastKey:
                painter.fillRect(col*size, row*size, size, size, Qt.blue)

            if i == self.cursorBox and i != self.lastKey:
                painter.fillRect(col*size, row*size, size, size, Qt.gray)

            x = col * size + size/2 - fontMetrics.width(self.symbols[i][1])/2
            y = row * size + 4 + fontMetrics.ascent()
            painter.setPen(Qt.black)
            painter.drawText(x, y, QString(self.symbols[i][1]))
            i += 1
            col += 1
            if col == numCols:
                col = 0
                row += 1



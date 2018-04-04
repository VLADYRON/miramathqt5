

#------------------------------------------------------------------------------
#   Copyright (c) 2008
#       Roger Hale    roger.hale@terra.es
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

class RubberBand(QRubberBand):
    def __init__(self, parent = None):
        QRubberBand.__init__(self, QRubberBand.Rectangle, parent)

    def paintEvent(self, event):
        painter = QPainter()
        painter.begin(self)
        painter.setPen(Qt.blue)
        painter.pen().setWidth(1)
        r = self.geometry()
        painter.drawRect(r)




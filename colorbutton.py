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

from PyQt4.QtGui import *
from PyQt4.QtCore import *


class ColorButton(QPushButton):
    def __init__(self, init_color, title='', alpha=False):
        QPushButton.__init__(self)
        self.title = title

        if alpha:
            self.alpha = QColorDialog.ShowAlphaChannel
        else:
            self.alpha = None

        self.set_color(init_color)
        self.connect(self, SIGNAL('clicked()'), self.changed_color)

    def changed_color(self):
        if self.alpha:
            color = QColorDialog.getColor(self.color, None, self.title, self.alpha)
        else:
            color = QColorDialog.getColor(self.color, None, self.title)

        if color.isValid():
            self.set_color(color)

    def set_color(self, c):
        image = QImage(100, 100, QImage.Format_RGB32)
        image.fill(c.rgb())
        pix = QPixmap.fromImage(image)
        icon  = QIcon(pix)
        self.setIcon(icon)
        self.color = c


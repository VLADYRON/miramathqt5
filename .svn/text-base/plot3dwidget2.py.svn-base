
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

from numpy import *
import sys
from PyQt4.Qwt3D import *
from PyQt4.Qt import *

import time

def matrix2d(nx, ny, minx, maxx, miny, maxy, function):
    """Return a data matrix to test the interface to the C++ member function
    bool SurfacePlot::loadFromData(
        double **, unsigned int, unsigned int, double, double, double, double);
    """
    # columns
    xs = multiply.outer(minx + ((maxx-minx)/(nx-1))*arange(nx), ones(ny, float))
    # rows
    ys = multiply.outer(ones((nx,), float), miny+((maxy-miny)/(ny-1))*arange(ny))

    return function(xs, ys)


def matrix3d(nx, ny, minx, maxx, miny, maxy, function):
    """Return a data matrix to test the interface to the C++ member function
    bool SurfacePlot::loadFromData(
        Triple **, unsigned int, unsigned int, bool = false, bool = false);
    """
    xyzs = zeros((nx, ny, 3), float)
    # columns
    xyzs[:,:,0] = multiply.outer(minx + ((maxx-minx)/(nx-1))*arange(nx), ones(ny, float))
    # rows
    xyzs[:,:,1] = multiply.outer(ones((nx,), float), miny+((maxy-miny)/(ny-1))*arange(ny))
    # result
    xyzs[:,:,2] = function(xyzs[:,:,0], xyzs[:,:,1])
    return xyzs


def saddle(x, y):
    r=x*x+y*y
    return 10*sin(sqrt(r)) * 1/r**0.5


class Thing(QGLWidget):
    def __init__(self, parent):
        fmt = QGLFormat()
        fmt.setDirectRendering(False)
        QGLWidget.__init__(self, fmt, parent)
        self.plot = Plot(self)
        self.show()

class Plot(SurfacePlot):
    def __init__(self, parent):
        SurfacePlot.__init__(self, parent)
#        fmt = QGLFormat()
#        fmt.setDirectRendering(False)
#        self.setFormat(fmt)
        
        #Hide this widget
        #self.hide()
        #self.show()
        
        self.setGeometry(0, 0, 640, 480)
        
        
        # fonts
        family = QCoreApplication.instance().font().family()
        if 'Serif' in QFontDatabase().families():
            family = 'Serif'
        else:
            family = 'Courier'

        self.coordinates().setLabelFont(family, 14)
        self.coordinates().setNumberFont(family, 14)

        self.setBackgroundColor(RGBA(1, 1, 1, 0.01))
        self.setRotation(30, 0, 15)
        self.setScale(1.0, 1.0, 1.0)
        self.minWidth = 50
        self.minHeight = 50

        nx, ny, minx, maxx, miny, maxy = 50, 50, -20.0, 20.0, -20.0, 20.0
        if 0:
            zs = matrix2d(nx, ny, minx, maxx, miny, maxy, saddle)
            self.loadFromData(zs, minx, maxx, miny, maxy)
        else:
            xyzs = matrix3d(nx, ny, minx, maxx, miny, maxy, saddle)
            self.loadFromData(xyzs)

        axes = self.coordinates().axes # alias

        for axis, label in ((X1, "x"), (Y1, "y"), (Z1, "z")):
            axes[axis].setAutoScale(False)
            axes[axis].setMajors(5) # 6 major ticks
            axes[axis].setMinors(3) # 2 minor ticks
            axes[axis].setLabelString(label)

        self.setCoordinateStyle(BOX)
        self.coordinates().setGridLines(True, True)
        self.coordinates().setLineSmooth(True)

        self.updateData()
        self.updateGL()

        
    def paintGL(self):
        SurfacePlot.paintGL(self)
        self.paint_flag = True



    def resizeGL(self, w, h):
        SurfacePlot.resizeGL(self, w, h)



def main(args):
    app = QApplication(args)
    #p = Plot(None)
    p = Thing(None)
    p.resize(600, 400)
    l = QLabel()
    l.setGeometry(0, 0, 400, 300)
    l.show()
    time.sleep(1)
    if p.plot.paint_flag:
        pixmap = QPixmap()
        pixmap.grabWidget(p.plot)
        l.setPixmap(pixmap)
    app.exec_()


if __name__ == '__main__':
    main(sys.argv)


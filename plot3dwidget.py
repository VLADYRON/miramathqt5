
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
import copy
import scipy

from PyQt4.Qwt3D import *
from PyQt4.QtCore import *
from PyQt4.QtGui import *
from PyQt4.QtOpenGL import QGLFramebufferObject

def sinc_function(x, y):
    r=x * x + y * y
    return 40*sin(r**0.5) * 1/r**0.2


class Plot(SurfacePlot):
    mesh_styles = [WIREFRAME, FILLEDMESH, FILLED, POINTS]
    axes_styles = [NOCOORD, BOX, FRAME]

    minmeshwidth = 0
    maxmeshwidth = 10
    axesminwidth = 0
    axesmaxwidth = 10
    initial_axes_color = QColor(0, 0, 0, 255)
    initial_mesh_color = QColor(0, 0, 0, 255)
    initial_axes_width = 1

    def __init__(self, pixmap, font, background_color):
        self.frame_buffer = QGLFramebufferObject(640, 480)
        SurfacePlot.__init__(self, None)

        self.pixmap = pixmap
        self.font = font
        self.min_width = 50
        self.min_height = 50

        #Hide this openGL widget
        self.hide()

        #Set up axes labels, colors, etc
        plot_coordinates = self.coordinates()
        plot_coordinates.setLabelFont(font)
        plot_coordinates.setNumberFont(font)
        plot_coordinates.setLabelColor(self.color_to_rgba(Plot.initial_axes_color))
        plot_coordinates.setNumberColor(self.color_to_rgba(Plot.initial_axes_color))
        plot_coordinates.setAxesColor(self.color_to_rgba(Plot.initial_axes_color))
        plot_coordinates.setGridLines(False, False, BACK)  # Show a grid on wall (use True)
        plot_coordinates.setLineSmooth(True)
        plot_coordinates.setLineWidth(Plot.initial_axes_width)
        self.setCoordinateStyle(BOX)  #BOX,FRAME,NOCOORD

        axes = plot_coordinates.axes
        for axis, label in ((X1, "x"), (X2, "x"), (X3, "x"), (X4, "x"),
                            (Y1, "y"), (Y2, "y"), (Y3, "y"), (Y4, "y"),
                            (Z1, "z"), (Z2, "z"), (Z3, "z"), (Z4, "z")):
            axes[axis].setAutoScale(True)
            axes[axis].setMajors(8) # 6 major ticks
            axes[axis].setMinors(5) # 2 minor ticks
            axes[axis].setLabelString(label)
            axes[axis].setNumbers(True)

        #Initialize plot background color
        self.set_plot_background_color(background_color)

        #self.setTitle("Thing Snoopy")
        self.setGeometry(0, 0, 640, 480)
        self.setTitlePosition(10, 20)
        self.setIsolines(4)
        self.setRotation(30, 0, 15)
        self.setScale(1.0, 1.0, 1.0)

        #Set up initial mesh
        self.setPlotStyle(WIREFRAME)  #FILLED, WIREFRAME, POINTS, FILLEDMESH
        self.setMeshColor(self.color_to_rgba(Plot.initial_mesh_color))
        self.setSmoothMesh(True)
        self.setMeshLineWidth(0)

        #self.setShading(FLAT)  #FLAT,GOURAUD
        self.setZoom(0.9)
        #self.legend()

#
#        #self.enr = Dot(10, 1)
#        #self.enr = CrossHair(0.005, 2, True, True)
#        self.enr = Cone(0.5, 4)
#        self.addEnrichment(self.enr)

        #self.setShininess(100)
        #self.illuminate(70)
        self.do_update_plot2()

    def mouseMoveEvent(self, event):
        SurfacePlot.mouseMoveEvent(self, event)

##        xr = self.xRotation()
##        yr = self.yRotation()
##        zr = self.zRotation()
##        print xr, yr, zr
##        print event.pos().x(), event.pos().y()
##        cx = change.x()
##        cy = change.y()
##
##        if xr < 90 and xr+cy >= 90:
##            self.xsign = -1
##            xr = xr + 180
##        elif xr < 270 and xr-cy >= 270:
##            self.xsign = 1
##            xr = xr - 180
##        elif xr > -90 and xr+cy <= -90:
##            self.xsign = -1
##            xr = xr + 180
##        elif xr > 90 and xr-cy <= 90:
##            self.xsign = 1
##            xr = xr - 180
##
##        self.setRotation(xr+self.xsign*cy, self.yRotation(), self.zRotation()+change.x())

        s = self.frame_buffer.size()
        SurfacePlot.resizeGL(self, s.width(), s.height())

    def wheelEvent(self, event):
        SurfacePlot.wheelEvent(self, event)
        s = self.frame_buffer.size()
        SurfacePlot.resizeGL(self, s.width(), s.height())

    def paintGL(self):
        f = self.frame_buffer.bind()
        SurfacePlot.paintGL(self)

        image = self.frame_buffer.toImage()
        p = QPixmap.fromImage(image)
        self.pixmap.setPixmap(p)

    def resizeGL(self, w, h):
        self.frame_buffer = QGLFramebufferObject(w, h)
        SurfacePlot.resizeGL(self, w, h)

    def set_all_fonts(self, font):
        size = font.pointSize()

        plot_coordinates = self.coordinates()
        plot_coordinates.setLabelFont(font)
        plot_coordinates.setNumberFont(font)

        self.update()

    def set_plot_background_color(self, background_color):
        self.setBackgroundColor(self.color_to_rgba(background_color))

        s = self.frame_buffer.size()
        SurfacePlot.resizeGL(self, s.width(), s.height())

    def set_mesh(self, color, i, width):
        self.current_plot_style = Plot.mesh_styles[i]
        self.setPlotStyle(self.current_plot_style)

        self.setMeshLineWidth(width)
        self.setMeshColor(self.color_to_rgba(color))

        self.update()
        self.updateData()

        s = self.frame_buffer.size()
        SurfacePlot.resizeGL(self, s.width(), s.height())

    def set_axes(self, color, i, width):
        plot_coordinates = self.coordinates()
        plot_coordinates.setLineSmooth(True)
        plot_coordinates.setAxesColor(self.color_to_rgba(color))
        plot_coordinates.setLineWidth(width)

        self.setCoordinateStyle(Plot.axes_styles[i])

        self.update()
        self.updateData()

        s = self.frame_buffer.size()
        SurfacePlot.resizeGL(self, s.width(), s.height())

    def show_plot(self, flag):
        if flag:
            pass
        else:
            pass

        self.updateData()
        s = self.frame_buffer.size()
        SurfacePlot.resizeGL(self, s.width(), s.height())

    def color_to_rgba(self, color):
        r = color.redF()
        g = color.greenF()
        b = color.blueF()
        a = color.alphaF()
        return RGBA(r, g, b, a)

    def matrix2d(self, nx, ny, minx, maxx, miny, maxy, function):
        """Return a data matrix to test the interface to the C++ member function
        bool SurfacePlot::loadFromData(
            double **, unsigned int, unsigned int, double, double, double, double);
        """
        # columns
        xs = scipy.multiply.outer(minx + ((maxx-minx)/(nx-1))*arange(nx), ones(ny, float))
        # rows
        ys = scipy.multiply.outer(ones((nx,), float), miny+((maxy-miny)/(ny-1))*arange(ny))
        return function(xs, ys)

    def matrix3d(self, nx, ny, minx, maxx, miny, maxy, function):
        """Return a data matrix to test the interface to the C++ member function
        bool SurfacePlot::loadFromData(
            Triple **, unsigned int, unsigned int, bool = false, bool = false);
        """
        xyzs = scipy.zeros((nx, ny, 3), float)
        # columns
        xyzs[:,:,0] = scipy.multiply.outer(minx + ((maxx-minx)/(nx-1))*arange(nx), ones(ny, float))
        # rows
        xyzs[:,:,1] = scipy.multiply.outer(ones((nx,), float), miny+((maxy-miny)/(ny-1))*arange(ny))
        # result
        xyzs[:,:,2] = function(xyzs[:,:,0], xyzs[:,:,1])

    def do_update_plot(self, nx, ny, z):
        self.loadFromData(z, 0.0, nx-1.0, 0.0, ny-1.0)

        #Use loaded data to update plot
        self.updateData()
        self.update()
        s = self.frame_buffer.size()
        SurfacePlot.resizeGL(self, s.width(), s.height())

    def do_update_plot2(self):
#        function = sinc_function
#        nx, ny, minx, maxx, miny, maxy = 50, 50, -20.0, 20.0, -20.0, 20.0
#        if 0:
#            zs = self.matrix2d(nx, ny, minx, maxx, miny, maxy, function)
#            self.loadFromData(zs, minx, maxx, miny, maxy)
#        else:
#            xyzs = self.matrix3d(nx, ny, minx, maxx, miny, maxy, function)
#            self.loadFromData(xyzs)

        N1 = 10
        N2 = 18
        R = 6
        r = 2
        xyzs = scipy.zeros((N1, N2, 3), float)
        for i in xrange(N1):
            for j in xrange(N2):
                u = i * 2*scipy.pi/(N1-1)
                v = j * 2*scipy.pi/(N2-1)
                xyzs[i, j, 0] = (R + r*scipy.cos(u)) * scipy.cos(v)
                xyzs[i, j, 1] = (R + r * scipy.cos(u)) * scipy.sin(v)
                xyzs[i, j, 2] = r * scipy.sin(u)

        self.loadFromData(xyzs)

        #Use loaded data to update plot
        self.updateData()

    def do_update_plot3(self, xyz_values):
        print xyz_values

        self.loadFromData(xyz_values)

        #Use loaded data to update plot
        self.updateData()
        #self.update()
        s = self.frame_buffer.size()
        SurfacePlot.resizeGL(self, s.width(), s.height())



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
from symbolscharmap import SymbolsTable

class MathToolBox(QDockWidget):
    def __init__(self, parent, iconsize):
        QDockWidget.__init__(self, 'Math Toolbox', parent)
        self.setFeatures(QDockWidget.DockWidgetMovable | QDockWidget.DockWidgetFloatable)
        self.setMinimumWidth(100)

        #*********Create new matrix dialog********
        self.newMatrixDialog = self.createMatrixDialog('Create a new matrix')
        self.connect(self.newMatrixDialog.button1, SIGNAL('clicked()'), self.newMatrixDialogOK)
        self.connect(self.newMatrixDialog.button1, SIGNAL('clicked()'), self.newMatrixDialog.close)
        self.connect(self.newMatrixDialog.button2, SIGNAL('clicked()'), self.newMatrixDialog.close)

        #*********Create new array dialog**********
        self.newArrayDialog = self.createMatrixDialog('Create a new array')
        self.connect(self.newArrayDialog.button1, SIGNAL('clicked()'), self.newArrayDialogOK)
        self.connect(self.newArrayDialog.button1, SIGNAL('clicked()'), self.newArrayDialog.close)
        self.connect(self.newArrayDialog.button2, SIGNAL('clicked()'), self.newArrayDialog.close)

        #Create a toolbox and place it inside dockwidget
        toolbox = QToolBox()
        self.setWidget(toolbox)

        #***********Fill toolbox*************
        #**Arithmetic tab**
        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setOriginCorner(Qt.TopLeftCorner)
        layout.setRowStretch(9,90)

        spc = 1 # pixels around edge of groupbox

        #Absolute
        b = ToolButton(self, 'icons/absolutebutton.svg', iconsize.width(), iconsize.height(), 'Absolute value', 'Absolute value', 'absolute')
        layout.addWidget(b, 0, 0, Qt.AlignLeft|Qt.AlignTop)

        #Square root
        b = ToolButton(self, 'icons/squarerootbutton.svg', iconsize.width(), iconsize.height(), 'Find the square root', 'Get squareroot', 'squareroot')
        layout.addWidget(b, 0, 1, Qt.AlignLeft|Qt.AlignTop)

        #Nth order root
        b = ToolButton(self, 'icons/ordernrootbutton.svg', iconsize.width(), iconsize.height(), 'Find the n-th order root', 'N-th order root', 'ordernroot')
        layout.addWidget(b, 1, 0, Qt.AlignLeft|Qt.AlignTop)

        #Complex conjugate
        b = ToolButton(self, 'icons/conjugatebutton.svg', iconsize.width(), iconsize.height(), 'Complex conjugate', 'Complex conjugate', 'conjugate')
        layout.addWidget(b, 1, 1, Qt.AlignLeft|Qt.AlignTop)

        #Power
        b = ToolButton(self, 'icons/powerbutton.svg', iconsize.width(), iconsize.height(), 'Power', 'Power', 'power')
        layout.addWidget(b, 2, 0, Qt.AlignLeft|Qt.AlignTop)

        #Superscript
        b = ToolButton(self, 'icons/superscriptbutton.svg', iconsize.width(), iconsize.height(), 'Superscript', 'Superscript', 'superscript')
        layout.addWidget(b, 2, 1, Qt.AlignLeft|Qt.AlignTop)

        #Assignment
        b = ToolButton(self, 'icons/assignmentbutton.svg', iconsize.width(), iconsize.height(), 'Assignment', 'Assignment', 'assignment')
        layout.addWidget(b, 3, 0, Qt.AlignLeft|Qt.AlignTop)

        #Subscript
        b = ToolButton(self, 'icons/subscriptbutton.svg', iconsize.width(), iconsize.height(), 'Subscript', 'Subscript', 'subscript')
        layout.addWidget(b, 3, 1, Qt.AlignLeft|Qt.AlignTop)

        #Equal to
        b = ToolButton(self, 'icons/equaltobutton.svg', iconsize.width(), iconsize.height(), 'Equal to', 'Equal to', 'equality')
        layout.addWidget(b, 4, 0, Qt.AlignLeft|Qt.AlignTop)

        #<
        b = ToolButton(self, 'icons/lessthanbutton.svg', iconsize.width(), iconsize.height(), 'Less than', 'Less than', 'operator', '<', '<')
        layout.addWidget(b, 4, 1, Qt.AlignLeft|Qt.AlignTop)

        #>
        b = ToolButton(self, 'icons/greaterthanbutton.svg', iconsize.width(), iconsize.height(), 'Greater than', 'Greater than', 'operator', '>', '>')
        layout.addWidget(b, 5, 0, Qt.AlignLeft|Qt.AlignTop)

        #<=
        b = ToolButton(self, 'icons/lessthanequalbutton.svg', iconsize.width(), iconsize.height(), \
                       'Less than or equal to', 'Less than or equal to', 'operator', u'\u2264', '<=')
        layout.addWidget(b, 5, 1, Qt.AlignLeft|Qt.AlignTop)

        #>=
        b = ToolButton(self, 'icons/greaterthanequalbutton.svg', iconsize.width(), iconsize.height(), \
                       'Greater than or equal to', 'Greater than or equal to', 'operator', u'\u2265', '>=')
        layout.addWidget(b, 6, 0, Qt.AlignLeft|Qt.AlignTop)

        #!=
        b = ToolButton(self, 'icons/notequalbutton.svg', iconsize.width(), iconsize.height(), 'Not equal to', 'Not equal to', 'operator', u'\u2260', '!=')
        layout.addWidget(b, 6, 1, Qt.AlignLeft|Qt.AlignTop)

        #Not
        b = ToolButton(self, 'icons/notbutton.svg', iconsize.width(), iconsize.height(), 'Bitwise not', 'Bitwise not', 'operator', u'\u00ac', '!!')
        layout.addWidget(b, 7, 0, Qt.AlignLeft|Qt.AlignTop)

        #And
        b = ToolButton(self, 'icons/andbutton.svg', iconsize.width(), iconsize.height(), 'Bitwise and', 'Bitwise and', 'operator', u'\u2227', '&&')
        layout.addWidget(b, 7, 1, Qt.AlignLeft|Qt.AlignTop)

        #Or
        b = ToolButton(self, 'icons/orbutton.svg', iconsize.width(), iconsize.height(), 'Bitwise or', 'Bitwise or', 'operator', u'\u2228', '||')
        layout.addWidget(b, 8, 0, Qt.AlignLeft|Qt.AlignTop)

        #Xor
        b = ToolButton(self, 'icons/xorbutton.svg', iconsize.width(), iconsize.height(), \
                       'Bitwise exclusive or', 'Bitwise exclusive or', 'operator', u'\u2295', '^^')
        layout.addWidget(b, 8, 1, Qt.AlignLeft|Qt.AlignTop)

        #Floor
        b = ToolButton(self, 'icons/floorbutton.svg', iconsize.width(), iconsize.height(), 'Floor', 'Floor', 'floor')
        layout.addWidget(b, 9, 0, Qt.AlignLeft|Qt.AlignTop)

        #Ceiling
        b = ToolButton(self, 'icons/ceilbutton.svg', iconsize.width(), iconsize.height(), 'Ceiling', 'Ceiling', 'ceil')
        layout.addWidget(b, 9, 1, Qt.AlignLeft|Qt.AlignTop)

        g = QGroupBox()
        g.setContentsMargins(spc, spc, spc, spc)
        g.setLayout(layout)
        toolbox.addItem(g, 'Arithmetic and Boolean')

        table = SymbolsTable()
        self.connect(table, SIGNAL("characterSelected(const QString &,  \
            const QString &)"), self.insertSpecialCharacter)
        layout = QGridLayout()
        layout.addWidget(table)
        g = QGroupBox()
        g.setContentsMargins(-2, -2, 0, 0)
        g.setLayout(layout)
        toolbox.addItem(g, 'Symbols')


        #**Toolbox matrices tab**
        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setOriginCorner(Qt.TopLeftCorner)
        layout.setRowStretch(5,90)

        b = QPushButton()
        b.setIcon(QIcon('icons/matrixbutton.svg'))
        b.setIconSize(QSize(iconsize.width(), iconsize.height()))
        b.setStatusTip('Create new matrix')
        b.setToolTip('Create a new matrix')
        self.connect(b, SIGNAL('clicked()'), self.newMatrixDialog.show)
        layout.addWidget(b, 0, 0, Qt.AlignLeft|Qt.AlignTop)

        b = QPushButton()
        b.setIcon(QIcon('icons/arraybutton.svg'))
        b.setIconSize(QSize(iconsize.width(), iconsize.height()))
        b.setStatusTip('Create new array')
        b.setToolTip('Create a new array')
        self.connect(b, SIGNAL('clicked()'), self.newArrayDialog.show)
        layout.addWidget(b, 0, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/determinantbutton.svg', iconsize.width(), iconsize.height(), 'Determinant', 'Determinant', 'determinant')
        layout.addWidget(b, 1, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/transposebutton.svg', iconsize.width(), iconsize.height(), 'Get Transpose', 'Get Transpose', 'transpose')
        layout.addWidget(b, 1, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/hermitianbutton.svg', iconsize.width(), iconsize.height(), \
                       'Get Hermitian', 'Get Hermitian (Transpose conjugate)', 'hermitian')
        layout.addWidget(b, 2, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/normbutton.svg', iconsize.width(), iconsize.height(), \
                       'Get second order norm', 'Get second order norm (=sqrt of sum of squares)', 'norm')
        layout.addWidget(b, 2, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/dotproductbutton.svg', iconsize.width(), iconsize.height(), 'Dot product', 'Dot product', 'dotproduct')
        layout.addWidget(b, 3, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/matrixsumbutton.svg', iconsize.width(), iconsize.height(), \
                       'Sum elements in vector/matrix', 'Sum elements in vector/matrix', 'matrixsum')
        layout.addWidget(b, 3, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/meanaveragebutton.svg', iconsize.width(), iconsize.height(), \
                       'Compute mean average of elements', 'Compute mean average of elements', 'meanaverage')
        layout.addWidget(b, 4, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/inserttablebutton.svg', iconsize.width(), iconsize.height(), \
                       'Insert input table', 'Insert input table', 'inputtable')
        layout.addWidget(b, 4, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/vectorizebutton.svg', iconsize.width(), iconsize.height(), 'Vectorize', 'Vectorize', 'vectorize')
        layout.addWidget(b, 5, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/convolutionbutton.svg', iconsize.width(), iconsize.height(), \
                       'Full Linear Convolution', 'Full Linear Convolution', 'convolution')
        layout.addWidget(b, 5, 1, Qt.AlignLeft|Qt.AlignTop)

        g = QGroupBox()
        g.setContentsMargins(spc, spc, spc, spc)
        #g.setFlat(True)
        g.setLayout(layout)
        toolbox.addItem(g, 'Matrices')

        #**Toolbox plotting tab**
        layout = QGridLayout()
        layout.setOriginCorner(Qt.TopLeftCorner)
        layout.setRowStretch(3,90)

        b = ToolButton(self, 'icons/plot2dbutton.svg', iconsize.width(), iconsize.height(), \
                       '2D line/scatter plot', '2D line/scatter plot', 'plot2d')
        layout.addWidget(b, 0, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/contourbutton.svg', iconsize.width(), iconsize.height(), 'Contour plot', 'Contour plot', 'contourplot')
        layout.addWidget(b, 0, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/plot3dbutton.svg', iconsize.width(), iconsize.height(), '3D Plot', '3D Plot', 'plot3d')
        layout.addWidget(b, 1, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/polarplotbutton.svg', iconsize.width(), iconsize.height(), 'Polar Plot', 'Polar Plot', 'polarplot')
        layout.addWidget(b, 1, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/sliderbutton.svg', iconsize.width(), iconsize.height(), 'Slider', 'Slider', 'slider')
        layout.addWidget(b, 2, 0, Qt.AlignLeft|Qt.AlignTop)

        g = QGroupBox()
        g.setContentsMargins(spc, spc, spc, spc)
        #g.setFlat(True)
        g.setLayout(layout)
        toolbox.addItem(g, 'Plots')

        #**Toolbox calculus tab**
        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setOriginCorner(Qt.TopLeftCorner)
        layout.setRowStretch(5,90)

        b = ToolButton(self, 'icons/sumbutton.svg', iconsize.width(), iconsize.height(), \
                       'Create new summation', 'Create new summation', 'summation')
        layout.addWidget(b, 0, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/rangesumbutton.svg', iconsize.width(), iconsize.height(), \
                       'Create new range summation', 'Create new range summation', 'rangesummation')
        layout.addWidget(b, 0, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/productbutton.png', iconsize.width(), iconsize.height(), \
                       'Create new product', 'Create new product', 'product')
        layout.addWidget(b, 1, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/definiteintegralbutton.svg', iconsize.width(), iconsize.height(), \
                       'Definite integral', 'Definite integral', 'defintegral')
        layout.addWidget(b, 1, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/indefiniteintegralbutton.svg', iconsize.width(), iconsize.height(), \
                       'Indefinite integral', 'Indefinite integral', 'indefintegral')
        layout.addWidget(b, 2, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/differentialbutton.svg', iconsize.width(), iconsize.height(), \
                       'Differentiate', 'Differentiate', 'differentiate')
        layout.addWidget(b, 2, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/ndifferentialbutton.svg', iconsize.width(), iconsize.height(), \
                       'Differentiate', 'Differentiate', 'ndifferentiate')
        layout.addWidget(b, 3, 0, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/limitrightbutton.svg', iconsize.width(), iconsize.height(), \
                       'Find limit from the right', 'Find limit from the right', 'limitright')
        layout.addWidget(b, 3, 1, Qt.AlignLeft|Qt.AlignTop)

        b = ToolButton(self, 'icons/limitleftbutton.svg', iconsize.width(), iconsize.height(), \
                       'Find limit from the left', 'Find limit from the left', 'limitleft')
        layout.addWidget(b, 4, 0, Qt.AlignLeft|Qt.AlignTop)

        g = QGroupBox()
        g.setContentsMargins(spc, spc, spc, spc)
        g.setLayout(layout)
        toolbox.addItem(g, 'Calculus')

        #**Toolbox symbolics tab**
        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setOriginCorner(Qt.TopLeftCorner)
        layout.setRowStretch(5,90)

        #Symbol create
        b = ToolButton(self, 'icons/symbolcreatebutton.svg', iconsize.width(), iconsize.height(), \
                       'Create symbol', 'Create symbol', 'createsymbol', None)
        layout.addWidget(b, 0, 0, Qt.AlignLeft|Qt.AlignTop)

        #Real symbol create
        b = ToolButton(self, 'icons/realsymbolcreatebutton.svg', iconsize.width(), iconsize.height(), \
                       'Create real symbol', 'Create real symbol', 'createsymbol', 'real')
        layout.addWidget(b, 0, 1, Qt.AlignLeft|Qt.AlignTop)

        #Integer symbol create
        b = ToolButton(self, 'icons/intsymbolcreatebutton.svg', iconsize.width(), iconsize.height(), \
                       'Create integer symbol', 'Create integer symbol', 'createsymbol', 'integer')
        layout.addWidget(b, 1, 0, Qt.AlignLeft|Qt.AlignTop)

        #Complex symbol create
        b = ToolButton(self, 'icons/complexsymbolcreatebutton.svg', iconsize.width(), iconsize.height(), \
                       'Create complex symbol', 'Create complex symbol', 'createsymbol', 'complex')
        layout.addWidget(b, 1, 1, Qt.AlignLeft|Qt.AlignTop)

        #Symbolic result compute
        b = ToolButton(self, 'icons/symbolicevaluatebutton.svg', iconsize.width(), iconsize.height(), \
                       'Symbolic evaluation', 'Symbolic evaluation', 'symbolicevaluate')
        layout.addWidget(b, 2, 0, Qt.AlignLeft|Qt.AlignTop)

        #Substitute
        b = ToolButton(self, 'icons/substitutionbutton.svg', iconsize.width(), iconsize.height(), \
                       'Perform substitution', 'Perform substitution', 'substitution')
        layout.addWidget(b, 2, 1, Qt.AlignLeft|Qt.AlignTop)

        g = QGroupBox()
        g.setContentsMargins(spc, spc, spc, spc)
        g.setLayout(layout)
        toolbox.addItem(g, 'Symbolics')

        #**Toolbox programming tab**
        layout = QGridLayout()
        layout.setSpacing(5)
        layout.setOriginCorner(Qt.TopLeftCorner)
        layout.setRowStretch(10, 9)

        #New program line
        b = ToolButton(self, 'icons/newlinebutton.svg', iconsize.width(), iconsize.height(), \
                       'Insert new program line', 'Insert new program line', 'newline')
        layout.addWidget(b, 0, 0, Qt.AlignLeft|Qt.AlignTop)

        #Program if
        b = ToolButton(self, 'icons/ifbutton.svg', iconsize.width(), iconsize.height(), 'Insert if statement', 'Insert if statement', 'if')
        layout.addWidget(b, 2, 0, Qt.AlignLeft|Qt.AlignTop)

        #Program else
        b = ToolButton(self, 'icons/elsebutton.svg', iconsize.width()*1.5, iconsize.height()*1.1, \
                       'Insert else statement', 'Insert else statement', 'else')
        layout.addWidget(b, 3, 0, Qt.AlignLeft|Qt.AlignTop)

        #Program elif
        b = ToolButton(self, 'icons/elifbutton.svg', iconsize.width()*1.5, iconsize.height()*1.1, \
                       'Insert elif statement', 'Insert elif statement', 'elif')
        layout.addWidget(b, 4, 0, Qt.AlignLeft|Qt.AlignTop)

        #Program for
        b = ToolButton(self, 'icons/forbutton.svg', iconsize.width(), iconsize.height(), \
                       'Insert for statement', 'Insert for statement', 'for')
        layout.addWidget(b, 5, 0, Qt.AlignLeft|Qt.AlignTop)

        #Program while
        b = ToolButton(self, 'icons/whilebutton.svg', iconsize.width()*2, iconsize.height()*1.1, \
                       'Insery while statement', 'Insery while statement', 'while')
        layout.addWidget(b, 6, 0, Qt.AlignLeft|Qt.AlignTop)

        #Program continue
        b = ToolButton(self, 'icons/continuebutton.svg', iconsize.width()*3, iconsize.height()*1.1, \
                       'Insert continue statement', 'Insert continue statement', 'continue')
        layout.addWidget(b, 7, 0, Qt.AlignLeft|Qt.AlignTop)

        #Program break
        b = ToolButton(self, 'icons/breakbutton.svg', iconsize.width()*2, iconsize.height()*1.1, \
                       'Insert break statement', 'Insert break statement', 'break')
        layout.addWidget(b, 8, 0, Qt.AlignLeft|Qt.AlignTop)

        #Program return
        b = ToolButton(self, 'icons/returnbutton.svg', iconsize.width()*2, iconsize.height()*1.1, \
                       'Insert return statement', 'Insert return statement', 'return')
        layout.addWidget(b, 9, 0, Qt.AlignLeft|Qt.AlignTop)

        g = QGroupBox()
        g.setContentsMargins(spc, spc, spc, spc)
        g.setLayout(layout)
        toolbox.addItem(g, 'Programming')

    #***********************Math toolbox callbacks***************************
    def insertSpecialCharacter(self, ascii_string, unicode_value):
        w = self.parent().getCurrentWorksheet()
        w.processToolbuttonInput('specialsymbol', unicode(unicode_value), str(ascii_string))

    def subscriptButtonCallback(self):
        w = self.parent().getCurrentWorksheet()
        w.processToolbuttonInput('subscript')

    #Create a matrix dialog window and callbacks
    def createMatrixDialog(self, title):
        matrix = QDialog(self)
        matrix.setWindowTitle(title)
        matrix.setGeometry(300, 300, 200, 100)
        matrix.setVisible(False)

        #Create rows spinbox
        rows = QSpinBox(matrix)
        rows.setRange(1, 10)
        rows.setValue(2)
        matrix.matrixRows = rows
        rowslabel = QLabel('Enter Number of Rows:', matrix)

        #Create cols spinbox
        cols = QSpinBox(matrix)
        cols.setRange(1, 10)
        cols.setValue(2)
        matrix.matrixCols = cols
        colslabel = QLabel('Enter Number of Columns:',matrix)

        #Create some buttons
        button1 = QPushButton('OK', matrix)
        button2 = QPushButton('Cancel', matrix)
        matrix.button1 = button1
        matrix.button2 = button2

        layout = QGridLayout(matrix)
        layout.addWidget(rowslabel, 0, 0)
        layout.addWidget(colslabel, 0, 1)
        layout.addWidget(rows, 1, 0)
        layout.addWidget(cols, 1, 1)
        layout.addWidget(button1, 2, 0)
        layout.addWidget(button2, 2, 1)
        matrix.setLayout(layout)
        matrix.hide()
        return matrix  #Return a dialog for creating matrices

    def newMatrixDialogOK(self):
        w = self.parent().getCurrentWorksheet()
        w.processToolbuttonInput('newmatrix', self.newMatrixDialog.matrixRows.value(), self.newMatrixDialog.matrixCols.value())

    def newArrayDialogOK(self):
        w = self.parent().getCurrentWorksheet()
        w.processToolbuttonInput('newarray', self.newArrayDialog.matrixRows.value(), self.newArrayDialog.matrixCols.value())



class ToolButton(QPushButton):
    def __init__(self, parent_dock, icon_name, w, h, status_tip, tool_tip, *commands):
        QPushButton.__init__(self)

        self.parent_window = parent_dock.parent()
        self.commands = commands
        icon = QIcon(icon_name)
        self.setIcon(icon)
        self.setIconSize(QSize(w, h))
        self.setStatusTip(status_tip)
        self.setToolTip(tool_tip)
        self.connect(self, SIGNAL('clicked()'), self.clicked_callback)

    def clicked_callback(self):
        w = self.parent_window.getCurrentWorksheet()
        w.processToolbuttonInput(*self.commands)



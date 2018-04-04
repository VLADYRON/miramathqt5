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
import worksheet
import mathtoolbox
import os

_ICONSIZE = 25

class MainWindow(QMainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        self.resize(1000, 800)

        #Set default icon size for all icons
        self.setIconSize(QSize(_ICONSIZE, _ICONSIZE))

        self.applicationName = '[*] - Snoopy'
        self.setWindowTitle('Untitled' + self.applicationName)

        self.currentDirectory = '/home/roger/'

        #Create worksheet list
        self.worksheets = []

        #Some setup
        self.createStatusBar()
        self.createTabsBar()
        self.createDialogs()
        self.createActions()
        self.createMenus()
        self.createToolbars()

        #Add the first tab (worksheet)
        self.addTab()

        #Add a dock with math toolbox
        mathdockwidget = mathtoolbox.MathToolBox(self, self.iconSize())
        self.addDockWidget(Qt.LeftDockWidgetArea, mathdockwidget)

    def closeEvent(self, event):
        #Check each worksheet to see if it needs to be saved before closing down application
        if self.saveAllOnExit():
            event.accept()
        else:
            event.ignore()

    def getCurrentWorksheet(self):
        index = self.tabs.currentIndex() #Current tab index
        w = self.worksheets[index]  #Current worksheet
        return w

    def createStatusBar(self):
        #Set up status bar messages
        status_bar = self.statusBar()
        self.runtimeStatusMessage = QLabel('Run Time: 0s  ')
        self.numEquationsStatusMessage = QLabel('Equation Count: 0 ')
        self.currentEquationStatusMessage = QLabel('Current Equation: None ')

        status_bar.addPermanentWidget(self.runtimeStatusMessage)
        status_bar.addPermanentWidget(self.numEquationsStatusMessage)
        status_bar.addPermanentWidget(self.currentEquationStatusMessage)

        status_bar.showMessage('Ready')

    def createTabsBar(self):
        #Create worksheet tab bar and add first worksheet
        self.tabs = QTabWidget()
        self.tabs.setTabPosition(QTabWidget.North)
        self.connect(self.tabs, SIGNAL('currentChanged(int)'), self.tabSelected)

        #Set main window central widget
        self.setCentralWidget(self.tabs)

    def createMenus(self):
        #**********Create file menu and add its' actions**********
        menubar = self.menuBar()
        file = menubar.addMenu('&File')
        file.addAction(self.newTabAction)
        file.addSeparator()
        file.addAction(self.openFileAction)
        file.addSeparator()
        file.addAction(self.saveAction)
        file.addAction(self.saveAsAction)
        file.addAction(self.saveAllAction)
        file.addSeparator()
        file.addAction(self.printPageAction)
        file.addSeparator()
        file.addAction(self.exportPDFAction)
        file.addSeparator()
        file.addAction(self.closeAction)
        file.addSeparator()
        file.addAction(self.exitAction)

        #**********Create edit menu and add its' actions**********
        edit = menubar.addMenu('&Edit')
        edit.addAction(self.cutAction)
        edit.addAction(self.copyAction)
        edit.addAction(self.pasteAction)
        edit.addAction(self.selectAllAction)
        insert = edit.addMenu('Insert')
        insert.addAction(self.insertPictureAction)
        edit.addSeparator()
        allignment = edit.addMenu('Alligment')
        allignment.addAction(self.allignLeftAction)
        allignment.addAction(self.allignRightAction)
        allignment.addAction(self.allignTopAction)
        allignment.addAction(self.allignBottomAction)

        #**********Create math menu and add its' actions**********
        math = menubar.addMenu('&Math')

        #**********Create settings menu and add its' actions**********
        settings = menubar.addMenu('&Settings')
        settings.addSeparator()
        settings.addAction(self.preferencesAction)

        #**********Create help menu and add its' actions**********
        help = menubar.addMenu('&Help')
        help.addAction(self.aboutQtAction)

    def createActions(self):
        index = self.tabs.currentIndex() #Current tab index
       # w = self.worksheets[index]  #Current worksheet

        #**************File menu actions*************
        #Create a new tab action
        newtab = QAction(QIcon('icons/tab_new.png'), 'New Tab', self)
        newtab.setShortcut('Ctrl+T')
        newtab.setStatusTip('Add a new worksheet tab')
        self.newTabAction = newtab
        self.connect(self.newTabAction, SIGNAL('triggered()'), self.addTab)

        #Open file action
        openfile = QAction(QIcon('icons/fileopen.png'), 'Open...', self)
        openfile.setShortcut('Ctrl+O')
        openfile.setStatusTip('Open file')
        self.openFileAction = openfile
        self.connect(self.openFileAction, SIGNAL('triggered()'), self.openFile)

        #Save file action
        save = QAction(QIcon('icons/filesave.png'), 'Save', self)
        save.setShortcut('Ctrl+S')
        save.setStatusTip('Save')
        self.saveAction = save
        self.connect(self.saveAction, SIGNAL('triggered()'), self.saveFile)

        #Save As file action
        saveAs = QAction(QIcon('icons/filesaveas.png'), 'Save As...', self)
        saveAs.setStatusTip('Save As...')
        self.saveAsAction = saveAs
        self.connect(self.saveAsAction, SIGNAL('triggered()'), self.saveFileAs)

        #Save All file action
        saveAll = QAction(QIcon('icons/save_all.png'), 'Save All', self)
        saveAll.setShortcut('Ctrl+L')
        saveAll.setStatusTip('SaveAll')
        self.saveAllAction = saveAll
        self.connect(self.saveAllAction, SIGNAL('triggered()'), self.saveAll)

        #Export as PDF action
        exportPDF = QAction(QIcon('icons/acroread.png'), 'Export scene contents to PDF', self)
        #exportPDF.setShortcut('Ctrl+P')
        exportPDF.setStatusTip('Export worksheet to PDF File')
        self.exportPDFAction = exportPDF
        self.connect(self.exportPDFAction, SIGNAL('triggered()'), self.exportPDF)

        #Print action
        printPage = QAction(QIcon('icons/fileprint.png'), 'Print current tab', self)
        printPage.setShortcut('Ctrl+P')
        printPage.setStatusTip('Print current tab')
        self.printPageAction = printPage
        self.connect(self.printPageAction, SIGNAL('triggered()'), self.printPage)

        #Close Tab action
        close = QAction(QIcon('icons/fileclose.png'), 'Close Current Tab', self)
        close.setShortcut('Ctrl+W')
        close.setStatusTip('Close Current Tab')
        self.closeAction = close
        self.connect(self.closeAction, SIGNAL('triggered()'), self.closeTab)

        #Quit action
        exit = QAction(QIcon('icons/exit.png'), 'Exit', self)
        exit.setShortcut('Ctrl+Q')
        exit.setStatusTip('Exit application')
        self.exitAction = exit
        self.connect(self.exitAction, SIGNAL('triggered()'), SLOT('close()'))

        #****************Edit menu actions***************
        #Select All action
        selectAll = QAction(QIcon('icons/exit.png'), 'Select All', self)
        selectAll.setShortcut('Ctrl+A')
        selectAll.setStatusTip('Select All')
        self.selectAllAction = selectAll
        self.connect(self.selectAllAction, SIGNAL('triggered()'), self.selectAll)

        #Cut action
        cut = QAction(QIcon('icons/editcut.png'), 'Cut', self)
        cut.setShortcut('Ctrl+X')
        cut.setStatusTip('Cut')
        self.cutAction = cut
        self.connect(self.cutAction, SIGNAL('triggered()'), self.cut)

        #Copy action
        copy = QAction(QIcon('icons/editcopy.png'), 'Copy', self)
        copy.setShortcut('Ctrl+C')
        copy.setStatusTip('Copy')
        self.copyAction = copy
        self.connect(self.copyAction, SIGNAL('triggered()'), self.copy)

        #Paste action
        paste = QAction(QIcon('icons/editpaste.png'), 'Paste', self)
        paste.setShortcut('Ctrl+V')
        paste.setStatusTip('Paste')
        self.pasteAction = paste
        self.connect(self.pasteAction, SIGNAL('triggered()'), self.paste)

        #Insert Picture action
        insertPicture = QAction(QIcon('icons/helicopter.png'), 'Insert Picture...', self)
        insertPicture.setStatusTip('Insert a Picture')
        self.insertPictureAction = insertPicture
        self.connect(self.insertPictureAction, SIGNAL('triggered()'), self.insertPicture)

        #Allign left action
        allignLeft = QAction(QIcon('icons/exit.png'), 'Allign Left', self)
        allignLeft.setStatusTip('Allign Left')
        self.allignLeftAction = allignLeft
        self.connect(self.allignLeftAction, SIGNAL('triggered()'), self.allignLeft)

        #Allign right action
        allignRight = QAction(QIcon('icons/exit.png'), 'Allign Right', self)
        allignRight.setStatusTip('Allign Right')
        self.allignRightAction = allignRight
        self.connect(self.allignRightAction, SIGNAL('triggered()'), self.allignRight)

        #Allign top action
        allignTop = QAction(QIcon('icons/exit.png'), 'Allign Top', self)
        allignTop.setStatusTip('Allign Top')
        self.allignTopAction = allignTop
        self.connect(self.allignTopAction, SIGNAL('triggered()'), self.allignTop)

        #Allign bottom action
        allignBottom = QAction(QIcon('icons/exit.png'), 'Allign Bottom', self)
        allignBottom.setStatusTip('Allign Bottom')
        self.allignBottomAction = allignBottom
        self.connect(self.allignBottomAction, SIGNAL('triggered()'), self.allignBottom)

        #****Math edit actions****

        #**************Settings menu actions*************
        #Preferences action
        preferences = QAction(QIcon('icons/exit.png'), 'Preferences', self)
        preferences.setStatusTip('Preferences')
        self.preferencesAction = preferences
        self.connect(self.preferencesAction, SIGNAL('triggered()'), self.preferencesDialog.show)

        #****************Help menu actions****************
        aboutQt = QAction(QIcon('icons/exit.png'), 'About Qt', self)
        aboutQt.setStatusTip('About Qt')
        self.aboutQtAction = aboutQt
        self.connect(self.aboutQtAction, SIGNAL('triggered()'), self.showAboutQt)

        #Bold action
        bold = QAction(QIcon('icons/boldbutton.svg'), 'Bold', self)
        bold.setStatusTip('Bold')
        bold.setCheckable(True)
        self.boldAction = bold
        self.connect(self.boldAction, SIGNAL('triggered(bool)'), self.bold)

        #Italic action
        italic = QAction(QIcon('icons/italicbutton.svg'), 'Italic', self)
        italic.setStatusTip('Italic')
        italic.setCheckable(True)
        self.italicAction = italic
        self.connect(self.italicAction, SIGNAL('triggered(bool)'), self.italic)

        #Underline action
        underline = QAction(QIcon('icons/underlinebutton.svg'), 'Underline', self)
        underline.setStatusTip('Underline')
        underline.setCheckable(True)
        self.underlineAction = underline
        self.connect(self.underlineAction, SIGNAL('triggered(bool)'), self.underline)

    def createToolbars(self):
        #*********Create file toobar*************
        fileToolBar = self.addToolBar('File')
        fileToolBar.setMovable(True)
        fileToolBar.addAction(self.openFileAction)
        fileToolBar.addAction(self.saveAction)
        fileToolBar.addAction(self.saveAsAction)
        fileToolBar.addAction(self.saveAllAction)
        fileToolBar.addSeparator()
        fileToolBar.addAction(self.newTabAction)
        fileToolBar.addAction(self.closeAction)
        fileToolBar.addSeparator()
        fileToolBar.addAction(self.exportPDFAction)

        #*********Create Edit toolbar************
        editToolBar = self.addToolBar('Edit')
        editToolBar.setMovable(True)
        editToolBar.addAction(self.cutAction)
        editToolBar.addAction(self.copyAction)
        editToolBar.addAction(self.pasteAction)

        #*********Create Font toolbar**************
        fontToolBar = self.addToolBar('Font')
        fontToolBar.setMovable(True)
        fontToolBar.layout().setSpacing(2)

        fontcombo = QFontComboBox()
        fontcombo.setFontFilters(QFontComboBox.ScalableFonts | QFontComboBox.ProportionalFonts)
        #fontcombo.setWritingSystem(QFontDatabase.Latin)
        fontcombo.setMaxVisibleItems(20)
        self.connect(fontcombo, SIGNAL('activated(const QString&)'), self.fontSelected)
        fontToolBar.addWidget(fontcombo)
        self.fontComboBox = fontcombo

        fontsizecombo = QComboBox()
        fontsizecombo.insertItems(0, ['8', '10', '12', '14', '16', '18', '20', '22', '24', '26', '28', '30', '32', \
            '34', '36', '38', '40', '42', '44', '46', '48', '50', '52', '54', '56', '58', '60', '62', '64'])
        self.connect(fontsizecombo, SIGNAL('activated(const QString&)'), self.fontSizeSelected)
        fontToolBar.addWidget(fontsizecombo)
        self.fontSizeComboBox = fontsizecombo

        fontToolBar.addAction(self.boldAction)
        fontToolBar.addAction(self.italicAction)
        fontToolBar.addAction(self.underlineAction)


    def createDialogs(self):
        #********Create preferences dialog*********
        prefs = QDialog()
        prefs.setWindowTitle('Edit Application Preferences')
        prefs.setGeometry(300, 300, 400, 250)
        prefs.setVisible(False)
        prefs.hide()
        self.preferencesDialog = prefs

        #Apply and cancel buttons
        applybutton = QPushButton('Apply')
        self.connect(applybutton, SIGNAL('clicked()'), prefs.close)
        self.connect(applybutton, SIGNAL('clicked()'), self.preferencesDialogApply)
        cancelbutton = QPushButton('Cancel')
        self.connect(cancelbutton, SIGNAL('clicked()'), prefs.close)
        prefsbuttonslayout = QHBoxLayout()
        prefsbuttonslayout.addWidget(cancelbutton)
        prefsbuttonslayout.addWidget(applybutton)

        #Font family and font size
        fontCombo = QFontComboBox()
        self.connect(fontCombo, SIGNAL('currentFontChanged(const QFont &)'), self.fontChanged)

        fontSizeCombo = QComboBox()
        fontSizeCombo.setEditable(1)
        for i in range(8,30,2):
            fontSizeCombo.addItem(QString().setNum(i))
        validator = QIntValidator(2, 64, self)
        fontSizeCombo.setValidator(validator)
        self.connect(fontSizeCombo, SIGNAL('currentIndexChanged(const QString &)'), self.fontSizeChanged)

        fontlayout = QHBoxLayout()
        fontlayout.addWidget(fontCombo)
        fontlayout.addWidget(fontSizeCombo)
        fontgroup = QGroupBox('Equation Font')
        fontgroup.setLayout(fontlayout)

        #Color selection
        c = QColor('red')
        buttonimage = QImage(20, 20, QImage.Format_RGB32)
        buttonimage.fill(c.rgb())
        buttonpixmap = QPixmap.fromImage(buttonimage)
        buttonicon  = QIcon(buttonpixmap)
        backgroundcolorlabel = QLabel('Background Color')
        backgroundcolorbutton = QPushButton()
        backgroundcolorbutton.setIcon(buttonicon)
        self.connect(backgroundcolorbutton, SIGNAL('clicked()'), self.getBackgroundColor)

        colorlayout = QGridLayout()
        colorlayout.addWidget(backgroundcolorlabel, 0, 0)
        colorlayout.addWidget(backgroundcolorbutton, 0, 1)
        colorgroup = QGroupBox('Default Colors')
        colorgroup.setLayout(colorlayout)

        #Layout everythang in preferences dialog
        preflayout = QGridLayout(self.preferencesDialog)
        preflayout.addWidget(fontgroup, 0, 0)
        preflayout.addLayout(prefsbuttonslayout, 1, 1)
        preflayout.addWidget(colorgroup, 0, 1)

    #******************************Callbacks for various dialogs*********************************
    def preferencesDialogApply(self):
        brush = QBrush(QColor('red'))

        worksheet.WorkSheet.backgroundColor = self.worksheetBackgroundColor
        for w in self.worksheets:
            w.setPreferences()

    def getBackgroundColor(self):
        c_before = worksheet.WorkSheet.backgroundColor
        c = QColorDialog.getColor(c_before)
        if c.rgb() != 0xff000000:
            self.worksheetBackgroundColor = c
        else:
            self.worksheetBackgroundColor = c_before

    def fontChanged(self, font):
        print "font changed=", font.family()

    def fontSizeChanged(self, size):
        print "font size changed=",str(size)


    #****************************************Callbacks for file menu*********************************
    def addTab(self):
        #Create a new worksheet, passing it pointers to the status bar messages
        w = worksheet.WorkSheet(self, self.runtimeStatusMessage, self.numEquationsStatusMessage, self.currentEquationStatusMessage)
        self.worksheets.append(w)
        index = self.tabs.addTab(w, 'Untitled')

        #Move to new tab
        self.tabs.setCurrentIndex(index)

    def tabSelected(self, index):
        #This function is called when a tab is clicked, new tab created or another tab closed
        #Set main window's status to reflect contents of worksheet inside clicked tab
        w = self.worksheets[index]
        w.updateEquationStatusMessage()

        for w2 in self.worksheets:
            w2.is_current_tab = False
        w.is_current_tab = True

        if w.hasChanged:
            self.setWindowModified(True)
        else:
            self.setWindowModified(False)

        #Set window title to show file (if any) being edited inside tab
        if w.fileNameDir == None:
            name = 'Untitled'
        else:
            name = w.fileNameDir
        self.setWindowTitle(name + self.applicationName)

        #Display font of current tab on font toolbar
        self.displayCurrentFont(w.font)

    def openFile(self):
        #Bring up an open file dialog
        filedir = QFileDialog.getOpenFileName(self, 'Open File' + self.applicationName, \
                                               self.currentDirectory, '*.dat', '*.dat')
        filedirstring = str(filedir)
        s = os.path.split(filedirstring)
        filename = s[1]
        directory = s[0]

        #filedirstring is zero if cancel button was hit
        if filedirstring:
            #Extract directory
            self.currentDirectory = directory

            #Create new worksheet if current one is not empty
            w = self.getCurrentWorksheet()
            if not w.isEmpty():
                #Current worksheet is not empty so create a new one
                self.addTab()
                w = self.getCurrentWorksheet()

            #Do the actual load
            w.loadWorksheet(filedirstring)

            #Setup window title
            self.setWindowTitle(filedirstring + self.applicationName)
            self.setWindowModified(False)

            #Put loaded filename into tab text
            self.tabs.setTabText(self.tabs.currentIndex(), filename)

    def saveFile(self):
        w = self.getCurrentWorksheet()

        #Is this the first time we are saving this page?
        if w.fileNameDir == None:
            self.saveFileAs()
        else:
            #Only save if something changed
            if w.hasChanged:
                w.saveWorksheet()
                self.setWindowModified(False)

    def saveFileAs(self):
        #Bring up a blocking save file dialog
        filename = QFileDialog.getSaveFileName(self, 'Save worksheet before closing tab', \
                                               '/home/roger', '*.dat', '*.dat')

        #filename is zero if 'cancel' button was hit
        if filename:
            w = self.getCurrentWorksheet()
            w.saveWorksheet(filename)

            self.setWindowTitle(filename + self.applicationName)
            self.setWindowModified(False)

            #Put new filename into tab text
            self.tabs.setTabText(self.tabs.currentIndex(), os.path.split(str(filename))[1])

    def saveAll(self):
        index = self.tabs.currentIndex()
        for i, w in enumerate(self.worksheets):

            #Only save if something changed
            if w.hasChanged:
                #Is this the first time we are saving this page?
                if w.fileNameDir == None:

                    #Bring up changed tab
                    self.tabs.setCurrentIndex(i)

                    #Bring up a blocking save file dialog
                    filename = QFileDialog.getSaveFileName(self, 'Save worksheet before closing tab', \
                                                            '/home/roger', '*.dat', '*.dat')

                    #filename is zero if 'cancel' button was hit
                    if filename:
                        w.saveWorksheet(filename)

                        if index == i:
                            self.setWindowTitle(filename + self.applicationName)
                            self.setWindowModified(False)

                        #Put new filename into tab text
                        self.tabs.setTabText(i, os.path.split(str(filename))[1])

                else:
                    w.saveWorksheet()
                    if index == i:
                        self.setWindowModified(False)

        #Go back to tab on display before saving
        self.tabs.setCurrentIndex(index)

    def saveAllOnExit(self):
        #Set up return value
        retval = True

        i = 0
        while i < len(self.worksheets):
            w = self.worksheets[i]

            #Only save if something changed
            if w.hasChanged:

                #Bring up changed tab
                self.tabs.setCurrentIndex(i)

                #Ask if want to save, discard or cancel close all
                ret = QMessageBox.warning(self, self.applicationName, ("The document has been modified.\n" "Do you want to save your changes?"),
                QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

                #Handle 'save' button hit
                if ret == QMessageBox.Save:
                    #If the page has no file name then bring up a file dialog
                    if w.fileNameDir == None:

                        #Bring up a blocking save file dialog
                        filename = QFileDialog.getSaveFileName(self, 'Save worksheet before closing \
                                   tab', '/home/roger', '*.dat', '*.dat')

                        #filename is zero if 'cancel' button was hit
                        if filename:
                            w.saveWorksheet(filename)
                            self.setWindowTitle(filename + self.applicationName)
                            self.setWindowModified(False)

                            #Put new filename into tab text
                            self.tabs.setTabText(i, os.path.split(str(filename))[1])

                        else:
                            #Cancel button was hit, let calling function know
                            retval = False
                            break  #Assume we changed our mind about closing application

                    #Worksheet already has a filename
                    else:
                        w.saveWorksheet()
                        if self.tabs.currentIndex() == i:
                            self.setWindowModified(False)

                #Handle 'Discard' button hit
                elif ret == QMessageBox.Discard:
                    numtabs = self.tabs.count()

                    #Don't bother deleting last tab, application is closing down anyway
                    if numtabs > 1:
                        self.deleteTab(i, numtabs)
                        i -= 1

                #Handle 'cancel' button hit
                elif ret == QMessageBox.Cancel:
                    #Cancel button was hit, let calling function know
                    retval = False
                    break   #Assume we changed our mind about closing application

            i += 1

        #Return False if 'cancel' was hit in the save file dialog, else return True
        return retval

    def closeTab(self):
        numtabs = self.tabs.count()
        if numtabs > 1:
            index = self.tabs.currentIndex()
            w = self.worksheets[index]

            #If changes were made to worksheet, try to save first before deleting
            if w.hasChanged:
                #Bring up a dialog asking if we want to save changes first before closing tab
                ret = QMessageBox.warning(self, self.applicationName, ("The document has been modified.\n"
                            "Do you want to save your changes?"),
                            QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)

                #Handle 'save' button hit
                if ret == QMessageBox.Save:
                    #Call to this function is blocking
                    filename = QFileDialog.getSaveFileName(self, 'Save worksheet before closing tab', \
                                                           '/home/roger', '*.dat', '*.dat')

                    #filename is zero if 'cancel' button was hit
                    if filename:
                        w.saveWorksheet(filename)

                        #Remove tab and its contents
                        self.deleteTab(index, numtabs)

                #Discard this worksheet
                elif ret == QMessageBox.Discard:
                    self.deleteTab(index, numtabs)

                #Handle 'cancel' button hit
                elif ret == QMessageBox.Cancel:
                    #Do nothing, leave tab alone
                    pass

            #No changes were made to worksheet so simply delete it
            else:
                self.deleteTab(index, numtabs)

    def deleteTab(self, index, numtabs):
        self.tabs.removeTab(index)
        del self.worksheets[index]
        numtabs -= 1

        #Force update of status message and window title
        index = self.tabs.currentIndex()
        self.tabSelected(index)

    def exportPDF(self):
        #Bring up a blocking save file dialog
        filename = QFileDialog.getSaveFileName(self, self.applicationName +  \
                   ': Create PDF file for worksheet ' + str(self.tabs.currentIndex()),  \
                   '/home/roger', '*.pdf', '*.pdf')

        #filename is zero if 'cancel' button was hit
        if filename:
            #Get scene to save
            w = self.getCurrentWorksheet()
            scene = w.scene

            #Create a printer paint device
            printer = QPrinter(QPrinter.ScreenResolution)
            printer.setCreator(self.applicationName)
            printer.setDocName(filename)
            printer.setPageSize(QPrinter.A4)
            printer.setOutputFormat(QPrinter.PdfFormat)
            printer.setOutputFileName(filename)
            printer.setFullPage(True)
            printerRect = QRectF(printer.pageRect())
            pw = printerRect.width()
            ph = printerRect.height()
            ratio = ph/pw
            sw = scene.sceneRect().width()
            sh = scene.sceneRect().height()
            if sw > sh:
                sh = sw * ratio
            else:
                sw = sh/ratio
            sceneRect = QRectF(0, 0, sw, sh)

            #Create a painter object, initialize using the printer paint device
            painter = QPainter()
            painter.begin(printer)
            scene.render(painter, printerRect, sceneRect)
            painter.end()

    def printPage(self):
        #Create a printer paint device
        printer = QPrinter(QPrinter.HighResolution)
        printer.setCreator(self.applicationName)
        printer.setPageSize(QPrinter.A4)
        printerRect = QRectF(printer.pageRect())

        printdialog = QPrintDialog(printer)
        printdialog.setWindowTitle('Print current Tab')
        #printdialog.addEnabledOption(QAbstractPrintDialog.PrintSelection)
        if printdialog.exec_() == QDialog.Accepted:
            w = self.getCurrentWorksheet()
            scene = w.scene

            #Create a painter object, initialize using the printer paint device
            painter = QPainter()
            painter.begin(printer)

            #Need a loop here to render portions of the sceneRect() into pages
            scene.render(painter, printerRect, scene.sceneRect())

            painter.end()

    #****************************************Callbacks for edit menu*********************************
    def selectAll(self):
        w = self.getCurrentWorksheet()
        w.selectAll()

    def cut(self):
        w = self.getCurrentWorksheet()
        w.cut()

    def copy(self):
        w = self.getCurrentWorksheet()
        w.copy()

    def paste(self):
        w = self.getCurrentWorksheet()
        w.paste()

    def allignLeft(self):
        w = self.getCurrentWorksheet()
        w.allignLeft()

    def insertPicture(self):
        w = self.getCurrentWorksheet()
        w.addNewImage()

    def allignRight(self):
        w = self.getCurrentWorksheet()
        w.allignRight()

    def allignTop(self):
        w = self.getCurrentWorksheet()
        w.allignTop()

    def allignBottom(self):
        w = self.getCurrentWorksheet()
        w.allignBottom()

    #****************************************Callbacks for help menu*********************************
    def showAboutQt(self):
        QMessageBox.aboutQt(self, self.applicationName)

    #****************************************Callbacks for font toolbar****************************
    def fontSelected(self, fontname):
        w = self.getCurrentWorksheet()
        w.fontSelected(fontname)

    def fontSizeSelected(self, size):
        w = self.getCurrentWorksheet()
        w.fontSize(int(size))

    def displayCurrentFont(self, font):
        bold = font.bold()
        italic = font.italic()

        font_index = self.fontComboBox.findText(font.family())
        self.fontComboBox.setCurrentIndex(font_index)

        size_index = self.fontSizeComboBox.findText(str(font.pointSize()))
        self.fontSizeComboBox.setCurrentIndex(size_index)

        self.boldAction.setChecked(font.bold())
        self.italicAction.setChecked(font.italic())
        self.underlineAction.setChecked(font.underline())

    def bold(self, state):
        w = self.getCurrentWorksheet()
        w.bold(state)

    def italic(self, state):
        w = self.getCurrentWorksheet()
        w.italic(state)

    def underline(self, state):
        w = self.getCurrentWorksheet()
        w.underline(state)



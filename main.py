#!/usr/bin/env python

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

import signal
import sys

#from PyQt4 import Qt

from mainwindow import *

class MyApplication(QApplication):
    def quit(self):
        print 'quit'

def main(args):
    print 'running...'
    app = MyApplication([])

    #Set up signal handlers
    signal.signal(signal.SIGINT, signalHandler)

    pixmap = QPixmap("./icons/splash.jpg")
    splash = QSplashScreen(pixmap)
    splash.show()

    splash.showMessage("Loading modules", Qt.AlignCenter|Qt.AlignBottom)
    app.processEvents()

    splash.showMessage("more messages", Qt.AlignCenter|Qt.AlignBottom)
    app.processEvents()

    main = MainWindow()
    main.show()
    splash.finish(main)

    #app.connect(app, SIGNAL("lastWindowClosed()"), app, SLOT("quit()"))
    app.connect(app, SIGNAL("lastWindowClosed()"), app.quit)


    app.exec_()
    #sys.exit(app.exec_())   #Enter event loop

def signalHandler(signum, frame):
    print 'Exiting...'
    QApplication.closeAllWindows()



if __name__ == "__main__":
    #Run with psyco if we have on the system
    try:
        import psyco
        print 'Running with psyco...'
        psyco.full()
    except ImportError:
        pass

    main(sys.argv)


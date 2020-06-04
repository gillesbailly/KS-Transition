from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QPageLayout

class SerieGallery(QScrollArea):

    def __init__(self):
        super(SerieGallery,self).__init__()
        self.setBackgroundRole(QPalette.Dark);
        self.setWidgetResizable( True )
        self.setMinimumHeight(230)
        self.container = QWidget()
        self.l = QGridLayout()
        self.container.setLayout( self.l )
        self.setWidget( self.container )
        self.container.show()
        

    def add_view(self, view, row, column):
        self.l.addWidget( view, row, column)
        QApplication.processEvents()
    



from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QPageLayout, QColor, QLinearGradient
from PyQt5.QtCore import Qt


##################################
def base_brush():
	bottom = QColor( 20, 20 , 40)
	top    = QColor( 70, 70 , 80)
	gradient = QLinearGradient(0, 0, 0, 200)
	gradient.setColorAt(0, top)
	gradient.setColorAt(1, bottom)
	return gradient


##################################
def LineEdit( text ):
	palette = QPalette()
	palette.setColor( QPalette.Text,Qt.lightGray )
	palette.setBrush( QPalette.Base, base_brush() )
	
	#palette.setColor ( QColor( 10, 10 , 20) )
	le = QLineEdit( text )
	le.setPalette( palette )
	return le

##################################
def deleteLayoutContent( cur_lay ):
    parent = cur_lay.parentWidget()
    if cur_lay is not None:
        while cur_lay.count():
            item = cur_lay.takeAt(0)
            widget = item.widget()
            if widget is not None:
                widget.deleteLater()
            else:
                parent.deleteLayout( item.layout() )


######################################
#                                    #
#      Serie2DGallery                #
#                                    #
######################################
class Serie2DGallery(QScrollArea):

    ###############################
    def __init__( self ):
        super(QScrollArea,self).__init__()
        #self.setBackgroundRole( QPalette.Dark )
        #p = self.palette()
        #p.setBrush( QPalette.Window, base_brush() )
        #p.setBrush( QPalette.Base, base_brush() )
        #p.setBrush( QPalette.Background, base_brush() )
        
        
        #self.setPalette( p )
        self.setWidgetResizable( True )
        self.container = QWidget()
        self.l = QGridLayout()
        self.container.setLayout( self.l )
        self.setWidget( self.container )
        self.container.show()


    ###############################
    def add_view(self, view, user_id, cmd):
        self.l.addWidget( view, user_id, cmd)
    

    ###############################
    def select_command(self,c):
        print("select command ", c)
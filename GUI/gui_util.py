
from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QPageLayout, QColor, QLinearGradient
from PyQt5.QtCore import Qt, pyqtSignal


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
#           SUB WINDOW               #
#                                    #
######################################
class Sub_Win( QMdiSubWindow ):
    
    ####################
    def __init__( self, name, w = 750, h = 250 ):
        super( QMdiSubWindow, self ).__init__()
        self.resize( w, h )
        self.container = Serie2DGallery()
        self.setWidget( self.container )
        self.setWindowTitle( name )

    ####################
    def add_view( self, view, x, y ):
        self.container.add_view( view, x, y )


######################################
#                                    #
#      MDI AREA                      #
#                                    #
######################################
class Area( QScrollArea):

    view_moved = pyqtSignal( int, int, int ) #trial infos

    #########################
    def __init__( self ):
        super( QScrollArea, self ).__init__()
        self.setWidgetResizable( True )
        
        self.container = QMdiArea()
        #self.container.resize(2000,2000)
        self.container.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded);
        self.container.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded);
        self.wins = dict()
        self.setWidget( self.container )
        self.container.show()

    #########################
    def resizeEvent( self, event ):
        for win in self.container.subWindowList():
            win.resize( event.size().width() - 10, win.height() )
        super().resizeEvent( event )

    #########################
    def window( self, name, w = 750, h = 250):
        if not name in self.wins:
            win = Sub_Win( name, w, h )
            self.container.addSubWindow( win )
            self.wins[ name ] = win
        return self.wins[ name ] 

    #########################
    def add_view( self, view, model_name, user_id, cmd, w = 750, h = 250 ):
        win = self.window( model_name, w, h )
        win.add_view( view, user_id, cmd )
        win.container.horizontalScrollBar().valueChanged.connect( self.view_horizontal_moved )
        win.container.verticalScrollBar().valueChanged.connect( self.view_vertical_moved )
        win.show()

    #########################
    def view_horizontal_moved( self, value ):
        #print( "view horizontal moved", value)
        self.view_moved.emit( value, 0, 0 )


    #########################
    def view_vertical_moved( self, value ):
        #print( "view vertical moved", value)
        self.view_moved.emit( 0, value, 1 )





######################################
#                                    #
#      Serie2DGallery                #
#                                    #
######################################
class Serie2DGallery(QScrollArea):

    ###############################
    def __init__( self ):
        super(QScrollArea,self).__init__()
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






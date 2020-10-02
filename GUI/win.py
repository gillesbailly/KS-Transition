import sys
import os
import numpy as np
from datetime import datetime
import argparse
import itertools

from PyQt5.QtWidgets import *
from PyQt5.QtGui import QPalette, QPageLayout
from PyQt5.QtPrintSupport import *
from PyQt5.QtCore import QCoreApplication, QSignalMapper


from data_explorer import *
from data_loader import *
from simple_episode_view import *
from model_fit import *
from filter_panel import *
from parameters_panel import *


#####################################
#                                   #
#              WIN                  #
#                                   #
#####################################
class Win ( QMainWindow ) :

    #########################
    def __init__( self) :
        super( QMainWindow, self ).__init__()
        self.init()
        self.resize( 1000, 800 )
        self.command_ids             = [ i for i in range(0, 14) ]
        self.model_vec               = []
        self.user_data_vec           = []
        self.model_fit_user_data_vec = []
        self.goodness_of_fit_vec     = []
        self.user_data_panel         = self.add_user_data_panel()
        self.model_fit               = self.add_model_fitting_component()
        self.view_menu = self.menuBar().addMenu( "Views" )
        self.docks = dict()
        self.parameters_panel = Parameters_Group_Panel()
        #self.parameters_panel.set_group( [ model.get_params() for model in self.model_vec ]  ) #REMOVE
        self.model_results_panel = Model_Result_Panel()
        #model_result1 = Model_Result.create( "RW", [1,2,3,4,7] )
        #model_result1.log_likelihood = [-1,-1,-3,-10,-9]
        #model_result2 = Model_Result.create( "CK", [1,2,3,6,7] )
        #model_result2.log_likelihood = [-1,-1,-3,-10,-9]
        #self.model_results_panel.set_group( [ model_result1, model_result2 ] )
        self.create_dock_widgets()

        #self.parameters_panel = Parameters_Comparison_Panel( ["User 3", "User 5" ], parameters_vec)
        #self.parameters_panel.set_group( parameters_vec )
        #self.parameters_panel.show()

        self.setCentralWidget( self.user_data_panel )
        self.show()



        #self.show()



    #########################
    def set_models( self, model_vec ):
        self.model_vec = model_vec
        self.parameters_panel.set_group( [ model.get_params() for model in model_vec ]  ) #REMOVE

         

    #########################
    def show_hide_view( self, checked, name ):
        dock = self.docks[ name ]
        dock.setVisible( checked )
        #dock.setVisible( not dock.isVisible() )

    

    #########################
    def add_dock_widget( self, name, area, widget ):
        dock = QDockWidget( name, self)
        dock.setWidget( widget )
        self.addDockWidget( area, dock )
        self.docks[ name ] = dock
        view_act = self.view_menu.addAction(  name )
        view_act.setCheckable( True )
        view_act.setChecked( True )
        view_act.toggled.connect( lambda checked : self.show_hide_view( checked, name ) )

    #########################
    def create_dock_widgets( self ):
        self.add_dock_widget( "Parameters Editor", Qt.RightDockWidgetArea, self.parameters_panel )
        self.add_dock_widget( "Fitting Results", Qt.RightDockWidgetArea, self.model_results_panel )
        self.add_dock_widget( "Trial Info", Qt.RightDockWidgetArea, self.user_data_panel.trial_info )

    #########################
    def add_user_data_panel_menu( self, configuration_vec ):
        explorer_menu = self.menuBar().addMenu( "Explorer" )

        config_menu = explorer_menu.addMenu( "Organizatation" )
        #self.signal_mapper = QSignalMapper()
        for i, name in enumerate( configuration_vec ) :
            name_str = '-'.join( name )
            act = config_menu.addAction( name_str )
            act.triggered.connect( lambda : self.set_config( i ) )
        #     act.triggered.connect( self.signal_mapper.map )
        #     self.signal_mapper.setMapping( act, i );
        # self.signal_mapper.mapped['int'].connect( self.set_config )

        strategies_act = explorer_menu.addAction( "Show Strategies probabilities" )
        strategies_act.setCheckable( True )
        strategies_act.setChecked( True )
        strategies_act.toggled.connect( self.show_hide_strategies_probs )

        
        action_act = explorer_menu.addAction( "Show Action probabilities" )
        action_act.setCheckable( True )
        action_act.setChecked( True )
        action_act.toggled.connect( self.show_hide_actions_probs )

        config_tool_bar = self.addToolBar( "Configuration ")
        config_tool_bar.addAction( config_menu.menuAction() )


    #########################
    def show_hide_strategies_probs( self, checked ):
        print( "show_hide_strategies_probs ", checked )

    #########################
    def show_hide_actions_probs( self, checked ):
        print( "show_hide_actions_probs ", checked )


    #########################
    def add_user_data_panel( self ) :
        user_data_panel = Empirical_Panel()
        self.add_user_data_panel_menu( user_data_panel.configuration_vec )        
        return user_data_panel


    #########################
    def add_model_fitting_menu( self ):
        fit_menu = self.menuBar().addMenu( "Model_Fitting" )
        act_select           = fit_menu.addAction( "Select...", self.model_fitting_select )
        act_optimize         = fit_menu.addAction( "Optimize parameters", self.model_fitting_optimize )
        act_select_and_apply = fit_menu.addAction( "Select and Apply...", self.model_fitting_select_and_apply )
        act_apply            = fit_menu.addAction( "Apply", self.model_fitting_apply )
        act_display          = fit_menu.addAction( "Display", self.model_fitting_display )                


    #########################
    def add_model_fitting_component( self ) :
        model_fit = Model_Fitting( debug = True)
        model_fit.command_ids = self.command_ids
        self.add_model_fitting_menu()
        return model_fit


    #########################
    def model_fitting_select( self ):
        fit_filter = Filter()
        fit_filter_panel = Filter_Panel( fit_filter )
        fit_filter_panel.set_user_data( self.user_data_vec  )
        dialog = QDialog( self )
        dialog.setWindowTitle("Model Fitting: Select Users - Apply on current parameters - Display Results ")
        l = QGridLayout()
        dialog.setLayout( l )
        l.addWidget( fit_filter_panel, 0, 0, 1, 2)
        apply_button = QPushButton( "Apply" )
        apply_button.clicked.connect( dialog.accept )
        l.addWidget( apply_button, l.rowCount() +1, 1 )
        cancel_button = QPushButton( "Cancel" )
        cancel_button.clicked.connect( dialog.reject )
        l.addWidget( cancel_button, l.rowCount() -1, 0 )

        if dialog.exec() == 1 :
            fit_filter_panel.apply()
            self.model_fit_user_data_vec = fit_filter.filter( self.user_data_vec  )
            print( "model fit user data vec: ", len(self.model_fit_user_data_vec) )
    

    #########################
    def model_fitting_select_and_apply( self ):
        fit_filter = Filter()
        fit_filter_panel = Filter_Panel( fit_filter )
        fit_filter_panel.set_user_data( self.user_data_vec  )
        dialog = QDialog( self )
        dialog.setWindowTitle("Model Fitting: Select Users - Apply on current parameters - Display Results ")
        l = QGridLayout()
        dialog.setLayout( l )
        l.addWidget( fit_filter_panel, 0, 0, 1, 2)
        display_checkbox = QCheckBox( "Display results", )
        l.addWidget( display_checkbox, l.rowCount() + 1, 1, 1, 1)
        apply_button = QPushButton( "Apply" )
        apply_button.clicked.connect( dialog.accept )
        l.addWidget( apply_button, l.rowCount() +1, 1 )
        cancel_button = QPushButton( "Cancel" )
        cancel_button.clicked.connect( dialog.reject )
        l.addWidget( cancel_button, l.rowCount() -1, 0 )

        if dialog.exec() == 1 :
            fit_filter_panel.apply()
            self.model_fit_user_data_vec = fit_filter.filter( self.user_data_vec  )
            print( "model fit user data vec: ", len(self.model_fit_user_data_vec) )
            self.model_fitting_apply()
            if display_checkbox.checkState() == Qt.Checked :
                self.model_fitting_display()


    #########################
    def model_fitting_apply( self ):
        print( "model fitting: apply" )
        self.goodness_of_fit_vec = self.model_fitting_long( self.model_fit_user_data_vec, self.model_vec )
        for goodness_of_fit in self.goodness_of_fit_vec :
            print( goodness_of_fit.name, goodness_of_fit.time,  goodness_of_fit.log_likelihood )


     #########################
    def model_fitting_long( self, user_data_vec, model_vec ):
        self.model_fit.user_data_vec = user_data_vec
        self.model_fit.model_vec = model_vec
        return self.model_fit.run()


    ########################
    def model_fitting_optimize( self ):
        print( "Model fitting optimize" )
        self.goodness_of_fit_vec  = self.model_fitting_optimize_long( self.model_fit_user_data_vec, self.model_vec )
        for goodness_of_fit in self.goodness_of_fit_vec :
            print( goodness_of_fit.name, goodness_of_fit.time,  goodness_of_fit.log_likelihood )

    ########################
    def model_fitting_optimize_long( self, user_data_vec, model_vec ):
        self.model_fit.user_data_vec = user_data_vec
        self.model_fit.model_vec = model_vec
        return self.model_fit.optimize()


   #########################
    def model_fitting_display( self ):
        print("model fitting: display")
        if len(self.goodness_of_fit_vec) < 1 :
            print("No model fitting has been recently performed... Action \"Diplay\" is ignored ")
            return 0
        
        self.model_results_panel.set_group( self.goodness_of_fit_vec )

        goodness_of_fit = self.goodness_of_fit_vec[ 0 ]  #TODO #BUG

        view_vec = []
        for view in self.user_data_panel.view_vec.values() :
            if view.user_id in goodness_of_fit.user_id:
                view_vec.append( view )
        self.update_views_with_model_fitting( view_vec , goodness_of_fit )

    ########################
    def user_data_input( self, user_id ):
        for user_data in self.user_data_vec :
            if user_data.id == user_id :
                return user_data.cmd
        return []

    ########################
    def update_views_with_model_fitting( self, view_vec, goodness_of_fit ): 
        for view in view_vec :
            i = goodness_of_fit.user_id.index( view.user_id )
            user_input = self.user_data_input( view.user_id )
            model_output = goodness_of_fit.output[ i ]
            model_prob   = goodness_of_fit.prob[ i ]
            model_name   = goodness_of_fit.name
            view.set_model_data( model_name, user_input, model_output, model_prob)





   

        


    #########################
    def set_user_data( self, user_data_vec ) :
        self.user_data_vec           = user_data_vec
        self.model_fit_user_data_vec = user_data_vec
        self.user_data_panel.set_sequences( user_data_vec )


    #########################
    def init( self ):
        
        #tool_bar.addAction("Config")
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = self.menuBar().addMenu( "File" )
        self.menuBar().show()
        import_act = file_menu.addAction( "Import", self.import_file )
        expert_act = file_menu.addAction( "Export", self.export_file )


    #########################
    def import_file( self ) :
        print( "import" )


    #########################
    def export_file( self ) :
        print( "export" )

    #########################
    def set_config( self, id ) :
        print( "config", id )
        self.user_data_panel.update_configuration( id )


#####################################
#                                   #
#              MAIN                 #
#                                   #
#####################################
def build_interface():
    path = './data/hotkeys_formatted_dirty.csv'
    parser = argparse.ArgumentParser()
    parser.add_argument( "-p", "--path", help="path of the empirical data" )
    
    args = parser.parse_args()
    if args.path != None :
        path = args.path
    print("sequences path: ", path)
    loader = HotkeyCoach_Loader()
    users_data = loader.experiment( path )
    print( "data of ", len( users_data ), "participants loaded" )

    app = QApplication(sys.argv)
    qApp.setStyle("Fusion")
    dark_palette = QPalette()

    dark_palette.setColor(QPalette.Window, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.WindowText, Qt.white)
    dark_palette.setColor(QPalette.Base, QColor(25, 25, 25))
    dark_palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ToolTipBase, Qt.white)
    dark_palette.setColor(QPalette.ToolTipText, Qt.white)
    dark_palette.setColor(QPalette.Text, Qt.white)
    dark_palette.setColor(QPalette.Button, QColor(53, 53, 53))
    dark_palette.setColor(QPalette.ButtonText, Qt.white)
    dark_palette.setColor(QPalette.BrightText, Qt.red)
    dark_palette.setColor(QPalette.Link, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    dark_palette.setColor(QPalette.HighlightedText, Qt.black)
    dark_palette.setColor(QPalette.Disabled, QPalette.Text, Qt.darkGray)
    dark_palette.setColor(QPalette.Disabled, QPalette.ButtonText, Qt.darkGray)
    dark_palette.setColor(QPalette.Disabled, QPalette.WindowText, Qt.darkGray)
    
    qApp.setPalette(dark_palette)




    my_filter = Filter(user_min = 0, user_max = 1, techniques=["traditional", "audio"] ) 
    filtered_users_data = my_filter.filter( users_data )
    print( "data of ",  len( filtered_users_data ), "users once filtered" )
    win = Win()
    win.show()
    win.set_user_data( filtered_users_data )
    win.set_models( [ Alpha_Beta_Model( None, 'RW' ), Alpha_Beta_Model( None, 'CK' ), Alpha_Beta_Model( None, 'RW_CK' ) ] )
    win.model_fitting_select_and_apply()
    #win.model_fitting_optimize()
    win.model_fitting_display()
    #panel.set_sequences( filtered_users_data )
    #panel.print_all('./tmp_graphs')
    #panel.print_unit('./tmp_graphs')
    #panel.ensure_view_visible("audio", 4, 2)
    #panel.update_configuration(4)
    #panel.ensure_view_visible("traditional", 3, 2)

    




    #win.show()
    #window.select_command( args.command )

    sys.exit(app.exec_())
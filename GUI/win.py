import sys
import os
import numpy as np
from datetime import datetime
import argparse
import itertools
import time as TIME

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
from user_data_loader import *
from user_data_export import *
from parameters_export import *
from ILHP_model import *

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
        self.explorer_user_data_vec  = []
        self.model_fit_user_data_vec = []
        self.goodness_of_fit_vec     = []
        self.explorer_panel          = self.add_explorer_panel()
        self.model_fit               = self.add_model_fitting_component()
        self.add_model_simulation_component()
        self.view_menu = self.menuBar().addMenu( "Views" )
        self.filters = dict()
        self.docks = dict()
        self.explorer_filter_panel = None
        self.parameters_panel = Parameters_Group_Panel()
        self.parameters_panel.reload.connect( self.model_fitting_apply )
        self.model_results_panel = Model_Result_Panel()
        self.create_dock_widgets()
        self.tmp_panel = None
        self.setCentralWidget( self.explorer_panel )
        self.show()

    #########################
    def set_models( self, model_vec ):
        self.model_vec = model_vec
        print( [ model.name for model in self.model_vec] )
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
        self.add_dock_widget( "Trial Info", Qt.RightDockWidgetArea, self.explorer_panel.trial_info )


    #########################
    def get_filter( self, _name ):
        if not _name in self.filters:
            self.filters[ _name ] = Filter( name = _name )
        return self.filters[ _name ]

    ###########################
    def exec_filter( self, filter ):
        filter_panel = Filter_Panel( filter )
        dialog = QDialog( self )
        dialog.setWindowTitle( filter.name + ": select..." )
        l = QGridLayout( dialog )
        l.addWidget( filter_panel, 0, 0, 1, 2)
        apply_button = QPushButton( "Apply" )
        apply_button.clicked.connect( dialog.accept )
        l.addWidget( apply_button, l.rowCount() +1, 1 )
        cancel_button = QPushButton( "Cancel" )
        cancel_button.clicked.connect( dialog.reject )
        l.addWidget( cancel_button, l.rowCount() -1, 0 )
        dialog.setLayout( l )
        res = dialog.exec()
        if res == 1 :
            filter_panel.apply()
        #win.setFocus()
        return res


    #########################
    def init( self ):
        
        #tool_bar.addAction("Config")
        menu_bar = QMenuBar()
        self.setMenuBar(menu_bar)

        file_menu = self.menuBar().addMenu( "File" )
        self.menuBar().show()
        import_menu = file_menu.addMenu( "Import" )
        hotkey_coach_act = import_menu.addAction( "HotkeyCoach Data", self.load_hotkeycoach_data )
        user_data_act = import_menu.addAction( "User Data", self.load_user_data )

        export_menu = file_menu.addMenu( "Export" )
        act_user_data = export_menu.addAction("As User Data", self.export_user_data )
        act_parameters = export_menu.addAction("Paramerters", self.export_parameters )



#####################################################################################################
###############################################  EXPLORER ###########################################
#####################################################################################################


    #########################
    def create_toggle_action( self, menu, name, state, method, shortcut ):
        act = menu.addAction( name )
        act.setCheckable( True )
        act.setChecked( state )
        act.toggled.connect( method )
        act.setShortcut( QKeySequence( shortcut ) )
        return act

    #########################
    def add_explorer_panel_menu( self, configuration_vec ):
        explorer_menu = self.menuBar().addMenu( "Explorer" )
        select_act  = explorer_menu.addAction( "Select..." , self.explorer_select )
        display_act = explorer_menu.addAction( "Display" , self.update_explorer_panel )

        config_menu = explorer_menu.addMenu( "Organizatation" )
        #self.signal_mapper = QSignalMapper()
        for i, name in enumerate( configuration_vec ) :
            name_str = '-'.join( name )
            act = config_menu.addAction( name_str )
            act.triggered.connect( lambda : self.set_config( i ) )
        
        self.create_toggle_action( explorer_menu, "Show User Data", True, self.show_user_data, "Ctrl+E")
        self.create_toggle_action( explorer_menu, "Show Stratgies Probabilities", True, self.show_strategy_probs, "Ctrl+D")
        self.create_toggle_action( explorer_menu, "Show Action Probabilities", True, self.show_action_probs, "Ctrl+C")
        self.create_toggle_action( explorer_menu, "Show Option 1", True, self.show_option_1, "Ctrl+R")
        self.create_toggle_action( explorer_menu, "Show Option 2", True, self.show_option_2, "Ctrl+F")

        config_tool_bar = self.addToolBar( "Configuration ")
        config_tool_bar.addAction( config_menu.menuAction() )

    #########################
    def explorer_select( self ):
        explorer_filter = self.get_filter( "Explorer" )
        self.exec_filter( explorer_filter )
        #explorer_filter.set_user_data( self.user_data_vec  )
        #explorer_filter.dialog_exec( self )

    #########################
    def update_explorer_panel( self ):
        data_vec = self.get_filter( "Explorer" ).filter( self.user_data_vec )
        self.explorer_panel.set_sequences( data_vec )
        print( "display data...\t OK ")

    #########################
    def show_strategy_probs( self, checked ):  
        for view in self.explorer_panel.view_vec.values() :
            for model in self.model_vec :
                view.show_strategy_probs( model.name, checked )

    #########################
    def show_action_probs( self, checked ):
        for view in self.explorer_panel.view_vec.values() :
            for model in self.model_vec :
                view.show_individual( model.name, checked )  

    #########################
    def show_user_data( self, checked ):
        for view in self.explorer_panel.view_vec.values() :
                if not view.model_name == "None":
                    view.show_user_data( checked )

    #########################
    def show_option_1( self, checked ):
       
        for view in self.explorer_panel.view_vec.values() :
            for model in self.model_vec :
                name = model.name + "_meta_info"
                view.show_individual( name, checked ) 

    #########################
    def show_option_2( self, checked ):

        for view in self.explorer_panel.view_vec.values() :
            for model in self.model_vec :
                name = model.name + "_meta_info"
                view.show_individual( name, checked ) 



    #########################
    def add_explorer_panel( self ) :
        explorer_panel = Empirical_Panel()
        self.add_explorer_panel_menu( explorer_panel.configuration_vec )        
        return explorer_panel



#####################################################################################################
###############################################  MODEL FITTING ######################################
#####################################################################################################



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
        fitting_filter = self.get_filter( "Model Fitting")
        self.exec_filter( fitting_filter )
    

    #########################
    def model_fitting_select_and_apply( self ):
        fitting_filter = self.get_filter( "Model Fitting")
        res = self.exec_filter( fitting_filter )
        if res == 1 :
            data_vec = fitting_filter.filter( self.user_data_vec  ) #I think it is useless
            print( "model fit user data vec: ", len( data_vec ) )
            self.model_fitting_apply()
            #if fitting_filter.display_checkbox.checkState() == Qt.Checked :
                #self.model_fitting_display()            


    #########################
    def model_fitting_apply( self ):
        print( "model fitting: apply" )
        fitting_filter = self.get_filter( "Model Fitting")
        data_vec = fitting_filter.filter( self.user_data_vec  )
        start = TIME.time()
        self.goodness_of_fit_vec = self.model_fitting_long( data_vec, self.model_vec )
        print("Model fitting: get goodness of fit of ", len(self.model_vec), "models on", len(data_vec), " users in", round(TIME.time() - start,2), "s" )
        self.model_fitting_display()
        #for goodness_of_fit in self.goodness_of_fit_vec :
            #print( goodness_of_fit.name, goodness_of_fit.time,  goodness_of_fit.log_likelihood )


     #########################
    def model_fitting_long( self, user_data_vec, model_vec ):
        self.model_fit.user_data_vec = user_data_vec
        self.model_fit.model_vec = model_vec
        return self.model_fit.run()


    ########################
    def model_fitting_optimize( self ):
        print( "Model fitting optimize" )
        fitting_filter = self.get_filter( "Model Fitting")
        data_vec = fitting_filter.filter( self.user_data_vec  )
        start = TIME.time()
        self.goodness_of_fit_vec  = self.model_fitting_optimize_long( data_vec, self.model_vec )
        print("Model fitting: Search Optimal parameters for ", len(self.model_vec), "models on", len(data_vec), " users in", round(TIME.time() - start,2), "s" )
        
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
        if len( self.goodness_of_fit_vec ) < 1 :
            print("No model fitting has been recently performed... Action \"Diplay\" is ignored ")
            return 0
        
        self.model_results_panel.set_group( self.goodness_of_fit_vec )
        self.explorer_panel.set_model_fitting_sequences( self.goodness_of_fit_vec, self.user_data_vec )

        #goodness_of_fit = self.goodness_of_fit_vec[ 0 ]  #TODO #BUG

        #view_vec = []
        #for view in self.explorer_panel.view_vec.values() :
        #    if view.user_id in goodness_of_fit.user_id:
        #        view_vec.append( view )
        #self.update_views_with_model_fitting( view_vec , goodness_of_fit )

    ########################
    def update_views_with_model_fitting( self, view_vec, goodness_of_fit ): 
        for view in view_vec :
            i = goodness_of_fit.user_id.index( view.user_id )
            user_input = self.user_data_input( view.user_id )
            model_output = goodness_of_fit.output[ i ]
            model_prob   = goodness_of_fit.prob[ i ]
            model_name   = goodness_of_fit.name
            view.set_model_data( model_name, user_input, model_output, model_prob)
            view.set_meta_info(  model_name, user_input, model_output.meta_info_1 )


#####################################################################################################
###############################################    SIMULATIONS  #####################################
#####################################################################################################



    #########################
    def add_model_simulation_component( self ) :
        self.add_model_simulation_menu()

    #########################
    def add_model_simulation_menu( self ):
        simulation_menu = self.menuBar().addMenu( "Model Simulation" )
        act_select           = simulation_menu.addAction( "Select...", self.model_simulation_select )
        act_select_and_apply = simulation_menu.addAction( "Select and Simulate...", self.model_simulation_select_and_apply )
        act_apply            = simulation_menu.addAction( "Simulate", self.model_simulation_apply )
        act_display          = simulation_menu.addAction( "Display", self.model_simulation_display )


    #########################
    def model_simulation_select( self ):
        m_filter = self.get_filter( "Model Simulation")
        self.exec_filter( m_filter )
    

    #########################
    def model_simulation_select_and_apply( self ):
        m_filter = self.get_filter( "Model Simulation")
        res = self.exec_filter( m_filter )
        if res == 1 :
            m_filter.filter( self.user_data_vec  )
            print( " model simulation: select and apply " )
            self.model_simulation_apply()          


    #########################
    def model_simulation_apply( self ):
        print( "model simulation: apply" )
        m_filter = self.get_filter( "Model Simulation")
        data_vec = m_filter.filter( self.user_data_vec  )
        start = TIME.time()
        self.goodness_of_fit_vec = self.model_simulation_long( data_vec, self.model_vec )
        print("Model fitting: get goodness of fit of ", len(self.model_vec), "models on", len(data_vec), " users in", round(TIME.time() - start,2), "s" )
        self.model_simulation_display()
        

     #########################
    def model_simulation_long( self, user_data_vec, model_vec ):
        print( "model simulation long" )


  
   #########################
    def model_simulation_display( self ):
        print("model simulation: display")
        



#####################################################################################################
###############################################    OTHER        #####################################
#####################################################################################################

    ########################
    def user_data_input( self, user_id ):
        for user_data in self.user_data_vec :
            if user_data.id == user_id :
                return user_data.cmd
        return []

    
    #########################
    def export_user_data( self ):
        folder = "./tmp/"
        filename = "user_data.csv"
        start = TIME.time()
        User_Data_Export.write( self.user_data_vec, folder, filename )
        print("export user in data (", round( TIME.time() - start, 2 )  , "s)" )


    ########################
    def export_parameters( self ):
        time_str = TIME.strftime("%Y-%m-%d-%H-%M-%S", TIME.gmtime() )
        for model in self.model_vec :
            parameters = model.get_params()
            path = "./backup/" + time_str + "/"
            filename = model.name + "_model.csv"
            print( path, filename )
            Parameters_Export.write( parameters, path, filename )


    #########################
    def load_hotkeycoach_data( self ) :
        loader = HotkeyCoach_Loader()
        path = './data/hotkeys_formatted_dirty.csv'
        self.load_data( loader, path )
        


    #########################
    def load_user_data( self ):
        loader = User_Data_Loader()
        path = './data/user_data.csv'
        self.load_data( loader, path )


    #########################
    def load_data( self, loader, filename ):
        start = TIME.time()
        user_data_vec = loader.load( filename )
        print( "data of ", len( user_data_vec ), "participants loaded with", loader.name, "in ", round( TIME.time() - start, 2 ), "seconds" )
        self.set_user_data( user_data_vec )

    #########################
    def set_user_data( self, user_data_vec ) :
        self.user_data_vec           = user_data_vec
        self.model_fit_user_data_vec = user_data_vec

    #########################
    def set_config( self, id ) :
        print( "config", id )
        self.explorer_panel.update_configuration( id )



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
    #loader = HotkeyCoach_Loader()
    #users_data = loader.load( path )
    #print( "data of ", len( users_data ), "participants loaded" )

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


    win = Win()
    win.show()
    #win.load_hotkeycoach_data()
    win.load_user_data()
    filter_name = "Explorer"
    win.filters[ filter_name ] = Filter(filter_name, user_min = 0, user_max = 4 )

    #win.set_models( [ ILHP_Model( None, "ILHP" ) ] )
    win.set_models( [ Alpha_Beta_Model( "RW" ), Alpha_Beta_Model( "CK" ) ] )
    filter_name = "Model Fitting"
    win.filters[ filter_name ] = Filter(filter_name, user_min = 0, user_max = 4 )
    win.update_explorer_panel()
    win.model_fitting_apply()
    win.model_fitting_display()
    

    # my_filter = Filter(user_min = 0, user_max = 1, techniques=["traditional", "audio"] ) 
    # print( "before filtering", len(win.user_data_vec) )

    # filtered_users_data = my_filter.filter( win.user_data_vec )
    # print( "data of ",  len( filtered_users_data ), "users once filtered" )
    

    #win.set_user_data( filtered_users_data )
    #win.export_user_data()
    #win.model_fitting_select_and_apply()
    #win.model_fitting_optimize()
    #win.model_fitting_display()
    #panel.set_sequences( filtered_users_data )
    #panel.print_all('./tmp_graphs')
    #panel.print_unit('./tmp_graphs')
    #panel.ensure_view_visible("audio", 4, 2)
    #panel.update_configuration(4)
    #panel.ensure_view_visible("traditional", 3, 2)

    




    #win.show()
    #window.select_command( args.command )


# This is a big fix for PyQt5 on macOS
    # When running a PyQt5 application that is not bundled into a
    # macOS app bundle; the main menu will not be clickable until you
    # switch to another application then switch back.
    # Thus to fix this we execute a quick applescript from the file
    # cmd.scpt which automates the keystroke "Cmd+Tab" twice to swap
    # applications then immediately swap back and set Focus to the main window.
    # if "darwin" in sys.platform:
    #     import please
    #     sourcepath = os.path.dirname(please.__file__)
    #     cmdpath = os.path.join(sourcepath, 'cmd.scpt')
    #     cmd = """osascript {0}""".format(cmdpath)
    #     os.system(cmd)
    #     # os.system(cmd)
    #     mw.viewer.setFocus()


    sys.exit(app.exec_())
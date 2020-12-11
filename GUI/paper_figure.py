import numpy as np
from sklearn.metrics import mean_squared_error
from matplotlib.lines import Line2D
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.backends.backend_qt5agg import NavigationToolbar2QT as NavigationToolbar
import matplotlib.pyplot as plt

from gui_util import *
from util import *
import seaborn as sns
from dataframe_util import *



def ilhp_fitting_figures( fitting_df, path ):
    df = fitting_df.copy()
    df['name'] = df['variant']
    df.loc[ df.variant == '', 'name'] = df.loc[ df.variant == '', 'model' ]
    model_vec = ['T', 'T_I', 'T_H', 'T_P', 'T_I_H', 'T_I_P', 'T_H_P', 'T_I_H_P']
    
    df = df.loc[ df[ 'name' ].isin( model_vec ) ]
    
    #BIC per model and technique
    technique_df = df.groupby( [ 'name', 'technique', 'user_id' ] ).mean()
    technique_df = technique_df.add_suffix('').reset_index()
    plt.figure( figsize=(12, 4), tight_layout=True )
    sns.barplot( x='technique', y = 'BIC', hue="name", palette = model_color, order = ['traditional', 'audio', 'disable'], hue_order = model_vec, data = technique_df )
    plt.ylabel( 'BIC' )
    plt.xlabel( "Technique" )
    plt.legend( framealpha = 0, fontsize='x-small', ncol = len( model_vec ) )
    plt.savefig( path + 'ilhp_technique_bic.pdf', figsize=(12, 4) )

    #BIC per model
    plt.figure( figsize=(12, 4), tight_layout=True )
    plt.rcParams[ 'font.size' ] = 12
    sns.barplot( x='name', y = 'BIC', color= 'name', palette = model_color, order = model_vec, data = technique_df )
    plt.ylabel( 'BIC' )
    plt.xlabel( "Model" )
    #plt.legend( framealpha = 0, fontsize='x-small', ncol = len( model_vec ) )
    plt.savefig( path + 'ilhp_bic.pdf', figsize=(12, 4) )



####################################
def add_mse( mean_df, model_name, col_name, x, y, ax, detail = False ):
    mse_vec = [0,0,0]
    technique_vec = ['traditional', 'audio', 'disable']
    for i, technique in enumerate( technique_vec) :
        tech_df = mean_df.loc[ mean_df.technique_name == technique, : ]
        y_true = tech_df.loc[ tech_df.name == 'Observations', col_name ]
        y_pred = tech_df.loc[ tech_df.name == model_name    , col_name ] 
        mse_vec[ i ] = round( mean_squared_error( y_true, y_pred ), 2 )

    y_true = mean_df.loc[ mean_df.name == 'Observations', col_name ]
    y_pred = mean_df.loc[ mean_df.name == model_name    , col_name ] 
    mse = round( mean_squared_error( y_true, y_pred ) , 1 )
    res_str = 'MSE=' + str( mse )
    if detail:
        res_str += '\n(' + str( mse_vec[0] ) + '; ' + str( mse_vec[1] )  + '-' + str( mse_vec[2] ) + ')' 
    ax.text(x, y, res_str, fontsize=10) #add text 

##########################################################
def ilhp_simulation_figures( simulation_df, users_df, path ):
    
    model_df = pd.concat( [ users_df, simulation_df ], ignore_index=True )
    model_df['hotkey'] = 0
    model_df.loc[ model_df.strategy == Strategy.HOTKEY, 'hotkey' ] = 100
    #model_df['success_plot'] = model_df['success'] * 100
    #model_df['hotkey_success'] = 0
    #model_df.loc[ (model_df.strategy == Strategy.HOTKEY) & (model_df.success == 1), 'hotkey_success' ] = 100
    
    model_df.loc[ model_df.model == 'Observations', 'variant'] = ''
    model_df[ 'name' ] = model_df[ 'variant' ]
    model_df.loc[ model_df.variant == '', 'name'] = model_df[ 'model' ]

    model_vec = ['RW', 'CK', 'RWCK']    
    n_cols = len( model_vec )
    n_rows = 1

    figure = plt.figure( figsize=(16, 4), tight_layout=True )
    ci = None

    for i, model_name in enumerate( model_vec ) :
        
        style_order = [model_name, 'Observations']
        dashes = dict()
        dashes[ model_name ]     = [1,0]
        dashes[ 'Observations' ] = [1, 18 ]

        df = model_df[ (model_df['name'] == model_name) | (model_df['name'] == 'Observations') ]
        mean_df = df.groupby( ['name', 'block_id', 'technique_name'] ).mean()
        mean_df = mean_df.add_suffix('_mean').reset_index()
        
        ax = figure.add_subplot( n_rows, n_cols, i + 1)
        sns.lineplot( x='block_id', y='hotkey', hue="technique_name", style = 'name', dashes = dashes, style_order = style_order, data=df )
        add_mse( mean_df, model_name, 'hotkey_mean' , 0.5, 90, ax )

        plt.title( model_name )
        plt.xlabel( 'Block id' )
        if i == 0 :
            plt.ylabel( 'Hotkey Use (%)' )
        plt.ylim( 0, 100 )
        plt.xlim(0,11)
        ax.legend().remove()


    legend_lines = [Line2D( [0], [0], color = technique_hue['traditional'], lw=1),
             Line2D( [0], [0], color = technique_hue['audio'], lw=1),
             Line2D( [0], [0], color = technique_hue['disable'], lw=1)]
    plt.legend(legend_lines, ['Traditional', 'Audio', 'Disable'], fontsize='x-small', ncol = 3, loc = 'lower right')
    plt.savefig( path + 'ilhp_simulation.pdf', figsize=(16, 4) )

        



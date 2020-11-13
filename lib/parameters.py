from util import *
import csv

class Parameter( object ):

    ##############################
    def __init__( self, _name="", _value=0, _min = 0, _max = 0, _step = 0,  _freedom = Freedom.USER_FREE, _comment = "" ):
        self.name  = _name
        self.value = _value
        self.min   = _min
        self.max   = _max
        self.step  = _step
        self.freedom  = _freedom
        self.comment = _comment

##########################################
#                                        #
#             Parameters                 #
#                                        #
##########################################
class Parameters(dict):

    ###############################
    def __init__( self, name='', path='' ):
        if not path == '': 
            self.load(path)
        self.name = name

    #######################
    def load(self, path):
        if not path:
            return
        with open(path, 'r') as csvFile:
            reader = csv.reader(csvFile, delimiter= ';')
            header = True
            for row in reader:
                if not header:
                    parameter = Parameter()
                    parameter.name    = row[ 0 ]
                    parameter.value   = float( row[1] ) if '.' in row[1] else int( row[1] )
                    parameter.min     = float( row[2] ) if '.' in row[2] else int( row[2] )
                    parameter.max     = float( row[3] ) if '.' in row[3] else int( row[3] )
                    parameter.step    = float( row[4] ) if '.' in row[4] else int( row[4] )
                    parameter.freedom = int( row[5] )
                    parameter.comment = row[ 6 ]
                    self[ parameter.name ] = parameter
                else:
                    header = False
    #########################
    def n( self, freedom_type = Freedom.USER_FREE ):
        res = 0
        for parameter in self.values():
            if parameter.freedom == freedom_type:
                res += 1
        return res


    #########################
    def values_str( self ):
        res = ''
        first = True
        for key, param in self.items():
            if first:
                first = False
            else:
                res += ','
            res += key + ':' + str( param.value )
        return res




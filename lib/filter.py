

##########################################
#                                        #
#               FILTER                   #
#                                        #
##########################################
class Filter(object):

    #####################
    def __init__( self, name = "No name", user_min=0, user_max=41, techniques = ["traditional", "audio", "disable"]) :
        self.name = name
        self.user_min = user_min
        self.user_max = user_max
        self.techniques = techniques
        self.users = [ i for i in range(user_min, user_max+1 ) ]
        self.all_technique_vec = ["traditional", "audio", "disable"]
        self.all_user_vec     = [i for i in range(0, 42) ]
    
    #####################
    def accepted( self, user_data ) :
        if not user_data.id in self.users :
            return False
        if not user_data.technique_name in self.techniques :
            return False
        return True    

    #####################
    def fast_accepted( self, user_data ) :
        if user_data.id < self.user_min :
            return False
        if user_data.id > self.user_max :
            return False
        if not user_data.technique_name in self.techniques :
            return False
        return True
        
    #####################
    def filter( self, user_data_vec ) :
        res = []
        for d in user_data_vec :
            if self.accepted( d ) :
                res.append( d )
        return res
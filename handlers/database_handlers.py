import uuid
from server import db


def add_new_profile(profile):
    """Inserts a single profile int into the database
       Generates a new id for the profile

       profile : the profile to be inserted
    """
    profile['id'] = str(uuid.uuid4())
    conv = _convert_for_insert(profile)
    db.insert(conv)

def get_profile_by_id(uid):
    """Queries the database by uid
    
       uid : uid of the profile to be FileNotFoundError
       
       return: tuple of profile belonging to the uid and a success flag
               flag is false if no profile is found of that uid
    """
    query = ["id = \'{}\'".format(uid)]
    response = db.search(query)
    if len(response) == 0:
        return (None, False)
    return (response[0], True)    


def find_profiles(query):
    """Queries the database

       returns : tuple of list of profile dictionaries and a success flag
                 flag is false if no matches are found.
    """
    conv = _convert_query_for_search(query)
    print(conv)
    reponse = db.search(conv)
    if len(response) == 0:
        return (None, False)
    return (response, True)

def update_profile(uid, new_vals):
    """Updates a profile in the database
       
       uid : uid of entry to update
       new_vals : dictionary of new profile
    """
    cols_values = [(k,v) for k,v in new_vals.items()]
    conds = ["id = \'{}\'".format(uid)]
    db.update(cols_values, conds)


def _convert_for_insert(profile):
    """Converts a profile dictionary into database insert format

        profile : the profile dictionary to be converted

        returns : a list of strings of the values in the profile
    """
    return [ str(value) for _, value in profile.items()]

def _convert_query_for_search(query):
    """Converts a query dictionary into database search format
    
       query : the query dictionary to be converted
       
       returns : a list of strings in query format
    """
    #return ["{0} = \"{1}\"".format(key, value) for key, value in query.items()]
    #TODO - For now just return query of names, nothing else will work
    return "name = \'{}\'".format(query["name"])

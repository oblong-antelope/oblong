import uuid
from database import DBm
from server import db

PROFILE_T_NAME = "profile_db"
PROFILE_T_COLUMNS = [("name",TEXT),("id",INTEGER),("keywords",TEXT)]
PROFILE_T_P_KEY =  ["name"]
TEXT = "text"
INTEGER = "integer"

def initalise():
    db = DBm()
    db.create_table(PROFILE_T_NAME, PROFILE_T_COLUMNS, PROFILE_T_P_KEY)
    return db


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
    query = _convert_id_query(uid)
    response = db.search(query)
    if len(response) == 0:
        return (None, False)
    return (response[0], True)


def find_profiles(query):
    """Queries the database TODO implement other finds

        query : a python dictionary of the format below, which gives the query:
                {'name':string, 'expertise':[string], 'role':string}

       returns : tuple of list of profile dictionaries and a success flag
                 flag is false if no matches are found.
    """
    conv = _convert_query_for_search(query)
    print("Searching for {}".format(conv))
    response = db.search(conv)
    if len(response) == 0:
        return (None, False)
    return (response, True)

def update_profile(uid, new_vals):
    """Updates a profile in the database

       uid : uid of entry to update
       new_vals : dictionary of new profile
    """
    cols_values = _convert_for_update(new_vals)
    conds = _convert_id_query(uid)
    db.update(cols_values, conds)


def _convert_for_insert(profile):
    """Converts a profile dictionary into database insert format

        profile : the profile dictionary to be converted

        returns : a list of strings of the values in the profile
    """
    return [ str(value) for _, value in profile.items()]

def _convert_for_update(vals):
    """Converts a dictionary of new values into tuples

        vals : the values dictionary to be converted

        returns : a list of tuples of the values in vals
    """
    return [(k,v) for k,v in new_vals.items()]

def _convert_id_query(uid):
    """Converts a uid query into query format

        uid : the id to be converted

        returns : a singleton list containing the id query
    """
    return ["id = \'{}\'".format(uid)]

def _convert_query_for_search(query):
    """Converts a query dictionary into database search format

       query : the query dictionary to be converted

       returns : a list of strings in query format
    """
    #return ["{0} = \"{1}\"".format(key, value) for key, value in query.items()]
    #TODO - For now just return query of names, nothing else will work
    return ["name = \'{}\'".format(query["name"])]

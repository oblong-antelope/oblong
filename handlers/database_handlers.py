from server import database as db


def add_profile(profile):
    return


def get_profile(uid):
    """Queries the database by uid
    
       uid : uid of the profile to be FileNotFoundError
       
       return: tuple of profile belonging to the uid and a success flag
               flag is false if no profile is found of that uid
    """
    return ({}, True)    


def find_profiles():
    """Queries the database

       returns : tuple of list of profile dictionaries and a success flag
                 flag is false if no matches are found.
    """
    return ([{}], True)
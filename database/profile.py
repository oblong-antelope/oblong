#!/usr/bin/python
# -*- coding: utf8 -*-
'''Interfaces with the database'''
import json
import pymongo
from database import CLIENT as client, DATABASE as db

def add_profile(profile):
    """We add a profile to the database

        profile : a dictionary representing one persons profile

        returns : the uuid of the object assigned by the database
    """
    profiles = db.profiles
    return profiles.insert_one(profile).inserted_id

def get_profile_by_id(post_id):
    """Getting a profile from the database by id explicitly
    
        post_id : the uuid of the profile assigned by the database on add
        
        returns : the stored profile object
    """
    profiles = db.profiles
    return profiles.find_one({"_id": post_id})
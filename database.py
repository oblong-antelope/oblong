#!/usr/bin/python
# -*- coding: utf8 -*-
'''Interfaces with the database'''
import json
import os
import config
import pymongo

class Database:
    """A class to represent the database"""

    client = {}
    db = {}

    def __init__(self, client=None, db=None):
        """Initialisation code, client and db will be none except for testing
        
            client : a client which will be passed in for testing
            db : a database of collections will be passed in for testin
        """
        if client is None and db is None:
            self._setup()
            return

        if client is not None:
            self.client = client
        
        if db is not None:
            self.db = db
        

    def add_profile(self, profile):
        """We add a profile to the database

            profile : a dictionary representing one persons profile

            returns : the uuid of the object assigned by the database
        """
        profiles = self.db.profiles
        return profiles.insert_one(profile).inserted_id

    def get_profile_by_id(self, post_id):
        """Getting a profile from the database by id explicitly
        
            post_id : the uuid of the profile assigned by the database on add
            
            returns : the stored profile object
        """
        profiles = self.db.profiles
        return profiles.find_one({"_id": post_id})

    def _setup(self):
        """Initates the database class
           Parses the database configuration
           Tries to find the client and access the database
        """
        cf = config.get_database_config()
        address = cf['address'] if ('address' in cf) else 'localhost'
        port = cf['port'] if ('port' in cf) else '27017'
        db_name = cf['database'] if ('database' in cf) else 'test'
        self.client = self._connect(address, int(port))
        self.db = self._database(db_name)

    def _connect(self, address, port):
        """Takes an address and port and attempts to connect to the Database Server"""
        try:
            conn = pymongo.MongoClient(address, port)
            return conn
        except pymongo.errors.ConnectionFailure as arg:
            print("Could not connect to server: %s" % arg)
        

    def _database(self, name):
        """Takes the database name and attempts to return the database object"""
        try:
            database = self.client[name]
            return database
        except pymongo.errors.InvalidName as arg:
            print("Could not find database: %s" % arg)

    def __del__(self):
        self.client.close()
        


	
if __name__ == "__main__":
    test = Database()

#!/usr/bin/python
# -*- coding: utf8 -*-
'''Connects with the database'''
import json
import os
import config
import pymongo
 
def setup():
    """Initates the database class
        Parses the database configuration
        Tries to find the client and access the database
    """
    cf = config.get_database_config()
    address = cf['address'] if ('address' in cf) else 'localhost'
    port = cf['port'] if ('port' in cf) else '27017'
    db_name = cf['database'] if ('database' in cf) else 'test'
    client = _connect(address, int(port))
    db = _database(db_name, client)
    return client, db

def _connect(address, port):
    """Takes an address and port and attempts to connect to the Database Server"""
    try:
        conn = pymongo.MongoClient(address, port)
        return conn
    except pymongo.errors.ConnectionFailure as arg:
        print("Could not connect to server: %s" % arg)
    

def _database(name, client):
    """Takes the database name and attempts to return the database object"""
    try:
        database = client[name]
        return database
    except pymongo.errors.InvalidName as arg:
        print("Could not find database: %s" % arg)
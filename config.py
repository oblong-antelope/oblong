#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Parses the configration file'''
import configparser

CONFIG_ADDRESS = 'config.ini'

config = {}

def get_config():
    """Takes the configuration file specified in CONFIG_ADDRESS
        and parses it into a config dictionary.
    """
    cf = configparser.ConfigParser()
    try:
        cf.read(CONFIG_ADDRESS)
    except:
        return
    
    sections = cf.sections()

    for section in sections:
        fields = cf.options(section)
        subconfig = {}
        for field in fields:
            subconfig[field] = cf.get(section, field)
        config[section] = subconfig

def get_server_config():
    """Returns the Server configurations"""
    if config == {}:
        get_config()
    return config['Server']

def get_database_config():
    """Returns the Database configurations"""
    if config == {}:
        get_config()
    return config['Database']
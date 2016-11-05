#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Scraper Api handlers.'''#
import json
import uuid
import extract_expertise
from flask import request, abort

def submit_data():
    if request.is_json:
        data = request.get_json()
        try:
            title = data['title']
            authors = data['authors']
            date = data['date']
            PROFILES = extract_expertise.augment_profile(data, PROFILES)
            
        except:
            return 'paper should have fields: title, authors, date', 415
    else:
        return 'JSON, please.', 415
      
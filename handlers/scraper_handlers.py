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
      
def scrape_symplectic():
    #gather data from symplectic using the APIs, returns canned Toni responses atm.
    for paper in papers:
        extract_expertise.augment_profile(paper)
    for paper in papers3:
        extract_expertise.augment_profile(paper)

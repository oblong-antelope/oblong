#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Scraper Api handlers.'''#
import json
import uuid
import extract_expertise as ee
from flask import request, abort

def submit_data():
    if request.is_json:
        paper = request.get_json()
        try:
            title = paper['title']
            authors = paper['authors']
            date = paper['date']
            ee.augment_profile(paper)
        except:
            return 'paper should have fields: title, authors, date', 415
    else:
        return 'JSON, please.', 415

def scrape_symplectic():
    #gather data from symplectic using the APIs, returns canned Toni responses atm.
    for paper in papers:
        ee.augment_profile(paper)
    for paper in papers3:
        ee.augment_profile(paper)

#Francesca Toni's publications from 2016
papers = [ {"title"   : "Argumentation-based multi-agent decision making with privacy preserved",
            "authors" : "Y. Gao, F. Toni, H. Wang, and F. Xu",
            "date"    : "2016"},
           {"title"   : "On the interplay between games, argumentation and dialogues",
            "authors" : "X. Fan and F. Toni",
            "date"    : "2016"},
           {"title"   : "Discontinuity-free decision support with quantitative argumentation debates",
            "authors" : "A. Rago, F. Toni, M. Aurisicchio, and P. Baroni",
            "date"    : "2016"},
           {"title"   : "Abstract argumentation for case-based reasoning",
            "authors" : "K. Cyras, K. Satoh, and F. Toni",
            "date"    : "2016"},
           {"title"   : "ABA+: assumption-based argumentation with preferences",
            "authors" : "K. Cyras and F. Toni",
            "date"    : "2016"},
           {"title"   : "Properties of ABA+ for non-monotonic reasoning",
            "authors" : "K. Cyras and F. Toni",
            "date"    : "2016"},
           {"title"   : "Smarter electricity and argumentation theory",
            "authors" : "M. Makriyiannis, T. Lung, R. Craven, F. Toni, and J. Kelly",
            "date"    : "2016"},
           {"title"   : "Online Argumentation-Based Platform for Recommending Medical Literature",
            "authors" : "A. Mocanu, X. Fan, F. Toni, M. Williams, and J. Chen",
            "date"    : "2016"},
           {"title"   : "Justifying Answer Sets using Argumentation",
            "authors" : "C. Schulz, F. Toni",
            "date"    : "2016"},
           {"title"   : "Argument Graphs and Assumption-Based Argumentation",
            "authors" : "R. Craven and F. Toni",
            "date"    : "2016"}
         ]


papers3 = [ {"title"   : "Argumentation-based multi-agent decision making with privacy preserved",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "On the interplay between games, argumentation and dialogues",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Discontinuity-free decision support with quantitative argumentation debates",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Abstract argumentation for case-based reasoning",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "ABA+: assumption-based argumentation with preferences",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Properties of ABA+ for non-monotonic reasoning",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Smarter electricity and argumentation theory",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Online Argumentation-Based Platform for Recommending Medical Literature",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Justifying Answer Sets using Argumentation",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Argument Graphs and Assumption-Based Argumentation",
            "authors" : "F. Toni",
            "date"    : "2016"}
         ]
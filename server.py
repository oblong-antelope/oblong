#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Webserver to handle the back end of Oblong.'''
from collections import defaultdict
import json
import os
import uuid
import extract_expertise
import config
from handlers import profile_handlers, scraper_handlers
from flask import Flask, request, abort
from flask_cors import CORS



PROFILES = { \
            'Dr. Tim Timson' : { 'name': 'Dr. Tim Timson'
                , 'department': 'Department of Tim Research'
                , 'email': 'tim@timresearch.ic.ac.uk'
                , 'awards':
                    [ 'Tim Medal 2009'
                    , 'Nobel Prize for Tim Research'
                    ]
                , 'papers':
                    [ 'https://arXiv.org/abs/1024.01232'
                    , 'https://arXiv.org/abs/1024.01233'
                    , 'https://arXiv.org/abs/1024.01234'
                    , 'https://arXiv.org/abs/1024.01235'
                    , 'https://arXiv.org/abs/1024.01236'
                    , 'https://arXiv.org/abs/1024.01237'
                    , 'https://arXiv.org/abs/1024.01238'
                    , 'https://arXiv.org/abs/1024.01239'
                    , 'https://arXiv.org/abs/1024.01240'
                    ]
                , 'keywords':
                    { 'learning': 2546
                    , 'machine': 1000
                    , 'ai': 1000
                    , 'Tim': 40
                    }
                }
        , 'Dr. Timonthy Timsworth' : { 'name': 'Dr. Timothy Timsworth'
                , 'department': 'Department of Tim Rights'
                , 'email': 'tim@timrights.ic.ac.uk'
                , 'awards':
                    [ 'Employee of the month June 2011'
                    , "World's best dad"
                    ]
                , 'papers':
                    [ 'https://arXiv.org/abs/1024.01232'
                    , 'https://arXiv.org/abs/1024.01233'
                    , 'https://arXiv.org/abs/1024.01234'
                    , 'https://arXiv.org/abs/1024.01235'
                    , 'https://arXiv.org/abs/1024.01236'
                    ]
                , 'keywords':
                    { 'learning': 2546
                    , 'machine': 1000
                    , 'ai': 1000
                    , 'Tim': 40
                    }
                }
        }

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
config = {}

@app.route('/api/query/submit', methods=['POST'])
def submit_query():
    return profile_handlers.submit_query()

@app.route('/api/query/<query_id>')
def get_query(query_id):
    return profile_handlers.get_query()

@app.route('/api/person/<person_id>/summary')
def person_summary(person_id):
    return profile_handlers.person_summary(person_id)

@app.route('/api/person/<person_id>/full')
def person_full(person_id):
    return profile_handlers.person_full(person_id)


@app.route('/api/submit_paper', methods=['POST'])
def submit_data():
    return scraper_handlers.submit_data()
      

if __name__ == '__main__':
    config = config.get_server_config()
    heroku_port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=heroku_port)

#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Webserver to handle the back end of Oblong.'''
import json
import os
import uuid
import config
from handlers import profile_handlers, scraper_handlers, database_handlers
from flask import Flask
from flask_cors import CORS

# Init Flask App
app = Flask(__name__)

# Add CORS headers to all responses/ requests
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# Parse the configurations
cfg = config.get_server_config()

# Init the database
database_handlers.initialise()

# TODO WHILE THE SCRAPER IS NOT IN, USE THE CANNED responses
scraper_handlers.scrape_symplectic()

# ------------ PROFILE API ROUTES -----------------
@app.route('/api/query/submit', methods=['POST'])
def submit_query():
    return profile_handlers.submit_query()

@app.route('/api/query/<query_id>')
def get_query(query_id):
    return profile_handlers.get_query(query_id)

@app.route('/api/person/<person_id>/summary')
def person_summary(person_id):
    return profile_handlers.person_summary(person_id)

@app.route('/api/person/<person_id>/full')
def person_full(person_id):
    return profile_handlers.person_full(person_id)

# ------------ SCRAPER API ROUTES -----------------
@app.route('/api/submit_paper', methods=['POST'])
def submit_data():
    return scraper_handlers.submit_data()


if __name__ == '__main__':
    heroku_port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=heroku_port)

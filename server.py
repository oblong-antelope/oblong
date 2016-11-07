#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Webserver to handle the back end of Oblong.'''
from collections import defaultdict
import json
import os
import uuid
import extract_expertise
import config
from database import DBm
from handlers import profile_handlers, scraper_handlers
from flask import Flask, request, abort
from flask_cors import CORS

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
cfg = {}
database = DBm()
database.create_table("profile_db", [("name","text"),("id","integer"),("keywords","text")], ["name"])

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

@app.route('/api/submit_paper', methods=['POST'])
def submit_data():
    return scraper_handlers.submit_data()
      

if __name__ == '__main__':
    cfg = config.get_server_config()
    heroku_port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=heroku_port)
    

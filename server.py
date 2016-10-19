#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Webserver to handle the back end of Oblong.'''
from collections import defaultdict
import json
import uuid
from flask import Flask, request

app = Flask(__name__)

queries = {}

@app.route('/api/query/submit', methods=['POST'])
def submit_query():
    if request.is_json:
        json = defaultdict(lambda: None)
        json.update(request.get_json())
    else:
        return 'JSON, please.', 415
    uuid = str(uuid.uuid4())
    if (json['speciality'] == 'artificial intelligence' 
        and json['role'] == 'supervisor'):
        queries[uuid] = [ {
            'name': 'Dr. Tim Timson',
            'department': 'Department of Tim Research',
            'info': '/api/person/<key>'
        }, {
            'name': 'Dr. Timothy Timsworth',
            'department': 'Department of Tim Rights',
            'info': '/api/person/<key>'
        } ]
    else:
        queries[uuid] = []
    response = {
        'success': True,
        'results': '/api/query/{}'.format(uuid)
    }
    return response

@app.route('/api/query/<query_id>')
def get_query(query_id):
    return json.dumps(queries[uuid])

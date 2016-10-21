#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Webserver to handle the back end of Oblong.'''
from collections import defaultdict
import json
import uuid
from flask import Flask, request, abort
from flask_cors import CORS

CANNED_RESPONSES =\
        [ ( lambda j: (j['expertise'].lower() == 'artificial intelligence'
                       and j['role'].lower() == 'supervisor')
          , [ { 'name': 'Dr. Tim Timson'
              , 'department': 'Department of Tim Research'
              , 'email': 'tim@timresearch.ic.ac.uk'
              , 'info': '/api/person/<key>'
              } 
            , { 'name': 'Dr. Timothy Timsworth'
              , 'department': 'Department of Tim Rights'
              , 'email': 'tim@timrights.ic.ac.uk'
              , 'info': '/api/person/<key>'
              } 
            ]
          )
        ]

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
queries = {}

@app.route('/api/query/submit', methods=['POST'])
def submit_query():
    if request.is_json:
        request_json = defaultdict(lambda: '')
        request_json.update(request.get_json())
    else:
        return 'JSON, please.', 415
    query_id = str(uuid.uuid4())
    for cond, value in CANNED_RESPONSES:
        if cond(request_json):
            queries[query_id] = value
    if queries.get(query_id, None) is None:
        queries[query_id] = []
    response = {
        'success': True,
        'results': '/api/query/{}'.format(query_id)
    }
    return json.dumps(response)

@app.route('/api/query/<query_id>')
def get_query(query_id):
    if query_id in queries:
        return json.dumps(queries[query_id])
    else:
        abort(404)

if __name__ == '__main__':
    app.run()

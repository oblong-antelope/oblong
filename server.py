#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Webserver to handle the back end of Oblong.'''
from collections import defaultdict
import json
import os
import uuid
import extract_expertise
from flask import Flask, request, abort
from flask_cors import CORS



PROFILES = {}

app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})
queries = {}

@app.route('/api/query/submit', methods=['POST'])
def submit_query():
    CANNED_RESPONSES =\
            [ (lambda j: (j['expertise'].lower() == 'artificial intelligence'
                          and j['role'].lower() == 'supervisor')
              , [0, 1])
            , (lambda j: j['expertise'].lower() == 'reinforcement learning'
              , [1])

            ]

    if request.is_json:
        request_json = defaultdict(lambda: '')
        request_json.update(request.get_json())
    else:
        return 'JSON, please.', 415
    query_id = str(uuid.uuid4())
    for cond, values in CANNED_RESPONSES:
        if cond(request_json):
            resp = []
            for i in values:
                resp.append({k: PEOPLE[i][k] for k in
                             ('name', 'email', 'department')})
                person = '/api/person/{}/'.format(i)
                resp[-1]['research_summary'] = person + 'summary'
                resp[-1]['full_profile'] = person + 'full'
            queries[query_id] = resp
            break
    if query_id not in queries:
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

@app.route('/api/person/<int:person_id>/summary')
def person_summary(person_id):
    if 0 <= person_id < len(PEOPLE):
        person = PEOPLE[person_id]
        resp = { 'papers': len(person['papers'])
               , 'keywords': sorted(list(person['keywords'].keys()))
               , 'recent_paper': person['papers'][0]
               , 'full_profile': '/api/person/{}/full'.format(person_id)
               }
        return json.dumps(resp)
    else:
        abort(404)

@app.route('/api/person/<int:person_id>/full')
def person_full(person_id):
    if 0 <= person_id < len(PEOPLE):
        return json.dumps(PEOPLE[person_id])
    else:
        abort(404)


@app.route('/api/submit_paper', methods=['POST'])
def submit_data():
    if request.is_json:
        data = request.get_json()
        try:
            title = data['title']
            authors = data['authors']
            date = data['date']
            PROFILES = extract_expertise.augment_author(data, PROFILES)
            
        except:
            return 'paper should have fields: title, authors, date', 415
    else:
        return 'JSON, please.', 415
      

if __name__ == '__main__':
    heroku_port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=heroku_port)

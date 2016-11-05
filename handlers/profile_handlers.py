#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Profile Api handlers.'''#
import json
import uuid
import extract_expertise
from flask import request, abort

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

QUERIES = {}

def submit_query():
    # CANNED_RESPONSES =\
    #         [ (lambda j: (j['expertise'].lower() == 'artificial intelligence'
    #                       and j['role'].lower() == 'supervisor')
    #           , [0, 1])
    #         , (lambda j: j['expertise'].lower() == 'reinforcement learning'
    #           , [1])

    #         ]

    if request.is_json:
        request_json = defaultdict(lambda: '')
        request_json.update(request.get_json())
    else:
        return 'JSON, please.', 415
    query_id = str(uuid.uuid4())

    name = request_json['name']

    profile = PROFILES[name]
    
    person = '/api/person/{}/'.format(name)
    profile['research_summary'] = person + 'summary'
    profile['full_profile'] = person + 'full'

    QUERIES[query_id] = [profile]
    
    # for cond, values in CANNED_RESPONSES:
    #     if cond(request_json):
    #         resp = []
    #         for i in values:
    #             resp.append({k: PROFILES[i][k] for k in
    #                          ('name', 'email', 'department')})
    #             person = '/api/person/{}/'.format(i)
    #         QUERIES[query_id] = resp
    #         break
    if query_id not in QUERIES:
        QUERIES[query_id] = []
    response = {
        'success': True,
        'results': '/api/query/{}'.format(query_id)
    }
    return json.dumps(response)

def get_query(query_id):
    if query_id in QUERIES:
        return json.dumps(QUERIES[query_id])
    else:
        abort(404)

def person_summary(person_id):
    if person_id in PROFILES:
    # if 0 <= person_id < len(QUERIES):
        person = PROFILES[person_id]
        resp = { 'papers': len(person['papers'])
               , 'keywords': sorted(list(person['keywords'].keys()))
               , 'recent_paper': person['papers'][0]
               , 'full_profile': '/api/person/{}/full'.format(person_id)
               }
        return json.dumps(resp)
    else:
        abort(404)

def person_full(person_id):
    if person_id in PROFILES:
    # if 0 <= person_id < len(QUERIES):
        return json.dumps(PROFILES[person_id])
    else:
        abort(404)

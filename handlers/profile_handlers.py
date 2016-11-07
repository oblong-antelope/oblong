#!/usr/bin/env python3
# -*- encoding: utf-8 -*-
'''Profile Api handlers.'''#
import json
import uuid
#import extract_expertise
import functools
import editdistance
from flask import request, abort

PROFILES = {}

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

    person = '/api/person/{}/'.format(name)

    try: #inside try block for the moment, i'm not sure if field is provided by the js
        field = request_json['field'] #field of research
        results = get_ordered_results(PROFILES, name, field)
        profile = results[0]
    except:
        profile = PROFILES[name]

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

def get_ordered_results(profiles, name, field):
    """Gets an ordered list of query results.

       profiles: the profile list to sort
       name: query name
       field: query field

       returns: an ordered list of query results
    """
    results = profiles.values() #extract profiles
    rank = functools.partial(get_rank, name=name, field=field) #partially apply ranking function to query
    return sorted(results, key=rank, reverse=True) #sort profiles

def get_rank(name, field, profile, name_weight=100):
    """Ranking function that gives a profile a rank on how well
       it matches a given query. Uses Levenshtein distance to compare
       name to query name.

       name: query name
       field: query field
       profile: profile to rank
       name_weight: scaling factor for the name comparison (100 for the moment)

       returns: an int value that represents how well a profile
                matches the query
    """
    name_rank = 0 if name == '' else -name_weight*editdistance.eval(name, profile['name'])
    try:
        field_rank = profile['keywords'][field]
    except:
        field_rank = 0
    return field_rank + name_rank

"""Webserver to allow queries to user profiles."""
from collections import defaultdict
import json
import os

from flask import Flask, abort, request
from flask_cors import CORS

from . import database as db
from . import profiling


# Init Flask App
app = Flask(__name__)

# Add CORS headers to all responses/ requests
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

# ------------ PROFILE API ROUTES -----------------
@app.route('/api/query/submit', methods=['POST'])
def submit_query():
    """Submits a query.
    
    When a query is made, a query object is created, accessible via
    ``/api/query/<query_id>``. Then the profile database is searched
    and a list of results is hosted at that endpoint.

    Currently, this method only searches for users by name, and only
    returns exact matches.

    In the future, this will create a task via something like `Celery`_
    and dispatch it.

    .. _Celery: http://docs.celeryproject.org/

    """
    if request.is_json:
        request_json = defaultdict(lambda: '')
        request_json.update(request.get_json())
    else:
        response = { 'error_code': 415
                   , 'message': 'JSON, please.' 
                   }
        return json.dumps('JSON, please.'), 415
 
    q = db.Query(status="in_progress")
    db.session.add(q)
    db.session.commit()

    profiling.fulfill_query(q, request_json['name'], request_json['expertise'])
        
    response = { 'success': True
               , 'results': '/api/query/{}'.format(q.id)
               }
    return json.dumps(response), 202

@app.route('/api/query/<query_id>')
def get_query(query_id):
    """Retreives a query from the database.
    
    The response will be a JSON object ``r`` such that ``r["status"]``
    is one of ``"in_progress"``, ``"finished"`` or ``"deleted"``. If 
    ``r["status"] == "finished"``, then ``r["results"]`` will be a
    list containing names and profile links for profiles that match the
    query.

    Args:
        query_id (str): The unique id of the query to be retrieved.

    """
    q = db.Query.query.get(query_id)
    if not q:
        abort(404)
    else:
        result = {'status': q.status}
        profiles = []
        for profile in q.results:
            uri_stub = '/api/person/{id:d}'.format(id=profile.id)
            profiles.append({ 'name': profile.name
                            , 'research_summary': uri_stub + '/summary'
                            , 'full_profile': uri_stub + '/full'
                            })
        if q.status == 'finished':
            result['results'] = profiles
        return json.dumps(result)

@app.route('/api/person/<person_id>/summary')
def person_summary(person_id):
    """Retrieves a summary of a person's research.
    
    The return summary contains the number of papers, keywords (as a
    list without frequency data), the title of a recent paper and a 
    link to the full profile.

    Args:
        person_id (str): The unique id of the person to retrieve a
            profile summary of.

    """
    profile = db.Profile.query.get(person_id)
    if not profile:
        abort(404)
    else:
        uri_stub = '/api/profile/{id:d}'.format(id=profile.id)
        result = { 'papers': len(profile.papers) if profile.papers else 0
                 , 'keywords': sorted(list(profile.keywords.keys()))
                 , 'full_profile': uri_stub + '/full'
                 }
        if profile.papers: result['recent_paper'] = profile.papers[0] 
        return json.dumps(result)

@app.route('/api/person/<person_id>/full')
def person_full(person_id):
    """Retrieves the full profile of a person.

    The full profile contains name, keywords as a dictionary of words
    to frequencies, a list of paper titles and a list of awards.

    Args:
        person_id (str): The unique id of the person to retrieve a
            profile summary of.

    """
    profile = db.Profile.query.get(person_id)
    if not profile:
        abort(404)
    else:
        result = { 'name': profile.name
                 , 'keywords': dict(profile.keywords)
                 , 'papers': profile.papers
                 , 'awards': profile.awards
                 }
        return json.dumps(result)

@app.route('/api/keywords/<keyword>')
def get_keyword(keyword):
    keyword = db.Keyword.query.filter_by(name=keyword).one_or_none()
    if not keyword:
        abort(404)
    else:
        profiles = []
        for profile in keyword.profiles:
            uri_stub = '/api/person/{id:d}'.format(id=profile.id)
            profiles.append({ 'name': profile.name
                            , 'research_summary': uri_stub + '/summary'
                            , 'full_profile': uri_stub + '/full'
                            })
        result = { 'name': keyword.name
                 , 'profiles': profiles
                 }
        return json.dumps(result)

# ------------ SCRAPER API ROUTES -----------------
@app.route('/api/submit_paper', methods=['POST'])
def submit_data():
    if request.is_json:
        paper = request.get_json()
        profiling.update_authors_profiles(
                paper['title'], 
                paper['authors'], 
                paper['date']) 
        response = { 'success': True }
        return json.dumps(response), 201
    else:
        response = { 'error_code': 415
                   , 'message': 'JSON, please.' 
                   }
        return json.dumps(response), 415

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Ensures that ``db.session`` is closed at the end of each request."""
    db.session.remove()

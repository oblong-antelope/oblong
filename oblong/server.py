"""Webserver to allow queries to user profiles."""
from collections import defaultdict
import json
import os

from flask import Flask, abort, request, url_for
from flask_cors import CORS

from . import database as db
from . import profiling


# Init Flask App
app = Flask(__name__)

# Add CORS headers to all responses/ requests
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def top_keywords(profile):
    # take up to five of the highest-ranked keywords
    keywords = sorted(tuple(profile.keywords.items()),
                      key=lambda p: p[1], reverse=True)[:5]
    return tuple(zip(*keywords))[0]


# ------------ PROFILE API ROUTES -----------------
@app.route('/api/query/submit', methods=['POST'])
def _submit_query():
    return "This endpoint is obsolete. Use POST:/api/queries", 404

@app.route('/api/query/<uid>')
def _get_query(uid):
    return "This endpoint is obsolete. Use /api/queries/<uid>.", 404

@app.route('/api/person/<person_id>/summary')
def _person_summary(person_id):
    return "This end point is obsolete. Use /api/people/<uid>.", 404

@app.route('/api/person/<person_id>/full')
def _person_full(person_id):
    return "This end point is obsolete. Use /api/people/<uid>.", 404


@app.route('/api/queries', methods=['POST'])
def queries():
    """Submits a query.
    
    When a query is made, a query object is created, accessible via
    ``/api/queries/<uid>``. Then the profile database is searched
    and a list of results is hosted at that endpoint.

    Currently, this method only searches for users by name, and only
    returns exact matches.

    In the future, this will create a task via something like `Celery`_
    and dispatch it.

    .. _Celery: http://docs.celeryproject.org/

    """
    q = db.Query(status="in_progress")
    db.session.add(q)
    db.session.commit()

    profiling.fulfill_query(q, request.get_data().decode('utf-8'))
        
    response = { 'success': True
               , 'results': url_for('query', uid=q.id)
               }
    return json.dumps(response), 202

@app.route('/api/queries/<uid>')
def query(uid):
    """Retreives a query from the database.
    
    The response will be a JSON object ``r`` such that ``r["status"]``
    is one of ``"in_progress"``, ``"finished"`` or ``"deleted"``. If 
    ``r["status"] == "finished"``, then ``r["results"]`` will be a
    list containing names and profile links for profiles that match the
    query.

    Args:
        uid (str): The unique id of the query to be retrieved.

    """
    q = db.Query.query.get(uid)
    if not q:
        abort(404)
    else:
        result = {'status': q.status}
        if q.status == 'finished':
            result['results'] = [{ 'name': profile.name
                                 , 'email': profile.email
                                 , 'faculty': profile.faculty
                                 , 'department': profile.department
                                 , 'keywords': top_keywords(profile)
                                 , 'link': url_for('profile', uid=profile.id)
                                 } for profile in q.results]
        return json.dumps(result)

@app.route('/api/people')
def profiles():
    try:
        page = int(request.args.get('page', 0))
        size = int(request.args.get('page_size', 25))
    except ValueError:
        response = { 'error_code': 415
                   , 'message': 'page and page_size must be uint' 
                   }
        return json.dumps(response), 415

    count = db.Profile.query.count()
    if not count:
        return json.dumps({"count": count})
    else:
        profiles = db.Profile.query.slice(page * size, (page + 1) * size)
        result = { 'count': count }
        if page > 0:
            result['previous_page'] = url_for('profiles', page=page - 1,
                                              page_size=size)
        if (page + 1) * size < count:
            result['next_page'] = url_for('profiles', page=page + 1,
                                          page_size=size)

        result['this_page'] = [{ 'name': profile.name
                               , 'faculty': profile.faculty
                               , 'department': profile.department
                               , 'keywords': top_keywords(profile)
                               , 'link': url_for('profile', uid=profile.id)
                               } for profile in profiles]

        return json.dumps(result)

@app.route('/api/people/<uid>')
def profile(uid):
    """Retrieves the full profile of a person.

    The full profile contains name, keywords as a dictionary of words
    to frequencies, a list of publications and so on and so forth.

    Args:
        uid (str): The unique id of the person.

    """
    profile = db.Profile.query.get(uid)
    if not profile:
        abort(404)
    else:
        result = {}
        for attribute in ['name', 'email', 'faculty', 'department', 'campus',
                'building', 'room', 'website']:
            result[attribute] = getattr(profile, attribute)

        result['keywords'] = dict(profile.keywords)

        result['publications'] = [url_for('publication', uid=pub.id) for pub in 
                                  profile.publications]

        return json.dumps(result)

@app.route('/api/keywords/<keyword>')
def keyword(keyword):
    keyword = db.Keyword.query.filter_by(name=keyword).one_or_none()
    if not keyword:
        abort(404)
    else:
        result = { 'name': keyword.name
                 , 'profiles': [{ 'name': profile.name
                                , 'email': profile.name
                                , 'faculty': profile.faculty
                                , 'department': profile.department
                                , 'link': url_for('profile', uid=profile.id)
                                } for profile in keyword.profiles]
                 }
        return json.dumps(result)

@app.route('/api/publications', methods=['GET', 'POST'])
def publications():
    if request.method == 'GET':
        try:
            page = int(request.args.get('page', 0))
            size = int(request.args.get('page_size', 25))
        except ValueError:
            response = { 'error_code': 415
                       , 'message': 'page and page_size must be uint' 
                       }
            return json.dumps(response), 415

        count = db.Publication.query.count()
        if not count:
            return json.dumps({"count": count})
        else:
            result = { 'count': count }
            if page > 0:
                result['previous_page'] = url_for('publications', page=page - 1,
                                                  page_size=size)
            if (page + 1) * size < count:
                result['next_page'] = url_for('publications', page=page + 1,
                                              page_size=size)

            pubs = db.Publication.query.slice(page * size, (page + 1) * size)
            result['this_page'] = [{ 'title': pub.title
                                   , 'date': str(pub.date)
                                   , 'authors': [url_for('profile', uid=a.id)
                                                 for a in pub.authors]
                                   , 'link': url_for('publication', uid=pub.id)
                                   } for pub in pubs]

            return json.dumps(result)

    elif request.method == 'POST':
        if request.is_json:
            paper = request.get_json()
            profiles = profiling.update_authors_profiles(
                    paper['title'], 
                    paper['abstract'],
                    paper['authors'], 
                    paper['date']) 
            response = { 'success': True }
            return json.dumps(response), 201
        else:
            response = { 'error_code': 415
                       , 'message': 'JSON, please.' 
                       }
            return json.dumps(response), 415

@app.route('/api/publications/<uid>')
def publication(uid):
    pub = db.Publication.query.get(uid)
    if not pub:
        abort(404)
    else:
        result = { 'title': pub.title
                 , 'abstract': pub.abstract
                 , 'date': str(pub.date)
                 , 'authors': [{ 'name': author.name
                               , 'email': author.email
                               , 'faculty': author.faculty
                               , 'department': author.department
                               , 'keywords': top_keywords(author)
                               , 'link': url_for('profile', uid=author.id)
                               } for author in pub.authors]
                 }
        return json.dumps(result)

@app.teardown_appcontext
def shutdown_session(exception=None):
    """Ensures that ``db.session`` is closed at the end of each request."""
    db.session.remove()

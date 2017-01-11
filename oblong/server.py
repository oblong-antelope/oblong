"""Webserver to allow queries to user profiles."""
from collections import defaultdict
from itertools import repeat
import json
import os

from flask import Flask, abort, request, url_for
from flask_cors import CORS

from . import database as db
from . import profiling

OKAY = 200
CREATED = 201
NOT_FOUND = 404
BAD_REQUEST = 400

def error_message(code, message):
    response = { 'error_code': code
               , 'message': message
               }
    return json.dumps(response), code

def obsolete(new_api, method='GET'):
    def decorator(f):
        """This function is obsolete"""
        def wrapper(*args, **kwargs):
            m = ('This endpoint is obsolete. Use {}:{}'
                 .format(request.method, new_api))
            return error_message(NOT_FOUND, m)
        wrapper.__name__ = f.__name__
        wrapper.__wrapped__ = f
        return wrapper
    return decorator

DEFAULT_PAGE_SIZE = 10

# Init Flask App
app = Flask(__name__)

# Add CORS headers to all responses/ requests
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})


def top_keywords(profile):
    # take up to five of the highest-ranked keywords
    app.logger.info("Sorting keywords for profile {}".format(profile.id))
    keywords = sorted(tuple(profile.keywords.items()),
                      key=lambda p: p[1], reverse=True)[:5]
    if keywords:
        return tuple(zip(*keywords))[0]
    else:
        return ()


# ------------ PROFILE API ROUTES -----------------
@app.route('/api/query/submit', methods=['POST'])
@obsolete('/api/queries')
def _submit_query(): pass

@app.route('/api/query/<uid>')
@obsolete('/api/queries/<uid>')
def _get_query(uid): pass

@app.route('/api/person/<person_id>/summary')
@obsolete('/api/people/<uid>')
def _person_summary(person_id): pass

@app.route('/api/person/<person_id>/full')
@obsolete('/api/people/<uid>')
def _person_full(person_id): pass

@app.route('/api/queries/<uid>')
@obsolete('/api/queries')
def _query(uid): pass


@app.route('/api/queries', methods=['POST'])
def queries():
    """Submits a query.
    
    When a query is made, a query object is created, accessible via
    ``/api/queries/<uid>``. Then the profile database is searched
    and a list of results is hosted at that endpoint.

    """
    try:
        page = int(request.args.get('page', 0))
        size = int(request.args.get('page_size', DEFAULT_PAGE_SIZE))
    except ValueError:
        return error_message(BAD_REQUEST, 'page and page_size must be uint')

    count, profiles = profiling.fulfill_query(
            request.get_data().decode('utf-8'),
            page_no=page,
            page_size=size
            )
    
    response = [{ 'name': profile.name
                , 'email': profile.email
                , 'faculty': profile.faculty
                , 'department': profile.department
                , 'keywords': top_keywords(profile)
                , 'link': url_for('profile', uid=profile.id)
                } for profile in profiles]

    return json.dumps(response)

@app.route('/api/people')
def profiles():
    try:
        query = request.args.get('query', '')
        page = int(request.args.get('page', 0))
        size = int(request.args.get('page_size', DEFAULT_PAGE_SIZE))
    except ValueError:
        return error_message(BAD_REQUEST, 'page and page_size must be uint')

    count, profiles = (profiling.fulfill_query(query, page, size)
                       if query else 
                       (db.Profile.count(), db.Profile.get_page(page, size)))

    if not count:
        return json.dumps({"count": count})
    else:
        result = { 'count': count }
        if page > 0:
            kwargs = {'page': page - 1, 'page_size': size}
            if query:
                kwargs['query'] = query
            result['previous_page'] = url_for('profiles', **kwargs)
        if (page + 1) * size < count:
            kwargs = {'page': page - 1, 'page_size': size}
            if query:
                kwargs['query'] = query
            result['next_page'] = url_for('profiles', **kwargs)

        result['this_page'] = [{ 'name': profile.name
                               , 'email': profile.email
                               , 'faculty': profile.faculty
                               , 'department': profile.department
                               , 'keywords': top_keywords(profile)
                               , 'link': url_for('profile', uid=profile.id)
                               } for profile in profiles]

        return json.dumps(result)

#TODO: Implement Put for submitting a user edited profile
@app.route('/api/people/<int:uid>', methods=['GET', 'PUT'])
def profile(uid):
    """
    GET: Retrieves the full profile of a person.

        The full profile contains name, keywords as a dictionary of words
        to frequencies, a list of publications and so on and so forth.

    PUT: A modified profile is submitted for a person

        The payload contains jwt (authentication token), name object,
        faculty, department, email and website or a list of
        keyword modification objects which contain the
        keyword and the action (add/ irrelevant)

    Args:
        uid (str): The unique id of the person.

    """
    print('hoopy frood')
    if request.method == 'GET':
        return get_profile(uid)
    elif request.method == 'PUT':
        return put_profile(uid)

def get_profile(uid):
    profile = db.Profile.get(uid)
    if not profile:
        abort(NOT_FOUND)
    else:
        result = {}
        for attribute in ['name', 'email', 'faculty', 'department', 'campus',
                'building', 'room', 'website']:
            result[attribute] = getattr(profile, attribute)

        result['keywords'] = dict(profile.keywords)
        #result['keywords'] = dict(top_keywords(profile))

        result['publications'] = [{ 'title': pub.title
                                  , 'link': url_for('publication', uid=pub.id) 
                                  } for pub in profile.publications]

        return json.dumps(result)

def put_profile(uid):
    if request.is_json:
        submission = request.get_json()
        if 'add_keyords' in submission:
            profiling.add_user_keywords(submission['add_keywords'],uid)
        if 'remove_keyords' in submission:
            profiling.remove_user_keywords(submission['remove_keywords'],uid)
        response = { 'success': True }
        return json.dumps(response), CREATED
    else:
        return error_message(BAD_REQUEST, 'JSON, please.')

@app.route('/api/people/find')
def find_person():
    try:
        profiles = db.Profile.find(**{k: v for k, v in request.args.items()})
        return json.dumps([url_for('profile', uid=p.id) for p in profiles])
    except AttributeError as e:
        return error_message(BAD_REQUEST, e.args[0])

@app.route('/api/keywords/<keyword>')
def keyword(keyword):
    """returns a list of profiles with this keyword
    """
    keyword = db.Keyword.find(name=keyword)
    if not keyword:
        abort(NOT_FOUND)
    else:
        assert len(keyword) == 1
        keyword = keyword[0]
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
    """
        GET: a paginated list of all publications.

        POST: for submitting single publications
    """
    if request.method == 'GET':
        try:
            page = int(request.args.get('page', 0))
            size = int(request.args.get('page_size', DEFAULT_PAGE_SIZE))
        except ValueError:
            return error_message(BAD_REQUEST, 'page and page_size must be uint')

        count = db.Publication.count()
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

            pubs = db.Publication.get_page(page, size)
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
            return json.dumps(response), CREATED
        else:
            return error_message(BAD_REQUEST, 'JSON, please.')

@app.route('/api/publications/<int:uid>')
def publication(uid):
    pub = db.Publication.get(uid)
    if not pub:
        abort(NOT_FOUND)
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

#TODO: Change this to delete Garbage keywords
@app.route('/api/keywords', methods=['DELETE'])
def delete_keywords(uid):
    """
       DELETE: accepts a list of user garbage keywords to be removed 
               from all profiles
               
               The body contains a jwt (authentication token), and a list of
               keywords.
    """
    if request.is_json:
        submission = request.get_json()
        for word in submission:
            db.session.delete(db.Keyword.find(name=word))
        response = { 'success': True }
        return json.dumps(response), CREATED
    else:
        return error_message(BAD_REQUEST, 'JSON, please.')


@app.teardown_appcontext
def shutdown_session(exception=None):
    """Ensures that ``db.session`` is closed at the end of each request."""
    db.session.remove()

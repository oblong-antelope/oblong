import json
import unittest

from flask import url_for
from . import server, database as db
from .database_tests import DatabaseTestCase

class ServerTestCase(DatabaseTestCase):
    def setUp(self):
        super().setUp()

        # set up database
        self.john = db.Profile( title='Mr'
                              , firstname='John'
                              , lastname='Smith'
                              , initials='J S'
                              , alias=None
                              , email='john.smith@ic.ac.uk'
                              , faculty='Natural Sciences'
                              , department='Department of Computing'
                              , campus='South Kensington'
                              , building='Huxley'
                              , room='308'
                              , website='http://www.doc.ic.ac.uk/~john.smith'
                              )
        self.jane = db.Profile( title='Ms'
                              , firstname='Jane'
                              , lastname='Doe'
                              , initials='J W'
                              , alias=None
                              , email='jane.doe@ic.ac.uk'
                              , faculty='Engineering'
                              , department='Department of Civil Engineering'
                              , campus='South Kensington'
                              , building='City & Guilds'
                              , room='201'
                              , website='http://www.ic.ac.uk/pages/jane.doe'
                              )
        self.mary = db.Profile( title='Mrs'
                              , firstname='Mary'
                              , lastname='Sue'
                              , initials='M Y'
                              , alias='Mabs'
                              , email='mary.sue@ic.ac.uk'
                              , faculty='Medicine'
                              , department='Department of Lungs'
                              , campus='Hammersmith'
                              , building='John Soane'
                              , room='-12'
                              , website='http://google.com'
                              )

        self.paper0 = db.Publication( title='Paper0'
                                    , abstract='A paper about argumentation.'
                                    , date='2016-01-01'
                                    , authors=[self.john, self.jane]
                                    )

        self.john.keywords['argumentation'] = 1.
        self.jane.keywords['argumentation'] = 2.

        self.paper1 = db.Publication( title='Paper1'
                                    , abstract='A paper about machine learning.'
                                    , date='2015-02-01'
                                    , authors=[self.john, self.mary]
                                    )

        self.john.keywords['machine learning'] = 4.
        self.mary.keywords['machine learning'] = 3.

        for p in (self.john, self.jane, self.mary, self.paper0, self.paper1):
            db.session.add(p)

        db.session.commit()

        # set up test client
        self.app = server.app.test_client()

class QueryTestCase(ServerTestCase):
    maxDiff = None

    def test_good_request(self):
        response = self.app.post('/api/queries', data='argumentation')
        data = json.loads(response.data.decode('utf-8'))
        
        self.assertEqual(data,
            [ { 'name': { 'title': 'Ms'
                        , 'first': 'Jane'
                        , 'last': 'Doe'
                        , 'initials': 'J W'
                        , 'alias': None
                        }
              , 'email': 'jane.doe@ic.ac.uk'
              , 'faculty': 'Engineering'
              , 'department': 'Department of Civil Engineering'
              , 'keywords': ['argumentation']
              , 'link': '/api/people/2'
              }
            , { 'name': { 'title': 'Mr'
                        , 'first': 'John'
                        , 'last': 'Smith'
                        , 'initials': 'J S'
                        , 'alias': None
                        }
              , 'email': 'john.smith@ic.ac.uk'
              , 'faculty': 'Natural Sciences'
              , 'department': 'Department of Computing'
              , 'keywords': ['machine learning', 'argumentation']
              , 'link': '/api/people/1'
              } 
            ]
        )

class PublicationSubmitTestCase(ServerTestCase):
    def test_known_author(self):
        pub_data = { 'title': 'Paper2'
                   , 'abstract': 'A paper about wild horses.'
                   , 'date': '2013-05-03'
                   , 'authors': [ { 'name': { 'title': 'Mr'
                                            , 'first': 'John'
                                            , 'last': 'Smith'
                                            , 'initials': None
                                            , 'alias': None
                                            }
                                  , 'email': None
                                  , 'faculty': 'Natural Sciences'
                                  , 'department': 'Department of Computing'
                                  , 'campus': None
                                  , 'building': None
                                  , 'room': None
                                  , 'website': None
                                  }
                                ]
                    }

        self.app.post('/api/publications', data=json.dumps(pub_data),
                content_type='application/json')
        
        self.assertIn('wild horses', self.john.keywords)
        self.assertNotIn('wild horses', self.jane.keywords)
        self.assertNotIn('wild horses', self.mary.keywords)
        self.assertEqual(db.Profile.query.count(), 3)
        
    def test_new_author(self):
        pub_data = { 'title': 'Paper2'
                   , 'abstract': 'A paper about wild horses.'
                   , 'date': '2013-05-03'
                   , 'authors': [ { 'name': { 'title': 'Ms'
                                            , 'first': 'Clara'
                                            , 'last': 'Oswald'
                                            , 'initials': None
                                            , 'alias': None
                                            }
                                  , 'email': None
                                  , 'faculty': 'Natural Sciences'
                                  , 'department': 'Department of Computing'
                                  , 'campus': None
                                  , 'building': None
                                  , 'room': None
                                  , 'website': None
                                  }
                                ]
                    }

        self.app.post('/api/publications', data=json.dumps(pub_data),
                content_type='application/json')
        
        self.assertNotIn('wild horses', self.john.keywords)
        self.assertNotIn('wild horses', self.jane.keywords)
        self.assertNotIn('wild horses', self.mary.keywords)
        self.assertEqual(db.Profile.query.count(), 4)

        clara = db.Profile.query.all()[3]

        self.assertIn('wild horses', clara.keywords)

import json
import unittest
import server

'''class QueryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()

    def test_good_request(self):
        response = self.app.post(
            '/api/query/submit',
            data=json.dumps(dict(
                expertise='artificial intelligence',
                role='supervisor'
            )),
            content_type='application/json'
        )
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])
        
        full_response = self.app.get(data['results'])
        full_data = json.loads(full_response.data.decode('utf-8'))
        self.assertEqual(full_data,
            [ { 'name': 'Dr. Tim Timson'
              , 'department': 'Department of Tim Research'
              , 'email': 'tim@timresearch.ic.ac.uk'
              , 'research_summary': '/api/person/0/summary'
              , 'full_profile': '/api/person/0/full'
              } 
            , { 'name': 'Dr. Timothy Timsworth'
              , 'department': 'Department of Tim Rights'
              , 'email': 'tim@timrights.ic.ac.uk'
              , 'research_summary': '/api/person/1/summary'
              , 'full_profile': '/api/person/1/full'
              } 
            ]
        )

    def test_bad_request(self):
        response = self.app.post(
            '/api/query/submit',
            data=json.dumps({}),
            content_type='application/json'
        )
        data = json.loads(response.data.decode('utf-8'))
        self.assertTrue(data['success'])

        full_response = self.app.get(data['results'])
        full_data = json.loads(full_response.data.decode('utf-8'))
        self.assertEqual(full_data, [])

class PersonResearchSummaryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()

    def test_good_request(self):
        response = self.app.get('/api/person/0/summary')
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data,
            { 'papers': 9
            , 'keywords': ['Tim', 'ai', 'learning', 'machine']
            , 'recent_paper': 'https://arXiv.org/abs/1024.01232'
            , 'full_profile': '/api/person/0/full'
            }
        )

class PersonFullTestCase(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()

    def test_good_request(self):
        response = self.app.get('/api/person/0/full')
        data = json.loads(response.data.decode('utf-8'))
        self.assertEqual(data,
            { 'name': 'Dr. Tim Timson'
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
        )'''

if __name__ == '__main__':
    unittest.main()

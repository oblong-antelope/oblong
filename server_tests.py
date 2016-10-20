import json
import unittest
import server

class QueryTestCase(unittest.TestCase):
    def setUp(self):
        self.app = server.app.test_client()

    def test_good_request(self):
        response = self.app.post(
            '/api/query/submit',
            data=json.dumps(dict(
                speciality='artificial intelligence',
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
              , 'info': '/api/person/<key>'
              } 
            , { 'name': 'Dr. Timothy Timsworth'
              , 'department': 'Department of Tim Rights'
              , 'info': '/api/person/<key>'
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

if __name__ == '__main__':
    unittest.main()

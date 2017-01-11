import unittest
from . import profiling, database as db
from .database_tests import DatabaseTestCase

class GetKeywordsTests(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(profiling.get_keywords(""), ())

    def test_plurals(self):
        self.assertEqual(profiling.get_keywords("porcupines"), ("porcupine",))

class UpdateProfilesTestCase(DatabaseTestCase):
    @staticmethod
    def profileToJSON(profile):
        return { 'name': profile.name
               , 'email': profile.email
               , 'faculty': profile.faculty
               , 'department': profile.department
               , 'campus': profile.campus
               , 'building': profile.building
               , 'room': profile.room
               , 'website': profile.website 
               }

    def setUp(self):
        super().setUp()

        self.john = db.Profile(title="Mr", firstname="John", lastname="Smith")
        db.session.add(self.john)

    def testPercentScaling(self):
        authors = [self.profileToJSON(self.john)]
        profiling.update_authors_profiles("porcupine, fluctuations", None, authors, "2016-01-01")
        profiling.update_authors_profiles("porcupine, gravitational waves", None, authors, "2015-01-01")

        self.assertIn("porcupine", self.john.keywords)
        self.assertIn("fluctuation", self.john.keywords)
        self.assertIn("gravitational waves", self.john.keywords)

        self.assertEquals(self.john.keywords["porcupine"], 100)

        


         
        

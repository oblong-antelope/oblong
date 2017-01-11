import unittest
import testing.postgresql
from . import database as db

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)

def gpbk(keywords):
    count, results = db.get_profiles_by_keywords(keywords, 0, 25)
    return count, list(results)

def tearDownModule():
    # clear cached database at end of tests
    Postgresql.clear_cache()

class DatabaseTestCase(unittest.TestCase):
    def setUp(self):
        self.postgresql = Postgresql()
        db.init(self.postgresql.url())

    def tearDown(self):
        db.session.remove()
        self.postgresql.stop()

class KeywordDictTestCase(DatabaseTestCase):
    def setUp(self):
        super().setUp()

        self.john = db.Profile(title="Mr", firstname="John", lastname="Smith")
        self.horse = db.Keyword(name='horse')
        db.session.add(self.john)
        db.session.add(self.horse)
        db.session.flush()
        self.horse_assoc = db.ProfileKeywordAssociation( profile=self.john
                                                       , keyword_=self.horse
                                                       , weight=.5
                                                       )
        db.session.add(self.horse_assoc)
        db.session.commit()

    def testExistingKeywords(self):
        self.assertEqual(self.john.keywords['horse'], .5)
        self.john.keywords['horse'] = 2.5
        db.session.commit()
        self.assertEqual(self.john.keywords['horse'], 2.5)
        self.assertEqual(self.horse_assoc.weight, 2.5)

    def testCreateKeywords(self):
        self.john.keywords['cart'] = .5
        db.session.commit()
        
        self.assertEqual(self.john.keywords['cart'], .5)
        
        cart = db.Keyword.query.filter_by(name='cart').one()
        self.assertEqual(cart.profiles_[0].weight, .5)

class QueryTestCase(DatabaseTestCase):
    def setUp(self):
        super().setUp()

        self.john = db.Profile(title="Mr", firstname="John", lastname="Smith")
        self.jane = db.Profile(title="Ms", firstname="Jane", lastname="Doe")
        self.mary = db.Profile(title="Mrs", firstname="Mary", lastname="Peng")
        self.peng = db.Profile(title="Mr", firstname="Peng", lastname="Peng",
                department="DoC", faculty="Engineering", campus="Hammersmith")

        for p in (self.john, self.jane, self.mary, self.peng):
            db.session.add(p)
        db.session.commit()

        self.john.keywords["porcupine taming"] = 1.25
        self.john.keywords["horse"] = 1.
        self.mary.keywords["horse"] = 2.
        self.mary.keywords["cart"] = 3.
        self.jane.keywords["cart"] = 4.
        self.jane.keywords["descartes"] = 5.
        self.peng.keywords["compsci"] = 2.33

        db.session.commit()

class QueryBasicTestCase(QueryTestCase):
    def testFirstname(self):
        self.assertEqual(gpbk(['Mary']), (1, [(self.mary, 5.)]))

    def testLastname(self):
        self.assertEqual(gpbk(['Doe']), (1, [(self.jane, 9.)]))
    
    def testDepartment(self):
        self.assertEqual(gpbk(['DoC']), (1, [(self.peng, 2.33)]))

    def testFaculty(self):
        self.assertEqual(gpbk(['Engineering']), (1, [(self.peng, 2.33)]))

    def testCampus(self):
        self.assertEqual(gpbk(['Hammersmith']), (1, [(self.peng, 2.33)]))

    def testDuplicateFields(self):
        self.assertEqual( gpbk(['Peng'])
                        , (2, [(self.mary, 5.), (self.peng, 2.33)])
                        )

    def testBothNames(self):
        self.assertEqual(gpbk(['John', 'Smith']), (1, [(self.john, 1.)]))

    def testFieldMatchingLowercase(self):
        self.assertEqual(gpbk(['mary']), (1, [(self.mary, 5.)]))

    def testFieldAndKeywordMatching(self):
        self.assertEqual(gpbk(['Mary', 'horse']), (1, [(self.mary, 2.)]))

    def testPartialQuery(self):
        self.assertEqual(gpbk(['porcupine']), (1, [(self.john, 1.25)])

class QuerySortingTestCase(QueryTestCase):
    def testOneKeyword(self):
        self.assertEqual( gpbk(['horse'])
                        , (2, [(self.mary, 2.), (self.john, 1.)])
                        )
        self.assertEqual( gpbk(['cart'])
                        , (2, [(self.jane, 4.), (self.mary, 3.)])
                        )
        self.assertEqual( gpbk(['descartes'])
                        , (1, [(self.jane, 5.)])
                        )
        self.assertEqual(gpbk(['not in db']), (0., []))

    def testManyKeywords(self):
        """Query is OR, so return profiles with any of the keywords."""
        self.assertEqual( gpbk(['horse', 'cart'])
                        , (3, [(self.mary, 5.), (self.jane, 4.), (self.john, 1.)])
                        )
        self.assertEqual( gpbk(['horse', 'descartes'])
                        , (3, [(self.jane, 5.), (self.mary, 2.), (self.john, 1.)])
                        )
        self.assertEqual( gpbk(['horse', 'not in db'])
                        , (2, [(self.mary, 2.), (self.john, 1.)])
                        )

class DeleteTestCase(DatabaseTestCase):
    keyword_name = "horse"
    other_keyword_name = "cart"

    def setUp(self):
        super().setUp()
        self.john = db.Profile(title="Mr", firstname="John", lastname="Smith")
        self.jane = db.Profile(title="Ms", firstname="Jane", lastname="Doe")

        for p in (self.john, self.jane):
            db.session.add(p)
        db.session.commit()

        self.john.keywords[self.keyword_name] = 1.
        self.jane.keywords[self.keyword_name] = 2.
        self.john.keywords[self.other_keyword_name] = 1.
        self.jane.keywords[self.other_keyword_name] = 2.

        db.session.commit()

    def testDeleteKeywordFromProfile(self):
        del self.john.keywords[self.keyword_name]
        db.session.commit()

        kw = db.Keyword.find(name=self.keyword_name)
        self.assertIn(self.jane, kw.profiles)
        self.assertNotIn(self.john, kw.profiles)

    def testDeleteKeyword(self):
        kw = db.Keyword.find(name=self.keyword_name)
        self.assertEquals(len(kw), 1)
        db.session.delete(kw[0])
        db.session.commit()

        self.assertNotIn(self.keyword_name, self.john.keywords)
        self.assertNotIn(self.keyword_name, self.jane.keywords)
        self.assertIn(self.other_keyword_name, self.john.keywords)
        self.assertIn(self.other_keyword_name, self.jane.keywords)

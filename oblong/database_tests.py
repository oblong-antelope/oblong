import unittest
import testing.postgresql
from . import database as db

Postgresql = testing.postgresql.PostgresqlFactory(cache_initialized_db=True)

def tearDownModule(self):
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
        self.horse_assoc = db.ProfileKeywordAssociation( profile=self.john
                                                       , keyword_=self.horse
                                                       , weight=.5
                                                       )
        db.session.add(self.john)
        db.session.add(self.horse)
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

class QuerySortingTestCase(DatabaseTestCase):
    def setUp(self):
        super().setUp()

        self.john = db.Profile(title="Mr", firstname="John", lastname="Smith")
        self.jane = db.Profile(title="Ms", firstname="Jane", lastname="Doe")
        self.mary = db.Profile(title="Mrs", firstname="Mary", lastname="Sue")

        for p in (self.john, self.jane, self.mary):
            db.session.add(p)
        db.session.commit()

        self.john.keywords["horse"] = 1.
        self.mary.keywords["horse"] = 2.
        self.mary.keywords["cart"] = 3.
        self.jane.keywords["cart"] = 4.
        self.jane.keywords["descartes"] = 5.

        db.session.commit()

    def testOneKeyword(self):
        self.assertEqual( db.get_profiles_by_keywords(['horse'])
                        , [(self.mary, 2.), (self.john, 1.)]
                        )
        self.assertEqual( db.get_profiles_by_keywords(['cart'])
                        , [(self.jane, 4.), (self.mary, 3.)]
                        )
        self.assertEqual( db.get_profiles_by_keywords(['descartes'])
                        , [(self.jane, 5.)]
                        )
        self.assertEqual(db.get_profiles_by_keywords(['not in db']), [])

    def testManyKeywords(self):
        """Query is OR, so return profiles with any of the keywords."""
        self.assertEqual( db.get_profiles_by_keywords(['horse', 'cart'])
                        , [(self.mary, 5.), (self.jane, 4.), (self.john, 1.)]
                        )
        self.assertEqual( db.get_profiles_by_keywords(['horse', 'descartes'])
                        , [(self.jane, 5.), (self.mary, 2.), (self.john, 1.)]
                        )
        self.assertEqual( db.get_profiles_by_keywords(['horse', 'not in db'])
                        , [(self.mary, 2.), (self.john, 1.)]
                        )

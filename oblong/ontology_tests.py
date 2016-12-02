import unittest
import rdflib
from . import ontology

class OntologyTestCate(unittest.TestCase):
    onto = ontology.Ontology()

    def test_find_superclasses(self):
        self.assertEqual( self.onto.find_superclasses('trees')
                        , [ 'trees'
                          , 'Graph theory'
                          , 'Discrete mathematics'
                          , 'Mathematics of computing'
                          ]
                        )
                          
    def test__find_parent(self):
        database = self.onto._find_URI('database')
        parent = self.onto._find_parent(database)
        self.assertIsInstance(parent, rdflib.term.URIRef)
        self.assertEqual(repr(parent).split('#')[-1], "10002951')")

    def test__find_URI(self):
        parent = self.onto._find_URI('database')
        self.assertIsInstance(parent, rdflib.term.URIRef)
        self.assertEqual(repr(parent).split('#')[-1], "10002952')")

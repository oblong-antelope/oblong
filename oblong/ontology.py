"""Library for accessing the ACM ontology"""

import rdflib

#define function for creating literals
def lit(string):
  return rdflib.term.Literal(string, lang='en')

#import ontology
onto = rdflib.Graph()
result = onto.parse("../ACMComputingClassificationSystemSKOSTaxonomy.xml")

#specify namespace
n = rdflib.Namespace("http://www.w3.org/2004/02/skos/core#")

#test
database = onto.value(None, n.prefLabel, lit("Data management systems"))


def find_superclasses(subject):
    """Given a subject title, returns a list of its superclases

    When provided with a computer science subject, looks it up in
    the ACM ontology and finds all of its superclasses. Returns
    superclass names in an ordered list, closest first.

    Args:
        subject (string): the name of the subject of which to find
            superclasses

    Returns:
        (list[str]): an ordered list of the superclasses of 'subject'.
            Closest parents are first, further parents progressively later
    """
    #TODO
    return 

"""Library for accessing the ACM ontology"""

import rdflib
import os.path

#define constants
ACM_ONTOLOGY = os.path.join(os.path.dirname(__file__), "data",
    "ACM_Computing_Ontology.xml")
SKOS_NAMESPACE = "http://www.w3.org/2004/02/skos/core#"

#define function for creating literals
def lit(string):
    """A function for simply creating literals of the form required for ACM"""
    return rdflib.term.Literal(string, lang='en')

class Ontology:
    """A class representing an ontology

    Attributes:
        g (rdflib.Graph): a graph representing the ontology
        n (rdflib.Namespace): the namespace for predicates
    """
    def __init__(self, path=ACM_ONTOLOGY, ns=SKOS_NAMESPACE):
        """Initialises the ontology

        Args:
            path (str): a path to the ontology file. Uses the 
                ACM ontology .xml file by default
            ns (str): a URL to the namespace. Uses W3's SKOS
                namespace by default
        """
        #import ontology
        self.g = rdflib.Graph()
        result = self.g.parse(path)

        #specify namespace
        self.n = rdflib.Namespace(ns)

    def find_superclasses(self, subject):
        """Given a subject title, returns a list of its superclasses

        When provided with a computer science subject, looks it up in
        the ACM ontology and finds all of its superclasses. Returns
        superclass names in an ordered list, closest first.
        Includes the subject's name for ease.

        Args:
            subject (str): the name of the subject of which to find
                superclasses

        Returns:
            (list[str]): an ordered list of the superclasses of 'subject'.
                Closest parents are first, further parents progressively later

        Example usage:
            >>> onto.find_superclasses("trees")
            ['trees', 'Graph theory', 'Discrete mathematics', 'Mathematics of computing']
        """
        results = [subject]
        parent = self._find_parent(self._find_URI(subject))
        while parent:
            parent_name = self._find_label(parent)
            results.append(parent_name)
            parent = self._find_parent(parent)
        return results

    def _find_parent(self, URI):
        """Finds the URI of the parent of a given URI

        Args:
            URI (rdflib.term.URIRef): the URI of which to find the parent

        Returns:
            (rdflib.term.URIRef): the URI of the parent. 'None' if not found.

        Example usage:
            >>> database = onto._find_URI("database")
            >>> onto._find_parent(database) # doctest:+ELLIPSIS
            rdflib.term.URIRef('...#10002951')
        """
        return self.g.value(URI, self.n.broader, None)

    def _find_URI(self, subject):
        """Returns the URI of a subject.

        Args:
            subject (str): name of the subject to search for

        Returns:
            (rdflib.term.URIRef): the URI of the subject. 'None' if not found.

        Exmaple usage:
            >>> onto._find_URI("database") # doctest:+ELLIPSIS
            rdflib.term.URIRef('...#10002952')
        """
        subject = subject.lower()
        subject_cap = subject.capitalize() #normalise capitalisation
        URI = self.g.value(None, self.n.prefLabel, lit(subject_cap))
        if not URI:
            URI = self.g.value(None, self.n.altLabel, lit(subject))
        return URI

    def _find_label(self, URI):
        """Returns the label of a given object

        Args:
            URI (rdflib.term.URIRef): the URI of the object we want 
                to find the name of

        Returns:
            (str): the label of the object
        """
        label = self.g.value(URI, self.n.prefLabel, None)
        if not label:
            label = self.g.value(URI, self.n.altLabel, None)
        return str(label)

if __name__ == "__main__":
    onto = Ontology()
    import doctest
    doctest.testmod()

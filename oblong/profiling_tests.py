import unittest
from . import profiling

class GetKeywordsTests(unittest.TestCase):
    def test_empty_string(self):
        self.assertEqual(profiling.get_keywords(""), ())

#!/usr/bin/python
# -*- coding: utf8 -*-

#Francesca Toni's publications from 2016
papers = [ {"title"   : "Argumentation-based multi-agent decision making with privacy preserved",
            "authors" : "Y. Gao, F. Toni, H. Wang, and F. Xu",
            "date"    : "2016"},
           {"title"   : "On the interplay between games, argumentation and dialogues",
            "authors" : "X. Fan and F. Toni",
            "date"    : "2016"},
           {"title"   : "Discontinuity-free decision support with quantitative argumentation debates",
            "authors" : "A. Rago, F. Toni, M. Aurisicchio, and P. Baroni",
            "date"    : "2016"},
           {"title"   : "Abstract argumentation for case-based reasoning",
            "authors" : "K. Cyras, K. Satoh, and F. Toni",
            "date"    : "2016"},
           {"title"   : "ABA+: assumption-based argumentation with preferences",
            "authors" : "K. Cyras and F. Toni",
            "date"    : "2016"},
           {"title"   : "Properties of ABA+ for non-monotonic reasoning",
            "authors" : "K. Cyras and F. Toni",
            "date"    : "2016"},
           {"title"   : "Smarter electricity and argumentation theory",
            "authors" : "M. Makriyiannis, T. Lung, R. Craven, F. Toni, and J. Kelly",
            "date"    : "2016"},
           {"title"   : "Online Argumentation-Based Platform for Recommending Medical Literature",
            "authors" : "A. Mocanu, X. Fan, F. Toni, M. Williams, and J. Chen",
            "date"    : "2016"},
           {"title"   : "Justifying Answer Sets using Argumentation",
            "authors" : "C. Schulz, F. Toni",
            "date"    : "2016"},
           {"title"   : "Argument Graphs and Assumption-Based Argumentation",
            "authors" : "R. Craven and F. Toni",
            "date"    : "2016"}
         ]

punc = ',.:;' #punctuation we want to remove
connectives = ['for', 'and', 'a', 'the', 'with'] #boring words to get rid of

def build_profiles(papers):
    """Produces a dictionary of name:profile pairs. The profiles are a
       prioritised list of keywords.
       
       papers : a list of papers to build profiles from

       returns : a dictionary of name:profile pairs
    """
    profiles = {}
    for paper in papers:
        author_list = split_authors(paper['authors'])
        word_list = split_title(paper['title'])
        for author in author_list:
            profiles = augment_author(author, profiles, word_list)
    return profiles

def split_authors(authors):
    """Produces a list of strings containing the authors' names.

    authors : a string containing an author list

    returns : a list of author names

    >>> split_authors("K. Cyras, K. Satoh, and F. Toni")
    ['K. Cyras', 'K. Satoh', 'F. Toni']
    """
    split = authors.split(', ')
    author_list = split[:-1]
    author_list.extend(author for author in split[-1].split('and ') if author != '')
    return author_list

def split_title(title):
    """Produces a list of keywords from the paper title with
       boring words removed.

    title : a title to analyse

    returns : a list of keywords

    >>> split_title("ABA+: assumption-based argumentation with preferences")
    ['ABA+', 'assumption-based', 'argumentation', 'preferences']
    """
    s = list(title)
    words = ''.join([o for o in s if not o in punc]).split()
    return [word for word in words if word not in connectives]

def augment_author(author, profiles, words):
    """Given a dict of profiles, an author name, and a list of words
       increase the word counts for the given author appropriately

       author : author name to augment
       profiles : dict of author:word_count pairs
       words : a list of words

       returns : the augmented profile

       >>> augment_author('F. Toni', {'F. Toni':{'argumentation':2}}, ['argumentation', 'preferences'])
       {'F. Toni': {'argumentation': 3, 'preferences': 1}}
    """
    if author not in profiles:
        profiles[author] = {}
    for word in words:
        author_words = profiles[author]
        if word not in author_words:
            author_words[word] = 1
        else:
            author_words[word] += 1
    return profiles


if __name__ == "__main__":
    import doctest
    doctest.testmod()

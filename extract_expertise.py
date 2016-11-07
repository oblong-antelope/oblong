#!/usr/bin/python
# -*- coding: utf8 -*-
from nltk.stem import *
from nltk import pos_tag
import nltk
import string
import collections
import handlers.database_handlers as dbh

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


papers3 = [ {"title"   : "Argumentation-based multi-agent decision making with privacy preserved",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "On the interplay between games, argumentation and dialogues",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Discontinuity-free decision support with quantitative argumentation debates",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Abstract argumentation for case-based reasoning",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "ABA+: assumption-based argumentation with preferences",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Properties of ABA+ for non-monotonic reasoning",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Smarter electricity and argumentation theory",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Online Argumentation-Based Platform for Recommending Medical Literature",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Justifying Answer Sets using Argumentation",
            "authors" : "F. Toni",
            "date"    : "2016"},
           {"title"   : "Argument Graphs and Assumption-Based Argumentation",
            "authors" : "F. Toni",
            "date"    : "2016"}
         ]


remove = ['for', 'and', 'a', 'the', 'with', 'of', 'using', 'on','between','based','non',',','.',':',';'] #boring stuff to get rid of

def augment_profiles(paper):
    """Given a single paper, augments the author of that paper.

       paper : a single paper to augment the author of
    """
    word_list = split_title(paper['title'])
    authors = split_authors(paper['authors'])
    for author in authors:
        augment_author(author, word_list)

def split_authors(authors):
    """Produces a list of strings containing the authors' names.

    authors : a string containing an author list

    returns : a list of author names
    """
    split = authors.split(', ')
    author_list = split[:-1]
    author_list.extend(author for author in split[-1].split('and ') if author != '')
    return author_list

def get_lemma_pos(tag):  #needed to for part of speech tagging for lemmatizer

    if tag.startswith('J'):
        return 'a'
    elif tag.startswith('V'):
        return 'v'
    elif tag.startswith('N'):
        return 'n'
    elif tag.startswith('R'):
        return 'r'
    else:
        return 'n'


def split_title(title):
    """Produces a list of keywords from the paper title with
       boring words removed.

       title : a title to analyse

       returns : a list of keywords
    """
    text = string.replace(title,'-',' ')                                       #replacing hyphens with spaces
    tokens = nltk.word_tokenize(text)                                           #tokenizing the title
    lowertokens = [word.lower() for word in tokens]                             #converting all words to lowercase
    taggedwords = nltk.pos_tag(lowertokens)                                    #tagging words as verb, noun etc to help lemmatizer
    list1 = [(x,get_lemma_pos(y)) for (x,y) in taggedwords if x not in remove] #converts those to format lemmatizer understands
    wl = WordNetLemmatizer()                                                    #initialising the lemmatizer
    list2 = [wl.lemmatize(x,pos=y) for (x,y) in list1]                          #lemmatizing each word in list
    return list2

def augment_author(author, words):
    """Given a dict of an author name and a list of words
       increase the word counts for the given author appropriately

       author : author name to augment
       words : a list of words
    """
    profiles = dbh.find_profiles({'name':author})[0] #find profiles
    if profiles == []:
        dbh.add_new_profile({'name':author, 'keywords':repr({})}) #if none, insert new
        profiles = [{'name':author, 'keywords':repr({})}]
    for word in words:
        author_profile = eval(find_author_profile(author, profiles)) #find first author of given name
        author_words = author_profile['keywords'] #find author's keywords
        if word not in author_words:
            author_words[word] = 1 #add new word
        else:
            author_words[word] += 1 #augment old word
    x = sorted(author_words.items(), key=lambda t: t[1], reverse=True)   #sorting the words from lowest to highest freq in list
    author_profile['keywords'] = repr(x) #update the word list in profile (dict converted to string for db)
    dbh.update_profile(author_profile['id'], author_profile) #update row in db

def find_author_profile(author, profiles):
    for p in profiles:
        if p['name'] == author:
            return p
    return {}

	
if __name__ == "__main__":
    import doctest
    doctest.testmod()

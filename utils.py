import os
from subprocess import check_call, CalledProcessError

def install_nltk():
    """Calls the nltk.download() function if needed"""
    try:
        check_call("nltk.download()")
    except CalledProcessError as e:
        print("nltk did not download: {}".format(e))

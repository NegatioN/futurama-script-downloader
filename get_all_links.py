#!/bin/python

from bs4 import BeautifulSoup
import sys, urllib.request
#creates links for all urls, but the ones which dont exist are not parsed by the main program.


def create_url(title):
    title = title.replace(' ', '-')
    return 'http://www.imsdb.com/transcripts/Futurama-' + title

request = urllib.request.Request(sys.argv[1])
webpage_bytes = urllib.request.urlopen(request)
soup = BeautifulSoup(webpage_bytes, 'html5lib')

file = open('all-links.txt', 'w')
for link in soup.findAll("a"):
    try:
        file.write(create_url(link['title']) + ' ')
    except:
        pass

file.close()

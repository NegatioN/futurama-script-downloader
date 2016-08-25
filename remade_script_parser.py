#!/usr/bin/python3
# coding: utf-8

# https://docs.python.org/3.0/library/urllib.request.html
# webpage type : https://docs.python.org/3.4/library/http.client.html
import sys, json, re, urllib.request, html5lib
from bs4 import BeautifulSoup, Tag, UnicodeDammit



# loop until we get a valid script_url

has_started = False
script_url = sys.argv[1]
is_webpage_fetched = False
title = ''
while not is_webpage_fetched:
    # get the script's URL from the parameters if it was passed
    if( script_url == '' ):
        print('miss')
    else:
        script_url = sys.argv[1]

        title = (script_url.rsplit('/', 1)[-1]).replace('.html', '')
        title = title.replace('Futurama-', '')

    try:
        request = urllib.request.Request(script_url)
        webpage_bytes = urllib.request.urlopen(request)
        soup = BeautifulSoup(webpage_bytes, 'html5lib')
        is_webpage_fetched = True
    except urllib.error.URLError as err:
        pass
    except ValueError as err:
        pass
    except:
        raise
    else:
        script_text = soup.find("pre")

        if( script_text.find("pre") ):
            script_text = script_text.find("pre")

        is_webpage_fetched = True

# script dict to be serialized as JSON
script=dict()

script['movie_title'] = title #set title


BLOCK_TYPES=['character', 'speech', 'stage direction', 'location']
CHARACTER=0
SPEECH=1
DIRECTIONS=2
LOCATION=3


# COMPILE ALL THE REGULAR EXPRESSIONS!
spaces_regex = re.compile("^(\s*).*")
location_regex = re.compile("^\s*(INT\.|EXT\.)")

def get_line_type(line, stripped_line, usual_spaces):
    spmatch = spaces_regex.search(line)
    spaces_number = len(spmatch.group(1))
    for block_type_usual_spaces in usual_spaces:
        if spaces_number in block_type_usual_spaces:
            return usual_spaces.index(block_type_usual_spaces)
    return -1


# DA big loop

usual_spaces=[[] for i in range(len(BLOCK_TYPES))]
usual_spaces[DIRECTIONS].append(15)
usual_spaces[CHARACTER].append(37)
usual_spaces[SPEECH].append(25)
usual_spaces[SPEECH].append(26)

# Ici on définit les variables qu'on remplira de texte
is_intro = True
movie_script = []
intro = []
last_line_type = -1
last_character = ''
text = []
characters=[]


for block in script_text.descendants:
    if(isinstance(block, Tag)):
        continue

    # UnicodeDammit converts any string to UTF-8
    # does not work so well
    block = UnicodeDammit(block, soup.original_encoding).unicode_markup
    # remove leading and ending end of lines
    block = block.strip('\n')

    # if the block doesn't have any text, skip it
    if( re.search('\w', block) == None ):
        continue

    # bs4 ne coupe pas toujours bien les différents blocs
    # Mieux vaut donc redécouper par paragraphe et les traiter un à un
    for line in block.split('\n'):
        stripped_line = line.strip(' \n\t\r')
        if( re.search('\w', line) == None ):
            continue

        line_type = get_line_type(line, stripped_line, usual_spaces)

        if(last_line_type == -1 # -1 = not initialized
           or last_line_type == line_type):
            text.append(stripped_line)
        else:
            if(last_line_type == CHARACTER):
                last_character=' '.join(text)
                if not last_character in characters:
                    characters.append(last_character)
            elif(last_line_type == SPEECH):
                movie_script.append({
                    'type': BLOCK_TYPES[last_line_type],
                    BLOCK_TYPES[CHARACTER]: last_character,
                    'text': ' '.join(text)})
            elif(last_line_type == None):
                intro.append(stripped_line)
            else:
                movie_script.append({
                    'type': BLOCK_TYPES[last_line_type],
                    'text': ' '.join(text)})
            text=[stripped_line]

        last_line_type = line_type

movie_script.append({
    'type': BLOCK_TYPES[line_type],
    'text': ' '.join(text)})
movie_script.pop(0)

script['movie_script'] = movie_script


try:
    fd = open('futurama/' + script['movie_title'] + '.json', 'w')
    json.dump(script, fd, indent=True)
    print('We just successfully wrote {}\'s script as JSON to {} .'.format(script['movie_title'], fd.name))
except:
    print("Shit happened: ", sys.exc_info()[0])
finally:
    fd.close()


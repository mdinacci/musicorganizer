#!/usr/bin/python

# This script is released under the Apache 2.0 License.
# I'm too lazy to post the license text here, sorry.
#
# Author: Marco Dinacci - www.intransitione.com -

# -*- coding: utf-8-*-

import mutagen as mg
import os,string,sys,shutil

path_exists = os.path.exists

__all__ = ["scan","arrange_song"]

def _sanitize_filename(f):
    return f.replace('-','_').replace('/','_').replace('&','').replace('+','').replace('*','_')

def _sanitize_tag(tag):
    words = map(string.capitalize, tag.split())

    return _sanitize_filename(" ".join(words))

def _mktree(target_dir,artist,album):
    artist_dir = os.path.join(target_dir,artist)
    album_dir = os.path.join(artist_dir, album)

    if not os.path.exists(artist_dir):
        print u"Creating directory %s" % artist_dir
        os.mkdir(artist_dir)
    if not os.path.exists(album_dir):
        print u"Creating directory %s" % album_dir
        os.mkdir(album_dir)

def _is_song(filename):
    flow = filename.lower()
    return flow.endswith("mp3") or flow.endswith("ogg") or flow.endswith("mp4") \
    or flow.endswith("wma") or flow.endswith("wav") or flow.endswith("flac")

def scan(source, target):
    print u"Scanning ", source

    for f in os.listdir(source):
        current = os.path.join(source,f)
        if os.path.isdir(current):
            scan(current, target)
        else:
            if _is_song(f):
                arrange_song(current, target)
    
def arrange_song(song,target_dir):
    print u"Fixing song: ", song

    try:
        song = mg.File(song)
    except mg.mp3.HeaderNotFoundError:
        print "Song %s is not a valid music file" % song
        return

    if song.has_key("TIT2"):
        title = _sanitize_tag(song["TIT2"].text[0])
    else:
        title = "Unknown Title"
    if song.has_key("TPE1"):
        artist = _sanitize_tag(song["TPE1"].text[0])
    else:
        artist = "Unknown Artist"
    if song.has_key("TALB"):
        album = _sanitize_tag(song["TALB"].text[0])
    else:
        album = "Unknown Album"

    _mktree(target_dir, artist,album)
    
    dest_dir = os.path.join(target_dir,artist,album)
    dest_file = os.path.join(dest_dir, title + ".mp3")
    # TODO check that file doesn't already exists
    
    while os.path.exists(dest_file):
        name, ext = dest_file.split(".")
        number = 0
        if '_' in name:
            name, number = name.split('_')
            number = int(number)
        dest_file = "%s_%s.%s" % (name,number,ext)
    
    shutil.move(song.filename, dest_file)
    os.chmod(dest_file,0644)

    try:
        print "%s moved to %s \n" % (song.filename.decode(), dest_dir.decode())
    except UnicodeDecodeError:
        pass
    except UnicodeEncodeError:
        pass


if __name__ == "__main__":
    if len(sys.argv) < 2:
        exit("Insufficient number of parameters [source dir and target dir required.]")

    source_dir = sys.argv[1]
    target_dir = sys.argv[2]

    scan(source_dir, target_dir)



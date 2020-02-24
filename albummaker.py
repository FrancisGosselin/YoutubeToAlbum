import eyed3
import os
import argparse
from pathlib import Path
import pafy
import sys
import numpy as np

plurl = "https://www.youtube.com/playlist?list=PLoXd1MHJHuY6rw5jrlUOt83lDPfy5rgcM"
playlist = pafy.get_playlist(plurl)

parser = argparse.ArgumentParser()
parser.add_argument('-s', '--skip-download', action='store_true', dest='skip', help='if you already have the mp3')
parser.add_argument('--name', action='store', dest='name', help='name of the album')
parser.add_argument('--year', action='store', dest='year', help='year of the album')
parser.add_argument('--genre', action='store', dest='genre', help='genre of the album')
parser.add_argument('--artist', action='store', dest='artist', help='artist')

parser.add_argument('directory', metavar='d', nargs='+',
                    help='directory of album')
args = parser.parse_args()

if not args.skip:
    print("Collecting playlist information ...")
    streams = [ item["pafy"].getbestaudio() for item in playlist['items'] ]
    print("Downloading " + str(len(streams)) + " music files ... Press any key to continue")
    for stream in streams:
        filename = stream.title + '.' + stream.extension
        try :
            stream.download(os.path.join(Path.cwd(),args.directory[0]))
        except OSError:
            stream.download(os.path.join(Path.cwd(),args.directory[0]))

        filepath =  os.path.join(os.path.join(Path.cwd(),args.directory[0]), filename)
        new_filepath = os.path.join(os.path.join(Path.cwd(),args.directory[0]), stream.title + '.mp3')

        child_pid = os.fork()
        if child_pid == 0:
            print("started conversion to FLAC")
            os.execl('/usr/bin/ffmpeg', '/usr/bin/ffmpeg', '-nostats', '-loglevel', '0', '-i', filepath,"-acodec", "libmp3lame", new_filepath)
        os.wait()
        os.remove(filepath) 

    print("All downloads are done!")
    print("Continue ? [Y/n]")
    x = input()

    if x != "y" and x != "Y":
        print("exiting")
        sys.exit(0)
else :
    print("Skipping download...")

num = 1
for file in os.listdir(os.path.join(Path.cwd(),args.directory[0])):
    if file.endswith('.mp3'):
        filepath = os.path.join(os.path.join(Path.cwd(),args.directory[0]), file)
        audiofile = eyed3.load(filepath)
        audiofile.tag.track_num = num
        num += 1
        audiofile.tag.title = '.'.join(file.split('.')[:-1])

        if args.name:
            audiofile.tag.album = args.name
        if args.year:
            audiofile.tag.year = args.year
        if args.genre:
            audiofile.tag.genre = args.genre
        if args.artist:
            audiofile.tag.album_artist = args.artist
            audiofile.tag.artist = args.artist
        audiofile.tag.save()


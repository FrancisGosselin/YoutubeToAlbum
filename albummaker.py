import eyed3
import os
import argparse
from pathlib import Path
import pafy
import sys
import numpy as np
from urllib import parse

parser = argparse.ArgumentParser()
parser.add_argument('url', help="Youtube URL of the playlist")

parser.add_argument('--name', action='store', dest='name', help='name of the album')
parser.add_argument('--year', action='store', dest='year', help='year of the album')
parser.add_argument('--genre', action='store', dest='genre', help='genre of the album')
parser.add_argument('--artist', action='store', dest='artist', help='artist')

args = parser.parse_args()

try:
    playlist = pafy.get_playlist(args.url)
except:
    print('ERROR: the playlist: ' + args.url + ' does not exist')
    sys.exit(0)


print("Collecting playlist information ...")
streams = [ item["pafy"].getbestaudio() for item in playlist['items'] ]
print("Downloading " + str(len(streams)) + " music files ...")

old_files = []
files = []

for stream in streams:
    filename = stream.title + '.' + stream.extension

    filepath =  os.path.join(Path.cwd(), filename)
    new_filepath = os.path.join(Path.cwd(), stream.title + '.mp3')

    files.append(new_filepath)
    old_files.append(filepath)

    if os.path.isfile(new_filepath):
        os.remove(new_filepath)

    child_pid = os.fork()
    if child_pid == 0:
        try :
            stream.download(Path.cwd())
        except OSError:
            stream.download(Path.cwd())

        os.execl('/usr/bin/ffmpeg', '/usr/bin/ffmpeg', '-nostats', '-loglevel', '0', '-i', filepath,"-acodec", "libmp3lame", new_filepath)
    os.wait()

for file in old_files:
    os.remove(file) 


print("All downloads are done!")

print("\n")

print("Enter the following informations (or leave blank):")
if not args.name:
    args.name = input("Album title: ")
if not args.year:
    args.year = input("Year: ")
if not args.genre:
    args.genre = input("Genre: ")
if not args.artist:
    args.artist = input("Artist: ")

print("Correct manualy the names of the songs (or leave blank to leave unchange):")
num = 1
for file in files:
    if file.endswith('.mp3'):

        path = '/'.join(file.split('/')[:-1])
        filename = '.'.join(file.split('/')[-1].split('.')[:-1])

        input_name = input(filename + " --> ")
        new_filename = input_name if input_name != '' else filename

        new_file =  path + '/' + new_filename + ".mp3"
        os.rename(file, new_file)

        audiofile = eyed3.load(new_file)
        audiofile.tag.track_num = num
        num += 1
        audiofile.tag.title = new_filename

        if args.name and args.name != "":
            audiofile.tag.album = args.name
        if args.year and args.year != "":
            audiofile.tag.year = args.year
        if args.genre and args.genre != "":
            audiofile.tag.genre = args.genre
        if args.artist and args.artist != "":
            audiofile.tag.album_artist = args.artist
            audiofile.tag.artist = args.artist
        audiofile.tag.save()

        print(new_file)

print("All done!")

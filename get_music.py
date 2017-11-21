!/usr/bin/python                                                                                                                                                                                                                                                            
"""Script for downloading youtube videos."""

import os.path
import string
import sys
import getopt

# Note:  this has to be imported like so, because just import                                                                                                                                                                                                                
# subprocess cannot find call and just the from line cannot find                                                                                                                                                                                                             
# subprocess                                                                                                                                                                                                                                                                 
import subprocess
from subprocess import call

class cmdLineUI(object):

    def __init__(self):
        self.download    = False
        self.show        = False
        self.example     = False
        self.directory = "/var/music/"


    def show_help(self):
        s = \
          "This script downloads the mp3s of Youtube videos for your music library.\n"\
          "  that have been listed in the file 'linksToGet.txt'"\
          "\nOptions:\n"\
          "-f fetch      -- download the links in the 'linksToGet.txt file\n"\
          "-s show       -- show a list of the youtube links you have, for easy sharing.\n"\
          "-e example    -- show example of linksToGet.txt.\n"\
          "-d directory <name> -- changes the default music vault directory from /var/music/ to <name>"\
          "   This is the directory that you keep your music in, not the ~/Music directory to which "\
          "   this program downloads.  Pass this option as you fetch or show your files."

        print s


    def commands(self, argv):

        try:
            opts, argv = getopt.getopt(argv, "hsd:ef",
                                       ["help","show", "directory=",
                                        "example","fetch"])
            if opts == []:
                self.show_help()

        except getopt.GetoptError:
            self.show_help()
            sys.exit(2)

        for opt, args in opts:
            if opt in ("-h", "--help"):
                show_help()
                sys.exit()
            elif opt in ("-d", "--directory"):
                if args:
                    self.directory = args
            elif opt in ("-s", "--show"):
                self.show = True
            elif opt in ("-f", "--fetch"):
                self.download = True
            elif opt in ("-e", "--example"):
                self.example = True

def check_if_youtube_dl_exists():

    try:
        _ = subprocess.check_output(["which", "youtube-dl"])
    except subprocess.CalledProcessError:
        print "youtube-dl was not found, please install it.\n"\
              "See: http://youtube-dl.org/"
        sys.exit()


def get_links_to_download():

    want_link = {}
    cur_artist = ""
    try:
        with open("linksToGet.txt", "r") as f:
            for line in f.readlines():
                line = string.replace(line, "\n", "")
                if line == '':
                    continue
                if line.startswith("#"):
                    cur_artist = line.replace("#", "")
                else:
                    want_link[string.replace(line, "https://youtu.be/", "")] = cur_artist

    except IOError:
        print "The file linksToGet.txt does not exist.\n\n"\
            "type python get_music.py -e\n"\
            "to see instructions how to create it."
        sys.exit()


    if len(want_link) == 0:
        print "The file linksToGet.txt is empty.\n\n"\
            "type python get_music.py -e\n"\
            "to see instructions how to populate it."

        sys.exit()

    return want_link


def create_music_list(directory):

    import re
    music_list = []
    for root, _, files in os.walk(directory, topdown=False):
        if root != directory:
            t_root = re.split("/",root)
            if len(t_root) > 0:
                music_list.append("#"+t_root[-1])
        for f in files:
            music_list.append("http://youtu.be/"+f[-15:-4])
    return music_list


def download_items(cmd):

    want_link = get_links_to_download()

    musicpath = os.path.expanduser('~')+"/Music"

    try:
        os.stat(musicpath)
    except OSError:
        os.mkdir(musicpath)
    os.chdir(musicpath)


    for k, v in want_link.iteritems():
        songpath = musicpath+"/"+v.strip()
        downloaditem = "http://youtu.be/"+k
        existing_music = []

        # We save the youtube id in the last 15 characters.                                                                                                                                                                                                                  
        for f in os.walk(cmd.directory):
            for s in f[2]:
                existing_music.append(s[-15:])

        try:
            os.stat(songpath)
        except OSError:
            os.mkdir(songpath)

        os.chdir(songpath)

        # The syntax for youtube-dl is:                                                                                                                                                                                                                                      
        #   youtube-dl --extract-audio --audio-format mp3 <url>                                                                                                                                                                                                              
        if not k in existing_music and not os.path.exists(downloaditem):
            call(["youtube-dl", "--extract-audio",
                  "--audio-format", "mp3", downloaditem])

    print ("Download complete.\n"
          "Please copy the contents of ~/Music to "
          "/var/music and empty the linksToGet.txt file.")


def show_linksToGet_example():
    s = \
        "\nExample of file contents for linksToGet.txt:\n\n"\
        "#The_Altai_band_from_Mongolia\n"\
        "https://youtu.be/7RujKG9hmCY\n"\
        "#DjangoReinhardt\n"\
        "https://youtu.be/a1j8VLPasO0\n"\
        "https://youtu.be/QAaOI0cAjhc\n"\
        "\nThis produces the following result in your ~/Music directory:\n"\
        "you@computer$ ls -R ~/Music/\n"\
        "/home/you/Music/:\n"\
        "DjangoReinhardt\n"\
        "The_Altai_band_from_Mongolia\n"\
        "\n"\
        "/home/you/Music/DjangoReinhardt:\n"\
        "Django Reinhardt & Stephane Grappelli - I Got Rhythm (Past Perfect) [Full Album]-QAaOI0cAjhc.mp3\n"\
        "Django Reinhardt - Sultan Of Swing-a1j8VLPasO0.mp3\n"\
        "\n"\
        "/home/you/Music/The_Altai_band_from_Mongolia:\n"\
        "The Altai band from Mongolia-7RujKG9hmCY.mp3\n"\
        "\n"\
        "The links are obtained from the youtube 'share' button.\n"\
        "You can have multiple artists/directories and links.\n"\
        "This program writes to the Music directory in your home and\n"\
        "checks ~/Music/* and /var/music/* if the file(s) you want already\n"\
        "exist before it downloads them.\n"\
        "If a directory does not exist it will be created.\n"\
        ""
    print s
    sys.exit()


def main(argv):

    cmd = cmdLineUI()
    cmd.commands(argv)

    if cmd.example == True:
        show_linksToGet_example()
    elif cmd.show == True:
        print "\n".join(create_music_list(cmd.directory))
    elif cmd.download == True:
        check_if_youtube_dl_exists()
        download_items(cmd)


if __name__ == '__main__':
    main(sys.argv[1:])



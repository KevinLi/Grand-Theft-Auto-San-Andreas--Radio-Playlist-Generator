import os

class PlaylistWriter(object):
    def __init__(self, filedir, filename):
        self.f = open(filename+".m3u", "a")
        self.filedir = filedir
        self.add_header()

    def add_header(self):
        self.f.write("#EXTM3U\n\n")

    def add_track(self, title, time, filepath):
        self.f.write("#EXTINF:{0},{1}\n{2}\n\n".format(time, title, self.filedir+os.sep+filepath))

    def close(self):
        self.f.close()

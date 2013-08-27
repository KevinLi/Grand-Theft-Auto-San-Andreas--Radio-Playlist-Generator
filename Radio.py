import datetime

import RadioChannels
import PlaylistGenerator

class PlaylistOptions(object):
    def __init__(self):
        self.musicdir = "STREAMS"
        self.time = 7200 # 2 hours
        self.ads = True
        self.dj = True
        
        self.gen()
    
    def gen(self):
        for channel in RadioChannels.channels:
            if channel != "Adverts":
                p = PlaylistGenerator.PlaylistGenerator(self.musicdir, channel, self.time, self.ads, self.dj)
                print(
                    "{0} playlist duration: {1}".format(
                        RadioChannels.channels[channel]["name"].ljust(16),
                        datetime.timedelta(seconds=round(p.get_total_length_sec()))
                    )
                )
        print()

if __name__ == "__main__":
    PlaylistOptions()

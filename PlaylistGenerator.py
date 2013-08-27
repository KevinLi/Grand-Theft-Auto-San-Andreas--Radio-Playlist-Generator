import os
from collections import deque
import datetime
import random

import RadioChannels as rc
import PlaylistWriter

class PlaylistGenerator(object):
    def __init__(self, musicdir, internalchannelname, time, ads, dj):
        self.internalchannelname = internalchannelname

        self.songs = rc.channels[internalchannelname]["ref"].songs
        self.channelname = rc.channels[internalchannelname]["name"]

        self.writer = PlaylistWriter.PlaylistWriter(musicdir, self.channelname)

        t = datetime.datetime.now()
        self.curtime = [t.hour, t.minute+5-t.minute%5, 0]
        #time events based on current time
        self.reset_time_today = False

        #total playlist time in seconds
        self.time = 0
        self.requested_length = time
        self.morning = []
        self.evening = []
        self.night = []

        self.tracks_last_played = deque()
        self.dj_last_played = deque()
        self.ad_last_played = deque()
        self.rn_last_played = deque()

        self.ads = ads
        if self.ads:
            self.adverts = rc.channels["Adverts"]["ref"].adverts
            self.time_since_ad = 0
            self.tracks_since_ad = 0

        self.dj = dj
        if self.dj:
            self.dj_talk = rc.channels[internalchannelname]["ref"].dj_talk
            self.time_since_dj = 0
            self.tracks_since_dj = 0

        self.rn = True
        self.radio_name = rc.channels[internalchannelname]["ref"].radio_name
        self.time_since_rn = 0
        self.tracks_since_rn = 0

        self.gen_playlist()

    def gen_playlist(self):
        tracks = list(self.songs.keys())
        adverts = list(self.adverts.keys())

        if self.dj:
            dj_talk = list(self.dj_talk.keys())
        if not dj_talk:
            self.dj = False

        radio_name = list(self.radio_name.keys())
        if not radio_name:
            self.rn = False

        self.reset_time_events()

        while self.time < self.requested_length:
            track_length = 0

            #Reset time events counter once a day
            if self.curtime[0] == 0 and self.reset_time_today == False:
                self.reset_time_events()
                self.reset_time_today = True
            elif self.curtime[0] >= 1:
                self.reset_time_today = False

            # Time events
            if self.curtime[0] == 7 and self.curtime[1] < 30 and len(self.morning) > 0:
                track = random.choice(self.morning)
                track_length = rc.channels[self.internalchannelname]["ref"].time.morning[track]
                self.writer.add_track(track, track_length, self.channelname+os.sep+track)
                self.morning.remove(track)
            elif self.curtime[0] == 18 and self.curtime[1] < 30 and len(self.evening) > 0:
                track = random.choice(self.evening)
                track_length = rc.channels[self.internalchannelname]["ref"].time.evening[track]
                self.writer.add_track(track, track_length, self.channelname+os.sep+track)
                self.evening.remove(track)
            elif self.curtime[0] == 21 and self.curtime[1] < 30 and len(self.night) > 0:
                track = random.choice(self.night)
                track_length = rc.channels[self.internalchannelname]["ref"].time.night[track]
                self.writer.add_track(track, track_length, self.channelname+os.sep+track)
                self.night.remove(track)

            self.time += track_length
            self.update_time(track_length)
            self.ad_time(track_length)
            self.dj_time(track_length)
            self.rn_time(track_length)

            # Ads, DJ, RN
            if self.ads and self.time_since_ad > 720 and self.tracks_since_ad > random.randint(2, 5):
                track = self.next_ad(adverts)
                track_length = self.adverts[track]

                self.writer.add_track(track, track_length, "Adverts"+os.sep+track)

                self.ad_time(0)
                self.dj_time(track_length)
                self.rn_time(track_length)

                self.ad_last_played.append(track)

            elif self.rn and self.time_since_rn > 360 and self.tracks_since_rn > random.randint(1,2):
                track = self.next_rn(radio_name)
                track_length = self.radio_name[track]

                self.writer.add_track(track, track_length, self.channelname+os.sep+track)

                self.ad_time(track_length)
                self.dj_time(track_length)
                self.rn_time(0)

                self.rn_last_played.append(track)

            elif dj_talk and self.time_since_dj > random.randint(210, 480) and self.tracks_since_dj > random.randint(1,2):
                track = self.next_dj(dj_talk)
                track_length = self.dj_talk[track]

                self.writer.add_track(track, self.dj_talk[track], self.channelname+os.sep+track)

                self.ad_time(track_length)
                self.dj_time(0)
                self.rn_time(track_length)

                self.dj_last_played.append(track)

            self.time += track_length
            self.update_time(track_length)

            #Tracks
            track = self.next_track(tracks)

            #(1) No DJ Intros/Outros:
            if self.songs[track][3] == 1:
                self.write_intro(track, (0, 0))
                self.write_main(track)
                self.write_outro(track, (0, 0))

            #(2) Only DJ Intros/Outros
            elif self.songs[track][3] == 2:
                self.write_intro(track, (1, 2))
                self.write_main(track)
                self.write_outro(track, (1, 2))

            #(3) No DJ Intros
            elif self.songs[track][3] == 3:
                self.write_intro(track, (0, 0))
                self.write_main(track)
                self.write_outro(track, (0, 2))

            #(4) No DJ Outros
            elif self.songs[track][3] == 4:
                self.write_intro(track, (0, 2))
                self.write_main(track)
                self.write_outro(track, (0, 0))

            #(5) No DJ2 Intros/Outros
            elif self.songs[track][3] == 5:
                self.write_intro(track, (0, 2))
                self.write_main(track)
                self.write_outro(track, (0, 1))

            #(6) No DJ2 Intro
            elif self.songs[track][3] == 6:
                self.write_intro(track, (0, 1))
                self.write_main(track)
                self.write_outro(track, (0, 1))

            #(7) No DJ2 Outro
            elif self.songs[track][3] == 7:
                self.write_intro(track, (0, 2))
                self.write_main(track)
                self.write_outro(track, (0, 1))

            #(0) Normal
            elif self.songs[track][3] == 0:
                self.write_intro(track, (0, 2))
                self.write_main(track)
                self.write_outro(track, (0, 2))

            total_track_length = self.songs[track][0] + self.songs[track][1] + self.songs[track][2]
            self.time += total_track_length
            self.update_time(total_track_length)

            self.ad_time(total_track_length)
            self.dj_time(total_track_length)
            self.rn_time(total_track_length)

            self.tracks_last_played.append(track)

        self.writer.close()

    def ad_time(self, length):
        if self.ads:
            if length == 0:
                self.time_since_ad = 0
                self.tracks_since_ad = 0
            else:
                self.time_since_ad += length 
                self.tracks_since_ad += 1

    def dj_time(self, length):
        if self.dj:
            if length == 0:
                self.time_since_dj = 0
                self.tracks_since_dj = 0
            else:
                self.time_since_dj += length
                self.tracks_since_dj += 1

    def rn_time(self, length):
        if self.rn:
            if length == 0:
                self.time_since_rn = 0
                self.tracks_since_rn = 0
            else:
                self.time_since_rn += length
                self.tracks_since_rn += 1

    def write_intro(self, track, range):
        intro = 0
        if self.dj or range[0] != 0:
            intro = random.randint(range[0], range[1])
        if intro == 0:
            self.writer.add_track(track, self.songs[track][0], self.channelname+os.sep+track+" (Intro).ogg")
        else:
            self.writer.add_track(track, self.songs[track][0], self.channelname+os.sep+track+" (Intro DJ "+str(intro)+").ogg")

    def write_main(self, track):
        self.writer.add_track(track, self.songs[track][1], self.channelname+os.sep+track+".ogg")

    def write_outro(self, track, range):
        outro = 0
        if self.dj or range[0] != 0:
            outro = random.randint(range[0], range[1])
        if outro == 0:
            self.writer.add_track(track, self.songs[track][2], self.channelname+os.sep+track+" (Outro).ogg")
        else:
            self.writer.add_track(track, self.songs[track][2], self.channelname+os.sep+track+" (Outro DJ "+str(outro)+").ogg")

    def next_ad(self, tracks):
        track = random.choice(tracks)
        if len(self.ad_last_played) >= 10:
            self.ad_last_played.popleft()
        if track in self.ad_last_played:
            return self.next_ad(tracks)
        else:
            return track

    def next_dj(self, tracks):
        track = random.choice(tracks)
        if len(self.dj_last_played) >= 10:
            self.dj_last_played.popleft()
        if track in self.dj_last_played:
            return self.next_dj(tracks)
        else:
            return track

    def next_rn(self, tracks):
        track = random.choice(tracks)
        if len(self.rn_last_played) >= 4:
            self.rn_last_played.popleft()
        if track in self.rn_last_played:
            return self.next_rn(tracks)
        else:
            return track

    def next_track(self, tracks):
        track = random.choice(tracks)
        if len(self.tracks_last_played) >= 7:
            self.tracks_last_played.popleft()
        if track in self.tracks_last_played:
            return self.next_track(tracks)
        else:
            return track

    def update_time(self, seconds):
        self.curtime[2] += seconds
        if self.curtime[2] >= 60:
            self.curtime[2] %= 60
            self.curtime[1] += seconds/60
        if self.curtime[1] >= 60:
            self.curtime[1] %= 60
            self.curtime[0] += 1
        if self.curtime[0] >= 24:
            self.curtime[0] %= 24
            self.time_played = [0, 0, 0]

    def reset_time_events(self):
        self.morning = list(rc.channels[self.internalchannelname]["ref"].time.morning.keys())
        self.evening = list(rc.channels[self.internalchannelname]["ref"].time.evening.keys())
        self.night = list(rc.channels[self.internalchannelname]["ref"].time.night.keys())

    def get_total_length_sec(self):
        return self.time

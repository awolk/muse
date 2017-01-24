#!/usr/local/bin/python3

import struct, subprocess
from music import BaseRenderer

class LogRenderer(BaseRenderer):
    names = {
        0: "C",
        1: "C#",
        2: "D",
        3: "D#",
        4: "E",
        5: "F",
        6: "F#",
        7: "G",
        8: "G#",
        9: "A",
        10: "A#",
        11: "B",
    }
    def note_on(self, delta_time, channel, note, velocity):
        name = LogRenderer.names[note % 12]
        print("{} Note On: {} ({})".format(delta_time, note, name))
    def note_off(self, delta_time, channel, note, velocity):
        name = LogRenderer.names[note % 12]
        print("{} Note Off: {} ({})".format(delta_time, note, name))

class MIDIRenderer(BaseRenderer):
    def __init__(self):
        self.buffer = b""
        self.eb = b""  # Event buffer
    def start(self, song):
        # Format 0, 1 Track, time divison
        self.buffer += b"MThd" + struct.pack(">IHHh",
                                             6, 0, 1, 96)
    def note_on(self, delta_time, channel, note, velocity):
        assert channel < 16
        assert note < 128
        assert velocity < 128
        evt = struct.pack("BBB", 144 + channel, note, velocity)
        self.eb += self.variable_length(self.ticks(delta_time)) + evt
    def note_off(self, delta_time, channel, note, velocity):
        assert channel < 16
        assert note < 128
        assert velocity < 128
        evt = struct.pack("BBB", 128 + channel, note, velocity)
        self.eb += self.variable_length(self.ticks(delta_time)) + evt
    def finalize(self):
        self.eb += struct.pack("BBBB", 0, 255, 47, 0)
        self.buffer += b"MTrk" + struct.pack(">I", len(self.eb)) + self.eb
    @staticmethod
    def ticks(sec):
        tempo = 120 # bpm
        division = 96
        return int(sec * tempo * division / 60)
    @staticmethod
    def variable_length(n, end=True):
        encode = lambda x: bytes([x])
        if n <= 127:
            if end:
                return encode(n)
            return encode(n + 128)
        start, last7 = n >> 7, n & 127
        if end:
            return MIDIRenderer.variable_length(start, False) + encode(last7)
        return MIDIRenderer.variable_length(start, False) + encode(last7 + 128)
    def write(self, filename):
        f = open(filename + ".mid", "wb")
        f.write(self.buffer)
        f.close()
        #subprocess.call(["fluidsynth", "-F", filename + ".raw", "-i", "font.sf2", filename + ".mid"])
        #subprocess.call(["sox", "-t", "raw", "-r", "44100", "-e",
        #                 "signed-integer", "-b", "16", "-c", "2",
        #                filename + ".raw", "-t", "wav", filename + ".wav"])
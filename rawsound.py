import wave, math, functools, array
from music import BaseRenderer

class RenderFunctions:
    sin = math.sin
    def sawtooth(x):
        p = x / math.pi / 2
        return 2 * (p - math.floor(.5 + p))
    def triangle(x):
        return 2 * abs(RenderFunctions.sawtooth2(x)) - 1
    def sawtooth2(x):
        return ((x / math.pi - 1) % 2) - 1
    def square(x):
        x %= 2 * math.pi
        if 0 <= x <= math.pi:
            return 1
        else:
            return -1

class WaveRenderer(BaseRenderer):
    def __init__(self, framerate = 44100, sampwidth = 2, sin_func=RenderFunctions.sin):
        self.framerate = framerate
        self.sampwidth = sampwidth
        self.buffer = b""
        self.sin = sin_func
    @staticmethod
    def max_notes_on(song):
        class NotesOnRenderer(BaseRenderer):
            def __init__(self):
                self.notes_on = []
                self.max_notes_on = 0
            def note_on(self, delta_time, channel, note, velocity):
                self.notes_on.append(note)
                self.max_notes_on = max(self.max_notes_on, len(self.notes_on))
            def note_off(self, delta_time, channel, note, velocity):
                self.notes_on.remove(note)
        nor = NotesOnRenderer()
        song.render(nor)
        return nor.max_notes_on
    def start(self, song):
        self.max_amp = (2 ** (self.sampwidth * 8)) / 2
        self.use_amp = (self.max_amp - 1) / self.max_notes_on(song)
        self.freqs = []
        self.t = 0
    def pack_array(self, value):
        if self.sampwidth == 1:
            return array.array("b", value).tostring()
        elif self.sampwidth == 2:
            return array.array("h", value).tostring()
        elif self.sampwidth == 4:
            return array.array("i", value).tostring()
    def wave_func(self, freq, amp, time):
        return int(self.sin(2 * math.pi * freq * time) * amp)
    @staticmethod
    @functools.lru_cache()
    def frequency(note):
        return 440 * (2 ** ((note-69)/12))
    def generate(self, delta_time):
        buff = []
        finish = self.t + delta_time
        while self.t <= finish:
            value = sum([int(self.sin(f * self.t) * self.use_amp)
                         for f in self.freqs])
            buff.append(value)
            self.t += 1/self.framerate
        self.buffer += self.pack_array(buff)
    def note_on(self, delta_time, channel, note, velocity):
        self.generate(delta_time)
        self.freqs.append(self.frequency(note) * 2 * math.pi)
    def note_off(self, delta_time, channel, note, velocity):
        self.generate(delta_time)
        self.freqs.remove(self.frequency(note) * 2 * math.pi)
    def write(self, filename):
        w = wave.open(filename + ".wav", "w")
        w.setparams((1, self.sampwidth, self.framerate, 0, "NONE", "not compressed"))
        w.writeframes(self.buffer)
        w.close()
class Note:
    def __init__(self, info, start, end, melody=True):
        self.info = info
        self.start = start
        self.end = end
        self.melody = melody

class Chord(list):
    def __rshift__(self, other):
        return Chord([note + other for note in self])
    def __lshift__(self, other):
        return Chord([note - other for note in self])
    def __add__(self, other):
        return Chord(list(self) + [other])

def inversion(chord, times=1):
    chord = Chord(sorted(chord))
    for _ in range(times):
        chord.append(chord.pop(0)+12)
    return chord

class Song:
    START = 0
    END = 1
    def __init__(self):
        self.events = []
    def __iadd__(self, other):
        combined = False
        for evt in self.events:
            if (evt.info == other.info) and (evt.melody == other.melody):
                if evt.end == other.start:
                    self.events.remove(evt)
                    self.events.append(Note(evt.info, evt.start, other.end, evt.melody))
                    combined = True
                    break
                elif evt.start == other.end:
                    self.events.remove(evt)
                    self.events.append(Note(evt.info, other.start, evt.end, evt.melody))
                    combined = True
                    break
        if not combined:
            self.events.append(other)
        return self
    def render(self, renderer):
        order = []
        for e in self.events:
            order.append((self.START, e.start, e))
            order.append((self.END, e.end, e))
        order.sort(key=lambda i: i[1])
        renderer.start(self)
        last_time = 0
        for signal, time, evt in order:
            if isinstance(evt, Note):
                channel = int(not evt.melody)
            else:
                channel = 0
            if signal == self.START:
                renderer.note_on(time-last_time, channel, evt.info, 127)
            elif signal == self.END:
                renderer.note_off(time-last_time, channel, evt.info, 127)
            last_time = time
        renderer.finalize()

class BaseRenderer:
    def start(self, num_notes): pass
    def note_on(self, delta_time, channel, note, velocity): pass
    def note_off(self, delta_time, channel, note, velocity): pass
    def finalize(self): pass
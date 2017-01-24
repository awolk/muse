import random
from harmony import voice_leading, parse_num_not, diatonics
from music import Note

random = random.Random()

class SongGen:
    @staticmethod
    def entire_scale(notes):
        base_notes = {n % 12 for n in notes}
        result = list(base_notes)
        multiplier = 1
        while max(result) < 126:
            for n in base_notes:
                result.append(n+12*multiplier)
            multiplier += 1
        return result
    progressions =[
        "I IV6/4 V6/5 I",
        "I vi6 ii V6/5 I",
        "I V vi IV I",
        "I V IV I",
    ]
    def __init__(self, song, seed=None):
        if seed is not None:
            random.seed(seed)
        self.key = random.randint(60, 72)
        self.keysig = self.entire_scale(diatonics(self.key))
        prog_not = random.choice(self.progressions)
        self.progression = voice_leading([parse_num_not(self.key, num) for num in prog_not.split()])
        self.progression_step = 0
        self.end = False
        self.song_struct = []
        self.pos = 0
        self.length = random.randint(5, 15) * len(self.progression)
        self.cur_note = random.choice(self.progression[0])
        self.ascending = True
        self.last_step = "next_measure"
        self.steps = {
            "upp_neb": random.randint(1, 10),
            "low_neb": random.randint(1, 10),
            "cont": random.randint(1, 10),
            "pass_tone": random.randint(1, 10),
            "random": random.randint(1, 10),
            "change_dir": random.randint(1, 10),
            "next_measure": random.randint(1, 10)
        }
        self.run()
        self.gen_song(song)
    def run(self):
        while self.pos < self.length:
            self.gen_measure()
    def next_step(self):
        options = [k for k in self.steps for _ in range(self.steps[k])]
        for _ in range(int(self.steps[self.last_step] / 2)):
            options.remove(self.last_step)
        self.last_step = random.choice(options)
        return self.last_step
    def gen_measure(self):
        measure = []
        notes = self.progression[self.progression_step]
        note_scale = self.entire_scale(notes)
        step = self.next_step()
        while ((step != "next_measure") or (len(measure) == 0)) and len(measure) < random.randint(5, 10):
            if step == "upp_neb":
                measure.append(self.keysig[self.keysig.index(self.cur_note) + 1])
                measure.append(self.cur_note)
            elif step == "low_neb":
                measure.append(self.keysig[self.keysig.index(self.cur_note) - 1])
                measure.append(self.cur_note)
            elif step == "cont":
                if self.ascending:
                    while not (self.cur_note in note_scale):
                        self.cur_note += 1
                    self.cur_note = note_scale[note_scale.index(self.cur_note) + 1]
                    measure.append(self.cur_note)
                else:
                    while not (self.cur_note in note_scale):
                        self.cur_note -= 1
                    self.cur_note = note_scale[note_scale.index(self.cur_note) - 1]
                    measure.append(self.cur_note)
            elif step == "pass_tone":
                if self.ascending:
                    measure.append(self.keysig[self.keysig.index(self.cur_note) + 1])
                    while not (self.cur_note in note_scale):
                        self.cur_note += 1
                    self.cur_note = note_scale[note_scale.index(self.cur_note) + 1]
                    measure.append(self.cur_note)
                else:
                    measure.append(self.keysig[self.keysig.index(self.cur_note) - 1])
                    while not (self.cur_note in note_scale):
                        self.cur_note -= 1
                    self.cur_note = note_scale[note_scale.index(self.cur_note) - 1]
                    measure.append(self.cur_note)
            elif step == "random":
                self.cur_note = random.choice(notes)
            elif step == "change_dir":
                self.ascending = not self.ascending
            step = self.next_step()
            if self.cur_note > self.key+15:
                self.ascending = False
            elif self.cur_note < self.key-15:
                self.ascending = True
        self.pos += 1
        self.progression_step = (self.progression_step + 1) % len(self.progression)
        self.song_struct.append((measure, notes))
    def gen_song(self, song):
        pos = 0
        tempo = random.uniform(0.25, 0.5)
        tempo_status = random.randint(-1, 1) # 1: inc, 0: cons, -1: dec
        tempo_reliability = random.random()*random.random()
        for melody, harmony in self.song_struct:
            measure_start = pos
            for note in melody:
                song += Note(note, pos, pos + tempo, True)
                pos += tempo
                if tempo_status == -1:
                    tempo -= random.uniform(0.01, 0.05)
                    if random.random() < tempo_reliability:
                        tempo_status = 0
                elif tempo_status == 1:
                    tempo += random.uniform(0.01, 0.05)
                    if random.random() < tempo_reliability:
                        tempo_status = 0
                else:
                    if random.random() > tempo_reliability:
                        tempo_status = random.choice([-1, 0, 1])
                if tempo < 0.25:
                    tempo_status = 1
                elif tempo > .5:
                    tempo_status = -1
            for note in harmony:
                song += Note(note, measure_start, pos, False)
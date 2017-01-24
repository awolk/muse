try:
    from statistics import mean
except ImportError:
    def mean(x):
        return sum(x)/len(x)
from music import inversion, Chord
import re

parser = re.compile(r"^([iv]+|[IV]+)([+|o]?)((?:[0-9]+)(?:\/[0-9]+)*)?$")
intervals = {
    "I": 1, "II": 2, "III": 3, "IV": 4, "V": 5, "VI": 6, "VII": 7
}
fig_base_parser = {
    None: (False, 0),
    "6": (False, 1),
    "6/4": (False, 2),
    "7": (True, 0),
    "6/5": (True, 1),
    "4/3": (True, 2),
    "2": (True, 3)
}

def diatonics(base):
    return [base, base+2, base+4, base+5, base+7, base+9, base+11, base+12]

def parse_num_not(base, num_not):
    interval_num, aug_or_dim, fig_base = parser.match(num_not).groups()
    interval = intervals[interval_num.upper()]
    base = diatonics(base)[interval-1]
    seventh, chord_inversion = fig_base_parser[fig_base]
    major = interval_num.isupper()
    if aug_or_dim == "+":
        chord = Chord([base, base+4, base+7])
    elif aug_or_dim == "o":
        chord = Chord([base, base+3, base+6])
    else:
        if major:
            chord = Chord([base, base+4, base+7])
        else:
            chord = Chord([base, base+3, base+7])
    if seventh:
        chord.append(base+10)
    return inversion(chord, chord_inversion)

def voice_leading(chords):
    vl_chords = []
    for i, c in enumerate(chords):
        if i == 0:
            vl_chords.append(c)
        else:
            vl_chords.append(voice_lead(vl_chords[i-1], c))
    return vl_chords
def voice_lead(chord1, chord2):
    avg_chord1 = mean(chord1)
    avg_chord2 = mean(chord2)
    while avg_chord2 > avg_chord1:
        chord2 <<= 12
        avg_chord2 = mean(chord2)
    dist1 = avg_chord1 - avg_chord2
    chord2 >>= 12
    avg_chord2 = mean(chord2)
    dist2 = abs(avg_chord1 - avg_chord2)
    if dist1 < dist2:
        return chord2 << 12
    else:
        return chord2
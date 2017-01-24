import random
from basesonggen import SongGen
from midi import MIDIRenderer
from music import Song
from rawsound import WaveRenderer, RenderFunctions
import subprocess

# short seed: 0.0666452736373695
seed = random.random()
s = Song()
print("seed: {}".format(seed))
SongGen(s, seed)

renderer_mid = MIDIRenderer()
s.render(renderer_mid)
renderer_mid.write("out_mid")
subprocess.call(["open", "out_mid.wav", "-a", "Quicktime Player"])

renderer_wav = WaveRenderer(framerate=44100, sampwidth=2, sin_func=RenderFunctions.sawtooth2)
s.render(renderer_wav)
renderer_wav.write("out_wav")
#subprocess.call(["open", "out_wav.wav", "-a", "Quicktime Player"])
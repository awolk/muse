all: midi.py font.sf2
	python3 main.py
	fluidsynth -i font.sf2 out.mid
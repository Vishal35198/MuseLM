import music21
import glob
from datasets.transformer_utils import (
    parse_midi_files,
    load_parsed_files
    )

file_list = glob.glob("data/bach-cello/*.mid")
print(f"Found {len(file_list)} midi files in the data")
print(file_list[1])


SEQ_LEN = 50
PARSED_DATA_PATH = "parsed_data"
PARSE_MIDI_FILES = False

parser = music21.converter

example_score = (
    music21.converter.parse(
        file_list[1]
    )
    .splitAtQuarterLength(12)[0]
    .chordify()
)

# example_score.show()
example_score.show("text")


if PARSE_MIDI_FILES:
    notes, durations = parse_midi_files(
        file_list, parser, SEQ_LEN + 1
    )
else:
    notes, durations = load_parsed_files(PARSED_DATA_PATH)
    
example_notes = notes[658]
example_durations = durations[658]
print("\nNotes string\n", example_notes, "...")
print("\nDuration string\n", example_durations, "...")
print(f"Length of the notes are {len(notes)}")
print(f"Length of the durations are {len(durations)}")
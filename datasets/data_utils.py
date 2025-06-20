import os
import pickle as pkl
import music21

from fractions import Fraction


# def parse_midi_files(file_list, parser, seq_len):
#     notes_list = []
#     duration_list = []
#     notes = []
#     durations = []

#     for i, file in enumerate(file_list):
#         print(i + 1, "Parsing %s" % file)
#         score = parser.parse(file)

#         notes.append("START")
#         durations.append("0.0")

#         for element in score.flat:
#             note_name = None
#             duration_name = None

#             # if isinstance(element, music21.key.Key):
#             #     note_name = str(element.tonic.name) + ":" + str(element.mode)
#             #     duration_name = "0.0"

#             # elif isinstance(element, music21.meter.TimeSignature):
#             #     note_name = str(element.ratioString) + "TS"
#             #     duration_name = "0.0"

#             # elif isinstance(element, music21.chord.Chord):
#             #     note_name = element.pitches[-1].nameWithOctave
#             #     duration_name = str(element.duration.quarterLength)

#             if isinstance(element, music21.note.Rest):
#                 note_name = str(element.name)
#                 duration_name = str(element.duration.quarterLength)

#             elif isinstance(element, music21.note.Note):
#                 note_name = str(element.nameWithOctave)
#                 duration_name = str(element.duration.quarterLength)

#             if note_name and duration_name:
#                 notes.append(note_name)
#                 durations.append(duration_name)
#         print(f"{len(notes)} notes parsed")

#     notes_list = []
#     duration_list = []
#     # dyanmically create a parsed_data
#     parsed_data_path = "/parsed_new_data"
#     os.makedirs(parsed_data_path, exist_ok=True)
#     print(f"Building sequences of length {seq_len}")
#     for i in range(len(notes) - seq_len):
#         notes_list.append(" ".join(notes[i : (i + seq_len)]))
#         duration_list.append(" ".join(durations[i : (i + seq_len)]))

#     if parsed_data_path:
#         with open(os.path.join(parsed_data_path, "notes.pkl"), "wb") as f:
#             pkl.dump(notes_list, f)
#         with open(os.path.join(parsed_data_path, "durations.pkl"), "wb") as f:
#             pkl.dump(duration_list, f)
#     else:
#         print("Paresed Path data ")

#     return notes_list, duration_list
import os
import pickle as pkl
import music21
from collections import Counter

def get_clean_vocab(notes):
    all_notes = []
    for seq_str in notes:
        all_notes.extend(seq_str.strip().split(" "))
    # Step 2: Count note frequencies
    note_counts = Counter(all_notes)

    # Step 3: Build vocabulary
    note_vocab = {note: idx for idx, (note, _) in enumerate(note_counts.most_common())}
    note_reverse_vocab = {idx: note for note, idx in note_vocab.items()}
    return note_vocab,note_reverse_vocab

def parse_midi_files(file_list, parser, seq_len, max_rest_ratio=0.2):
    notes = []
    durations = []

    for i, file in enumerate(file_list):
        print(f"{i + 1}. Parsing {file}")
        try:
            score = parser.parse(file)
        except Exception as e:
            print(f"Error parsing {file}: {e}")
            continue

        # First pass: collect all notes and rests
        temp_notes = []
        temp_durations = []
        
        for part in score.parts:
            for element in part.recurse().notesAndRests:
                note_name = None
                duration_name = None

                if isinstance(element, music21.note.Note):
                    note_name = str(element.nameWithOctave)
                    duration_name = str(element.duration.quarterLength)
                elif isinstance(element, music21.chord.Chord):
                    # Use highest pitch for melody
                    note_name = element.pitches[-1].nameWithOctave
                    duration_name = str(element.duration.quarterLength)
                elif isinstance(element, music21.note.Rest):
                    note_name = "rest"
                    duration_name = str(element.duration.quarterLength)

                if note_name and duration_name:
                    temp_notes.append(note_name)
                    temp_durations.append(duration_name)
        
        # Calculate rest ratio and filter if needed
        rest_count = temp_notes.count("rest")
        total_elements = len(temp_notes)
        rest_ratio = rest_count / total_elements if total_elements > 0 else 0
        
        if rest_ratio <= max_rest_ratio or max_rest_ratio == -1:
            notes.extend(temp_notes)
            durations.extend(temp_durations)
        else:
            print(f"Skipping {file} - rest ratio {rest_ratio:.2f} exceeds threshold {max_rest_ratio}")

    print(f"Total notes collected: {len(notes)}")
    print(f"Rest ratio in final dataset: {notes.count('rest')/len(notes):.2f}")

    # Build sequences
    parsed_data_path = "parsed_clean_data"
    os.makedirs(parsed_data_path, exist_ok=True)

    notes_list = []
    duration_list = []
    print(f"Building sequences of length {seq_len}...")

    for i in range(len(notes) - seq_len):
        # Skip sequences that are mostly rests
        current_seq = notes[i:i + seq_len]
        if current_seq.count("rest") / seq_len <= max_rest_ratio:
            notes_seq = " ".join(current_seq)
            durations_seq = " ".join(durations[i : i + seq_len])
            notes_list.append(notes_seq)
            duration_list.append(durations_seq)

    # Save sequences
    with open(os.path.join(parsed_data_path, "notes.pkl"), "wb") as f:
        pkl.dump(notes_list, f)
    with open(os.path.join(parsed_data_path, "durations.pkl"), "wb") as f:
        pkl.dump(duration_list, f)

    print("Parsing complete ✅")
    return notes_list, duration_list



def load_parsed_files(parsed_data_path):
    with open(os.path.join(parsed_data_path, "notes.pkl"), "rb") as f:
        notes = pkl.load(f)
    with open(os.path.join(parsed_data_path, "durations.pkl"), "rb") as f:
        durations = pkl.load(f)
    return notes, durations


def get_midi_note(sample_note, sample_duration):
    new_note = None

    if "TS" in sample_note:
        new_note = music21.meter.TimeSignature(sample_note.split("TS")[0])

    elif "major" in sample_note or "minor" in sample_note:
        tonic, mode = sample_note.split(":")
        new_note = music21.key.Key(tonic, mode)

    elif sample_note == "rest":
        new_note = music21.note.Rest()
        new_note.duration = music21.duration.Duration(
            float(Fraction(sample_duration))
        )
        new_note.storedInstrument = music21.instrument.Violoncello()

    elif "." in sample_note:
        notes_in_chord = sample_note.split(".")
        chord_notes = []
        for current_note in notes_in_chord:
            n = music21.note.Note(current_note)
            n.duration = music21.duration.Duration(
                float(Fraction(sample_duration))
            )
            n.storedInstrument = music21.instrument.Violoncello()
            chord_notes.append(n)
        new_note = music21.chord.Chord(chord_notes)

    elif sample_note == "rest":
        new_note = music21.note.Rest()
        new_note.duration = music21.duration.Duration(
            float(Fraction(sample_duration))
        )
        new_note.storedInstrument = music21.instrument.Violoncello()

    elif sample_note != "START":
        new_note = music21.note.Note(sample_note)
        new_note.duration = music21.duration.Duration(
            float(Fraction(sample_duration))
        )
        new_note.storedInstrument = music21.instrument.Violoncello()

    return new_note
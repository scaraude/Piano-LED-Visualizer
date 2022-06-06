from mappers.maps import midi_note_to_literal_note_map


def map_midi_note_to_literal_note(midiNote):
    return midi_note_to_literal_note_map[midiNote]

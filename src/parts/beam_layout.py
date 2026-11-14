"""Reconciled S05-07 deck-beam and stern-timber schedule. Data only."""
import json
from pathlib import Path

_RECORD = json.loads((Path(__file__).resolve().parents[2] /
                      'references/drawing_package/m4_deck_schedule.json').read_text())

BEAMS = _RECORD['members']
STERN_TIMBERS = _RECORD['stern_timbers']

# Each opening is carried by the source beam sets on its aft and fore sides.
# The after-deck hatch has no separate aft header: its carlings bear on the
# cabin fore header (set 17), as the milestone note anticipated.
OPENING_SUPPORTS = {
    'Forepeak hatch': {'aft': 6, 'fore': 5},
    'Main hold hatch': {'aft': 10, 'fore': 7},
    'After deck hatch': {'aft': 17, 'fore': 15},
    'Cabin deck opening': {'aft': 21, 'fore': 17},
}


def forward(beam):
    """Build station: source pick, snapped by <= the pick allowance only
    where needed to keep a measured opening clear."""
    return beam['build_forward_ft']


def by_set(number):
    return next(beam for beam in BEAMS if beam['set'] == number)


def opening_support(opening_name, end):
    return by_set(OPENING_SUPPORTS[opening_name][end])


def opening_splits(opening_name):
    return [beam for beam in BEAMS
            if beam['role'] == 'split' and beam['opening'] == opening_name]


def beam_name(beam):
    if beam['role'] == 'header_aft':
        return f"{beam['opening']} aft deck beam"
    if beam['role'] == 'header_fore':
        return f"{beam['opening']} fore deck beam"
    return f"Deck beam {beam['set']:02d} (S05)"

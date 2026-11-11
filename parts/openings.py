"""Shared clear openings and timber interfaces; no hull/deck import cycle."""
from dataclasses import dataclass

from .params import (
    HATCHES_FT, HATCH_ACROSS_FT, HATCH_WALL_FT, HATCH_HEIGHTS_FT,
    DECK_BEAM_SIDED_FT, ACCESS_WELL_AFT_FT, ACCESS_WELL_FORE_FT,
    ACCESS_WELL_WIDTH_FT,
    CABIN_FORWARD_FT, CABIN_WIDTH_FT, CABIN_LENGTH_FT, CABIN_WALL_FT,
)
from .primitives import block


@dataclass(frozen=True)
class DeckOpening:
    name: str
    forward: float
    across: float
    width: float
    length: float

    @property
    def clear_width(self):
        return self.width - 2 * HATCH_WALL_FT

    @property
    def clear_length(self):
        return self.length - 2 * HATCH_WALL_FT

    @property
    def aft(self):
        return self.forward - self.clear_length / 2

    @property
    def fore(self):
        return self.forward + self.clear_length / 2

    @property
    def frame_aft(self):
        return self.aft - DECK_BEAM_SIDED_FT

    @property
    def frame_fore(self):
        return self.fore + DECK_BEAM_SIDED_FT

    def passage_tool(self):
        return block(self.across, self.forward, -5,
                     self.clear_width, self.clear_length, 25)

    def coaming_levels(self, deck_height):
        heights = [deck_height(f, x) for f in (self.forward - self.length / 2,
                                              self.forward, self.forward + self.length / 2)
                   for x in (self.across - self.width / 2, self.across,
                             self.across + self.width / 2)]
        # Lower ends embed into the deck/header seating; level tops take boards.
        return min(heights) - .25, max(heights) + HATCH_HEIGHTS_FT[self.name]


def hatch_openings():
    return [DeckOpening(name, forward, HATCH_ACROSS_FT.get(name, 0), width, length)
            for name, forward, width, length in HATCHES_FT]


def framed_openings():
    companion = DeckOpening(
        'Cabin deck opening', CABIN_FORWARD_FT, 0,
        CABIN_WIDTH_FT-2*CABIN_WALL_FT+2*HATCH_WALL_FT,
        CABIN_LENGTH_FT-2*CABIN_WALL_FT+2*HATCH_WALL_FT)
    return [companion, *hatch_openings()]

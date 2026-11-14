"""Shared companionway interfaces, independent of the hull/deck builders."""
from dataclasses import dataclass

from .params import (
    CABIN_FORWARD_FT, CABIN_HEIGHT_FT, CABIN_ROOF_CAMBER_FT,
    CABIN_ROOF_THICKNESS_FT, COMPANIONWAY_HEIGHT_FT,
    COMPANIONWAY_AFT_FT, COMPANIONWAY_LENGTH_FT,
    ACCESS_CLEAR_WIDTH_FT, ACCESS_WELL_WIDTH_FT, ACCESS_WELL_AFT_FT,
    ACCESS_WELL_FORE_FT, ACCESS_SILL_HEIGHT_FT, ACCESS_SOLE_DROP_FT,
    ACCESS_TIMBER_FT, ACCESS_TREAD_COUNT, ACCESS_TREAD_GOING_FT,
)
from .primitives import block


@dataclass(frozen=True)
class CompanionwayAccess:
    entry_deck: float
    cabin_floor: float
    minimum_sole: float = -100

    @property
    def upper_base(self):
        return (self.cabin_floor + CABIN_HEIGHT_FT + CABIN_ROOF_CAMBER_FT
                + CABIN_ROOF_THICKNESS_FT - .08)

    @property
    def sill(self):
        return self.entry_deck + ACCESS_SILL_HEIGHT_FT

    @property
    def head(self):
        return self.upper_base + COMPANIONWAY_HEIGHT_FT - .12

    @property
    def sole(self):
        return max(self.entry_deck - ACCESS_SOLE_DROP_FT, self.minimum_sole)

    @property
    def well_bottom(self):
        # The landing embeds 0.02 ft into the supporting hull material.
        return self.sole - ACCESS_TIMBER_FT + .02

    @property
    def riser(self):
        return (self.sill - self.sole) / (ACCESS_TREAD_COUNT + 1)

    def tread(self, index):
        """Forward centre and top of a tread, indexed from one at the top."""
        assert 1 <= index <= ACCESS_TREAD_COUNT
        return (ACCESS_WELL_AFT_FT + .25 + (index - 1) * ACCESS_TREAD_GOING_FT,
                self.sill - index * self.riser)

    def well_tool(self):
        """Only the local access well, through deck and into the filled hull."""
        return block(0, (ACCESS_WELL_AFT_FT + ACCESS_WELL_FORE_FT) / 2,
                     self.well_bottom, ACCESS_WELL_WIDTH_FT,
                     ACCESS_WELL_FORE_FT - ACCESS_WELL_AFT_FT,
                     self.entry_deck + .5 - self.well_bottom)

    def door_tool(self):
        """One aligned aperture through both aft walls and the roof overhang."""
        aft, fore = COMPANIONWAY_AFT_FT - .4, ACCESS_WELL_AFT_FT + .02
        return block(0, (aft + fore) / 2, self.sill, ACCESS_CLEAR_WIDTH_FT,
                     fore - aft, self.head - self.sill)

    def roof_tool(self):
        fore = COMPANIONWAY_AFT_FT + COMPANIONWAY_LENGTH_FT - .2
        return block(0, (ACCESS_WELL_AFT_FT + fore) / 2,
                     self.upper_base - .6, ACCESS_WELL_WIDTH_FT,
                     fore - ACCESS_WELL_AFT_FT, 1.0)


def companionway_access(deck_height, bottom_height=None):
    """Accept the hull's height function without creating an import cycle."""
    minimum = -100
    if bottom_height is not None:
        minimum = max(bottom_height(f, x) for f in (ACCESS_WELL_AFT_FT,
                      (ACCESS_WELL_AFT_FT+ACCESS_WELL_FORE_FT)/2, ACCESS_WELL_FORE_FT)
                      for x in (-ACCESS_WELL_WIDTH_FT/2, ACCESS_WELL_WIDTH_FT/2)) + ACCESS_TIMBER_FT + .06
    return CompanionwayAccess(deck_height(COMPANIONWAY_AFT_FT),
                              deck_height(CABIN_FORWARD_FT) - .1, minimum)

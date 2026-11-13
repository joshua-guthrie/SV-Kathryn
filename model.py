"""Kathryn skipjack, from the supplied measured drawings. Output units: mm."""
from soma import add_part, param, import_step, import_assembly

from parts.params import MODEL_MM_PER_FOOT, IVORY
from parts.hull import (
    make_hull, make_deck, make_keel, make_rudder, make_centreboard,
    make_rudder_fittings, make_skeg, make_worm_shoe, make_stern_moulding_parts,
)
from parts.spars import make_spars
from parts.bow import make_bow_details
from parts.deck import (make_deckhouse_parts, make_hatches, make_helm,
                        make_bow_post, make_jib_traveller)
from parts.rails import make_rails
from parts.equipment import make_equipment
from parts.framing import make_opening_frames
from parts.interior import make_enclosure_parts, make_cabin_fitout_parts
from parts.centreline import make_centreline_parts
from parts.hull_frames import make_frame_parts,make_support_parts
from parts.stern_fittings import make_stern_fittings
from parts.deck_planking import (make_deck_board_parts, make_kingplank_scarf_parts,
                                  make_waterway_parts)
from parts.deck_beams import make_deck_beam_parts


def register(name, shape, color, group):
    assert shape.isValid() and len(shape.Solids()) == 1, f"Invalid part: {name}"
    add_part(name, shape.scale(MODEL_MM_PER_FOOT), color=color, group=group)


upper_hull, underwater_hull = make_hull()
register("Painted topsides", upper_hull, (.88, .88, .83), "Hull/Planking envelope")
register("Underwater hull", underwater_hull, (.11, .17, .19), "Hull/Planking envelope")
for name, shape, color, group in make_deck_board_parts():
    register(name, shape, color, group)
for name, shape, color in make_waterway_parts():
    register(name, shape, color, "Deck/Waterway")
for name, shape, color in make_kingplank_scarf_parts():
    register(name, shape, color, "Deck/Scarfs/Kingplank")
register("Keel", make_keel(), (.13, .18, .18), "Hull")
register("Keel worm shoe", make_worm_shoe(), (.17, .21, .19), "Hull")
register("Rudder", make_rudder(), (.25, .27, .25), "Hull")
register("Skeg", make_skeg(), (.13, .18, .18), "Hull")
for name, shape in make_rudder_fittings():
    register(name, shape, (.25, .27, .25), "Hull/Rudder fittings")
register("Centreboard", make_centreboard(), (.16, .20, .20), "Hull")

for name, shape, color in make_deck_beam_parts():
    register(name, shape, color, "Deck/Beams")

for maker, group in (
    (make_stern_moulding_parts, "Hull/Stern moulding"),
    (make_deckhouse_parts, "Deck/Cabin"),
    (make_hatches, "Deck/Hatches"),
    (make_opening_frames, "Interior/Opening framing"),
    (make_enclosure_parts, "Interior/Enclosure and bearings"),
    (make_cabin_fitout_parts, "Interior/Cabin fit-out"),
    (make_centreline_parts, "Interior/Keelson trunk and mast supports"),
    (make_frame_parts, "Interior/Hull frames and repairs"),
    (make_support_parts, "Interior/Clamps strongback and stanchions"),
    (make_helm, "Deck/Helm"),
    (make_rails, "Deck/Rails"),
    (make_equipment, "Deck/Equipment"),
    (make_stern_fittings, "Deck/Stern fittings"),
):
    for name, shape, color in maker():
        part_group = 'Deck/Cabin/Roofs' if name in ('Main cabin roof','Companionway roof') else group
        register(name, shape, color, part_group)
register("Samson post", make_bow_post(), IVORY, "Deck/Foredeck")
register("Jib sheet traveller", make_jib_traveller(), (.18, .21, .22), "Deck/Foredeck")

for name, shape, color in make_spars():
    register(name, shape, color, "Spars")
for name, shape, color in make_bow_details():
    register(name, shape, color, "Spars/Bow details")

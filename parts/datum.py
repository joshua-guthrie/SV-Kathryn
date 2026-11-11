"""Checked source registration/measurements, independent of display scale."""
from bisect import bisect_right
import json
from pathlib import Path

_record = json.loads((Path(__file__).resolve().parents[1] /
                      'drawing_package/registration.json').read_text())
LINE_STATIONS_FT = {row['lines_station']: row['canonical_forward_ft']
                    for row in _record['line_stations']}


def source_forward(sheet, grid_x):
    """Located source grid point to full-size canonical F; grid is 1440 wide."""
    slope, intercept = _record['transformations'][sheet]['grid_x_to_F']
    return slope * grid_x + intercept


HULL_AFT_FT = source_forward('S02', 151.0)
HULL_FORE_FT = source_forward('S02', 939.0)
_legacy = [0., *[row['legacy_model_forward_ft'] for row in _record['line_stations']], 50.]
_source = [HULL_AFT_FT, *LINE_STATIONS_FT.values(), HULL_FORE_FT]


def legacy_forward(forward):
    """Transfer an inherited attachment by hull-station correspondence.

    Explicitly measured deck features use source_forward instead. Beyond the
    body, lengths are retained with the adjacent endpoint's datum translation.
    This transfer is not a new claim that an old detail was source-measured.
    """
    if forward <= _legacy[0]:
        return forward + _source[0] - _legacy[0]
    if forward >= _legacy[-1]:
        return forward + _source[-1] - _legacy[-1]
    index = bisect_right(_legacy, forward) - 1
    t = (forward-_legacy[index])/(_legacy[index+1]-_legacy[index])
    return _source[index] + t*(_source[index+1]-_source[index])


_band_record = json.loads((Path(__file__).resolve().parents[1] /
                          'drawing_package/sheer_band_measurements.json').read_text())
_band_rows = sorted([*_band_record['measurements'], *_band_record['closures']],
                    key=lambda row: row['forward_ft'])
CENTRELINE_SOURCE = json.loads((Path(__file__).resolve().parents[1] /
                               'drawing_package/m2_centreline_measurements.json').read_text())
FRAME_SOURCE = json.loads((Path(__file__).resolve().parents[1] /
                          'drawing_package/m3_frame_schedule.json').read_text())
STERN_SOURCE = json.loads((Path(__file__).resolve().parents[1] /
                          'drawing_package/stern_helm_registration.json').read_text())
STERN_REMEDY_SOURCE = json.loads((Path(__file__).resolve().parents[1] /
                                 'drawing_package/stern_remedy_targets.json').read_text())


def _band_value(forward, key):
    xs = [row['forward_ft'] for row in _band_rows]
    if forward <= xs[0]: return _band_rows[0][key]
    if forward >= xs[-1]: return _band_rows[-1][key]
    i = bisect_right(xs, forward)-1
    t = (forward-xs[i])/(xs[i+1]-xs[i])
    return _band_rows[i][key]*(1-t)+_band_rows[i+1][key]*t


def sheer_band_height(forward):
    return _band_value(forward,'band_height_ft')


def sheer_band_flare(forward):
    return _band_value(forward,'outward_flare_ft')

# coding=utf-8
"""
Module
"""
from __future__ import absolute_import

from copy import deepcopy

import pytest

from datacube.index._storage import _ensure_valid
from datacube.index.fields import InvalidDocException

mapping_with_only_mandatory_fields = {
    'name': 'ls7_nbar',
    'file_path_template': '{platform[code]}_{instrument[name]}_{tile_index[0]}_{tile_index[1]}_'
                          '{start_time:%Y-%m-%dT%H-%M-%S.%f}.nc',
    'location_name': 'eotiles',
    'match': {
        'metadata': {
        }
    },
    'measurements': {
        '10': {'dtype': 'int16',
               'nodata': -999,
               'resampling_method': 'cubic',
               'varname': 'band_10'},
        '20': {'dtype': 'int16',
               'nodata': -999,
               'resampling_method': 'cubic',
               'varname': 'band_20'},
        '30': {'dtype': 'int16',
               'nodata': -999,
               'resampling_method': 'cubic',
               'varname': 'band_30'},
        '40': {'dtype': 'int16',
               'nodata': -999,
               'resampling_method': 'cubic',
               'varname': 'band_40'},
        '50': {'dtype': 'int16',
               'nodata': -999,
               'resampling_method': 'cubic',
               'varname': 'band_50'},
        '70': {'dtype': 'int16',
               'nodata': -999,
               'resampling_method': 'cubic',
               'varname': 'band_70'}
    },
    'storage': {
        'chunking': {
            'latitude': 500, 'longitude': 500, 'time': 1
        },
        'crs': 'GEOGCS["WGS 84",\n'
               '    DATUM["WGS_1984",\n'
               '        SPHEROID["WGS 84",6378137,298.257223563,\n'
               '            AUTHORITY["EPSG","7030"]],\n'
               '        AUTHORITY["EPSG","6326"]],\n'
               '    PRIMEM["Greenwich",0,\n'
               '        AUTHORITY["EPSG","8901"]],\n'
               '    UNIT["degree",0.0174532925199433,\n'
               '        AUTHORITY["EPSG","9122"]],\n'
               '    AUTHORITY["EPSG","4326"]]\n',
        'dimension_order': ['time', 'latitude', 'longitude'],
        'driver': 'NetCDF CF',
        'resolution': {'latitude': -0.00025, 'longitude': 0.00025},
        'tile_size': {'latitude': 1.0, 'longitude': 1.0}
    }
}


@pytest.mark.parametrize("valid_mapping_update", [
    {},
    {'match': {'metadata': {'anything': 'anything'}}},
    # With the optional properties
    {'global_attributes': {'anything': 'anything'}},
    {'description': 'Some string'},
])
def test_accepts_valid_mappings(valid_mapping_update):
    mapping = deepcopy(mapping_with_only_mandatory_fields)
    mapping.update(valid_mapping_update)
    # Should have no errors.
    _ensure_valid(mapping)


def test_incomplete_mapping_invalid():
    # Invalid: An empty doc.
    with pytest.raises(InvalidDocException) as e:
        _ensure_valid({})


# Changes to the above dict that should render it invalid.
@pytest.mark.parametrize("invalid_mapping_update", [
    # Mandatory
    {'name': None},
    {'file_path_template': None},
    # Should be an object
    {'storage': 's'},
    # Should be a string
    {'file_path_template': {}},
    {'description': 123},
    # Unknown property
    {'asdf': 'asdf'},
    # Name must have alphanumeric & underscores only.
    {'name': ' whitespace '},
    {'name': 'with-dashes'},
    # Mappings
    {'mappings': {}},
    {'mappings': ''}
])
def test_rejects_invalid_docs(invalid_mapping_update):
    mapping = deepcopy(mapping_with_only_mandatory_fields)
    mapping.update(invalid_mapping_update)
    with pytest.raises(InvalidDocException) as e:
        _ensure_valid(mapping)


@pytest.mark.parametrize("valid_mapping_measurmemnt", [
    {},
    # With the optional properties
    {'fill_value': -999},
])
def test_accepts_valid_measurements(valid_mapping_measurmemnt):
    mapping = deepcopy(mapping_with_only_mandatory_fields)
    mapping['measurements'].update(
        {
            '10': valid_mapping_measurmemnt
        }
    )
    # Should have no errors.
    _ensure_valid(mapping)


# Changes to the above dict that should render it invalid.
@pytest.mark.parametrize("invalid_mapping_measurement", [
    # nodata must be numeric
    {'nodata': '-999'},
    # Limited dtype options
    {'dtype': 'asdf'},
    {'dtype': 'intt13'},
    {'dtype': 13},
    # Unknown property
    {'asdf': 'asdf'},
    # Unknown resampling method
    {'resampling_method': 'dartboard'},
    # Invalid varname
    {'varname': 'white space'},
    {'varname': '%chars%'},
])
def test_rejects_invalid_measurements(invalid_mapping_measurement):
    mapping = deepcopy(mapping_with_only_mandatory_fields)
    mapping['measurements'].update(
        {
            '10': invalid_mapping_measurement
        }
    )
    with pytest.raises(InvalidDocException) as e:
        _ensure_valid(mapping)

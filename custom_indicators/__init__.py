"""
Custom Investigation Indicators
===============================

Bandicoot indicators designed for homicide and criminal investigations.
Analyzes production order cell phone records (CDRs) to extract evidentiary
insights about relationships, movements, and coordination between subjects.

Modules
-------
relationship : Relationship strength, reciprocity, initiation patterns
temporal : Communication gaps, bursts, pattern changes, timelines
location : Single-user location analysis (frequent locations, unusual visits)
colocation : Multi-user co-location detection
network : Network centrality, communication chains, subgroups
utils : Shared utilities (ID mapping, time windows)

Usage
-----
>>> from custom_indicators import relationship, colocation
>>> from custom_indicators.utils import load_id_mapping
>>>
>>> # Single-user indicator
>>> strength = relationship.relationship_strength(user, groupby=None)
>>>
>>> # Multi-user indicator
>>> overlaps = colocation.antenna_overlap(user_a, user_b, window_minutes=30)
>>>
>>> # Resolve phone numbers to names
>>> mapping = load_id_mapping('data/_ID_MAPPING.csv')
>>> named_results = utils.resolve_contacts(strength, mapping)
"""

from . import relationship
from . import temporal
from . import location
from . import colocation
from . import network
from . import utils

__all__ = [
    'relationship',
    'temporal',
    'location',
    'colocation',
    'network',
    'utils',
]

__version__ = '0.1.0'

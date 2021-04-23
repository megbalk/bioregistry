# -*- coding: utf-8 -*-

"""Download and parse the UniProt Cross-ref database."""

import json
import logging
import os
from typing import Mapping

from defusedxml import ElementTree
from pystow.utils import download

from bioregistry.data import EXTERNAL

__all__ = [
    'get_uniprot',
]

logger = logging.getLogger(__name__)

#: Download URL for the UniProt registry
URL = 'https://www.uniprot.org/database/?format=rdf'
UNPARSED_PATH = os.path.join(EXTERNAL, 'uniprot.xml')
PATH = os.path.join(EXTERNAL, 'uniprot.json')

kz = {
    'prefix': '{http://purl.uniprot.org/core/}abbreviation',
    'identifier': '{http://purl.org/dc/terms/}identifier',
    'name': '{http://www.w3.org/2000/01/rdf-schema#}label',
    'type': '{http://www.w3.org/1999/02/22-rdf-syntax-ns#}type',
    'primary_topic_of': '{http://xmlns.com/foaf/0.1/}primaryTopicOf',
    'category': '{http://purl.uniprot.org/core/}category',
    'link_is_explicit': '{http://purl.uniprot.org/core/}linkIsExplicit',
    'see_also': '{http://www.w3.org/2000/01/rdf-schema#}seeAlso',
    'formatter': '{http://purl.uniprot.org/core/}urlTemplate',
    'citation': '{http://purl.uniprot.org/core/}citation',
    'exact_match': '{http://www.w3.org/2004/02/skos/core#}exactMatch',
    'comment': '{http://www.w3.org/2000/01/rdf-schema#}comment',
}
kzi = {v: k for k, v in kz.items()}


def get_uniprot(force_download: bool = False) -> Mapping[str, Mapping[str, str]]:
    """Get the UniProt registry."""
    if not os.path.exists(PATH) or force_download:
        download(URL, UNPARSED_PATH)
    with open(UNPARSED_PATH) as file:
        tree = ElementTree.parse(file)
    root = tree.getroot()
    rv = {}
    for element in root.findall('{http://www.w3.org/1999/02/22-rdf-syntax-ns#}Description'):
        entry = {}
        for key, path in kz.items():
            value = element.findtext(path)
            if not value:
                continue
            entry[key] = value
        prefix = entry.get('prefix')
        if prefix is not None:
            rv[prefix] = entry

    with open(PATH, 'w') as file:
        json.dump(rv, file, indent=2)
    return rv


if __name__ == '__main__':
    get_uniprot(force_download=True)
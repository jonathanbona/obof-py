from rdflib import Graph, Literal, BNode, Namespace, RDF, RDFS, URIRef
import typing
import warnings
import os
import json
import wget

#TODO fix file paths -- too much hard-coded nonsense here 
# TODO - how about get these from http://www.obofoundry.org/registry/ontologies.jsonld ?


cached_base = './json/%s-labels.json'
ontologies = ['http://purl.obolibrary.org/obo/iao.owl',
              'http://purl.obolibrary.org/obo/uberon.owl',
              'http://purl.obolibrary.org/obo/ogms.owl']

def ouri_name(ouri):
    return ouri.split('/')[-1].split('.')[0].upper()

"""
   Given an ontology URI, generate a dict {label : uri} pairs for each term in the ontology, 
    and write it to a JSON file.
"""
def _write_uri_label_json(ouri : str):
    warnings.warn('_write_uri_label_json may overwrite exiting file. TODO: check that')
    name = ouri_name(ouri)
    d = _gen_uri_label_dict(ouri)
    with open(cached_base % (name), 'w') as f:
        json.dump(d, f)
    return d

"""
   Given an ontology URI, get the dict {label : uri} with pairs for each term in the ontology, 
    either by reading from a JSON file, or by generating the dict and then writing to a file. 
"""
def get_uri_label_dict(ouri : str, force_refresh = False):
    name = ouri_name(ouri)
    fname = cached_base % (name)

    try:
        with open(fname, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        print('Cached file %s not found. Generating...' % fname)
        return _write_uri_label_json(ouri)
    
def _gen_uri_label_dict(ouri : str):
    name = ouri_name(ouri)
    og = Graph()
    try:
        # Read from file. Later: download / refresh 
        og.parse('./ontologies/%s' % (ouri.split('/')[-1]))
    except:
        print('Could not find a source file for ontology %s.' % (name))
        print('Downloading from %s' % (ouri))
        wget.download(ouri, './ontologies/%s' % (ouri.split('/')[-1]))
        
    terms = [(s, o.toPython()) for (s, __, o) in  og.triples((None, RDFS.label, None)) if s.toPython().startswith('http://purl.obolibrary.org/obo/%s_' % (name))]
    return {l : u for (u, l) in terms}

def build_ontology_type(ouri : str):
    name = ouri_name(ouri)
    d = get_uri_label_dict(ouri)
    return (name, type(name, (), {l.strip().replace(' ', '_') : u for (l, u) in d.items()}))


for (n, c) in [build_ontology_type(o) for o in ontologies]:
    print(c)
    globals()[n] = c


#OBO = type('OBO', (), {n : c for (n, c) in [build_ontology_type(o) for o in ontologies]})



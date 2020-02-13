#!/usr/bin/env python
# -*- coding: utf-8 -*-
import sys, argparse, json, csv
import qwikidata
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

def unify_namings(name0):
    return name0.replace(' ','_').lower()

def get_wikidata(str0):
    try:
        res0 = return_sparql_query_results(str0)
    except:
        return {}
    bindings = res0['results'].get('bindings',[])
    if len(bindings) < 1:
        return {}
    for b in bindings:
        qid = b['item']['value'].split('/')[-1]
        if 'itemDescription' in b and len(qid) < 16:
            return {'wikidata_qid': qid, 'wikidata_name': b['itemLabel']['value'], 'wikidata_desc': b['itemDescription']['value']}
    return {}

def wikidata_from_freenetid(freenetid):
    sparql_query = """
    SELECT distinct ?item ?itemLabel ?itemDescription WHERE{  
      ?item ?P646 "%s"
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    return get_wikidata(sparql_query%freenetid)
   
def wikidata_from_name(name):
    sparql_query = """
    SELECT distinct ?item ?itemLabel ?itemDescription WHERE{  
      ?item ?label "%s"
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    return get_wikidata(sparql_query%name.replace('_',' '))

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--imagenet_src', type=str, default="./label_definitions/wordnet.json",
                    help='Path to json file containing wordnet 3.0 label mappings')
    parser.add_argument('--limit_labels', type=str, default="./label_definitions/panoptic_coco_categories.json",
                    help='Path to json file containing subset of names for relevant imagenet labels')
    parser.add_argument('--freenet_src', type=str, default="./label_definitions/oid-class-descriptions-boxable.csv",
                    help='Path to json file containing source freenet labels')
    parser.add_argument('--output', type=str, default="joint_mapping.json",
                        help="Output json file path")
    args = parser.parse_args(argv)
    
    with open(args.imagenet_src, 'r') as ifile:
        imagenet_labels_raw = json.load(ifile)
    
    imagenet_labels = {}
    for wid,synset in imagenet_labels_raw['synset'].items():
        for w in synset['word']:
            imagenet_labels[unify_namings(w)] = wid

    with open(args.limit_labels, 'r') as ifile:
        limit_labels_raw = json.load(ifile)
    joined_label_space = {unify_namings(entry['name']) : {'coco_id':entry['id'], 'coco_name':entry['name']} for entry in limit_labels_raw}
    
    with open(args.freenet_src, newline='') as ifile:
        freenet_labels_raw = list(csv.reader(ifile))
    
    
    all_qids = {}
    for (fid, name) in freenet_labels_raw:
        key = unify_namings(name)
        if not key in joined_label_space:
            key = key.replace('-stuff','').replace('-merged','').replace('-other','')
        add_entry =  {'oid_name': name, 'oid_id': fid}
        add_entry.update(wikidata_from_freenetid(fid))
        if 'wikidata_qid' in add_entry:
            qid = add_entry['wikidata_qid']
            if qid in all_qids:
                print("Warning: dublicate qid: ", all_qids[qid], key)
            all_qids[qid] = key
        if key in joined_label_space:
            joined_label_space[key].update(add_entry)
        else:
            joined_label_space[key] = add_entry
    
    for key, vals in joined_label_space.items():
        if 'wikidata_qid' in vals:
            continue
        n_qid = wikidata_from_name(key)
        if len(n_qid) == 0:
            continue
        qid = n_qid['wikidata_qid']
        if qid in all_qids:
            vals.update(joined_label_space[all_qids[qid]])
            joined_label_space[all_qids[qid]].update(vals)
        else:
            vals.update(n_qid)
            
    fix_wordnet = {'playing_field':'ball_field', 'skis':'ski'}
    #no wordnet: stop_sign sports_ball potted_plant floor-wood playingfield wall-brick wall-stone wall-tile wall-wood window-blind
    for key, vals in joined_label_space.items():
        key0 = key.replace('-stuff','').replace('-merged','').replace('-other','')
        key0 = fix_wordnet.get(key0,key0)
        if not key0 in imagenet_labels:
            key0 = key0.replace('_','')
        if not key0 in imagenet_labels:
            print('Not found in wordnet: '+key)
            continue
        joined_label_space[key]['wordnet_id'] = imagenet_labels[key0]
        if 'oid_id' in vals and 'coco_id' in vals:
            continue
        #TODO: use qwikidata to map wordnet <-> freenet; decrease cnt_open
    
    cnt_open = 0
    for key, vals in joined_label_space.items():
        if 'oid_id' in vals and 'coco_id' in vals:
            continue
        cnt_open += 1
    
    print("Could not find mappings for %i entries of %i" % (cnt_open ,len(joined_label_space)))
    
    with open(args.output, 'w') as ofile:
        json.dump(joined_label_space, ofile, sort_keys=True, indent=4)
        
    return 0
    
if __name__ == "__main__":
    print("Automatically generate mapping between freenet and imagenet (=wordnet 3.0) ids")
    sys.exit(main())
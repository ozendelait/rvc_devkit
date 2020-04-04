#!/usr/bin/env python
# -*- coding: utf-8 -*-
# add missing mapping_wordnet.json from here:
# https://github.com/ozendelait/wordnet-to-json/releases
# install qwikidata (used 0.4.0) : pip install qwikidata
import sys, argparse, json, csv, pickle
import qwikidata
from qwikidata.sparql import (get_subclasses_of_item,
                              return_sparql_query_results)

def unify_namings(name0):
    return name0.replace(' ','_').lower()

def get_wikidata(str0, context = None):
    try:
        res0 = return_sparql_query_results(str0)
    except:
        return {}
    bindings = res0['results'].get('bindings',[])
    if len(bindings) < 1:
        return {}
    best_b = None
    min_q = None
    for b in bindings[:min(16, len(bindings))]:
        qid = b['item']['value'].split('/')[-1]
        if not 'itemDescription' in b or len(qid) > 16:
            continue
        prev_has_wn3 = False
        if not context is None:
            #check if context words are in the first sentence
            pos_context = min([b['itemDescription']['value'].find(c) for c in context])
            if pos_context < 0:
                continue
            pos_fullstop = b['itemDescription']['value'].find('.')
            if pos_fullstop > 0 and pos_context > pos_fullstop:
                continue
        curr_q = int(b['item']['value'].split('/')[-1][1:])
        if best_b is None:
            best_b = b
            min_q = curr_q
        else:
            prev_has_wn3 = 'WN3' in best_b

        if curr_q < min_q: #smaller q usually stands for a more general entry (vs. an instance)
            best_b = b
            break
        has_wn3 = 'WN3' in b
        has_frn = 'FREEN' in b
        if has_wn3 and has_frn:
            best_b = b
            break
        elif has_wn3 or not prev_has_wn3 and has_frn:
            best_b = b

    if not best_b is None:
        ret_b = {'wikidata_qid': best_b['item']['value'].split('/')[-1], 'wikidata_name': best_b['itemLabel']['value'], 'wikidata_desc': best_b['itemDescription']['value']}
        if 'WN3' in best_b and best_b['WN3']['value'].find('wordnet-rdf.princeton.edu/wn30/') >= 0:
            wn3_conv = best_b['WN3']['value'].split('/')[-1]
            ret_b['wordnet_id'] = wn3_conv[-1]+wn3_conv[:-2]
        if 'FREEN' in best_b:
            ret_b['freebase_id'] = best_b['FREEN']['value']
        return ret_b
    return {}

def wikidata_from_freebaseid(freebaseid):
    sparql_query = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 WHERE{  
      ?item ?P646 "%s"
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    return get_wikidata(sparql_query%freebaseid)

def wikidata_from_wordnet3p0(wordnetid):
    conv_wn = wordnetid[1:]+'-'+ wordnetid[0]
    sparql_query = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 WHERE{  
      ?item ?P646  <http://wordnet-rdf.princeton.edu/wn30/%s>
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    return get_wikidata(sparql_query%conv_wn)

def wikidata_from_name(name, context = None):
    sparql_query0 = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 WHERE{  
      ?item ?label "%s"@en.  
      ?article schema:about ?item .
      ?article schema:inLanguage "en" .
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      OPTIONAL { ?item  wdt:P646  ?FREEN }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    sparql_query1 = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 WHERE{  
      ?item ?label "%s"
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      OPTIONAL { ?item  wdt:P646  ?FREEN }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    label_check = name.replace('_', ' ')
    d0 = get_wikidata(sparql_query0 % label_check, context=context)
    if len(d0) == 0:
        d0 = get_wikidata(sparql_query1 % label_check, context=context)
    return d0

#this is necessary to split words of the same meaning
oid_context_fixed = {"gondola": ("boat","n03447447"), "cucumber":("fruit","n07718472"), "dog":("animal","n02084071"),
                     "sink":("basin","n04553703"), "hat":("head", "n03497657"), "sombrero":("hat", "n04259630"),
                     "dumbbell":("weight", "n03255030"), "diaper":("garment ", "n03188531"), "ruler":("stick", "n04118776"),
                     "jellyfish":("aquatic","n01910747"), "broccoli":("vegetable","n07714990"), "hot_dog":("bun", "n07697537"),
                     "microwave":("appliance","n03761084"), "toaster":("appliance","n04442312"), "bow_and_arrow":("weapon","n02879718"),
                     "drum":("instrument","n03249569"), "door":("entrance","n03221720"), "harp":("instrument", "n03495258"),
                     "racket":("equipment","n04039381"), "bowl":("tableware","n13893694"), "missile":("propelled","n03773504"),
                     "party_balloon":("inflatable","n02782329"), "balloon":("aerostat", "n02782093"), "banana":("fruit","n07753592"),
                     "car":("auto","n02958343"), "orange":("fruit","n07747607"),
                     }
#OID "balloon" is mixture of party balloons and balloon vehicles
#TODO: COCO keyboard-> keypad or musical keyboard

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--imagenet_src', type=str, default="./label_definitions/wordnet.json",
                    help='Path to json file containing wordnet 3.0 label mappings')
    parser.add_argument('--limit_labels', type=str, default="./label_definitions/panoptic_coco_categories.json",
                    help='Path to json file containing subset of names for relevant imagenet labels')
    parser.add_argument('--freebase_src', type=str, default="./label_definitions/oid-class-descriptions-boxable.csv",
                    help='Path to json file containing source freebase labels')
    parser.add_argument('--output', type=str, default="joint_mapping.json",
                        help="Output json file path")
    args = parser.parse_args(argv)
    
    with open(args.imagenet_src, 'r') as ifile:
        imagenet_labels_raw = json.load(ifile)
    
    imagenet_labels = {}
    for wid,synset in imagenet_labels_raw['synset'].items():
        if wid[0] != 'n': #currently only nouns are relevant
            continue
        for w in synset['word']:
            w = unify_namings(w)
            imagenet_labels[w] = wid

    #overwrite/fix defined wids
    for w, (context, wid) in oid_context_fixed.items():
        imagenet_labels[w] = wid

    with open(args.limit_labels, 'r') as ifile:
        limit_labels_raw = json.load(ifile)
    joined_label_space = {unify_namings(entry['name']) : {'coco_id':entry['id'], 'coco_name':entry['name']} for entry in limit_labels_raw}
    
    with open(args.freebase_src, newline='') as ifile:
        freebase_labels_raw = list(csv.reader(ifile))

    all_qids = {}
    for (fid, name) in freebase_labels_raw:
        key = unify_namings(name)
        if not key in joined_label_space:
            key = key.replace('-stuff','').replace('-merged','').replace('-other','')
        add_entry = {'oid_name': name, 'oid_id': fid}
        context = key.split('(')
        if len(context) > 1 and context[1][-1] == ')':
            key = context[0].replace('_', '')
            add_entry['context'] = context[1][:-1]
        elif key.find('human_') == 0:
            key = key.split('_')[-1]
            add_entry['context'] = 'human'
        if key in oid_context_fixed:
            add_entry['context'] = oid_context_fixed[key][0]
        add_entry.update(wikidata_from_freebaseid(fid))
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
        n_qid = wikidata_from_name(key, context=vals.get('context','').split('_'))
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
        if 'wordnet_id' in vals and vals['wordnet_id'] != imagenet_labels[key0]:
            print('Wordnet clash for '+ key +': ' + vals['wordnet_id'] + ' vs ' + imagenet_labels[key0])
            continue

        joined_label_space[key]['wordnet_id'] = imagenet_labels[key0]
        if not 'freebase_id' in vals or not 'wikidata_qid' in vals:
            w1 = wikidata_from_wordnet3p0(imagenet_labels[key0])
            if 'freebase_id' in w1 and 'oid_id' in vals and vals['oid_id'] != w1['freebase_id']:
                print('Freebase clash for ' + key + ': ' + w1['freebase_id']  + ' vs ' + vals['oid_id'])
                continue
            vals.update(w1)

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
    print("Automatically generate mapping between freebase and imagenet (=wordnet 3.0) ids")
    sys.exit(main())
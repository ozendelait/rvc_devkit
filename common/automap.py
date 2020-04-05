#!/usr/bin/env python
# -*- coding: utf-8 -*-
# add missing mapping_wordnet.json from here:
# https://github.com/ozendelait/wordnet-to-json/releases

import sys, argparse, json, csv, time
import requests

retry_time_sleep_s = 1.0
max_retries_wikidata = 3

#OPEN: OID "balloon" is mixture of party balloons and balloon vehicles
#TODO: check if COCO keyboard-> computer_keyboard or musical_keyboard

#fixed renaming of matching concepts with different writing
fix_unified_labels = {'flying_disc':'frisbee', 'doughnut':'donut', 'keyboard': 'computer_keyboard',
                 'cell_phone':'mobile_phone', 'microwave_oven':'microwave',
                 'playing_field':'ball_field', 'skis':'ski', 'loveseat':'couch',
                 'maracas':'maraca', 'houseplant':'potted_plant', 'remote_control':'remote'}

# these manual corrections are necessary to resolve conflicts with identical words of different meaning
# tuple of context and wordnet_pwn30 per joined label key; context is used to find correct entry on wikidata
oid_context_fixed = {"gondola": ("boat","n03447447"), "cucumber":("fruit","n07718472"), "dog":("animal","n02084071"),
                     "sink":("basin","n04553703"), "hat":("head", "n03497657"), "sombrero":("hat", "n04259630"),
                     "dumbbell":("weight", "n03255030"), "diaper":("garment ", "n03188531"), "ruler":("stick", "n04118776"),
                     "jellyfish":("aquatic","n01910747"), "broccoli":("vegetable","n07714990"), "hot_dog":("bun", "n07697537"),
                     "microwave":("appliance","n03761084"), "toaster":("appliance","n04442312"), "bow_and_arrow":("weapon","n02879718"),
                     "drum":("instrument","n03249569"), "door":("entrance","n03221720"), "harp":("instrument", "n03495258"),
                     "racket":("equipment","n04039381"), "bowl":("tableware","n13893694"), "missile":("propelled","n03773504"),
                     "party_balloon":("inflatable","n02782329"), "balloon":("aerostat", "n02782093"), "banana":("fruit","n07753592"),
                     "car":("auto","n02958343"), "orange":("fruit","n07747607"), "train":("rail","n04468005"),
                     "mirror":("surface","n03773035"), "sports_equipment": ("object","n04285146"), "envelope": ("letter","n03291819"),
                     "submarine": ("submersible","n04347754"), "sock": ("foot", "n04254777"), "hand": ("extremity", "n05564590"),
                     "ball" :("round","n02778669"), "printer": ("computer","n04004767"), "wardrobe":("furniture","n04550184"),
                     "perfume":("mixture","n03916031"), "remote": ("device","n04074963"),
                     }

def unify_namings(name0):
    unif_name = name0.replace(' ','_').lower()
    return fix_unified_labels.get(unif_name,unif_name)

def get_wikidata(str0, context = None, retries = 0):
    res0 = None
    try:
        res0_r = requests.get(
        "https://query.wikidata.org/sparql", params={"query": str0, "format": "json"})
        if res0_r.status_code == 200:
            res0 = res0_r.json()
    except:
        print("Unexpected error:", sys.exc_info()[0], res0_r)
        res0 = None
    if res0 == None:
        if retries <= 0:
            print("Warning: bad request:", res0_r)
            return {}
        else:
            time.sleep(retry_time_sleep_s)#wait 1s to reduce number of 429 errors
            return get_wikidata(str0, context, retries - 1)
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
            ret_b['wordnet_pwn30'] = wn3_conv[-1]+wn3_conv[:-2]
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
    return get_wikidata(sparql_query%freebaseid,retries=max_retries_wikidata)

def wikidata_from_wordnet3p0(wordnetid):
    conv_wn = wordnetid[1:]+'-'+ wordnetid[0]
    sparql_query = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 WHERE{  
      ?item ?P646  <http://wordnet-rdf.princeton.edu/wn30/%s>
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    return get_wikidata(sparql_query%conv_wn,retries=max_retries_wikidata)

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
    d0 = get_wikidata(sparql_query0 % label_check, context=context, retries=max_retries_wikidata)
    if len(d0) == 0:
        d0 = get_wikidata(sparql_query1 % label_check, context=context, retries=max_retries_wikidata)
    return d0

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

    #imagenet_labels_raw = {'synset':{}}
    with open(args.imagenet_src, 'r') as ifile:
        imagenet_labels_raw = json.load(ifile)
    
    imagenet_labels = {}
    imagenet_gloss = {}
    for wid,synset in imagenet_labels_raw['synset'].items():
        if wid[0] != 'n': #currently only nouns are relevant
            continue
        imagenet_gloss[wid] = synset.get('gloss',"")
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
        add_entry = {'oid_name': name, 'freebase_id': fid}
        context = key.split('(')
        if len(context) > 1 and context[1][-1] == ')':
            key = context[0].replace('_', '')
            add_entry['context'] = context[1][:-1]
        elif key.find('human_') == 0:
            key = key.split('_')[-1]
            add_entry['context'] = 'human'
        if key in oid_context_fixed:
            add_entry['context'] = oid_context_fixed[key][0]
        f_wd = wikidata_from_freebaseid(fid)
        add_entry.update(f_wd)
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
            print("Warning: dublicate qid: ", all_qids[qid], key)
        else:
            vals.update(n_qid)
            

    #no wordnet: stop_sign sports_ball potted_plant floor-wood playingfield wall-brick wall-stone wall-tile wall-wood window-blind
    for key, vals in joined_label_space.items():
        key0 = key.replace('-stuff','').replace('-merged','').replace('-other','')
        if not key0 in imagenet_labels:
            key0 = key0.replace('_','')
        key0 = fix_unified_labels.get(key0, key0)

        if not key0 in imagenet_labels:
            print('Not found in wordnet: '+key)
            continue
        if 'wordnet_pwn30' in vals and vals['wordnet_pwn30'] != imagenet_labels[key0]:
            print('Wordnet clash for '+ key +': ' + vals['wordnet_pwn30'] + ' vs ' + imagenet_labels[key0])
            continue

        joined_label_space[key]['wordnet_pwn30'] = imagenet_labels[key0]

        if imagenet_labels[key0] in imagenet_gloss:
            joined_label_space[key]['wordnet_gloss'] = imagenet_gloss[imagenet_labels[key0]]

        if not 'freebase_id' in vals or not 'wikidata_qid' in vals:
            w1 = wikidata_from_wordnet3p0(imagenet_labels[key0])
            if 'freebase_id' in w1 and 'freebase_id' in vals and vals['freebase_id'] != w1['freebase_id']:
                print('Freebase clash for ' + key + ': ' + w1['freebase_id']  + ' vs ' + vals['freebase_id'])
                continue
            vals.update(w1)

    cnt_open = 0
    for key, vals in joined_label_space.items():
        if 'freebase_id' in vals and 'wordnet_id' in vals:
            continue
        cnt_open += 1
    
    print("Could not find mappings for %i entries of %i" % (cnt_open ,len(joined_label_space)))
    
    with open(args.output, 'w') as ofile:
        json.dump(joined_label_space, ofile, sort_keys=True, indent=4)
        
    return 0
    
if __name__ == "__main__":
    print("Automatically generate mapping between freebase, imagenet (=wordnet 3.0) ids and optionally wikidata qids")
    sys.exit(main())
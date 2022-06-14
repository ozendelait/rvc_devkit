#!/usr/bin/env python
# -*- coding: utf-8 -*-
# add missing mapping_wordnet.json from here:
# https://github.com/ozendelait/wordnet-to-json/releases

import os, sys, argparse, json, csv, time
import requests

retry_time_sleep_s = 1.0
max_retries_wikidata = 3

#OPEN: OID "balloon" is mixture of party balloons and balloon vehicles
#TODO: check if COCO keyboard-> computer_keyboard or musical_keyboard

#fixed renaming of matching concepts with different writing
fix_unified_labels = {'flying_disc':'frisbee', 'doughnut':'donut', 'keyboard': 'computer_keyboard',
                 'cell_phone':'mobile_phone', 'microwave_oven':'microwave',
                 'playing_field':'ball_field', 'skis':'ski', 'loveseat':'couch',
                 'maracas':'maraca', 'houseplant':'potted_plant', 'remote_control':'remote',
                 'hair_drier':'hair_dryer', 'earrings':'earring', 'band-aid': 'adhesive_bandage', 'ring-binder':'ring_binder',
                 'chopsticks':'chopstick', 'headphones':'headphone', 'vehicle_registration_plate':'license_plate', 'cosmetics':'cosmetic',
                 'crash_helmet' : 'bicycle_helmet', 'shoes':'shoe', 'picture':'picture_frame', 'speaker':'loudspeaker',
                 'monitor' : 'computer_monitor', 'gun' : 'handgun', 'luggage':'luggage_and_bags', 'table_tennis':'table_tennis_racket',
                 "noddles":"noodle", 'asparagus' : 'garden_asparagus', 'drill' : 'electric_drill',
                 'shower' : 'showerhead', 'tape' : 'adhesive_tape',
                 'tablet' : 'tablet_computer', 'football' : 'american_football', 'formula_1_':'race_car',
                 'carriage' : 'horse_carraige', 'bakset' : 'basket', 'barrel/bucket':'barrel', 'cigar/cigarette_':'roll_of_tobacco',
                 'billards' : 'billard_ball', 'blackboard/whiteboard':'whiteboard', 'tennis' : 'tennis_ball',
                 'cosmetics_brush/eyeliner_pencil' : 'eyeliner_pencil', 'wallet/purse':'purse', 'trolley':'handcart',
                 'soccer' : 'soccer_ball', 'skating_and_skiing_shoes':'ski_boot', 'router/modem' : 'router', 'paint_brush' : 'paintbrush',
                 'other_shoes' : 'shoes', "other_fish": "fish", 'Other_Balls' : 'ball', 'nuts' : 'nut', 'moniter/tv' : 'monitor_or_tv',
                 'french' : 'french_horn', 'fan':'electric_fan', 'extractor' : 'exhaust_hood', 'extention_cord' : 'extension_cord',
                 'curling' : 'curling_stone', 'converter' : 'power_brick', 'computer_box' : 'computer_housing',
                 'table_teniis_paddle' : 'table_teniis_racket', 'table_tennis' : 'table_tennis_ball', 'chips' : 'potato_chip',
                 'earphones':'in-ear-earphones', 'head_phone' : 'headphone', 'cd' : 'compact_disc', 'music_instrument': 'musical_instrument'
                }

#faulty qid (corresp./data must be fixed on wikidata itself): "balance_beam"
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
                     "perfume":("mixture","n03916031"), "remote": ("device","n04074963"), "alpaca" :("camelid","n02438272"),
                     "apple":("fruit","n07739125"), "arm":("human","n05563770"), "banner":("cloth","n02788021"),
                     "bat":("animal", "n02139199"), "bathroom_cabinet":("toiletries","n03742115"), "bear":("mammal","n02131653"),
                     "beard":("human", "n05261566"), "pitcher":("spout", "n03950228"), "belt":("waist","n02827606"),  #"window_blind":("covering","n02851099"),
                     "boot":("footwear","n02872752"), "beetle":("insect","n02164464"), "bird":("animal", "n01503061"),
                     "bull":("cattle","n02403325"), "roll_of_tobacco":("smoke", "n04103491")
                     }

def unify_namings(name0):
    unif_name = name0.replace(' ','_').lower().replace('_-_','_').replace('(','').replace(')','')
    return fix_unified_labels.get(unif_name,unif_name)

def get_wordnet_gloss(pwn30, retries = 0, wd_id=None):
    res0, res0_r = None, None
    try:
        if not wd_id is None: #use specific wordnet id instead of pwn30
            request_url = "http://wordnet-rdf.princeton.edu/json/id/%s"%(wd_id)
        else:
            request_url = "http://wordnet-rdf.princeton.edu/json/pwn30/%s"%(pwn30[1:]+'-'+pwn30[0])
        res0_r = requests.get(
        request_url , params={"format": "json"})
        if res0_r.status_code == 200:
            res0 = res0_r.json()
    except:
        print("Unexpected error:", sys.exc_info()[0], res0_r)
        res0 = None
    ret_pwn30 = None
    if not res0 is None and len(res0) > 0:
        ret_pwn30 = res0[0]['old_keys']['pwn30'][0][-1]+res0[0]['old_keys']['pwn30'][0][:-2]
    if ret_pwn30 is None or (not pwn30 is None and ret_pwn30 != pwn30):
        if retries <= 0:
            print("Warning: bad request:", pwn30, res0_r)
            return {}
        else:
            time.sleep(retry_time_sleep_s)#wait 1s to reduce number of 429 errors
            return get_wordnet_gloss(pwn30, retries - 1)
    
    names = [l["lemma"] for l in res0[0]["lemmas"] if l["language"] == "en"]
    names = list(sorted(names, key=len)) # find shortest lemma
    dict_ret =  {'wordnet_pwn30': ret_pwn30, 'wordnet_gloss': res0[0]['definition']} 
    if len(names) > 0:     
        dict_ret['wordnet_name'] = names[0]
    parents_pwn30 = []
    if wd_id is None:
        #find parent ("hypernym")
        for r in res0[0].get("relations",[]):
            if r["rel_type"] == "hypernym":
                for _ in range(max_retries_wikidata):
                    get_pwn30 = get_wordnet_gloss(None, retries = 0, wd_id=r["target"])
                    if 'wordnet_pwn30' in get_pwn30 and not get_pwn30['wordnet_pwn30'] is None:
                        parents_pwn30.append(get_pwn30['wordnet_pwn30'])
                        break
                
        if len(parents_pwn30) > 0:
            dict_ret['parents_pwn30'] = list(set(parents_pwn30))

    return dict_ret


def get_wordnet(str0, context = None, retries = 0):
    res0 = None
    if not context is None and len(context) == 1 and len(context[0]) == 0:
        context = None
    try:
        res0_r = requests.get(
        "http://wordnet-rdf.princeton.edu/json/lemma/%s"%str0.replace('_','%20'), params={"format": "json"})
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
            return get_wordnet(str0, context, retries - 1)

    if res0 == [] and retries > 0 and str0[0].lower() == str0[0]: #search is case sensitve
        return get_wordnet(str0[0].upper()+str0[1:], context, 0)

    best_r = None
    for r in res0[:min(16, len(res0))]:
        if not 'old_keys' in r or not 'pwn30' in r['old_keys']:
            continue
        pwn30 = r['old_keys']['pwn30'][0]
        if pwn30[-2:] != '-n':
            continue
        curr_pwn = int(pwn30[:-2])
        if not context is None:
            if len(context) > 1 or r['subject'] != "noun."+context[0].replace('human','body'):
                # check if context words are in the gloss.
                pos_context = min([r['definition'].find(c) for c in context])
                if pos_context < 0:
                    continue
        if best_r is None:
            best_r = r
        if context is None:
            if r['subject'] == 'noun.artifact' and best_r['subject'] != 'noun.artifact':
                best_r = r #usually man-made objects are the best represenation for COCo/OID representations
            if best_r['subject'] == 'noun.artifact' and r['subject'] != 'noun.artifact':
                continue
        min_pwn = int(best_r['old_keys']['pwn30'][0][:-2])
        if curr_pwn < min_pwn:  # smaller q usually stands for a more general entry (vs. an instance)
            best_r = r
            continue
    if not best_r is None:
        names = [l["lemma"] for l in best_r["lemmas"] if not l is None and l["language"] == "en"]
        names = list(sorted(names, key=len)) # find shortest lemma
        ret_b = {'wordnet_pwn30': 'n'+best_r['old_keys']['pwn30'][0][:-2], 'wordnet_gloss': best_r['definition']}
        if len(names) > 0:
            ret_b["wordnet_name"] = names[0]
        return ret_b
    return {}

def get_wikidata(str0, context = None, retries = 0):
    res0, res0_r = None, None
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
    for b in bindings[:min(16, len(bindings))]:
        qid = b['item']['value'].split('/')[-1]
        if len(qid) > 16:
            continue
        prev_has_wn3 = False
        if best_b is None:
            best_b = b
        else:
            prev_has_wn3 = 'WN3' in best_b and best_b['WN3']['value'].find('/wn30/') > 0
        if not 'itemDescription' in b:
            continue
        if not context is None:
            #check if context words are in the first sentence
            pos_context = min([b['itemDescription']['value'].find(c) for c in context])
            if pos_context < 0:
                continue
            pos_fullstop = b['itemDescription']['value'].find('.')
            if pos_fullstop > 0 and pos_context > pos_fullstop:
                continue
        curr_q = int(b['item']['value'].split('/')[-1][1:])

        min_q = int(best_b['item']['value'].split('/')[-1][1:])
        if curr_q < min_q: #smaller q usually stands for a more general entry (vs. an instance)
            best_b = b
            break
        has_wn3 = 'WN3' in b and b['WN3']['value'].find('/wn30/') > 0
        has_frn = 'FREEN' in b
        if has_wn3 and has_frn:
            best_b = b
            break
        elif has_wn3 or not prev_has_wn3 and has_frn:
            best_b = b

    if not best_b is None:
        ret_b = {'wikidata_qid': best_b['item']['value'].split('/')[-1], 'wikidata_name': "", 'wikidata_desc': ""}
        if 'itemLabel' in  best_b:
            ret_b['wikidata_name'] = best_b['itemLabel']['value']
        if 'itemDescription' in best_b:
            ret_b['wikidata_desc'] = best_b['itemDescription']['value']
        if 'WN3' in best_b and best_b['WN3']['value'].find('wordnet-rdf.princeton.edu/wn30/') >= 0:
            wn3_conv = best_b['WN3']['value'].split('/')[-1]
            ret_b['wordnet_pwn30'] = wn3_conv[-1]+wn3_conv[:-2]
        if 'FREEN' in best_b:
            ret_b['freebase_mid'] = best_b['FREEN']['value']
        if 'INSTANCEOF' in best_b:
            ret_b['parents_qid'] = [best_b['INSTANCEOF']['value'].split('/')[-1]]
        if 'SUBCLASS' in best_b:
            ret_b.setdefault('parents_qid',[]).append(best_b['SUBCLASS']['value'].split('/')[-1])
        if 'PARTOF' in best_b:
            ret_b.setdefault('parents_qid',[]).append(best_b['PARTOF']['value'].split('/')[-1])
        if 'parents_qid' in ret_b:
            ret_b['parents_qid'] = list(set(ret_b['parents_qid']))
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

def wikidata_from_qid(qid):
    sparql_query0 = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 ?FREEN ?INSTANCEOF ?SUBCLASS ?PARTOF WHERE{  
      ?article schema:about ?item .
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      OPTIONAL { ?item  wdt:P646  ?FREEN }
      OPTIONAL { ?item  wdt:P31  ?INSTANCEOF }
      OPTIONAL { ?item  wdt:P279  ?SUBCLASS }
      OPTIONAL { ?item  wdt:P361  ?PARTOF }
      BIND(wd:%s AS ?item).
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". } 
    }
    """
    sparql_query1 = """
        SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 ?FREEN ?INSTANCEOF ?SUBCLASS ?PARTOF WHERE{  
          ?item ?label "%s"@en
          OPTIONAL { ?item  wdt:P2888  ?WN3 }
          OPTIONAL { ?item  wdt:P646  ?FREEN } 
          OPTIONAL { ?item  wdt:P31  ?INSTANCEOF }
          OPTIONAL { ?item  wdt:P279  ?SUBCLASS }
          OPTIONAL { ?item  wdt:P361  ?PARTOF }  
        }
        """
    d0 = get_wikidata(sparql_query0 % qid, retries=max_retries_wikidata)
    if len(d0) == 0:
        d0 = get_wikidata(sparql_query1 % qid, retries=max_retries_wikidata)
    return d0

def wikidata_from_wordnet3p0(wordnetid):
    if len(wordnetid) < 3:
        return {}
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
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 ?FREEN WHERE{  
      ?item ?label "%s"@en.  
      ?article schema:about ?item .
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      OPTIONAL { ?item  wdt:P646  ?FREEN }
      SERVICE wikibase:label { bd:serviceParam wikibase:language "en". }    
    }
    """
    sparql_query1 = """
    SELECT distinct ?item ?itemLabel ?itemDescription ?WN3 ?FREEN WHERE{  
      ?item ?label "%s"@en
      OPTIONAL { ?item  wdt:P2888  ?WN3 }
      OPTIONAL { ?item  wdt:P646  ?FREEN }   
    }
    """
    label_check = name.replace('_', ' ')
    d0 = get_wikidata(sparql_query0 % label_check, context=context, retries=max_retries_wikidata)
    if len(d0) == 0:
        d0 = get_wikidata(sparql_query1 % label_check, context=context, retries=max_retries_wikidata)
    return d0

unique_id_params = ['wordnet_pwn30','freebase_mid','wikidata_qid',
                    'coco_pano_id','mvd_pano_id','cityscapes_id', 'mvd_v2p0_name','cityscapes_name',
                    'scannet_name', 'ade20k_id', 'wilddash_name', 'wilddash_pano_id',
                    'viper_id', 'viper_name', 'viper_inst_id', 'viper_pano_id', 'ade20k_name']
check_dubl = {p:{} for p in unique_id_params}

def check_for_dublicates(key, add_entry, cmp_entry = {}, append_dubl_data = True):
    for p in unique_id_params:
        if not p in add_entry or add_entry[p] == '':
            continue
        if add_entry[p] in check_dubl[p] and check_dubl[p][add_entry[p]] != key:
            print(p + ' id for ' + key + ' already exists at key: ' + check_dubl[p][add_entry[p]])
            return False
        if p in cmp_entry and cmp_entry[p] != add_entry[p]:
            print(p+' collision for ' + key + ': ' + str(cmp_entry[p]) + ' vs ' + str(add_entry[p]))
            return False
        if append_dubl_data:
            check_dubl[p][add_entry[p]] = key
    return True

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--append_file', type=str, default="./label_definitions/wilddash-config.json",
                        help='Path to csv or json file containing additional mappings') #./label_definitions/panoptic_coco_categories.json
    parser.add_argument('--input', type=str, default="joint_mapping.json",
                        help="Input json file path, set to empty string to generate anew")
    parser.add_argument('--output', type=str, default="joint_mapping_tmp.json",
                        help="Output json file path")
    args = parser.parse_args(argv)

    inv_fix_unified_labels = {v: k for k, v in fix_unified_labels.items()}

    if os.path.exists(args.input):
        with open(args.input, 'r') as ifile:
            joined_label_space = json.load(ifile)
        for key, vals in joined_label_space.items():
            check_for_dublicates(key, vals)

    if len(args.append_file) > 0 and os.path.exists(args.append_file):
        is_names_txt_format = args.append_file[-9:] == "names.txt"
        is_csv_format = args.append_file[-4:] == ".csv"
        if is_names_txt_format:
            with open(args.append_file, newline='\n') as ifile:
                appendf = [l.strip() for l in ifile.readlines()]
        elif is_csv_format:
            with open(args.append_file, newline='') as ifile:
                appendf = list(csv.reader(ifile))
        else:
            with open(args.append_file, 'r') as ifile:
                appendf = json.load(ifile)
        if is_names_txt_format: #load/compare mseg supplied names
            dsname_old = os.path.basename(args.append_file).split('-')[0].replace("mapillary","mvd")
            dsname_new = os.path.basename(args.append_file).split('_')[0]
            for idx0, name in enumerate(appendf):
                key = None
                corr_name = dsname_old+'_name' if dsname_old+'_name' in check_dubl else dsname_old+'_pano_name'
                checkids = [dsname_old+'_id', dsname_old+'_inst_id', dsname_old+'_pano_id', corr_name]
                for checkid in checkids:
                    if not checkid in check_dubl or (not idx0 in check_dubl[checkid] and not name in check_dubl[checkid]):
                        continue
                    if key is None:
                        key = check_dubl[checkid].get(idx0, check_dubl[checkid].get(name, None))
                    elif key != check_dubl[checkid][idx0]:
                        print("Warning: Multiple entries for same key!", key, check_dubl[checkid][idx0], name)
                    checkentry = joined_label_space[key]
                    if checkentry[corr_name] != name:
                        print("Warning: Names mismatch:", check_dubl[checkid][idx0], checkentry[dsname_old+'_name'], name)
                    continue
                if key is None:
                    key = unify_namings(name)
                if not key in joined_label_space:
                    print("Adding: "+key+ " for ", name)
                    joined_label_space[key] = {}
                trg_entry = joined_label_space[key]
                #trg_entry.update({dsname_new+"_name":name})
                trg_entry.update({corr_name:name, checkids[0]:idx0})
        elif is_csv_format and "/m/" in appendf[0][0]:
            #oid_file
            for (mid, name) in appendf:
                if mid in check_dubl['freebase_mid']:
                    continue
                key = unify_namings(name)
                add_entry = {'oid_name': name, 'freebase_mid': mid}
                context = key.split('(')
                if len(context) > 1 and context[1][-1] == ')':
                    key = context[0].replace('_', '')
                    add_entry['context'] = context[1][:-1]
                elif key.find('human_') == 0:
                    key = key.split('_')[-1]
                    add_entry['context'] = 'human'
                f_wd = wikidata_from_freebaseid(mid)
                if not check_for_dublicates(key,f_wd):
                    continue
                add_entry.update(f_wd)
                joined_label_space.setdefault(key, {}).append(add_entry)
        elif isinstance(appendf, dict) and "labels" in appendf and "id_prefix" in appendf:
            #mapillary-style json
            id_param = appendf["id_prefix"]+"_id"
            name_param = appendf["id_prefix"]+"_name"
            id_is_idx = "pano" in appendf["id_prefix_eval"]
            id_param_eval = appendf["id_prefix_eval"]
            id_param_eval += "_id" if id_is_idx else "_name"
            possible_cat = None
            id_is_idx = not "boxable" in id_param_eval
            for idx0, vals in enumerate(appendf["labels"]):               
                if not id_is_idx and not vals.get('instances', True):
                    continue # quick hack to add all instance classes as boxables / inst
                if vals['name'] in check_dubl[name_param]:
                    key = check_dubl[name_param][vals['name']]
                else:
                    key = vals["readable"]
                    possible_cat = None
                    if ' Arrow (' in vals["readable"] or ' Way (' in vals["readable"] or \
                       ' General (' in vals["readable"] or ' Direction (' in vals["readable"] or \
                       ' Hatched (' in vals["readable"] or ' Symbol (' in vals["readable"] or \
                       ' Temporary (' in vals["readable"]:
                        vals["readable"] = vals["readable"].replace(' (',' ')[:-1] #fix for arrow() captions at 
                    context = vals["readable"].split('(')
                    if len(context) > 1 and context[1][-1] == ')':
                        key = context[0].strip().replace('_', '')
                        possible_cat = context[1][:-1]
                    pos_dd = vals['name'].find('--')
                    if pos_dd > 0:
                        possible_cat = vals['name'][:pos_dd]
                    key = unify_namings(key)

                if not key in joined_label_space:
                    print("Adding: "+key+ " for ", vals)
                    joined_label_space[key] = {}
                trg_entry = joined_label_space[key]
                vals_add = {name_param:vals['name']}
                if id_is_idx:
                    vals_add[id_param] = idx0
                if vals.get("evaluate", True):
                    vals_add[id_param_eval] =  idx0 if id_is_idx else vals['name']
                if not possible_cat is None:
                    vals_add['context'] = possible_cat
                if not check_for_dublicates(key, vals_add, trg_entry):
                    continue
                trg_entry.update(vals_add)
        elif isinstance(appendf, list) and isinstance(appendf[0], dict) and "supercategory" in appendf[0]:
            # coco panoptic file
            coco_pano = {
                unify_namings(entry['name']): {'coco_pano_id': entry['id'], 'coco_pano_name': entry['name']} for entry
                in appendf}
            joined_label_space.update(coco_pano)
        elif is_csv_format and isinstance(appendf, list) and "Ratio" in appendf[0]:
            # ade20k format
            for idx0,ratio,train_num, val_num, is_stuff, names in appendf[1:]:
                if idx0 in check_dubl['ade20k_id']:
                    continue
                names_s = names.split(';')
                key = names_s[0]
                for n in names_s:
                    check_key = unify_namings(n)
                    if check_key in joined_label_space:
                        key = check_key
                        break
                if not key in joined_label_space:
                    print("Adding: "+key+ " for ", names)
                    joined_label_space[key] = {}
                trg_entry = joined_label_space[key]
                trg_entry.update({'ade20k_names':names,'ade20k_id':idx0})

    skip_auto = ["lane_marking_", "traffic_light_", "lane_marking_dashed_", "signage_", "traffic_light_", "traffic_sign_"]
    #automatically adds qids
    for key, vals in joined_label_space.items():
        if 'wikidata_qid' in vals:
            if len(vals['wikidata_qid']) > 0 and not 'wikidata_name' in vals:
                w1 = wikidata_from_qid(vals['wikidata_qid'])
                if not check_for_dublicates(key, w1, vals):
                    continue
                vals.update(w1)
            continue
        if any([s in key for s in skip_auto]):
            continue
        n_qid = wikidata_from_name(key, context=vals.get('context','').split('_'))
        if len(n_qid) == 0:
            print("Did not find a qid for "+key)
            continue
        if not check_for_dublicates(key, n_qid,vals):
            continue
        vals.update(n_qid)

    for key, vals in joined_label_space.items():
        #find missing wordnet entries
        if 'wordnet_pwn30' in vals:
            if len(vals['wordnet_pwn30']) == 0:
                continue
            add_entry = vals
        else:
            if any([s in key for s in skip_auto]):
                continue
            key0 = key.replace('-stuff','').replace('-merged','').replace('-other','')
            key0 = fix_unified_labels.get(key0, key0)
            if key0 in joined_label_space and 'wordnet_pwn30' in joined_label_space[key0]:
                continue
            add_entry = get_wordnet(key0, context=vals.get('context','').split('_'), retries=max_retries_wikidata)
            if len(add_entry) == 0:
                if key0 in inv_fix_unified_labels:
                    key0 = inv_fix_unified_labels[key0]
                else:
                    key0 = key0.replace('_','')
                key0 = fix_unified_labels.get(key0, key0)
                if key0 in joined_label_space and 'wordnet_pwn30' in joined_label_space[key0]:
                    continue
                add_entry = get_wordnet(key0, context=vals.get('context', '').split('_'), retries=max_retries_wikidata)
        if not 'wordnet_pwn30' in add_entry:
            print('Not found in wordnet: ' + key)
            continue
        if not 'wordnet_gloss' in add_entry:
            g0 = get_wordnet_gloss(add_entry['wordnet_pwn30'], retries=0)
            add_entry.update(g0)
        if not check_for_dublicates(key, add_entry, vals):
            continue
        vals.update(add_entry)
        #find wikidata via pwn30
        if not 'wikidata_qid' in vals:
            w1 = wikidata_from_wordnet3p0(vals['wordnet_pwn30'])
            if not check_for_dublicates(key, w1, vals):
                continue
            vals.update(w1)

    cnt_both = 0
    cnt_qid = 0
    for key, vals in joined_label_space.items():
        if 'freebase_mid' in vals and 'wordnet_pwn30' in vals:
            cnt_both += 1
        if 'wikidata_qid' in vals:
            cnt_qid += 1
    
    print("Found mappings for %i entries and %i have qids of %i" % (cnt_both , cnt_qid, len(joined_label_space)))
    
    with open(args.output, 'w', newline='\n') as ofile:
        json.dump(joined_label_space, ofile, sort_keys=True, indent=4)
        
    return 0
    
if __name__ == "__main__":
    print("Automatically generate mapping between freebase, imagenet (=wordnet 3.0) ids and optionally wikidata qids")
    sys.exit(main())
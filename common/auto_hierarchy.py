#!/usr/bin/env python
# -*- coding: utf-8 -*-
# add missing mapping_wordnet.json from here:
# https://github.com/ozendelait/wordnet-to-json/releases

import os, sys, argparse, json, csv, time
from automap import get_wordnet_gloss, wikidata_from_qid, wikidata_from_wordnet3p0, fix_unified_labels

retry_time_sleep_s = 1.0
max_retries_wikidata = 3

def get_parents(vals):
    if 'parent_name' in vals:
        return
    if 'wordnet_pwn30' in vals and not 'wikidata_qid' in vals:
        add0 = wikidata_from_wordnet3p0(vals['wordnet_pwn30'])
        vals['wikidata_qid'] = add0.get('wikidata_qid','')
        vals['parents_qid'] = add0.get('parents_qid',[])
        if 'freebase_mid' in add0 and not 'freebase_mid' in vals:
            vals['freebase_mid'] = add0['freebase_mid']
    if 'wikidata_qid' in vals and len(vals['wikidata_qid']) > 0 and not 'parents_qid' in vals:
        add0 = wikidata_from_qid(vals['wikidata_qid'])
        vals['parents_qid'] = add0.get('parents_qid',[])
    if 'wordnet_pwn30' in vals and len(vals['wordnet_pwn30']) > 0  and not 'parents_pwn30' in vals:
        add0 = get_wordnet_gloss(vals['wordnet_pwn30'])
        vals['parents_pwn30'] = add0.get('parents_pwn30',[])


#find direct parents
link_pwn30 = {}
link_qid = {}
link_freebase = {}
def fix_links(addtmp, key):
    global link_pwn30, link_qid, link_freebase
    if 'freebase_mid' in addtmp:
        link_freebase[addtmp['freebase_mid']] = key
    if "wordnet_pwn30" in addtmp:
        link_pwn30[addtmp['wordnet_pwn30']] = key
    if "wikidata_qid" in addtmp:
        link_qid[addtmp['wikidata_qid']] = key


def add_parent_as_tmp(joined_label_space, key, addtmp):
    if "wordnet_pwn30" in addtmp and addtmp["wordnet_pwn30"] in link_pwn30 and link_pwn30[addtmp["wordnet_pwn30"]].find("_tmp_") < 0:
        print("Warning: rebending parent of "+key+" to "+ link_pwn30[addtmp["wordnet_pwn30"]])
        joined_label_space[key]['parent_name'] = link_pwn30[addtmp["wordnet_pwn30"]]
        return None,None
    if 'freebase_mid' in addtmp and addtmp['freebase_mid'] in link_freebase and link_freebase[addtmp["freebase_mid"]].find("_tmp_") < 0:
        print("Warning: rebending parent of "+key+" to "+ link_freebase[addtmp["freebase_mid"]])
        joined_label_space[key]['parent_name'] = link_freebase[addtmp["freebase_mid"]]
        return None,None
    keyparent = None
    if "wordnet_name" in addtmp:
        keyparent = addtmp["wordnet_name"]
    if keyparent is None and "wikidata_name" in addtmp and len("wikidata_name") > 0:
        keyparent = addtmp["wikidata_name"]  
    if not keyparent is None:
        keyparent = keyparent.lower().replace("'","").replace(" ","_").replace("class_of_","")
        keyparent = fix_unified_labels.get(keyparent, keyparent)
        if not keyparent in joined_label_space and len(keyparent) > 5 and fix_unified_labels.get(keyparent[:-1],keyparent[:-1]) in joined_label_space:
            keyparent = fix_unified_labels.get(keyparent[:-1],keyparent[:-1])
        if keyparent == key:
            return {}, None
        if keyparent in joined_label_space:
            print("Warning: rebending parent of "+key+" to "+ keyparent)
            joined_label_space[key]['parent_name'] = keyparent
            return None,None
        keyparent = "_tmp_"+keyparent
        get_parents(addtmp)
        return addtmp, keyparent
    return {}, None

def get_possible_keys(joined_label_space, start_key, max_depth=16):
    visited_keys = [start_key]
    for _ in range(max_depth):
        next_key = joined_label_space[visited_keys[-1]].get("parent_name","")
        if next_key == "" or next_key in visited_keys:
            break
        visited_keys.append(next_key)
    return visited_keys
    
def main(argv=sys.argv[1:]):
    global link_pwn30, link_qid, link_freebase
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default="joint_mapping.json",
                        help="Input json file path, set to empty string to generate anew")
    parser.add_argument('--output', type=str, default="joint_mapping_tmp.json",
                        help="Output json file path")
    args = parser.parse_args(argv)
    with open(args.input, 'r') as ifile:
        joined_label_space = json.load(ifile)

    #automatically adds missing parent candidates 
    remove_keys = []
    possible_keys = []
    cnt_no_parent = 0
    for key,vals in joined_label_space.items():
        is_tmp_key = key.find('_tmp_') >= 0
        if key.find(' ') > 0 or key.find("'") > 0 or (is_tmp_key and key.replace('_tmp_','') in joined_label_space):
            remove_keys.append(key)
            continue
        if 'parent_name' in vals and len(vals["parent_name"]) > 0 and not vals['parent_name'] in joined_label_space:
            vals.pop('parent_name') #invalid parent
        if 'parent_name' in vals and vals['parent_name'].find('_tmp_') >= 0 and vals['parent_name'].replace('_tmp_','') in joined_label_space:
            vals['parent_name'] = vals['parent_name'].replace('_tmp_','')#fix connection            
        get_parents(vals)
        if not 'parent_name' in vals:
            print("Warning: Found no parent for "+key)
            cnt_no_parent += 1
        elif not is_tmp_key:
            vals.pop("parents_pwn30", None)
            vals.pop("parents_qid", None)
            pkeys = get_possible_keys(joined_label_space, key)
            if vals['parent_name'].find("_tmp") >= 0:
                for p in pkeys[1:]:
                    if p.find("_tmp") < 0:
                        vals['parent_name'] = p
                        break
            if  vals['parent_name'].find("_tmp") >= 0:
                print("Warning: temporary entry as parent: ",pkeys)
                cnt_no_parent += 1
            if pkeys[-1] != "unlabeled": #all paths should lead to unlabeled
                print("Warning: incomplete entry: ",pkeys)
            possible_keys += pkeys
    print("Open entries: ", cnt_no_parent)
    possible_keys = set(possible_keys)   
    cleanup_keys = [key for key in joined_label_space.keys() if key.find('_tmp_') >= 0 and not key in possible_keys]
    remove_keys = list(set(remove_keys+cleanup_keys))
    for r in remove_keys:
        joined_label_space.pop(r)
    
    #find direct parents
    link_pwn30 = {vals['wordnet_pwn30']:key  for key,vals in joined_label_space.items() if 'wordnet_pwn30' in vals}
    link_qid = {vals['wikidata_qid']:key  for  key,vals in joined_label_space.items() if 'wikidata_qid' in vals}
    link_freebase = {vals['freebase_mid']:key  for  key,vals in joined_label_space.items() if 'freebase_mid' in vals}
    
    tmp_keys = {}
    for key, vals in joined_label_space.items():
        if 'parent_name' in vals:
            continue
        found_link0 = [link_pwn30[p] for p in vals.get('parents_pwn30',[]) if p in link_pwn30]
        found_link1 = [link_qid[p] for p in vals.get('wikidata_qid',[]) if p in link_qid]
        found_link0 = set(found_link0+found_link1)
        found_link0_clean = set([p for p in list(found_link0) if p.find("_tmp") < 0])
        if len(found_link0_clean) > 0:
            found_link0 = found_link0_clean #skip tmp entries for regular ones
        if len(found_link0) == 1:
            key_parent = list(found_link0)[0]
            vals['parent_name'] = key_parent
        elif len(found_link0) > 1:
            print("Warning: Multiple parents found for "+key+':', found_link0)
        #if False:
        elif key.find("_tmp") < 0:
            #add temporary jump nodes
            for p in vals.get('parents_qid',[]):
                addtmp = wikidata_from_qid(p)
                addtmp, keyparent = add_parent_as_tmp(joined_label_space, key, addtmp)
                if addtmp is None:
                    break
                if keyparent is None:
                    continue
                tmp_keys.setdefault(keyparent, {}).update(addtmp)
                fix_links(addtmp, keyparent)
            if 'parent_name' in vals:
                continue
            for p in vals.get('parents_pwn30',[]):
                addtmp = get_wordnet_gloss(p)
                addtmp, keyparent = add_parent_as_tmp(joined_label_space, key, addtmp)
                if addtmp is None:
                    break
                if keyparent is None:
                    continue
                tmp_keys.setdefault(keyparent, {}).update(addtmp)
                fix_links(addtmp, keyparent)
    joined_label_space.update(tmp_keys) 

    #print("Found mappings for %i entries and %i have qids of %i" % (cnt_both , cnt_qid, len(joined_label_space)))
    with open(args.output, 'w', newline='\n') as ofile:
        json.dump(joined_label_space, ofile, sort_keys=True, indent=4)
        
    return 0
    
if __name__ == "__main__":
    print("Automatically generate hierarchy structure based on  imagenet (=wordnet 3.0) ids and wikidata qids")
    sys.exit(main())
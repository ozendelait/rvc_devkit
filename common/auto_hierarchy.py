#!/usr/bin/env python
# -*- coding: utf-8 -*-
# add missing mapping_wordnet.json from here:
# https://github.com/ozendelait/wordnet-to-json/releases

import os, sys, argparse, json, csv, time
from automap import get_wordnet_gloss, wikidata_from_qid, get_wikidata

retry_time_sleep_s = 1.0
max_retries_wikidata = 3

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default="joint_mapping.json",
                        help="Input json file path, set to empty string to generate anew")
    parser.add_argument('--output', type=str, default="joint_mapping_tmp.json",
                        help="Output json file path")
    args = parser.parse_args(argv)

    with open(args.input, 'r') as ifile:
        joined_label_space = json.load(ifile)

    #automatically adds parent candidates 
    for key, vals in joined_label_space.items():
        if 'parent_name' in vals:
            continue
        if 'wikidata_qid' in vals and len(vals['wikidata_qid']) > 0 and not 'parents_qid' in vals:
            add0 = wikidata_from_qid(vals['wikidata_qid'])
            if 'parents_qid' in add0:
                vals['parents_qid'] = add0['parents_qid']
                
        if 'wordnet_pwn30' in vals and len(vals['wordnet_pwn30']) > 0  and not 'parents_pwn30' in vals:
            add0 = get_wordnet_gloss(vals['wordnet_pwn30'])
            if 'parents_pwn30' in add0:
                vals['parents_pwn30'] = add0['parents_pwn30']

    #find direct parents
    link_pwn30 = {vals['wordnet_pwn30']:key  for key,vals in joined_label_space.items() if 'wordnet_pwn30' in vals}
    link_qid = {vals['wikidata_qid']:key  for  key,vals in joined_label_space.items() if 'wikidata_qid' in vals}
    tmp_keys = {}
    for key, vals in joined_label_space.items():
        if 'parent_name' in vals:
            continue
        found_link0 = [link_pwn30[p] for p in vals.get('parents_pwn30',[]) if p in link_pwn30]
        found_link1 = [link_qid[p] for p in vals.get('wikidata_qid',[]) if p in link_qid]
        found_link0 = set(found_link0+found_link1)
        if len(found_link0) == 1:
            vals['parent_name'] = found_link0[0]
        elif len(found_link0) > 1:
            print("Warning: Multiple parents found for "+key+':', found_link0)
        else:
            #add temporary jump nodes
            for p in vals.get('wikidata_qid',[]):
                addtmp = wikidata_from_qid(p)
                if "wordnet_pwn30" in addtmp and addtmp["wordnet_pwn30"] in link_pwn30:
                    print("Warning: rebending parent of "+key+" to "+ link_pwn30[addtmp["wordnet_pwn30"]])
                    vals['parent_name'] = link_pwn30[addtmp["wordnet_pwn30"]]
                    break
                if "wordnet_name" in addtmp:
                    key = "_tmp_"+addtmp["wordnet_name"]
                    tmp_keys[key] = addtmp
            if 'parent_name' in vals:
                continue
            for p in vals.get('parents_pwn30',[]):
                addtmp = get_wordnet_gloss(p)
                if "wordnet_name" in addtmp:
                    key = "_tmp_"+addtmp["wordnet_name"]
                    tmp_keys.setdefault(key, {}).update(addtmp)
              
    joined_label_space.update(tmp_keys) 

    #print("Found mappings for %i entries and %i have qids of %i" % (cnt_both , cnt_qid, len(joined_label_space)))
    with open(args.output, 'w', newline='\n') as ofile:
        json.dump(joined_label_space, ofile, sort_keys=True, indent=4)
        
    return 0
    
if __name__ == "__main__":
    print("Automatically generate hierarchy structure based on  imagenet (=wordnet 3.0) ids and wikidata qids")
    sys.exit(main())
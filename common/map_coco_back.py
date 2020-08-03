#!/usr/bin/env python
# -*- coding: utf-8 -*-
# remap boxable COCO annotations using a supplied mapping csv file

import os
import sys
import argparse
import csv
from tqdm import tqdm
import rvc_json_helper

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--predictions', type=str, 
                        help="Input json file of predictions to remap")
    parser.add_argument('--annotations', type=str, 
                        help="annotations json file used to create the mapping")
    parser.add_argument('--mapping', type=str, default='./obj_det_mapping.csv',
                        help="Csv file defining mapping")
    parser.add_argument('--mapping_row', type=str, default=None,
                        help="Row header from row in csv file to use; default: second row")
    parser.add_argument('--map_to', type=str, default=id,
                        help="Map to id, freebase_id or any other category type")
    parser.add_argument('--void_id', type=int, default=0,
                        help="Void id for labels not found in mapping csv")
    parser.add_argument('--remove_void',  dest='remove_void', action='store_true',
                        help="Only keep boxes with labels that can be remapped")
    parser.add_argument('--output', type=str, 
                        help="Output json file path for result.")
    parser.add_argument('--reduce_boxable', dest='reduce_boxable', action='store_true',
                        help="Only keep minimum of annotation data needed for boxable training.")
    parser.add_argument('--reduce_pano', dest='reduce_pano', action='store_true',
                        help="Only keep minimum of annotation data needed for panoptic/instance segm. training.")

    parser.set_defaults(remove_void=False, reduce_boxable=False, reduce_pano=False)
    args = parser.parse_args(argv)
    
    print("Loading source predictions file " + args.predictions + "...")
    pred = rvc_json_helper.load_json(args.predictions)

    print("Loading annotation file " + args.annotations + "...")
    annot = rvc_json_helper.load_json(args.annotations)

    # load pre-defined mapping; first row is target label name, row from --mapping_row
    # defines source row for this input data; use semicolon from N->1 mappings
    # e.g.
    # animal,cat;dog
    # will map both cat and dog source labels to the target label animal
    with open(args.mapping, newline='') as ifile:
        mapping0 = list(csv.reader(ifile))
        if args.mapping_row is None:
            idx_use = 1
        else:
            idx_use = mapping0[0].index(args.mapping_row)
        trg_labels = {m[0]:m[idx_use] for m in mapping0[1:]}
        cats_sorted = list(sorted(trg_labels.keys()))
        trg_cats = {c:{'supercategory':'rvc_jls', 'id': id0+1, 'name':c} for id0, c in enumerate(cats_sorted)}
        src_cats = {c['name'].lower().strip():c  for c in annot['categories']}
        trg_to_src = {}
        for t, src_all in trg_labels.items():
            t_id = trg_cats[t]['id']
            for s in src_all.split(';'): #allows multi-to-one mappings
                if len(s)  == 0:
                    continue
                s = s.lower().strip()
                if not s in src_cats: #quick fix for mix of supercategory and name tag in some mvd json file; mix of name/id in oid cat. file
                    check_cat =  "freebase_id" if "freebase_id" in annot['categories'][0] else 'supercategory'
                    pot_supcat = [c['name'].lower().strip() for c in annot['categories'] if c.get(check_cat,'') == s]
                    if len(pot_supcat) == 1:
                        s = pot_supcat[0]
                if not s in src_cats:
                    print("Warning: Unknown source cat "+s+" requested. Skipping.")
                    continue
                trg_to_src[t_id] = src_cats[s][args.map_to]


    for p in tqdm(pred, desc='Remapping predictions '):
        if 'category_id' in p:
            p['category_id'] = trg_to_src.get(p['category_id'], args.void_id)
            p['bbox'] = [round(box, 2) for box in p['bbox']]
            p['score'] = round(p['score'], 4)
        if 'segments_info' in p:
            for s in p['segments_info']:
                s["category_id"] = trg_to_src.get(s['category_id'], args.void_id)
                s['bbox'] = [round(box, 2) for box in s['bbox']]
                p['score'] = round(p['score'], 4)
        if args.reduce_boxable or args.reduce_pano:
            p.pop('segmentation',None)
        
    if args.remove_void:
        if 'category_id' in pred[0]:
            pred = [p for p in pred if p['category_id'] != args.void_id]
        if 'segments_info' in pred[0]:
            pred = [[s for s in p if s['category_id'] != args.void_id] for p in pred]

            
    print("Saving target prediction file "+args.output+"...")
    rvc_json_helper.save_json(pred, args.output)

    return 0
    
if __name__ == "__main__":
    sys.exit(main())
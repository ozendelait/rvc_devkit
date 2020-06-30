#!/usr/bin/env python
# -*- coding: utf-8 -*-
# remap boxable COCO annotations using a supplied mapping csv file

import os
import sys
import argparse
import csv
from tqdm import tqdm
import rvc_json_helper

def get_relative_path(root_rel, trg_dir):
    pos_curly = root_rel.find('{')
    pos_slash = root_rel.rfind('/',pos_curly) if pos_curly > 0 else -1
    recover_curly = ""
    if pos_slash >= 0:
        recover_curly = root_rel[pos_slash:]
        root_rel = root_rel[:pos_slash]
    return  root_rel, os.path.relpath(root_rel, os.path.dirname(trg_dir)).replace('\\','/') + recover_curly + '/' #use only unix-style slashes

def fix_missing_slash(path0):
    if not path0 is None and path0[-1] != '/' and path0[-1] != '\\':
        path0 += '/'
    return path0

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, 
                        help="Input json file of annotations to remap")
    parser.add_argument('--mapping', type=str, default='./obj_det_mapping.csv',
                        help="Csv file defining mapping")
    parser.add_argument('--mapping_row', type=str, default=None,
                        help="Row header from row in csv file to use; default: second row")
    parser.add_argument('--image_root', type=str, default=None,
                        help="adds image root to each filepath")
    parser.add_argument('--image_root_rel', type=str, default=None,
                        help="adds relative path between output json dir and this directory each filepath")
    parser.add_argument('--annotation_root', type=str, default=None,
                        help="adds annotation mask root to each filepath")
    parser.add_argument('--annotation_root_rel', type=str, default=None,
                        help="adds relative path between output json dir and annotation mask directory each filepath")
    parser.add_argument('--void_id', type=int, default=0,
                        help="Void id for labels not found in mapping csv")
    parser.add_argument('--output', type=str, 
                        help="Output json file path for result.")
    parser.add_argument('--reduce_boxable', dest='reduce_boxable', action='store_true',
                        help="Only keep minimum of annotation data needed for boxable training.")
    parser.add_argument('--reduce_pano', dest='reduce_pano', action='store_true',
                        help="Only keep minimum of annotation data needed for panoptic/instance segm. training.")

    parser.set_defaults(do_merging=False, reduce_boxable=False, reduce_pano=False)
    args = parser.parse_args(argv)
    if not args.image_root_rel is None:
        args.image_root_rel, args.image_root = get_relative_path(args.image_root_rel, args.output)
    if not args.annotation_root_rel is None:
        args.annotation_root_rel, args.annotation_root = get_relative_path(args.annotation_root_rel, args.output)

    fix_missing_slash(args.image_root)
    fix_missing_slash(args.annotation_root)

    print("Loading source annotation file " + args.input + "...")
    annot = rvc_json_helper.load_json(args.input)

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
        src_to_trg = {}
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
                src_to_trg[src_cats[s]['id']]= t_id

    if 'categories' in annot:
        annot['categories'] = [trg_cats[c] for c in cats_sorted]

    if not args.image_root is None:
        if args.image_root[-1] != '/' and args.image_root[-1] != '\\':
            args.image_root += '/'
        for i in annot['images']:
            i['file_name'] = args.image_root.format(file_name=i['file_name'], file_name_su = i['file_name'].split('_')) + i['file_name']
    if args.reduce_pano or args.reduce_boxable:
        reduce_size_entries = ["date_captured","coco_url","url","flickr_url"]
        for i in annot['images']:
            for e in reduce_size_entries:
                i.pop(e,None)

    if 'annotations' in annot:
        for a in tqdm(annot['annotations'], desc='Remapping annotations '):
            if 'category_id' in a:
                a['category_id'] = src_to_trg.get(a['category_id'],args.void_id)
            if 'segments_info' in a:
                for s in a['segments_info']:
                    s["category_id"] = src_to_trg.get(s['category_id'],args.void_id)
            if args.reduce_boxable or args.reduce_pano:
                a.pop('segmentation',None)
            if not args.annotation_root is None and 'file_name' in a:
                a['file_name'] = args.annotation_root.format(file_name=a['file_name'], file_name_su = a['file_name'].split('_')) + a['file_name']

    print("Saving target annotation file "+args.output+"...")
    rvc_json_helper.save_json(annot, args.output)

    return 0
    
if __name__ == "__main__":
    sys.exit(main())
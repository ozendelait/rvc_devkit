#!/usr/bin/env python
# -*- coding: utf-8 -*-
# remap boxable COCO annotations using a supplied mapping csv file

import os, sys, argparse, json, csv, tqdm

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
    parser.add_argument('--void_id', type=int, default=0,
                        help="Void id for labels not found in mapping csv")
    parser.add_argument('--output', type=str, 
                        help="Output json file path for result.")
    parser.add_argument('--do_merging', dest='do_merging', action='store_true',
                        help="Merge new data to existing data in output file (both must share same target label space).")
    parser.add_argument('--reduce_size', dest='reduce_size', action='store_true',
                        help="Only keep minimum of annotation data needed for boxable training.")

    parser.set_defaults(do_merging=False, reduce_size=False)
    args = parser.parse_args(argv)

    print("Loading source annotation file " + args.input + "...")
    with open(args.input, 'r') as ifile:
        annot = json.load(ifile)


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
            i['file_name'] += args.image_root
    if args.reduce_size:
        reduce_size_entries = ["date_captured","coco_url","url","flickr_url"]
        for i in annot['images']:
            for e in reduce_size_entries:
                i.pop(e,None)

    if 'annotations' in annot:
        for a in tqdm.tqdm(annot['annotations'], desc='Remapping annotations '):
            a['category_id'] = src_to_trg.get(a['category_id'],args.void_id)
            if args.reduce_size:
                a.pop('segmentation',None)

    if args.do_merging and os.path.exists(args.output):
        print("\nLoading existing target annotation file " + args.output + " for merging...")
        with open(args.output, 'r') as ifile:
            annot_exists = json.load(ifile)
        #quick check if annot['categories'] is correct
        versions_match = len(annot['categories']) == len(annot_exists['categories'])
        if versions_match:
            for id0, a in enumerate(annot_exists['categories']):
                a_cmp = annot['categories'][id0]
                if a_cmp['name'] != a['name'] or a_cmp['id'] != a['id']:
                    print("Category mismatch at entry %i:"%id0, a_cmp, a)
                    versions_match = False
                    break
        if not versions_match:
            print("Cannot merge new data to existing file; incompatible formats")
            return -3
        #TODO fix info and license merging
        #find maximum image id
        max_image_id = -1
        for i in annot_exists['images']:
            max_image_id = max(max_image_id, i['id'])

        for i in annot['images']:
            i['id'] += max_image_id
        annot_exists['images'] += annot.pop('images')
        for a in annot['annotations']:
            a['image_id'] += max_image_id
        annot_exists['annotations'] += annot.pop('annotations')

        #TODO fix annotation's ids
        annot = annot_exists

    print("Saving target annotation file "+args.output+"...")
    with open(args.output, 'w', newline='\n') as ofile:
        json.dump(annot, ofile)
        
    return 0
    
if __name__ == "__main__":
    sys.exit(main())
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# reduce samples to balance training or split one json into training and validation

import os, sys, argparse
import numpy as np
import rvc_json_helper

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str,
                        help="Coco json file to split")
    parser.add_argument('--split_perc', type=str,
                        help="Percentage numbers semicolon seperated for splitting. Specify 70;30 for a result with two json files.")
    parser.add_argument('--output', type=str, default=None,
                        help="Output json file path for result; a _0, _1, _2 etc is added to the basename for each split.")
    args = parser.parse_args(argv)
    if args.output is None:
        args.output = args.input
    print("Loading source coco annotation file " + args.input + "...")
    annot = rvc_json_helper.load_json(args.input)

    num_imgs = len(annot['images'])
    img_to_idx = {}
    for im_idx, i in enumerate(annot['images']):
        img_to_idx[im_idx] = i
    annot['images'] = []
    annot_to_idx = {}
    for a in annot['annotations']:
        annot_to_idx[a['image_id']] = annot_to_idx.get(a['image_id'],[]) + [a]
    annot['annotations'] = []

    all_indices = np.arange(num_imgs)
    np.random.shuffle(all_indices)
    split_start = 0
    for split_idx,split_perc in enumerate(args.split_perc.split(';')):
        trg_file = args.output.replace(".json","_%i.json"%split_idx)
        split_num = min(int(float(split_perc)*0.01*num_imgs+0.5), num_imgs-split_start)
        split_idc = list(sorted(all_indices[split_start:split_start+split_num]))
        split_start += split_num
        images0 = []
        add_image_ids = []
        for i in split_idc:
            img_entry = img_to_idx.pop(i)
            add_image_ids.append(img_entry['id'])
            images0.append(img_entry)
        annot0 = []
        for a in add_image_ids:
            annot0 += annot_to_idx.pop(a)
        annot_split = annot
        annot_split["images"] = images0
        annot_split["annotations"] = annot0
        print("Saving %i images into coco annotation file " % split_num + trg_file + "...")
        rvc_json_helper.save_json(annot_split, trg_file)

    if len(img_to_idx) > 0:
        print("Warning: A total of %i image entries are in neither of the resulting splitted json files."%len(img_to_idx))
    if len(annot_to_idx) > 0:
        print("Warning: A total of %i annotation entries are in neither of the resulting splitted json files."%len(annot_to_idx))
    return 0
    
if __name__ == "__main__":
    sys.exit(main())
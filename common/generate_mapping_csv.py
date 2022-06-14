#!/usr/bin/env python
# -*- coding: utf-8 -*-
# add missing mapping_wordnet.json from here:
# https://github.com/ozendelait/wordnet-to-json/releases

import os, sys, argparse, json, csv, time

#boxable
#join_data = ["oid_boxable_leaf","coco_boxable_name","mvd_v2p0_boxable_name"]
#instance
#join_data = ["oid_inst_leaf", "coco_inst_id_name", "cityscapes_inst_id_name", "mvd_inst_id_name", 'scannet_pano_id_name', 'viper_inst_id_name', 'cityscapes_inst_id_name', 'wilddash_inst_id_name']
#panoptic
#join_data = ["coco_pano_id_name", "cityscapes_pano_id_name", "cityscapes_pano_id_name", "mvd_pano_id_name", 'viper_name', 'wilddash_pano_id_name']
#join_data = [ "mvd_pano_id_name", "mvd_pano_id", "cityscapes_pano_id", "cityscapes_pano_id_name", "cityscapes_inst_id_name"]
#semseg
join_data = ["ade20k_id", "coco_pano_id", "cityscapes_pano_id", "mvd_v2p0_pano_id", 'scannet_pano_id', 'cityscapes_pano_id', 'wilddash_pano_id']

def solve_leaf_boxable(joined_label_space, oid_n, mid_to_key):
    if "Subcategory" in oid_n:
        for n in oid_n["Subcategory"]:
            solve_leaf_boxable(joined_label_space, n, mid_to_key)
    else:
        key0 = mid_to_key[oid_n["LabelName"]]
        joined_label_space[key0]["oid_inst_leaf"] = oid_n["LabelName"]

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default="joint_mapping.json",
                        help="Input json file path, set to empty string to generate anew")
    parser.add_argument('--output', type=str, default="joint_mapping.csv",
                        help="Output json file path")
    parser.add_argument('--populate_empty', type=str,
                        help="Populate empty entries of these entries using next parent id found in target label space. Seperate mutliple entries using semicolon.")
    args = parser.parse_args(argv)
    with open(args.input, 'r') as ifile:
        joined_label_space = json.load(ifile)

    #mid_to_key = {vals['freebase_mid']: key for key, vals in joined_label_space.items() if 'freebase_mid' in vals}
    #with open('label_definitions/challenge-2019-label300-segmentable-hierarchy.json', 'r') as ifile:
    #    super_cat_info = json.load(ifile)
    #solve_leaf_boxable(joined_label_space, super_cat_info, mid_to_key)
    populate_empty = {} if not args.populate_empty else args.populate_empty.split(';')

    all_lines = [['key']+join_data]
    for key, vals in joined_label_space.items():
        add_line = []
        is_valid_line = False
        for j in join_data:
            add_val = ""
            j_in_vals = j in vals
            j_use = j
            j_use0 = j_use
            if not j_in_vals and j.find("_id_name") > 0:
                j_in_vals = j.replace("_name","") in vals
                j_use = j.split('_')[0]+"_name"
                j_use0 = j_use
                if not j_use in vals:
                    j_use = j_use.replace("_name","_pano_name")
            if j_in_vals:
                add_val = vals[j_use]
                is_valid_line = True
            elif j in populate_empty:
                curr_name = key
                max_depth_hierarchy = 32
                for _ in range(max_depth_hierarchy):
                    parent = joined_label_space[curr_name].get('parent_name', 'unlabeled')
                    if not parent in joined_label_space or parent == curr_name:
                        curr_name = 'unlabeled'
                        break
                    curr_name = parent
                    if j in joined_label_space[curr_name]:
                        j_use = j
                        break
                    if j_use0 in joined_label_space[curr_name]:
                        j_use = j_use0
                        break
                    if j_use in joined_label_space[curr_name]:
                        break
                if j_use in joined_label_space[curr_name]:
                    add_val = joined_label_space[curr_name][j_use]
            add_line.append(add_val)
        if is_valid_line:
            all_lines.append([key]+add_line)

    with open(args.output, mode='w', newline='\n', encoding='utf-8') as ofile:
        cvswr = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL, lineterminator='\n',)
        for l in all_lines:
            cvswr.writerow(l)

    #with open(args.output, 'w') as ofile:
    #    json.dump(joined_label_space, ofile, sort_keys=True, indent=4)
    return 0
    
if __name__ == "__main__":
    print("Create src_datassets -> joint label space mapping csv file")
    sys.exit(main())
#!/usr/bin/env python
# -*- coding: utf-8 -*-
# add missing mapping_wordnet.json from here:
# https://github.com/ozendelait/wordnet-to-json/releases

import os, sys, argparse, json, csv, time

#join_obj_det = ["oid_boxable_leaf","obj365_boxable_name","coco_boxable_name","mvs_boxable_name"]
join_inst = ["oid_inst_leaf","coco_inst_id","cityscapes_inst_id","mvs_boxable_name"] #TODO: KITTI,

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
    args = parser.parse_args(argv)
    with open(args.input, 'r') as ifile:
        joined_label_space = json.load(ifile)

    #mid_to_key = {vals['freebase_mid']: key for key, vals in joined_label_space.items() if 'freebase_mid' in vals}
    #with open('label_definitions/challenge-2019-label300-segmentable-hierarchy.json', 'r') as ifile:
    #    super_cat_info = json.load(ifile)
    #solve_leaf_boxable(joined_label_space, super_cat_info, mid_to_key)

    all_lines = [['key']+join_obj_det]
    for key, vals in joined_label_space.items():
        add_line = []
        is_valid_line = False
        for j in join_obj_det:
            add_val = ""
            if j in vals:
                add_val = vals[j]
                is_valid_line = True
            add_line.append(add_val)
        if is_valid_line:
            all_lines.append([key]+add_line)

    with open(args.output, mode='w', newline='\n', encoding='utf-8') as ofile:
        cvswr = csv.writer(ofile, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for l in all_lines:
            cvswr.writerow(l)

    #with open(args.output, 'w') as ofile:
    #    json.dump(joined_label_space, ofile, sort_keys=True, indent=4)
    return 0
    
if __name__ == "__main__":
    print("Create src_datassets -> joint label space mapping csv file")
    sys.exit(main())
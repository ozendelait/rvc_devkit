#!/usr/bin/env python
# -*- coding: utf-8 -*-
# converts from joint csv mapping file (all datasets) to a single mseg-compatible tsv files (per dataset)

import os, sys, argparse, json, csv, time

dataset_names = {"ade20k_id":"ade20k-151",
                 "coco_pano_id":"coco-panoptic-201",
                 "kitti_pano_id":"kitti-34",
                 "mvd_pano_id":"mapillary-public66",
                 "scannet_pano_id":"scannet-20",
                 "key":"rvc_uint8"}

#fixes compatibility with mseg
fix_ade20k_two_words = {"chest":"chest of drawers",
              "pool": "pool table",
              "screen": "screen door",
              "coffee": "coffee table",
              "kitchen": "kitchen island",
              "swivel" : "swivel chair",
              "arcade":"arcade machine",
              "television":"television receiver",
              "dirt":"dirt track",
              "bulletin": "bulletin board",
              "traffic": "traffic light",
              "swimming": "swimming pool",
              "conveyer": "conveyer belt",
              "trade":"trade name",
              "crt":"crt screen",
              }

#TODO: VIPER, WildDash2

def fix_ade20k(mapping_path):
    with open(mapping_path, 'r') as ifile:
        joined_label_space = json.load(ifile)
    res_labels = []
    for j, vals in joined_label_space.items():
        if "ade20k_names" in vals:
            names = vals["ade20k_names"].split(';')
            vals["ade20k_name"] = fix_ade20k_two_words.get(names[0],names[0])
            if vals["ade20k_name"] in res_labels:
                print("Warning: dublicate name entry: "+vals["ade20k_name"])
            res_labels.append(vals["ade20k_name"])
    with open(mapping_path, 'w', newline='\n') as ofile:
        json.dump(joined_label_space, ofile, sort_keys=True, indent=4)

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, default='../segmentation/ss_mapping_uint8.csv',
                        help="Csv file defining input mapping")
    parser.add_argument('--output', type=str, default='../segmentation/ss_mapping_uint8_mseg.tsv',
                        help="Output tsv file path")
    parser.add_argument('--mapping', type=str, default='./joint_mapping.json',
                        help="Json file containing names for all ids")
    args = parser.parse_args(argv)
    #fix_ade20k(args.mapping)

    with open(args.mapping, 'r') as ifile:
        joined_label_space = json.load(ifile)

    with open(args.input, newline='') as ifile: #load existing entries
        csv_content = list(csv.reader(ifile))

    name_per_id = {}
    all_keys = []
    for key, v in joined_label_space.items():
        all_keys += v.keys()
    all_keys = list(set(all_keys))
    for id_key in csv_content[0]:
        name_key = None
        id_key_check = id_key.replace("kitti", "cityscapes")
        for c in [id_key_check.replace("_id", "_name"), id_key_check.replace("_pano_id", "_name")]:
            if c in all_keys:
                name_key = c
                break
        if name_key is None:
            print("Warning: no name field for id "+ id_key)
            continue
        name_per_id[id_key] = {int(v[id_key_check]):v[name_key] for v in joined_label_space.values() if id_key_check in v}

    tsv_content = [[dataset_names.get(n,n) for n in csv_content[0]]]
    for vals in csv_content[1:]:
        one_col = []
        for idx, v in enumerate(vals):
            if idx == 0:
                one_col.append(v)
                continue
            elif len(v) == 0:
                one_col.append('unlabeled')
                continue
            #find name of this id in source space
            names = []
            for id0 in v.split(';'):
                if not int(id0) in name_per_id[csv_content[0][idx]]:
                    print("Warning: Unknown idx "+ id0+ " for "+ csv_content[0][idx])
                    continue
                names.append(name_per_id[csv_content[0][idx]][int(id0)])
            if len(names) == 0:
                one_col.append('unlabeled')
            elif len(names) == 1:
                one_col.append(str(names[0]))
            else:
                one_col.append("{"+", ".join(names)+"}")
        tsv_content.append(one_col)

    with open(args.output, mode='w', newline='', encoding='utf-8') as ofile:
        cvswr = csv.writer(ofile, delimiter='\t', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        for l in tsv_content:
            cvswr.writerow(l)

if __name__ == "__main__":
    sys.exit(main())
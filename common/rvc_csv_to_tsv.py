#!/usr/bin/env python
# -*- coding: utf-8 -*-
# converts from joint csv mapping file (all datasets) to a single mseg-compatible tsv files (per dataset)

import os, sys, argparse, json, csv, time

dataset_names = {"ade20k_id":"ade20k-151",
                 "coco_pano_id":"coco-panoptic-201",
                 "kitti_pano_id":"kitti-34",
                 "mvs_pano_id":"mapillary-public66",
                 "scannet_pano_id":"scannet-20"}

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
    parser.add_argument('--input', type=str, default='../segmentation/ss_mapping.csv',
                        help="Csv file defining input mapping")
    parser.add_argument('--output', type=str, default='../segmentation/ss_mapping_mseg.tsv',
                        help="Output tsv file path")
    parser.add_argument('--mapping', type=str, default='./joint_mapping.json',
                        help="Json file containing names for all ids")
    args = parser.parse_args(argv)
    #fix_ade20k(args.mapping)

    with open(args.mapping, 'r') as ifile:
        joined_label_space = json.load(ifile)



    with open(args.input, newline='') as ifile: #load existing entries
        csv_content = list(csv.reader(ifile))

    tsv_content = [[dataset_names.get(n,n) for n in csv_content[0]]]
    for vals in csv_content[1:]:
        one_col = []
        for idx, v in enumerate(vals):
            if len(v) == 0:
                one_col.append('unlabeled')
                continue
            #find name of this id in source space
            entry = joined_label_space[vals[0]]
            corr_name = 'unlabeled'
            for c in [vals[0].replace("_id", "_name"), vals[0].replace("pano_id", "_name")]:
                if c in entry:
                    corr_name = entry[c]
                    break
            if corr_name == 'unlabeled':
                i = 0

            one_col.append(corr_name)
        tsv_content.append(one_col)

    with open(args.output, mode='w', newline='', encoding='utf-8') as ofile:
        cvswr = csv.writer(ofile, delimiter='\t', quotechar='"', lineterminator='\n', quoting=csv.QUOTE_MINIMAL)
        for l in tsv_content:
            cvswr.writerow(l)

if __name__ == "__main__":
    sys.exit(main())
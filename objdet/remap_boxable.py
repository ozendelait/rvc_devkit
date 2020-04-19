#!/usr/bin/env python
# -*- coding: utf-8 -*-
# remap boxable COCO annotations using a supplied mapping csv file

import os, sys, argparse, json, csv, tqdm


def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, 
                        help="Input json file of annotations to remap")
    parser.add_argument('--mapping', type=str, default='./obj_det_mapping.csv'
                        help="Csv file defining mapping")
    parser.add_argument('--output', type=str, 
                        help="Output json file path for result.")
    args = parser.parse_args(argv)
    
    with open(args.input, 'r') as ifile:
        inp_mapping = json.load(ifile)

    with open(args.append_file, newline='') as ifile:
        appendf = list(csv.reader(ifile))

    with open(args.output, 'w', newline='\n') as ofile:
        json.dump(joined_label_space, ofile, sort_keys=True, indent=4)
        
    return 0
    
if __name__ == "__main__":
    sys.exit(main())
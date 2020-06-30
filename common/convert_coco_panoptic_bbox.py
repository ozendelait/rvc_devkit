#!/usr/bin/env python
# -*- coding: utf-8 -*-
# remap boxable COCO annotations using a supplied mapping csv file

import os
import sys
import argparse
import rvc_json_helper

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', type=str, 
                        help="Input json file of annotations to remap")
    parser.add_argument('--output', type=str,
                        help="Output json file path for result.")

    args = parser.parse_args(argv)

    print("Loading source annotation file " + args.input + "...")
    annot = rvc_json_helper.load_json(args.input)

    anns = []
    for a in annot['annotations']:

        file_name = a['file_name']
        image_id = os.path.splitext(file_name)[0]

        for segment in a['segments_info']:
            segment['image_id'] = image_id
            anns.append(segment)
            
    annot['annotations'] = anns

    print("Saving target annotation file "+args.output+"...")
    rvc_json_helper.save_json(annot, args.output)

    return 0
    
if __name__ == "__main__":
    sys.exit(main())
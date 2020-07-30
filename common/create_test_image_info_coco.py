#!/usr/bin/env python
# -*- coding: utf-8 -*-
# create COCO annotations for test images

import os
import sys
import argparse
import imagesize
import rvc_json_helper


from tqdm import tqdm

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
    parser.add_argument('--image_root', type=str, default=None,
                        help="adds image root to each filepath")
    parser.add_argument('--image_root_rel', type=str, default=None,
                        help="adds relative path between output json dir and this directory each filepath")
    parser.add_argument('--annotations_val', type=str, 
                        help="Validation annotation file to get categories")
    parser.add_argument('--output', type=str,
                        help="Output json file path for result.")

    args = parser.parse_args(argv)
    if not args.image_root_rel is None:
        args.image_root_rel, args.image_root = get_relative_path(args.image_root_rel, args.output)   
    args.image_root = fix_missing_slash(args.image_root)
    args.image_root_rel = fix_missing_slash(args.image_root_rel)
    
    # load annotations 
    val_annot = rvc_json_helper.load_json(args.annotations_val)
    
    # process images
    images = []
    image_files = os.listdir(args.image_root_rel)
    for file in tqdm(image_files, desc="Processing images ..."):
        
        # get relative filename
        file_name = args.image_root.format(file_name=file, file_name_su = file.split('_')) + file
        # get image size
        image_path = args.image_root_rel.format(file_name=file, file_name_su = file.split('_')) + file
        width, height = imagesize.get(image_path)
        # create image info
        img = {
            'file_name': file_name,
            'id': os.path.splitext(file)[0],
            'width': width,
            'height': height
        }
        images.append(img)
      
    # create dataset
    test_image_info = {'images': images, 'categories': val_annot['categories']}

    # save output
    print("Saving target annotation file "+args.output+"...")
    rvc_json_helper.save_json(test_image_info, args.output)

    return 0
    
if __name__ == "__main__":
    sys.exit(main())
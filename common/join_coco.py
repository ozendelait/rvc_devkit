#!/usr/bin/env python
# -*- coding: utf-8 -*-
# remap boxable COCO annotations using a supplied mapping csv file

import os, sys, argparse, datetime
import rvc_json_helper

def join_info(old_info, add_info = {}):
    initialize = len(add_info) == 0
    if initialize:
        contributor = old_info.get('contributor','')
        add_info = old_info
    else:
        contributor = old_info.get('contributor','') +"; "+ add_info.get('contributor','')
    ret_info = {"year":2022, "version":"0.2", "description": 'Joint dataset for RVC, see element "datasets" for included datasets; original root element "licenses" is added to "info"; individual image entries contain a ds_id which references the original dataset within this table. The license field refers to the original license idx.',
                "contributor": contributor,
                "datasets": old_info.get("datasets",[])+[add_info],
                "url":"robustvision.net", "date_created": str(datetime.datetime.now())}
    return ret_info

def check_versions_match(annot, annot_add):
    #quick check if annot['categories'] is correct
    versions_match = len(annot['categories']) == len(annot_add['categories'])
    if versions_match:
        for id0, a in enumerate(annot_add['categories']):
            a_cmp = annot['categories'][id0]
            if a_cmp['name'] != a['name'] or a_cmp['id'] != a['id']:
                print("Category mismatch at entry %i:"%id0, a_cmp, a)
                versions_match = False
                break
    return versions_match

def main(argv=sys.argv[1:]):
    parser = argparse.ArgumentParser()
    parser.add_argument('--join', type=str,
                        help="Coco json file(s) to join, seperate list entries by semicolon, merging is done in order from first to last")
    parser.add_argument('--output', type=str, 
                        help="Output json file path for result.")
    args = parser.parse_args(argv)

    annot = {}
    joint_image_id = 0
    for j in args.join.split(';'):
        if not os.path.exists(j):
            print("Error: file "+j+" not found!")
            return 1
        print("Loading coco annotation file " + j + "...")
        annot_add = rvc_json_helper.load_json(j)
            
        src_info_idx = len(annot_add.get("info",{}).get("datasets",[]))
        if not 'info' in annot_add:
            annot_add["info"]={"description":" loaded "+j}
        if "licenses" in annot_add:
            annot_add["info"]["licenses"] =  annot_add["licenses"]
        if src_info_idx == 0:
            annot['info'] = join_info(annot_add)
            annot['categories'] = annot_add['categories']
        else:
            annot['info'] = join_info(annot['info'], annot_add['info'])
            if not check_versions_match(annot, annot_add):
                print("Cannot merge new data to existing file; incompatible formats!")
                return -3

        old_id_to_new = {}
        for i in annot_add['images']:
            #save original ids for reference
            i['ds_id'] = i['id']
            i['ds_id'] = src_info_idx # idx from src_info
            old_id_to_new[i['id']] = joint_image_id
            i['id'] = joint_image_id
            joint_image_id += 1
        annot['images'] = annot.get('images',[]) + annot_add.pop('images')
        for a in annot_add['annotations']:
            a['image_id'] = old_id_to_new[a['image_id']]
        annot['annotations'] = annot.get('annotations', []) + annot_add.pop('annotations')
        del annot_add

    print("Saving result joint annotations to file "+args.output+"...")
    rvc_json_helper.save_json(annot, args.output)
    return 0
    
if __name__ == "__main__":
    sys.exit(main())
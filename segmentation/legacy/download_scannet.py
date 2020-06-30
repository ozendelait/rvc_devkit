#!/usr/bin/env python
# Downloads ScanNet public data release
# Run with ./download-scannet.py (or python download-scannet.py on Windows)
# -*- coding: utf-8 -*-
import argparse
import os
import tempfile
import sys, time

common_rvc_subfolder = os.path.realpath(os.path.join(os.path.dirname(os.path.realpath(os.path.abspath(__file__))),"../../common/"))
if common_rvc_subfolder not in sys.path:
    sys.path.insert(0, common_rvc_subfolder)
from rvc_download_helper import download_file_with_resume

BASE_URL = 'http://kaldir.vc.in.tum.de/scannet/'
TOS_URL = BASE_URL + 'ScanNet_TOS.pdf'
FILETYPES = ['.aggregation.json', '.sens', '.txt', '_vh_clean.ply', '_vh_clean_2.0.010000.segs.json', '_vh_clean_2.ply', '_vh_clean.segs.json', '_vh_clean.aggregation.json', '_vh_clean_2.labels.ply', '_2d-instance.zip', '_2d-instance-filt.zip', '_2d-label.zip', '_2d-label-filt.zip']
RELEASE = 'v1/scans'
RELEASE_TASKS = 'v1/tasks/'
RELEASE_SIZE = '1.2TB'


def get_release_scans(release_file):
    dstname = tempfile.mktemp(suffix='_rvc_scannet')
    download_file_with_resume(release_file, dstname)
    with open(dstname, 'r', newline='\n') as release_scan_fo:
        scans = [s.rstrip('\n') for s in release_scan_fo.readlines() if len(s) > 3]
    return scans


def download_release(release_scans, out_dir, file_types):
    print('Downloading ScanNet release to ' + out_dir + '...')
    for scan_id in release_scans:
        scan_out_dir = os.path.join(out_dir, scan_id)
        download_scan(scan_id, scan_out_dir, file_types)
    print('Downloaded ScanNet release.')


def download_file(url, out_file):
    conn_reset_retry = 3 #needed for some http connection resets; typically at ~828MB
    for _ in range(conn_reset_retry):
        try:
            download_file_with_resume(url, out_file, try_resume_bytes=0, total_sz = None, params={})
        except:
            time.sleep(1.2) #prevent connection overload
            continue
        break

def download_scan(scan_id, out_dir, file_types):
    print('Downloading ScanNet scan ' + scan_id + ' ...')
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
    for ft in file_types:
        url = BASE_URL + RELEASE + '/' + scan_id + '/' + scan_id + ft
        out_file = out_dir + '/' + scan_id + ft
        download_file(url, out_file)
    print('Downloaded scan ' + scan_id)


def download_task_data(out_dir):
    print('Downloading ScanNet task data...')
    files = [
        'scannet-labels.combined.tsv', 'obj_classification/data.zip',
        'obj_classification/trained_models.zip', 'voxel_labeling/data.zip',
        'voxel_labeling/trained_models.zip'
    ]
    for file in files:
        url = BASE_URL + RELEASE_TASKS + '/' + file
        localpath = os.path.join(out_dir, file)
        localdir = os.path.dirname(localpath)
        if not os.path.isdir(localdir):
          os.makedirs(localdir)
        download_file(url, localpath)
    print('Downloaded task data.')


def download_label_map(out_dir):
    print('Downloading label mapping file...')
    files = [ 'scannet-labels.combined.tsv' ]
    for file in files:
        url = BASE_URL + RELEASE_TASKS + '/' + file
        localpath = os.path.join(out_dir, file)
        localdir = os.path.dirname(localpath)
        if not os.path.isdir(localdir):
          os.makedirs(localdir)
        download_file(url, localpath)
    print('Downloaded label mapping file.')


def download_rob_task_data(out_dir, scan_ids=[]):
    type = 'all' if len(scan_ids) == 0 else str(len(scan_ids))
    print('Downloading ScanNet Robust Vision task data for ' + type + ' scans...')
    if not os.path.isdir(out_dir):
        os.makedirs(out_dir)
        
    download_file(TOS_URL, out_dir + '/ScanNet_TOS.pdf')
    if len(scan_ids) == 0: # download all
        url = BASE_URL + '/v2/tasks/scannet_frames_25k.zip'
        out_file = out_dir + '/scannet_frames_25k.zip'
        download_file(url, out_file)
        url = BASE_URL + '/v2/tasks/scannet_frames_test.zip'
        out_file = out_dir + '/scannet_frames_test.zip'
        download_file(url, out_file)
    else:
        for scan_id in scan_ids:
            url = BASE_URL + RELEASE_TASKS + '/rob_tasks/' + scan_id + '.zip'
            out_file = out_dir + '/' + scan_id + '.zip'
            download_file(url, out_file)
    print('Downloaded ROB task data.')


def main():
    parser = argparse.ArgumentParser(description='Downloads ScanNet public data release.')
    parser.add_argument('-o', '--out_dir', required=True, help='directory in which to download')
    parser.add_argument('--task_data', action='store_true', help='whether to download task data')
    parser.add_argument('--rob_task_data', action='store_true', help='only download robust vision challenge task data.')
    parser.add_argument('--label_map', action='store_true', help='whether to download label map file')
    parser.add_argument('--id', help='specific scan id to download')
    parser.add_argument('--type', help='specific file type to download (.aggregation.json, .sens, .txt, _vh_clean.ply, _vh_clean_2.0.010000.segs.json, _vh_clean_2.ply, _vh_clean.segs.json, _vh_clean.aggregation.json, _vh_clean_2.labels.ply, _2d-instance.zip, _2d-instance-filt.zip, _2d-label.zip, _2d-label-filt.zip)')
    args = parser.parse_args()

    print('By executing this script you confirm that you have agreed to the ScanNet terms of use as described at:')
    print(TOS_URL)
    #print('***')
    #print('Press any key to continue, or CTRL-C to exit.')
    #key = raw_input('')

    release_file = BASE_URL + RELEASE + '.txt'
    release_scans = get_release_scans(release_file)
    file_types = FILETYPES;

    if args.type:  # download file type
        file_type = args.type
        if file_type not in FILETYPES:
            print('ERROR: Invalid file type: ' + file_type)
            return
        file_types = [file_type]
    if args.task_data:  # download task data
        download_task_data(args.out_dir)
    elif args.label_map:  # download label map file
        download_label_map(args.out_dir)
    elif args.id:  # download single scan
        scan_id = args.id
        if scan_id not in release_scans:
            print('ERROR: Invalid scan id: ' + scan_id)
        else:
            if args.rob_task_data:
                download_rob_task_data(args.out_dir, [scan_id])
            else:
                out_dir = os.path.join(args.out_dir, scan_id)
                download_scan(scan_id, out_dir, file_types)
    elif args.rob_task_data:  # download rob task data
        download_rob_task_data(args.out_dir)
    else:  # download entire release
        if len(file_types) == len(FILETYPES):
            print('WARNING: You are downloading the entire ScanNet release which requires ' + RELEASE_SIZE + ' of space.')
        else:
            print('WARNING: You are downloading all ScanNet scans of type ' + file_types[0])
        print('Note that existing scan directories will be skipped. Delete partially downloaded directories to re-download.')
        print('***')
        #print('Press any key to continue, or CTRL-C to exit.')
        #key = raw_input('')
        download_release(release_scans, args.out_dir, file_types)


if __name__ == "__main__": main()

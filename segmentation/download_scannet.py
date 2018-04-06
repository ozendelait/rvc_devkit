#!/usr/bin/env python
# Downloads ScanNet public data release
# Run with ./download-scannet.py (or python download-scannet.py on Windows)
# -*- coding: utf-8 -*-
import argparse
import os
import urllib
import tempfile

BASE_URL = 'http://dovahkiin.stanford.edu/scannet-public/'
TOS_URL = BASE_URL + 'ScanNet_TOS.pdf'
FILETYPES = ['.aggregation.json', '.sens', '.txt', '_vh_clean.ply', '_vh_clean_2.0.010000.segs.json', '_vh_clean_2.ply', '_vh_clean.segs.json', '_vh_clean.aggregation.json', '_vh_clean_2.labels.ply', '_2d-instance.zip', '_2d-instance-filt.zip', '_2d-label.zip', '_2d-label-filt.zip']
RELEASE = 'v1/scans'
RELEASE_TASKS = 'v1/tasks/'
RELEASE_SIZE = '1.2TB'


def get_release_scans(release_file):
    scan_lines = urllib.urlopen(release_file)
    scans = []
    for scan_line in scan_lines:
        scan_id = scan_line.rstrip('\n')
        scans.append(scan_id)
    return scans


def download_release(release_scans, out_dir, file_types):
    print('Downloading ScanNet release to ' + out_dir + '...')
    for scan_id in release_scans:
        scan_out_dir = os.path.join(out_dir, scan_id)
        download_scan(scan_id, scan_out_dir, file_types)
    print('Downloaded ScanNet release.')


def download_file(url, out_file):
    out_dir = os.path.dirname(out_file)
    if not os.path.isfile(out_file):
        print('\t' + url + ' > ' + out_file)
        fh, out_file_tmp = tempfile.mkstemp(dir=out_dir)
        f = os.fdopen(fh, 'w')
        f.close()
        urllib.urlretrieve(url, out_file_tmp)
        os.rename(out_file_tmp, out_file)
    else:
        print('WARNING: skipping download of existing file ' + out_file)

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
    if len(scan_ids) == 0: # download all
        url = BASE_URL + RELEASE_TASKS + '/rob_tasks/scenes_all.zip'
        out_file = out_dir + '/scenes_all.zip'
        download_file(url, out_file)
        url = BASE_URL + RELEASE_TASKS + '/rob_tasks/scenes_test.zip'
        out_file = out_dir + '/scenes_test.zip'
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

    print('By pressing any key to continue you confirm that you have agreed to the ScanNet terms of use as described at:')
    print(TOS_URL)
    print('***')
    print('Press any key to continue, or CTRL-C to exit.')
    key = raw_input('')

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
        print('Press any key to continue, or CTRL-C to exit.')
        key = raw_input('')
        download_release(release_scans, args.out_dir, file_types)


if __name__ == "__main__": main()

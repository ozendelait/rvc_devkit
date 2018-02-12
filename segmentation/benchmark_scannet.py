import math
import os.path as op
import png
import shutil

from benchmark import *
from benchmark_kitti2015 import KITTI2015
from dataset_format_kitti2015 import *
from util import *
from util_segmentation import *
import download_scannet

import numpy as np
import scipy.misc as sp


class ScanNet(KITTI2015):

    def Name(self):
        return 'ScanNet Instance-Level Semantic Labeling Task'
    
    
    def Prefix(self):
        return 'ScanNet_'
    
    
    def Website(self):
        return 'http://www.scan-net.org/'
    
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return False
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        print('By pressing any key to continue you confirm that you have agreed to the ScanNet terms of use as described at:')
        print('http://dovahkiin.stanford.edu/scannet-public/ScanNet_TOS.pdf')
        print('***')
        print('Press any key to continue, or CTRL-C to exit.')
        key = raw_input('')
        scannet_train_scans = download_scannet.get_release_scans('http://dovahkiin.stanford.edu/scannet-public/v1/scans.txt')
        download_scannet.download_rob_task_data(op.join(archive_dir_path, 'train'), scannet_train_scans)
        expected_train_archives = [os.path.join(op.join(archive_dir_path,  'train'), scan + '.zip') for scan in scannet_train_scans]
        scannet_test_scans = download_scannet.get_release_scans('http://dovahkiin.stanford.edu/scannet-public/v1/scannet_rob_test.txt')
        download_scannet.download_rob_task_data(op.join(archive_dir_path, 'test'), scannet_test_scans)
        expected_test_archives = [os.path.join(op.join(archive_dir_path, 'test'), scan + '.zip') for scan in scannet_test_scans]

        # Try to unpack input and ground truth files
        self.ExtractDownloadArchives(expected_train_archives, op.join(unpack_dir_path, 'scannet', 'train'))
        self.ExtractDownloadArchives(expected_test_archives, op.join(unpack_dir_path, 'scannet', 'test'))


    def ExtractDownloadArchives(self, expected_archives, unpack_dir_path):
        missing_archives = []
        for archive_path in expected_archives:
            if not op.isfile(archive_path):
                missing_archives.append(archive_path)

        # Extract archives
        if not missing_archives:
            for archive_path in expected_archives:
                UnzipFile(archive_path, unpack_dir_path)
        # Report missing files
        else:
            for missing_archive in missing_archives:
                print('ERROR: Could not find: ' + missing_archive)
            print('%s must be downloaded manually. Please register at %s\nto download the data and place it '
                  'according to the path(s) above.' % (self.Prefix()[:-1], self.Website()))
            sys.exit(1)


    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)


    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        train_path = op.join(unpack_dir_path, 'scannet', 'train')
        scenes = os.listdir(train_path)
        for scene in scenes:
            scene_path = op.join(train_path, scene)
            color_path = os.path.join(scene_path, 'color')
            instance_path = os.path.join(scene_path, 'instance')
            label_path = os.path.join(scene_path, 'label')
            files = os.listdir(color_path)
            for f in files:
                shutil.move(op.join(color_path, f), op.join(training_dir_path, 'image_2', self.Prefix() + scene + '_' + f))
            files = os.listdir(instance_path)
            for f in files:
                shutil.move(op.join(instance_path, f), op.join(training_dir_path, 'instance', self.Prefix() + scene + '_' + f))
            files = os.listdir(label_path)
            for f in files:
                shutil.move(op.join(label_path, f), op.join(training_dir_path, 'semantic', self.Prefix() + scene + '_' + f))
        test_path = op.join(unpack_dir_path, 'scannet', 'test')
        scenes = os.listdir(test_path)
        for scene in scenes:
            scene_path = op.join(test_path, scene)
            color_path = os.path.join(scene_path, 'color')
            files = os.listdir(color_path)
            for f in files:
                shutil.move(op.join(color_path, f), op.join(test_dir_path, 'image_2', self.Prefix() + scene + '_' + f))


    def CanCreateSubmissionFromFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)
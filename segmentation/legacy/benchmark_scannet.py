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
        return 'ScanNet Semantic Labeling Task'
    
    
    def Prefix(self):
        return 'ScanNet_'
    
    
    def Website(self):
        return 'http://www.scan-net.org/'
    
    def LabelIds(self):
        return [34,35,36,37,38,39,40,41,42,43,44,45,47,49,57,61,66,67,69,72]

    def LabelNames(self):
        return ["wall","floor","cabinet","bed","chair","sofa","table","door",
        "window","bookshelf","picture","counter","desk","curtain","refridgerator",
        "shower curtain","toilet","sink","bathtub","otherfurniture"]
    
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
        #scannet_train_scans = download_scannet.get_release_scans('http://dovahkiin.stanford.edu/scannet-public/v1/scans.txt')
        #download_scannet.download_rob_task_data(op.join(archive_dir_path, 'train'), scannet_train_scans)
        #expected_train_archives = [os.path.join(op.join(archive_dir_path,  'train'), scan + '.zip') for scan in scannet_train_scans]
        #scannet_test_scans = download_scannet.get_release_scans('http://dovahkiin.stanford.edu/scannet-public/v1/scannet_rob_test.txt')
        #download_scannet.download_rob_task_data(op.join(archive_dir_path, 'test'), scannet_test_scans)
        #expected_test_archives = [os.path.join(op.join(archive_dir_path, 'test'), scan + '.zip') for scan in scannet_test_scans]
        download_scannet.download_rob_task_data(archive_dir_path)
        expected_train_archives = [os.path.join(archive_dir_path, 'scenes_all.zip')]
        expected_test_archives = [os.path.join(archive_dir_path, 'scenes_test.zip')]

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

    def CreateSubmission(self, task_name, dataset_format, method, pack_dir_path,
                         metadata_dict, training_dir_path, training_datasets,
                         test_dir_path, test_datasets, archive_base_path):

        # do we want semantic and instance results to be packed into the same submission?
        # currently, separate directories and archives are created
        archive_base_path = op.join(archive_base_path + "_" + task_name)
        method_dir = op.join(pack_dir_path, method + "_" + task_name)

        if task_name == "semantic":
            archive_filename = self.CreateSemanticSubmission(task_name, method, method_dir, pack_dir_path,
                                                             test_dir_path, test_datasets, archive_base_path)

        if task_name == "instance":
            archive_filename = self.CreateInstanceSubmission(task_name, method, method_dir, pack_dir_path,
                                                             test_dir_path, test_datasets, archive_base_path)

        return archive_filename


    def CreateSemanticSubmission(self, task_name, method, method_dir, pack_dir_path,
                                 test_dir_path, test_datasets, archive_base_path):

        MakeDirsExistOk(op.join(method_dir, task_name))

        # copy semantic segmentation results
        for rob_name, original_name in test_datasets:
            src_img = op.join(test_dir_path, "algo_%s_semantic" % method, rob_name)
            tgt_img = op.join(method_dir, task_name, original_name)
            shutil.copy(src_img, tgt_img)

        # create archive and clean up
        archive_filename = ZipDirectory(archive_base_path, method_dir)
        DeleteFolderContents(pack_dir_path)

        return archive_filename


    def CreateInstanceSubmission(self, task_name, method, method_dir, pack_dir_path,
                                 test_dir_path, test_datasets, archive_base_path):

        # prepare source directories and retrieve all binary instance mask names
        src_pred_list_dir = op.join(test_dir_path, "algo_%s_instance" % method, "pred_list")
        src_pred_img_dir = op.join(test_dir_path, "algo_%s_instance" % method, "pred_img")
        mask_names = [op.splitext(img)[0] for img in os.listdir(src_pred_img_dir) if img.startswith(self.Prefix())]

        # prepare target directories
        tgt_pred_list_dir = op.join(method_dir, task_name, "pred_list")
        tgt_pred_img_dir = op.join(method_dir, task_name, "pred_img")
        MakeDirsExistOk(tgt_pred_list_dir)
        MakeDirsExistOk(tgt_pred_img_dir)
        labeIds = self.LabelIds()

        # for each image: copy the list file and all corresponding mask files
        for rob_name, original_name in test_datasets:

            # read original mask list file
            with open(op.join(src_pred_list_dir, rob_name.replace(".jpg", ".txt")), "r") as f:
                lines = f.readlines()

            # save converted file with removed prefixes
            with open(op.join(tgt_pred_list_dir, original_name.replace(".jpg", ".txt")), "w") as f:
                for line in lines:
                    relative_path, label_id, confidence = line.strip().split(" ")
                    if int(label_id) in labeIds:
                        relative, subdir, img_name = relative_path.split("/")
                        new_line = "%s/%s/%s %s %s\n" % (
                        relative, subdir, img_name[len(self.Prefix()):], label_id, confidence)
                        f.write(new_line)

            # copy all binary masks for the given image
            img_masks = [img for img in mask_names if img.startswith(op.splitext(rob_name)[0])]
            for img_mask in img_masks:
                src_mask = op.join(test_dir_path, "algo_%s_instance" % method, "pred_img", img_mask + ".png")
                tgt_mask = op.join(tgt_pred_img_dir, img_mask[len(self.Prefix()):] + ".png")
                shutil.copy2(src_mask, tgt_mask)

        archive_filename = ZipDirectory(archive_base_path, op.join(method_dir,task_name))
        DeleteFolderContents(pack_dir_path)

        return archive_filename
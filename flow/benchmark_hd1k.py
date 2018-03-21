import argparse
import math
import png
import shutil
import struct

from benchmark import *
from dataset_format_middlebury import *
from dataset_format_kitti2015 import *
from util import *
from util_flow import *
from benchmark_kitti2015 import Kitti2015


class HD1K2018(Kitti2015):
    def Name(self):
        return "HD1K Flow Challenge 2018"


    def Prefix(self):
        return "HD1K2018_"


    def Website(self):
        return 'http://hci-benchmark.org/flow'


    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        # Download input images (training)
        DownloadAndUnzipFile('http://hci-benchmark.org/media/downloads/hd1k_input.zip', archive_dir_path, unpack_dir_path)

        # Download ground truth for left view files (training)
        DownloadAndUnzipFile('http://hci-benchmark.org/media/downloads/hd1k_flow_gt.zip', archive_dir_path, unpack_dir_path)

        # Download input images (test)
        DownloadAndUnzipFile('http://hci-benchmark.org/media/downloads/hd1k_challenge.zip', archive_dir_path, unpack_dir_path)

        # Uncertainty maps for the optical flow ground truth are here:
        # 'http://hci-benchmark.org/media/downloads/hd1k_flow_uncertainty.zip'


    def ConvertToKittiFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Move the downloaded files to the target directory structure
        base_input_dir = os.path.join(unpack_dir_path, 'hd1k_input')
        base_gt_dir = os.path.join(unpack_dir_path, 'hd1k_flow_gt')
        base_test_dir = os.path.join(unpack_dir_path, 'hd1k_challenge')

        # Move input image sequences
        self._MoveKittiFiles('image_2', base_input_dir, training_dir_path)

        # Move optical flow ground truth
        self._MoveKittiFiles('flow_occ', base_gt_dir, training_dir_path)

        # Move input image sequences
        self._MoveKittiFiles('image_2', base_test_dir, test_dir_path)

        # Delete original folders
        dir_paths = [base_input_dir, base_gt_dir]
        for dir_path in dir_paths:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)


    def _MoveKittiFiles(self, dir_name, src_dir_base_path, dest_dir_base_path):
        src_dir_path = os.path.join(src_dir_base_path, dir_name)
        dest_dir_path = os.path.join(dest_dir_base_path, dir_name)

        # Move files
        MakeDirsExistOk(dest_dir_path)
        for file_name in os.listdir(src_dir_path):
            src_file_path = os.path.join(src_dir_path, file_name)
            dest_file_path = os.path.join(dest_dir_path, self.Prefix() + file_name)
            shutil.move(src_file_path, dest_file_path)


    def ConvertToMiddleburyFormat(self, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        # Move the downloaded files to the target directory structure
        base_input_dir = os.path.join(unpack_dir_path, 'hd1k_input')
        base_gt_dir = os.path.join(unpack_dir_path, 'hd1k_flow_gt')
        base_test_dir = os.path.join(unpack_dir_path, 'hd1k_challenge')

        src_image_dir_path = os.path.join(base_input_dir, 'image_2')  # contains left images (training)
        src_gt_dir_path = os.path.join(base_gt_dir, 'flow_occ')  # contains flow ground truth (training)
        src_test_dir_path = os.path.join(base_test_dir, 'image_2')  # contains left images (test)

        outdir_training_images = os.path.join(training_dir_path, 'images')
        outdir_training_flow = os.path.join(training_dir_path, 'flow')
        outdir_test_images = os.path.join(test_dir_path, 'images')

        # Move input image sequences (training)
        self._MoveMiddleburyFiles(src_image_dir_path, outdir_training_images)

        # Move optical flow ground truth (training)
        self._MoveMiddleburyFiles(src_gt_dir_path, outdir_training_flow, convert_to_flo=True)

        # Move input image sequences (test)
        self._MoveMiddleburyFiles(src_test_dir_path, outdir_test_images)

        # Delete original folders
        dir_paths = [base_input_dir, base_gt_dir]
        for dir_path in dir_paths:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)


    def _MoveMiddleburyFiles(self, src_dir_path, dest_dir_path, convert_to_flo=False):
        for image in os.listdir(src_dir_path):
            img_sequence = image.split("_")[0]
            img_frame = int(os.path.splitext(image)[0].split("_")[1])

            src_file_path = os.path.join(src_dir_path, image)
            dest_sequence_dir_path = os.path.join(dest_dir_path, "%s%s" % (self.Prefix(), img_sequence))
            MakeDirsExistOk(dest_sequence_dir_path)

            if convert_to_flo:
                dest_file_path = os.path.join(dest_sequence_dir_path, "frame_%04d.flo" % img_frame)
                ConvertKittiPngToMiddleburyFlo(src_file_path, dest_file_path)
            else:
                dest_file_path = os.path.join(dest_sequence_dir_path, "frame_%04d.png" % img_frame)
                shutil.move(src_file_path, dest_file_path)
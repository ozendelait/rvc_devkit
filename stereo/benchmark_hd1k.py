import argparse
import math
import png
import shutil

from benchmark import *
from dataset_format_middlebury2014 import *
from util import *
from util_stereo import *
from benchmark_kitti2015 import Kitti2015


class HD1K2018(Kitti2015):
    def Name(self):
        return "HD1K Stereo Challenge 2018"
    
    
    def Prefix(self):
        return "HD1K2018_"
    
    
    def Website(self):
        return 'http://hci-benchmark.org/stereo'


    def GetOptions(self, metadata_dict):
        parser = argparse.ArgumentParser()
        parser.add_argument('--hd1k_with_unc', action='store_true', default=False)
        args, unknown = parser.parse_known_args()
        metadata_dict['with_uncertainties'] = args.hd1k_with_unc


    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        # Download input images (training)
        DownloadAndUnzipFile('http://hci-benchmark.org/media/downloads/hd1k_input.zip', archive_dir_path, unpack_dir_path)

        # Download ground truth and calibration files for left view (training)
        DownloadAndUnzipFile('http://hci-benchmark.org/media/downloads/hd1k_stereo_gt.zip', archive_dir_path, unpack_dir_path)

        if metadata_dict['with_uncertainties']:
            # Download uncertainty maps for ground truth (training)
            DownloadAndUnzipFile('http://hci-benchmark.org/media/downloads/hd1k_stereo_uncertainty.zip', archive_dir_path, unpack_dir_path)

        # NOTE: Input images for the test set will soon be available at:
        # 'http://hci-benchmark.org/media/downloads/hd1k_stereo_flow_challenge.zip'


    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        base_input_path = os.path.join(unpack_dir_path, 'hd1k_input')
        base_gt_path = os.path.join(unpack_dir_path, 'hd1k_stereo_gt')
        base_unc_path = os.path.join(unpack_dir_path, 'hd1k_stereo_uncertainty')

        src_image_left_path = os.path.join(base_input_path, 'image_2')  # contains left images
        src_image_right_path = os.path.join(base_input_path, 'image_3')  # contains right images
        src_gt_path = os.path.join(base_gt_path, 'disp_occ_0')  # contains stereo ground truth
        src_calib_path = os.path.join(base_gt_path, 'calib')  # contains calibration files
        src_unc_path = os.path.join(base_unc_path, 'disp_unc')  # contains uncertainties

        for image_name in os.listdir(src_image_left_path):
            dataset_name = os.path.splitext(image_name)[0]  # remove file extension

            output_dataset_path = os.path.join(training_dir_path, self.Prefix() + dataset_name)
            MakeDirsExistOk(output_dataset_path)

            # Move images
            shutil.move(os.path.join(src_image_left_path, image_name), os.path.join(output_dataset_path, 'im0.png'))
            shutil.move(os.path.join(src_image_right_path, image_name), os.path.join(output_dataset_path, 'im1.png'))

            # Create calib.txt
            calib_input_path = os.path.join(src_calib_path, image_name.replace(".png", ".txt"))
            calib = ReadMiddlebury2014CalibFile(calib_input_path)

            width = calib['width']
            height = calib['height']
            ndisp = calib['ndisp']
            cam0 = calib['cam0'].replace(";", "").replace("[", "").replace("]", "").strip()
            [left_fx, _, left_cx, _, left_fy, left_cy, _, _, _] = cam0.split(" ")
            cam1 = calib['cam1'].replace(";", "").replace("[", "").replace("]", "").strip()
            [right_fx, _, right_cx, _, right_fy, right_cy, _, _, _] = cam1.split(" ")

            # NOTE: The parameters below are unknown, setting them all to zero
            #       (which might be better compatible with parsers than setting
            #        them to NaN).
            baseline_in_mm = 0

            calib_output_path = os.path.join(output_dataset_path, 'calib.txt')
            WriteMiddlebury2014CalibFile(
                calib_output_path,
                int(left_fx), int(left_fy), int(left_cx), int(left_cy),
                int(right_fx), int(right_fy), int(right_cx), int(right_cy),
                baseline_in_mm,
                int(width),
                int(height),
                int(ndisp))

            # Convert and move disparity maps
            src_occ_0_path = os.path.join(src_gt_path, image_name)
            dest_occ_0_path = os.path.join(output_dataset_path, 'disp0GT.pfm')
            ConvertKitti2015PngToMiddlebury2014Pfm(src_occ_0_path, dest_occ_0_path)

            # Convert and move uncertainty maps
            if metadata_dict['with_uncertainties']:
                src_unc_0_path = os.path.join(src_unc_path, image_name)
                dest_unc_0_path = os.path.join(output_dataset_path, 'disp0Unc.pfm')
                ConvertKitti2015PngToMiddlebury2014Pfm(src_unc_0_path, dest_unc_0_path)

        # Delete original folders
        dir_paths = [base_input_path, base_gt_path, base_unc_path]
        for dir_path in dir_paths:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
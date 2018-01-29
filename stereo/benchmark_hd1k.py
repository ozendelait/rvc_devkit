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
        return 'http://hci-benchmark.org/benchmark/table?hc=stereo'


    def GetOptions(self, metadata_dict):
        parser = argparse.ArgumentParser()
        parser.add_argument('--hd1k_with_uncertainties', action='store_true',
                            help='Download optional uncertainty maps for the stereo ground truth of the HD1K dataset.')
        args, unknown = parser.parse_known_args()

        if args.hd1k_with_uncertainties is not None:
            metadata_dict['with_uncertainties'] = args.hd1k_with_uncertainties
        else:
            print('Please choose whether uncertainty maps for the stereo ground truth '
                  'should be downloaded [y] or not [n]:')
            while True:
                response = GetUserInput("> ")
                if response == 'y':
                    print('')
                    metadata_dict['with_uncertainties'] = True
                    break
                elif response == 'n':
                    metadata_dict['with_uncertainties'] = False
                    break
                else:
                    print('Please enter y or n.')


    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):

        # Download input images and calibration files (training)
        DownloadAndUnzipFile('http://hci-benchmark.org/media/downloads/hd1k_input.zip', archive_dir_path, unpack_dir_path)

        # Download ground truth for left view (training)
        DownloadAndUnzipFile('http://hci-benchmark.org/media/downloads/hd1k_stereo_gt.zip', archive_dir_path, unpack_dir_path)

        if metadata_dict['with_uncertainties']:
            # Download uncertainty maps for ground truth (training)
            DownloadAndUnzipFile('http://hci-benchmark.org/media/downloads/hd1k_stereo_uncertainty.zip', archive_dir_path, unpack_dir_path)

        # NOTE: Input images for the test set will soon be available at:
        # 'http://hci-benchmark.org/media/downloads/hd1k_stereo_flow_challenge.zip'


    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        src_input_path = os.path.join(unpack_dir_path, 'hd1k_input')
        src_gt_path = os.path.join(unpack_dir_path, 'hd1k_stereo_gt')
        src_unc_path = os.path.join(unpack_dir_path, 'hd1k_stereo_uncertainty')

        image_2_path = os.path.join(src_input_path, 'image_2')  # contains left images
        image_3_path = os.path.join(src_input_path, 'image_3')  # contains right images
        calib_path = os.path.join(src_input_path, 'calib')  # contains calibration files

        for image_name in os.listdir(image_2_path):
            dataset_name = image_name[:image_name.rfind('.')]  # remove file extension
            if dataset_name.endswith('_11'):
                continue  # These files are for flow only, skip them

            output_dataset_path = os.path.join(training_dir_path, self.Prefix() + dataset_name)
            MakeDirsExistOk(output_dataset_path)

            # Move images
            shutil.move(os.path.join(image_2_path, image_name),
                        os.path.join(output_dataset_path, 'im0.png'))
            shutil.move(os.path.join(image_3_path, image_name),
                        os.path.join(output_dataset_path, 'im1.png'))

            # Create calib.txt
            calib_input_path = os.path.join(calib_path, image_name.replace(".png", ".txt"))
            calib = ReadMiddlebury2014CalibFile(calib_input_path)

            width = calib['width']
            height = calib['height']
            ndisp = calib['ndisp']
            cam0 = calib['cam0'].replace(";", "").replace("[", "").replace("]", "").strip()
            [left_fx, _, left_cx, _, left_fy, left_cy, _, _, _] = cam0.split(" ")
            right_fx = left_fx
            right_fy = left_fy
            right_cx = left_cx
            right_cy = left_cy

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
            src_occ_0_path = os.path.join(src_gt_path, 'disp_occ_0', image_name)
            dest_occ_0_path = os.path.join(output_dataset_path, 'disp0GT.pfm')
            ConvertKitti2015PngToMiddlebury2014Pfm(src_occ_0_path, dest_occ_0_path)

            # Convert and move uncertainty maps
            if metadata_dict['with_uncertainties']:
                src_unc_0_path = os.path.join(src_unc_path, 'disp_unc_0', image_name)
                dest_unc_0_path = os.path.join(output_dataset_path, 'disp0Unc.pfm')
                ConvertKitti2015PngToMiddlebury2014Pfm(src_unc_0_path, dest_unc_0_path)

        # Delete original folders
        dir_paths = [src_input_path, src_gt_path, src_unc_path]
        for dir_path in dir_paths:
            if os.path.isdir(dir_path):
                shutil.rmtree(dir_path)
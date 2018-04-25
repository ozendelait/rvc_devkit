import math
import os.path as op
import png
import shutil

from benchmark import *
from dataset_format_kitti2015 import *
from util import *
from util_segmentation import *
from benchmark_cityscapes import Cityscapes


class WildDash(Cityscapes):
    def Name(self):
        return 'WildDash Segmentation 2018'
    
    
    def Prefix(self):
        return 'WildDash_'
    
    
    def Website(self):
        return 'http://wilddash.cc/'
    
    def LabelIds(self):
        return range(0,34)

    def LabelNames(self):
        return ["unlabeled","ego vehicle","rectification border","out of roi","static",
                "dynamic","ground","road","sidewalk","parking","rail track","building","wall","fence",
                "guard rail","bridge","tunnel","pole","polegroup","traffic light","traffic sign","vegetation",
                "terrain","sky","person","rider","car","truck","bus","caravan","trailer","train","motorcycle",
                "bicycle"]
    
    def SupportsTrainingDataOnlySubmissions(self):
        return False
    
    
    def SupportsTrainingDataInFullSubmissions(self):
        return False
    
    
    def GetOptions(self, metadata_dict):
        return  # No options
    
    
    def DownloadAndUnpack(self, archive_dir_path, unpack_dir_path, metadata_dict):
        file_path = op.join(archive_dir_path, 'wd_val_01.zip')
        file_path_test = op.join(archive_dir_path, 'wd_both_01.zip')

        expected_archives = [file_path,file_path_test]

        # Try to unpack input and ground truth files
        self.ExtractManualDownloadArchives(expected_archives, op.join(unpack_dir_path, self.Prefix() + 'dirs'))


    def CanConvertOriginalToFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)


    def ConvertOriginalToFormat(self, dataset_format, unpack_dir_path, metadata_dict, training_dir_path, test_dir_path):
        src_dir_path = op.join(unpack_dir_path, self.Prefix() + 'dirs', 'wd_val_01')
        src_dir_path_test = op.join(unpack_dir_path, self.Prefix() + 'dirs', 'wd_both_01')

        # Read the image file names
        img_names = ['_'.join(f.split('_')[:2]) for f in os.listdir(src_dir_path) if
                     op.isfile(op.join(src_dir_path, f)) and f.endswith('_polygons.json')]

        for img_name in img_names:
            # Move the training image data
            shutil.move(op.join(src_dir_path, img_name + '.png'),
                        op.join(training_dir_path, 'image_2', self.Prefix() + img_name + '.png'))

            # Copy the semantic segmentation files
            shutil.copy2(op.join(src_dir_path, img_name + "_labelIds.png"),
                         op.join(training_dir_path, 'semantic', self.Prefix() + img_name + ".png"))

            # Convert the instance files to the Kitti2015 format
            src_path_cs_instance = op.join(src_dir_path, img_name + '_instanceIds.png')
            src_path_cs_semantic = op.join(src_dir_path, img_name + '_labelIds.png')
            dest_path = op.join(training_dir_path, 'instance', self.Prefix() + img_name + '.png')
            cs_instance = sp.imread(src_path_cs_instance)
            kitti_instance = ConvertCityscapesToKittiInstances(cs_instance)
            SaveKittiInstance(kitti_instance,dest_path)

        # Read the image file names
        img_names_test = [f.split('.')[0] for f in os.listdir(src_dir_path_test) if
                     op.isfile(op.join(src_dir_path_test, f)) and f.endswith('.png')]
        for img_name in img_names_test:
            # Move the training image data
            shutil.move(op.join(src_dir_path_test, img_name + '.png'),
                        op.join(test_dir_path, 'image_2', self.Prefix() + img_name + '.png'))

        shutil.rmtree(op.join(unpack_dir_path, self.Prefix() + 'dirs'))


import math
import os.path as op
import png
import shutil

from benchmark import *
from benchmark_kitti2015 import KITTI2015
from dataset_format_kitti2015 import *
from util import *
from util_segmentation import *



class Cityscapes(KITTI2015):

    def Name(self):
        return 'Cityscapes Semantic Labeling Task'
    
    
    def Prefix(self):
        return 'Cityscapes_'
    
    
    def Website(self):
        return 'https://cityscapes-dataset.com/'
    
    def LabelIds(self):
        return range(0,33)

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
        input_file_path = op.join(archive_dir_path, 'leftImg8bit_trainvaltest.zip')
        gt_file_path = op.join(archive_dir_path, 'gtFine_trainvaltest.zip')
        expected_archives = [input_file_path, gt_file_path]

        # Try to unpack input and ground truth files
        self.ExtractManualDownloadArchives(expected_archives, op.join(unpack_dir_path, self.Prefix() + 'dirs'))


    def ExtractManualDownloadArchives(self, expected_archives, unpack_dir_path):
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
        print("Converting Cityscapes to %s ..."%dataset_format.Identifier()) 

        img_dir_path = op.join(unpack_dir_path, self.Prefix() + 'dirs', 'leftImg8bit')
        gt_dir_path = op.join(unpack_dir_path, self.Prefix() + 'dirs', 'gtFine')

        # Retrieve the dataset splits (train, test, val)
        splits = [d for d in os.listdir(img_dir_path) if op.isdir(op.join(img_dir_path, d))]

        # Move the training data
        for split in splits:

            # Extract all cities
            city_names = [c for c in os.listdir(op.join(img_dir_path, split)) if op.isdir(op.join(img_dir_path, split, c))]

            for city in city_names:
                city_img_dir_path = op.join(img_dir_path, split, city)
                city_gt_dir_path = op.join(gt_dir_path, split, city)

                # Read the image file names without the prefix
                img_names = ['_'.join(f.split('_')[:3]) for f in os.listdir(city_img_dir_path) if op.isfile(op.join(city_img_dir_path, f))]

                for img_name in img_names:
                    if split == 'test':
                        # Move the test image data
                        shutil.move(op.join(city_img_dir_path, img_name + '_leftImg8bit.png'),
                                    op.join(test_dir_path, 'image_2', self.Prefix() + img_name + '.png'))
                    else:
                        # Move the training image data (train and val)
                        shutil.move(op.join(city_img_dir_path, img_name + '_leftImg8bit.png'),
                                    op.join(training_dir_path, 'image_2', self.Prefix() + img_name + '.png'))

                        # Copy the semantic segmentation files
                        shutil.copy2(op.join(city_gt_dir_path, img_name + "_gtFine_labelIds.png"),
                                     op.join(training_dir_path, 'semantic', self.Prefix() + img_name + ".png"))

                        # Convert the instance segmentation files to the Kitti2015 format
                        src_path_cs_instance = op.join(city_gt_dir_path, img_name + '_gtFine_instanceIds.png')
                        # src_path_cs_semantic = op.join(city_gt_dir_path, img_name + '_gtFine_labelIds.png')
                        dest_path = op.join(training_dir_path, 'instance', self.Prefix() + img_name + '.png')
                        cs_instance = sp.imread(src_path_cs_instance)
                        kitti_instance = ConvertCityscapesToKittiInstances(cs_instance)
                        SaveKittiInstance(kitti_instance,dest_path)

        shutil.rmtree(op.join(unpack_dir_path, self.Prefix() + 'dirs'))


    def CanCreateSubmissionFromFormat(self, dataset_format):
        return isinstance(dataset_format, KITTI2015Format)